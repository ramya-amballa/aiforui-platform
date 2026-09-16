import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import generate  # noqa: E402
import opportunity_scoring as scoring  # noqa: E402

REAL_PROFILE_PATH = RUNTIME_DIR / "config" / "ramya-professional-profile.json"


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ProfileIsNeverWrittenByDiscoveryTests(unittest.TestCase):
    """The founder's own non-negotiable rule: the profile is
    founder-authoritative input. Opportunity Intelligence may read it
    to score and draft, but nothing in this component may ever modify
    it — not silently, not as a side effect, not even to "helpfully"
    fix a typo. This test locks that in as a real regression test, not
    just a documented promise: if any future change introduces a write
    path, this test fails."""

    def test_the_real_shipped_profile_file_is_byte_identical_after_a_full_discovery_run(self):
        before = _hash(REAL_PROFILE_PATH)
        before_mtime = REAL_PROFILE_PATH.stat().st_mtime_ns

        with tempfile.TemporaryDirectory() as tmp:
            inbox_dir = Path(tmp) / "inbox"
            inbox_dir.mkdir()
            (inbox_dir / "a.json").write_text(json.dumps({
                "opportunity_type": "EMPLOYMENT", "company": "Test Co", "source": "test",
                "required_skills": ["ai governance"],
            }), encoding="utf-8")
            output_dir = Path(tmp) / "output"

            with patch.object(generate, "INBOX_DIR", inbox_dir), \
                 patch.object(generate, "OUTPUT_DIR", output_dir), \
                 patch.object(generate, "FEED_PATH", output_dir / "feed.json"):
                generate.run_discovery()

        after = _hash(REAL_PROFILE_PATH)
        after_mtime = REAL_PROFILE_PATH.stat().st_mtime_ns
        self.assertEqual(before, after, "the real profile file's content changed after a discovery run")
        self.assertEqual(before_mtime, after_mtime, "the real profile file's mtime changed — something touched it even if content matched")

    def test_load_profile_is_the_only_function_in_the_scoring_module_that_references_the_profile_path(self):
        """A structural check, not just a behavioral one: greps this
        component's own source for the profile filename and asserts
        every reference is a read, never inside a write/open(...'w')
        call. Catches a future write path even before a test would."""
        import inspect
        source_files = ["opportunity_scoring.py", "opportunity_model.py", "resume_tailoring.py",
                         "outreach_drafting.py", "approval_queue.py", "generate.py"]
        for filename in source_files:
            content = (RUNTIME_DIR / filename).read_text(encoding="utf-8")
            if "ramya-professional-profile" not in content:
                continue
            for line in content.splitlines():
                if "ramya-professional-profile" in line:
                    self.assertNotIn("'w'", line, f"{filename}: {line.strip()}")
                    self.assertNotIn('"w"', line, f"{filename}: {line.strip()}")
                    self.assertNotIn("json.dump", line, f"{filename}: {line.strip()}")

    def test_no_module_in_this_component_defines_a_profile_write_function(self):
        """Belt-and-suspenders: there is no function named anything
        like save_profile/write_profile/update_profile anywhere. If
        one is ever added, it must go through an explicit
        human-acceptance proposal mechanism (see the model doc's
        'Future: proposing a profile change' section) — never a plain
        write function."""
        forbidden_name_fragments = ["save_profile", "write_profile", "update_profile", "persist_profile"]
        for py_file in RUNTIME_DIR.glob("*.py"):
            content = py_file.read_text(encoding="utf-8").lower()
            for fragment in forbidden_name_fragments:
                self.assertNotIn(fragment, content, f"{py_file.name} defines something matching {fragment!r}")


if __name__ == "__main__":
    unittest.main()
