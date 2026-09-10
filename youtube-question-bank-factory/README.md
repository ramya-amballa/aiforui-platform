# YouTube Question-Bank Video Factory

A local-first, batch-oriented pipeline that turns a question bank you supply
(XLSX/CSV/JSON) into narrated, rendered YouTube-ready MP4 videos --
without per-character TTS billing and without a ceiling on how many
questions you can process.

**This system never generates, searches for, or invents questions.**
You supply the question bank; the system explains, narrates, voices and
renders it.

```
QUESTION BANK (xlsx/csv/json)
        |
QUESTION INTAKE          normalize, validate, dedupe, assign IDs
        |
ANSWER VALIDATION AGENT  flags NEEDS_REVIEW, never overwrites your answer
        |
EXPLANATION AGENT        why correct is correct, why each wrong option is wrong
        |
NARRATION AGENT           deterministic teacher-style script (no AI call, no cost)
        |
LOCAL VOICE AGENT         Kokoro (primary) or Piper (fallback) - zero recurring cost
        |
AUDIO (wav/mp3 + timing)
        |
VIDEO RENDERER            Pillow + ffmpeg, template-driven, no LLM involved
        |
FINAL MP4 + QA + REPORTS
```

## Why this design

- **Zero recurring TTS cost.** Kokoro and Piper run entirely on your own
  hardware. There is no ElevenLabs/Polly/Azure-TTS bill, and no "free tier
  runs out at video 20" ceiling.
- **Batch-first, not one-question-at-a-time.** `produce` processes 1, 60,
  or 1,000+ questions in a single command with bounded concurrency. One
  question failing never stops the batch.
- **Resumable.** Every stage (validate/explain/narrate/audio/video) is
  content-hash cached. Kill the process at question 47 of 100 and re-run
  the same command -- it picks up at 48, and nothing already produced is
  regenerated, even across different video-batch splits of the same input.
- **Provider-independent.** The AI provider (explanation/narration
  reasoning support) and the TTS engine are both swappable via config/env,
  never hard-coded through the app. See "AI provider" and "TTS provider"
  below.
- **Human-in-the-loop by design, not an afterthought.** The Answer
  Validation Agent never silently changes your supplied answer. It flags
  `NEEDS_REVIEW` with its own reasoning and confidence, and production
  audio/video for those questions is withheld by default until a human
  clears them (or you explicitly opt in with `--include-needs-review`).

## Quickstart

See [SETUP.md](SETUP.md) for full installation instructions. Short version:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
sudo apt-get install ffmpeg          # or brew install ffmpeg on macOS
python scripts/download_models.py --engine kokoro   # one-time, ~350MB

python main.py produce --input examples/sample_questions.xlsx --video-size 6 --include-needs-review
```

`--include-needs-review` is only needed for this quick demo because the
default `AI_PROVIDER=local` has no external subject-matter knowledge and
therefore never clears its own confidence bar -- see "AI provider" below.
With a real provider configured, high-confidence questions flow straight
through with no flag required.

## CLI reference

```
python main.py ingest <file>                          Read/normalize/validate a question bank
python main.py validate --input <file>                 Run the Answer Validation Agent
python main.py explain  --input <file>                  ...through explanation
python main.py narrate  --input <file>                   ...through narration
python main.py voice    --input <file>                    ...through local TTS audio
python main.py render   --input <file> [--video-size N] [--manifest video.json] [--template default|minimal|exam]
python main.py qa       --input <file>                  Audio+video QA, writes reports/
python main.py produce  --input <file> [--video-size N] [--include-needs-review] [--batch N]
python main.py resume   [--job-id ID]                    Continue an interrupted job
python main.py status   [--job-id ID]                     Show per-question stage progress
python main.py retry-failed [--job-id ID]                  Re-run only FAILED questions
python main.py review   [--job-id ID]                       Print/export the human review queue
python main.py clean-cache [--namespace X] [--yes]           Clear cached artifacts
```

Every stage command shares the same batch pipeline as `produce` -- they
only differ in how far through the pipeline they run. Running `voice`
before `produce` is not wasted work: `produce` picks up exactly where the
cache leaves off.

### One video from a curated question list

Rather than splitting by size, point `render`/`produce` at a manifest:

```json
{ "title": "Top 10 AI Governance Questions", "questions": ["Q003", "Q014", "Q029", "Q041"] }
```

```bash
python main.py render --input questions.xlsx --manifest video_001.json
```

## Question bank format (XLSX/CSV/JSON)

| column | required | notes |
|---|---|---|
| `question_id` | no | auto-assigned (stable, content-derived) if blank |
| `question` | yes | |
| `option_a`..`option_d` | yes | all four required |
| `correct_answer` | yes | one of A/B/C/D |
| `topic`, `difficulty`, `source`, `notes` | no | passed through untouched |

Malformed rows are rejected with a reason, never silently dropped -- see
`reports/validation_report.csv` after `ingest`.

## AI provider (explanation/narration reasoning)

```yaml
ai:
  provider: local     # local | claude | openai | gemini
```

`local` is the zero-cost, zero-API-key, fully offline default. It composes
structurally valid explanations from the question's own fields but has no
external subject-matter knowledge, so its Answer Validation confidence
never clears the default 0.75 threshold -- every question is conservatively
flagged `NEEDS_REVIEW`. This is intentional: a provider with no way to
verify a fact should not claim confidence in it. For autonomous
high-confidence production, set `AI_PROVIDER=claude|openai|gemini` and the
matching API key in `.env` (see `.env.example`). Claude Code, the tool used
to build this project, is a development-time tool and is not assumed to be
available as a runtime API for the shipped application -- it is exactly
one of these three interchangeable options.

## TTS provider (local, zero recurring cost)

```yaml
tts:
  provider: kokoro           # kokoro | piper
  fallback_provider: piper   # used automatically if kokoro fails to load
```

Both run fully offline once their model weights are downloaded (one time,
via `scripts/download_models.py`). Nothing in the application imports
`kokoro_onnx` or `piper` directly outside `src/tts/` -- see "Voice Agent"
architecture in SETUP.md.

## Templates

`templates/default`, `templates/minimal`, `templates/exam` are pure YAML --
fonts, colors, layout, timer/reveal durations. Add a new look by adding a
new `templates/<name>/template.yaml`; the renderer code never changes.

## Known limitations

- The `local` AI provider's explanations are structurally complete but not
  subject-matter verified -- it is a zero-cost fallback/demo path, not a
  substitute for a real LLM provider in production use.
- Piper (the TTS fallback) is implemented against its real Python API but
  its voice weights are hosted on Hugging Face; on a network that blocks
  huggingface.co, download them from a machine that can reach it and copy
  the two files into `models/piper/`. Kokoro (the primary engine) has no
  such dependency and was verified end-to-end during development.
- `retry-failed` re-runs the audio pipeline for failed questions; a
  question whose *video* segment failed (audio succeeded) is retried by
  re-running `render`, which re-renders only segments whose content hash
  changed or is missing.
- The countdown/reveal visuals assume a question wraps to at most ~3 lines
  at the template's configured font size; an unusually long question can
  crowd the countdown badge. `qa` does not currently flag this.

## Project layout

See `SETUP.md` for the full directory reference and `config.yaml` for every
tunable setting (concurrency, retries, review thresholds, video resolution,
etc). No API keys are ever read from `config.yaml` -- only from the
environment / `.env` (gitignored).

---
Built for the AIforU&I platform tooling set.
