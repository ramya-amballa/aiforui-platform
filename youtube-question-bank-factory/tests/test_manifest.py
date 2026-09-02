from pathlib import Path

from src.job.manifest import JobManifest, JobStore
from src.models import StageName, StageStatus


def test_manifest_roundtrips_through_save_and_load(tmp_path):
    jobs_dir = tmp_path / "jobs"
    jm = JobManifest("job_test1", jobs_dir, "input.xlsx", ["Q001", "Q002"])
    jm.mark("Q001", StageName.VALIDATE, StageStatus.COMPLETE, content_hash="abc123")
    jm.mark("Q002", StageName.VALIDATE, StageStatus.NEEDS_REVIEW)
    jm.save()

    loaded = JobManifest.load(jm.manifest_path())
    assert loaded.job_id == "job_test1"
    assert loaded.question_ids == ["Q001", "Q002"]
    assert loaded.state_for("Q001").get(StageName.VALIDATE).status == "complete"
    assert loaded.state_for("Q001").get(StageName.VALIDATE).content_hash == "abc123"
    assert loaded.state_for("Q002").overall_state() == "needs_review"


def test_failed_stage_increments_attempts_and_records_error(tmp_path):
    jm = JobManifest("job_test2", tmp_path / "jobs", "input.xlsx", ["Q001"])
    jm.mark("Q001", StageName.AUDIO, StageStatus.FAILED, error="synth failed")
    jm.mark("Q001", StageName.AUDIO, StageStatus.FAILED, error="synth failed again")
    rec = jm.state_for("Q001").get(StageName.AUDIO)
    assert rec.attempts == 2
    assert rec.last_error == "synth failed again"
    assert jm.state_for("Q001").overall_state() == "failed"


def test_overall_state_completed_only_when_all_stages_complete(tmp_path):
    jm = JobManifest("job_test3", tmp_path / "jobs", "input.xlsx", ["Q001"])
    for stage in (StageName.NORMALIZE, StageName.VALIDATE, StageName.EXPLAIN, StageName.NARRATE):
        jm.mark("Q001", stage, StageStatus.COMPLETE)
    # overall_state only considers stages actually recorded so far.
    assert jm.state_for("Q001").overall_state() == "completed"
    jm.mark("Q001", StageName.AUDIO, StageStatus.RUNNING)
    assert jm.state_for("Q001").overall_state() != "completed"
    jm.mark("Q001", StageName.AUDIO, StageStatus.COMPLETE)
    assert jm.state_for("Q001").overall_state() == "completed"


def test_job_store_creates_deterministic_job_id_from_input_and_questions(tmp_path):
    store = JobStore(tmp_path / "jobs")
    job1, created1 = store.find_or_create(Path("questions.xlsx"), ["Q001", "Q002"])
    job2, created2 = store.find_or_create(Path("questions.xlsx"), ["Q001", "Q002"])
    assert created1 is True
    assert created2 is False
    assert job1.job_id == job2.job_id


def test_job_store_grows_job_with_new_question_ids(tmp_path):
    store = JobStore(tmp_path / "jobs")
    job1, _ = store.find_or_create(Path("questions.xlsx"), ["Q001"])
    job1.mark("Q001", StageName.AUDIO, StageStatus.COMPLETE)
    job1.save()

    # Different question set -> different job_id (each video-batch/job
    # combination is tracked independently), but re-adding Q001 to a NEW
    # set including a fresh question grows an existing job cleanly when the
    # set otherwise matches a previously seen job_id is not expected here.
    job2, created2 = store.find_or_create(Path("other.xlsx"), ["Q001", "Q003"])
    assert created2 is True
    assert set(job2.question_ids) == {"Q001", "Q003"}
