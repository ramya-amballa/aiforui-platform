"""End-to-end smoke tests (spec section 27/29): one question all the way
to a QA'd MP3+MP4, then a small batch all the way to one QA'd video.
Uses FakeTTSProvider so the smoke test runs in CI seconds rather than
loading a real multi-hundred-MB Kokoro model; the real model was verified
manually (see SETUP.md) and is exercised by scripts/smoke_test_real_tts.py.
"""
import shutil

import pytest

from src.ai.local_provider import LocalTemplateProvider
from src.cache import Cache
from src.ingestion.intake import QuestionIntake
from src.job.batch import BatchProcessor
from src.job.manifest import JobStore
from src.qa.audio_qa import run_audio_qa
from src.qa.video_qa import run_video_qa
from src.models import StageName
from src.tts.voice_agent import VoiceAgent
from src.video.assembler import VideoAssembler
from src.video.renderer import VideoRenderer
from tests.fakes import FakeTTSProvider

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def test_smoke_single_question_end_to_end(cfg, sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions[:1]
    cache = Cache(cfg.path("paths.cache_dir"))
    ai = LocalTemplateProvider()
    voice_agent = VoiceAgent(cfg, provider=FakeTTSProvider())
    store = JobStore(cfg.path("paths.jobs_dir"))
    job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in questions])

    bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
    out = bp.run(questions, include_needs_review=True)
    assert out["summary"].get("failed", 0) == 0
    assert job.state_for(questions[0].question_id).get(StageName.AUDIO).status == "complete"

    q = questions[0]
    assert (job.audio_dir(q.question_id) / f"{q.question_id}.mp3").exists()

    audio_qa = run_audio_qa(job.dir, [q.question_id])
    assert audio_qa["passed"] == 1

    from src.models import AudioResult
    import json
    audio_data = json.loads((job.audio_dir(q.question_id) / f"{q.question_id}.json").read_text())
    audio_data["wav_path"] = str(job.audio_dir(q.question_id) / f"{q.question_id}.wav")
    audio = AudioResult.from_dict(audio_data)

    renderer = VideoRenderer(cfg, "default")
    assembler = VideoAssembler(cfg, renderer)
    report = assembler.build_video(
        "smoke_video", questions, {q.question_id: audio},
        job.dir / "video_segments", cfg.path("paths.videos_dir"),
    )
    assert report["final_path"]
    video_qa = run_video_qa(report, [q.question_id])
    assert video_qa["passed"], video_qa["issues"]


def test_smoke_ten_question_batch_produces_one_video(cfg, sample_xlsx):
    questions = QuestionIntake().process(sample_xlsx).questions  # 11 available
    cache = Cache(cfg.path("paths.cache_dir"))
    ai = LocalTemplateProvider()
    voice_agent = VoiceAgent(cfg, provider=FakeTTSProvider())
    store = JobStore(cfg.path("paths.jobs_dir"))
    job, _ = store.find_or_create(sample_xlsx, [q.question_id for q in questions])

    bp = BatchProcessor(cfg, cache, ai, voice_agent, job)
    out = bp.run(questions, include_needs_review=True)
    assert out["summary"].get("failed", 0) == 0
    assert all(job.state_for(q.question_id).get(StageName.AUDIO).status == "complete" for q in questions)

    import json
    from src.models import AudioResult
    audios = {}
    for q in questions:
        data = json.loads((job.audio_dir(q.question_id) / f"{q.question_id}.json").read_text())
        data["wav_path"] = str(job.audio_dir(q.question_id) / f"{q.question_id}.wav")
        audios[q.question_id] = AudioResult.from_dict(data)
        assert (job.audio_dir(q.question_id) / f"{q.question_id}.mp3").exists()

    audio_qa = run_audio_qa(job.dir, [q.question_id for q in questions])
    assert audio_qa["passed"] == len(questions)

    renderer = VideoRenderer(cfg, "default")
    assembler = VideoAssembler(cfg, renderer)
    report = assembler.build_video(
        "batch_video", questions, audios, job.dir / "video_segments", cfg.path("paths.videos_dir"),
    )
    assert len(report["included"]) == len(questions)
    assert report["final_path"]

    video_qa = run_video_qa(report, [q.question_id for q in questions])
    assert video_qa["passed"], video_qa["issues"]
