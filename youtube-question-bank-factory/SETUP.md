# Setup

## 1. Python version

Python 3.10+ (developed and tested on 3.11).

## 2. Virtual environment

```bash
cd youtube-question-bank-factory
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## 3. Dependencies

```bash
pip install -r requirements.txt
```

This installs: `click` (CLI), `pandas`/`openpyxl` (xlsx/csv), `numpy`,
`soundfile`/`pydub` (audio), `Pillow` (video frames), `kokoro-onnx`
(primary local TTS), `piper-tts` (fallback local TTS), `pytest`.

The commented-out lines at the bottom of `requirements.txt`
(`anthropic`/`openai`/`google-generativeai`) are **only** needed if you set
`AI_PROVIDER` to `claude`/`openai`/`gemini` in `config.yaml`. The default
`AI_PROVIDER=local` needs none of them.

If `pip install kokoro-onnx` or `piper-tts` fails to build on your system,
see Troubleshooting below.

## 4. FFmpeg

Required for audio format conversion and all video rendering.

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg   # or download a static build and add it to PATH
```

Verify: `ffmpeg -version`

## 5. Local TTS model installation (one-time, needs internet)

```bash
python scripts/download_models.py --engine kokoro
```

This downloads two files (~350MB total) into `models/`:
`kokoro-v1.0.onnx` and `voices-v1.0.bin`. They are gitignored -- every
machine that runs this project downloads them once, locally.

Optionally, also fetch the Piper fallback voice:

```bash
python scripts/download_models.py --engine piper --piper-voice en_US-lessac-medium
```

(Piper voices are hosted on Hugging Face at
`huggingface.co/rhasspy/piper-voices`. If your network blocks that host,
download the `.onnx` and `.onnx.json` files for your chosen voice from a
machine that can reach it and place them in `models/piper/`.)

After this step, **no further network access is required** to synthesize
audio. `TTS_PROVIDER=kokoro` (default) and `TTS_PROVIDER=piper` both run
fully offline from here on.

## 6. Environment file (only if using a paid AI provider)

```bash
cp .env.example .env
```

Leave `.env` empty/untouched if you're using the default
`AI_PROVIDER=local`. Otherwise set the matching key
(`ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`GOOGLE_API_KEY`) and set
`AI_PROVIDER` in `config.yaml` (or export `AI_PROVIDER=claude` etc. as an
environment variable, which overrides `config.yaml`).

**`.env` is gitignored. Never commit API keys.**

## 7. First test (one question)

```bash
python main.py produce --input examples/sample_questions.xlsx --batch 1 --include-needs-review --video-size 1
```

This ingests the bundled 12-row example question bank, processes the
first question through validation/explanation/narration/TTS/video, and
writes:

- `data/jobs/<job_id>/content/Q001/{question,validation,explanation,narration}.json`
- `data/jobs/<job_id>/audio/Q001/{Q001.wav,Q001.mp3,Q001.json}`
- `data/videos/video_001/final.mp4`
- `data/reports/{production_report.json,audio_qa_report.json,review_queue.csv,failed_items.csv}`

`--include-needs-review` is used here only because the zero-cost `local`
AI provider always flags its own answers for review (see README's "AI
provider" section) -- it is not needed with a real provider configured at
a normal confidence level.

## 8. Batch processing (10 / 60 / 1000+ questions)

```bash
python main.py produce --input your_questions.xlsx --video-size 60
```

No flag changes are needed to go from 1 question to 1,000 -- `--batch N`
optionally caps how many questions this *run* touches (useful for staged
rollout), and `--video-size N` controls how many questions go into each
final MP4. Concurrency is controlled by `concurrency.tts_concurrency` in
`config.yaml` (default 2) -- raise it if your machine has CPU/GPU headroom,
but benchmark first: local TTS is the dominant cost per question.

## 9. Resume behavior

If the process is killed (crash, Ctrl-C, power loss) partway through a
batch:

```bash
python main.py resume
```

resumes the most recently touched job. Or target a specific one:

```bash
python main.py status                 # lists all jobs and their job_id
python main.py resume --job-id job_xxxxxxxx
```

Nothing already completed is redone -- each stage's output is
content-hash cached (`data/cache/`), and the job manifest
(`data/jobs/<job_id>/manifest.json`) tracks per-question, per-stage state.
Re-running `produce` with the same `--input` file resolves to the same
`job_id` automatically, so `resume` and re-running `produce` are
interchangeable.

```bash
python main.py retry-failed            # only re-attempts FAILED questions
```

## 10. Output locations

```
data/
  input/        your uploaded question banks (gitignored)
  normalized/    normalized question-bank snapshots (used by resume)
  processed/     ingestion issue reports
  jobs/<job_id>/
    manifest.json         per-question, per-stage state
    content/<qid>/         question.json, validation.json, explanation.json, narration.json
    audio/<qid>/            <qid>.wav, <qid>.mp3, <qid>.json (timing manifest)
    video_segments/         per-question rendered video clips (cached)
  videos/<video_id>/
    final.mp4
  reports/
    validation_report.csv   ingestion issues
    review_queue.csv         NEEDS_REVIEW questions with reasons
    failed_items.csv          hard failures with stage + error
    production_report.json    full run summary
    audio_qa_report.json       per-question audio QA results
  cache/                    content-addressed cache shared across jobs
```

## Troubleshooting

**`pip install kokoro-onnx` or `piper-tts` fails to build a dependency
(e.g. `docopt`) on newer Python/setuptools.** This is a known
incompatibility between very old transitive dependencies and modern
`setuptools`. `kokoro-onnx` (used here) avoids the PyTorch-based `kokoro`
package's heavier dependency chain and installs cleanly in most
environments; if it still fails, upgrade `pip`/`setuptools`
(`pip install -U pip setuptools wheel`) and retry.

**`ffmpeg: command not found`.** Install it per step 4 above and make sure
it's on `PATH` -- the renderer shells out to the `ffmpeg`/`ffprobe`
binaries directly, there is no Python ffmpeg dependency to satisfy.

**Video text looks wrong / uses a fallback bitmap font.** The renderer
looks for DejaVu fonts by name across common system font directories. On
a minimal Linux image without any fonts installed, install
`fonts-dejavu-core` (Debian/Ubuntu) or point the template's `fonts.*.family`
values at an absolute `.ttf` path.

**Audio synthesis is slow.** Local TTS is CPU-bound. On a typical
multi-core CPU, one question's full narration (~15 segments) takes on the
order of 30-45 seconds; with `tts_concurrency: 2` a 60-question video takes
roughly 15-25 minutes end to end (audio + video). This scales with your
hardware, not with any external quota.

**A question stays `NEEDS_REVIEW` forever.** By design, production
audio/video is withheld for `NEEDS_REVIEW` questions unless you pass
`--include-needs-review` or set `review.allow_video_for_needs_review: true`
in `config.yaml`. Check `reports/review_queue.csv` for the agent's stated
reason and suspected answer, resolve it in your source question bank if
appropriate, then re-run -- or explicitly override once you've reviewed it.

**`phonemizer: words count mismatch` warnings during voice synthesis.**
Harmless -- this comes from Kokoro's internal grapheme-to-phoneme step on
certain phrasing and does not affect the produced audio. It is not an
error and does not stop the batch.

**I need to force full regeneration.** `python main.py clean-cache --yes`
clears the content-addressed cache; add `--namespace validation` (etc.) to
clear just one stage's cache.
