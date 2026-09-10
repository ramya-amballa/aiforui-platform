from src.ai.local_provider import LocalTemplateProvider
from src.explanation.explainer import ExplanationAgent
from src.ingestion.intake import QuestionIntake
from src.narration.narrator import NarrationAgent
from src.tts.voice_agent import VoiceAgent
from tests.fakes import FakeTTSProvider

PAUSE_MS = {"after_question": 100, "after_option": 50, "before_reveal": 100,
            "after_reveal": 50, "between_explanations": 50}


def _build_narration(sample_xlsx):
    q = QuestionIntake().process(sample_xlsx).questions[0]
    exp = ExplanationAgent(LocalTemplateProvider()).explain(q)
    narration = NarrationAgent(PAUSE_MS).narrate(q, exp, countdown_seconds=1)
    return q, narration


def test_synthesize_produces_wav_mp3_and_timing(cfg, sample_xlsx, tmp_path):
    q, narration = _build_narration(sample_xlsx)
    provider = FakeTTSProvider()
    agent = VoiceAgent(cfg, provider=provider)

    out_dir = tmp_path / "audio_out"
    result = agent.synthesize_narration(narration, out_dir)

    assert (out_dir / f"{q.question_id}.wav").exists()
    assert (out_dir / f"{q.question_id}.mp3").exists()
    assert (out_dir / f"{q.question_id}.json").exists()
    assert result.duration_seconds > 0
    assert len(result.cues) == len(narration.segments)
    assert provider.calls == len(narration.segments)


def test_unchanged_narration_is_not_resynthesized(cfg, sample_xlsx, tmp_path):
    q, narration = _build_narration(sample_xlsx)
    provider = FakeTTSProvider()
    agent = VoiceAgent(cfg, provider=provider)
    out_dir = tmp_path / "audio_out"

    agent.synthesize_narration(narration, out_dir)
    calls_after_first = provider.calls
    agent.synthesize_narration(narration, out_dir)  # should hit the cache
    assert provider.calls == calls_after_first


def test_changed_voice_forces_resynthesis(cfg, sample_xlsx, tmp_path):
    q, narration = _build_narration(sample_xlsx)
    provider = FakeTTSProvider()
    agent = VoiceAgent(cfg, provider=provider)
    out_dir = tmp_path / "audio_out"

    agent.synthesize_narration(narration, out_dir)
    calls_after_first = provider.calls

    cfg.get("tts.voice")
    cfg._data["tts"]["voice"] = "different_voice"
    agent2 = VoiceAgent(cfg, provider=provider)
    agent2.synthesize_narration(narration, out_dir)
    assert provider.calls > calls_after_first


def test_deterministic_filenames(cfg, sample_xlsx, tmp_path):
    q, narration = _build_narration(sample_xlsx)
    agent = VoiceAgent(cfg, provider=FakeTTSProvider())
    out_dir = tmp_path / "audio_out"
    result = agent.synthesize_narration(narration, out_dir)
    assert result.wav_path.endswith(f"{q.question_id}.wav")
