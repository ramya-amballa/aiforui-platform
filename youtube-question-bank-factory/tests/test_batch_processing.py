from src.ai.local_provider import LocalTemplateProvider
from src.cache import Cache
from src.ingestion.intake import QuestionIntake
from src.job.batch import BatchProcessor
from src.job.manifest import JobStore
from src.tts.voice_agent import VoiceAgent
from tests.fakes import FakeTTSProvider


def test_batch_processes_all_questions_with_no_manual_intervention(cfg, sample_xlsx):
    """The core non-negotiable: N questions in, N questions processed,
    with a single call and no per-question approval step."""
    questions = QuestionIntake().process(sample_xlsx).questions  # 11 valid rows
    cache = Cache(cfg.path("paths.cache_dir"))
    ai = LocalTemplateProvider()
    voice_agent = VoiceAgent(cfg, provider=FakeTTSProvider())
    store = JobStore(cfg.path("paths.jobs_dir"))
    job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in questions])

    bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
    out = bp.run(questions, include_needs_review=True)

    assert len(out["results"]) == len(questions)
    total = sum(out["summary"].values())
    assert total == len(questions)
    assert out["summary"]["failed"] == 0


def test_batch_respects_needs_review_gate_by_default(cfg, sample_xlsx):
    """Without --include-needs-review, audio must not be produced for
    flagged questions (the local provider flags everything)."""
    questions = QuestionIntake().process(sample_xlsx).questions[:3]
    cache = Cache(cfg.path("paths.cache_dir"))
    ai = LocalTemplateProvider()
    provider = FakeTTSProvider()
    voice_agent = VoiceAgent(cfg, provider=provider)
    store = JobStore(cfg.path("paths.jobs_dir"))
    job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in questions])

    bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
    out = bp.run(questions, include_needs_review=False)

    assert out["summary"]["needs_review"] == 3
    assert provider.calls == 0  # no TTS calls at all - audio stage was skipped


def test_batch_size_is_not_hardcoded(cfg, sample_xlsx):
    """Same code path handles 1 question or many; only the input list size differs."""
    questions = QuestionIntake().process(sample_xlsx).questions
    cache = Cache(cfg.path("paths.cache_dir"))
    ai = LocalTemplateProvider()
    voice_agent = VoiceAgent(cfg, provider=FakeTTSProvider())
    store = JobStore(cfg.path("paths.jobs_dir"))

    for n in (1, 5, len(questions)):
        subset = questions[:n]
        job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in subset])
        bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
        out = bp.run(subset, include_needs_review=True)
        assert sum(out["summary"].values()) == n
