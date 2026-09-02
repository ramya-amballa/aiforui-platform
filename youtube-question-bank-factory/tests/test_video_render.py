import shutil

import pytest

from src.ingestion.intake import QuestionIntake
from src.models import AudioResult, TimingCue
from src.video.renderer import VideoRenderer
from src.video.templates import list_templates, load_template

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def _fake_audio(q, tmp_path, duration=6.0):
    import numpy as np
    import soundfile as sf

    sr = 8000
    samples = (0.05 * np.sin(2 * 3.14159 * 220 * (np.arange(int(sr * duration)) / sr))).astype("float32")
    wav_path = tmp_path / f"{q.question_id}.wav"
    sf.write(str(wav_path), samples, sr)

    cues = [
        TimingCue("question", 0.0, 1.5),
        TimingCue("countdown", 1.5, 2.0),
        TimingCue("reveal", 3.0, 3.5),
    ]
    return AudioResult(
        question_id=q.question_id, wav_path=str(wav_path), mp3_path=None,
        duration_seconds=duration, sample_rate=sr, voice="af_heart", speed=1.0,
        tts_provider="fake", model_version="fake-v1", narration_hash="deadbeef",
        cues=cues,
    )


def test_all_three_templates_load_without_error():
    names = list_templates()
    assert set(names) == {"default", "minimal", "exam"}
    for name in names:
        tpl = load_template(name)
        assert "fonts" in tpl and "layout" in tpl


def test_render_question_segment_produces_valid_mp4(cfg, sample_xlsx, tmp_path):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    audio = _fake_audio(q, tmp_path)

    renderer = VideoRenderer(cfg, "default")
    out_dir = tmp_path / "segments"
    out_path = renderer.render_question_segment(q, audio, out_dir)

    assert out_path.exists()
    assert out_path.stat().st_size > 1000


def test_segment_is_cached_on_unchanged_input(cfg, sample_xlsx, tmp_path):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    audio = _fake_audio(q, tmp_path)
    renderer = VideoRenderer(cfg, "default")
    out_dir = tmp_path / "segments"

    p1 = renderer.render_question_segment(q, audio, out_dir)
    mtime1 = p1.stat().st_mtime
    p2 = renderer.render_question_segment(q, audio, out_dir)
    assert p2.stat().st_mtime == mtime1  # not re-rendered
