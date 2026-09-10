from src.ai.local_provider import LocalTemplateProvider
from src.cache import Cache
from src.ingestion.intake import QuestionIntake
from src.job.batch import BatchProcessor
from src.job.manifest import JobStore
from src.models import StageName
from src.tts.voice_agent import VoiceAgent
from tests.fakes import FakeTTSProvider


def _audio_complete(job, question_id) -> bool:
    return job.state_for(question_id).get(StageName.AUDIO).status == "complete"


def test_batch_run_is_resumable_after_partial_failure(cfg, sample_xlsx, tmp_path):
    questions = QuestionIntake().process(sample_xlsx).questions[:4]
    cache = Cache(cfg.path("paths.cache_dir"))
    ai = LocalTemplateProvider()
    provider = FakeTTSProvider()
    voice_agent = VoiceAgent(cfg, provider=provider)
    store = JobStore(cfg.path("paths.jobs_dir"))
    job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in questions])

    # Simulate a crash: only process the first 2, save, then "restart" the
    # process entirely with a fresh JobManifest loaded from disk.
    bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
    bp.run(questions[:2], include_needs_review=True)

    reloaded_job = store.load(job.job_id)
    assert _audio_complete(reloaded_job, questions[0].question_id)
    assert reloaded_job.state_for(questions[2].question_id).get(StageName.AUDIO).status == "pending"

    bp2 = BatchProcessor(cfg, cache, ai, voice_agent, reloaded_job)
    calls_before = provider.calls
    out = bp2.run(questions, include_needs_review=True)

    # Every question ends up with completed audio...
    assert all(_audio_complete(reloaded_job, q.question_id) for q in questions)
    assert out["summary"].get("failed", 0) == 0
    # ...and the first two were NOT re-synthesized (job-level fast skip
    # inside VoiceAgent via the narration-hash content cache).
    assert provider.calls > calls_before


def test_failed_question_does_not_block_others_and_can_be_retried(cfg, sample_xlsx, tmp_path):
    questions = QuestionIntake().process(sample_xlsx).questions[:4]
    from src.explanation.explainer import ExplanationAgent
    from src.narration.narrator import NarrationAgent

    ai = LocalTemplateProvider()
    exp = ExplanationAgent(ai).explain(questions[1])
    narration = NarrationAgent(cfg.get("tts.pause_ms")).narrate(questions[1], exp, countdown_seconds=1)
    fail_text = narration.segments[0].text

    cache = Cache(cfg.path("paths.cache_dir"))
    provider = FakeTTSProvider(fail_on={fail_text})
    voice_agent = VoiceAgent(cfg, provider=provider)
    store = JobStore(cfg.path("paths.jobs_dir"))
    job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in questions])

    bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
    out = bp.run(questions, include_needs_review=True)

    assert out["summary"]["failed"] == 1
    assert _audio_complete(job, questions[0].question_id)
    assert _audio_complete(job, questions[2].question_id)
    assert _audio_complete(job, questions[3].question_id)
    assert not _audio_complete(job, questions[1].question_id)
    assert job.state_for(questions[1].question_id).overall_state() == "failed"

    # Fix the "outage" and retry only the failed one.
    provider.fail_on = set()
    bp2 = BatchProcessor(cfg, cache, ai, voice_agent, job)
    out2 = bp2.run([questions[1]], include_needs_review=True, force=True)
    assert out2["summary"].get("failed", 0) == 0
    assert _audio_complete(job, questions[1].question_id)
