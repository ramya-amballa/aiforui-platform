import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import status_vocabulary as sv  # noqa: E402


class GapMarkerTests(unittest.TestCase):
    def test_str_enum_members_equal_the_real_existing_string_literal(self):
        self.assertEqual(sv.GapMarker.NOT_SPECIFIED, "Not specified")
        self.assertEqual(sv.GapMarker.NOT_TRACKED, "Not tracked")
        self.assertEqual(sv.GapMarker.INSUFFICIENT_SIGNAL, "Not enough signal yet")

    def test_members_serialize_identically_to_the_existing_plain_string(self):
        import json
        self.assertEqual(json.dumps({"x": sv.GapMarker.NOT_STARTED}), json.dumps({"x": "Not started"}))

    def test_covers_every_phrase_found_in_the_real_codebase_grep(self):
        expected = {
            "Not specified", "Not started", "Not enough signal yet",
            "Not yet estimated", "Not tracked", "None yet", "Not set",
        }
        self.assertEqual({m.value for m in sv.GapMarker}, expected)


class IsGapMarkerTests(unittest.TestCase):
    def test_recognises_a_real_gap_phrase(self):
        self.assertTrue(sv.is_gap_marker("Not specified"))
        self.assertTrue(sv.is_gap_marker(sv.GapMarker.NOT_TRACKED))

    def test_does_not_recognise_real_data_as_a_gap(self):
        self.assertFalse(sv.is_gap_marker("BBVA"))
        self.assertFalse(sv.is_gap_marker(""))
        self.assertFalse(sv.is_gap_marker(None))

    def test_does_not_fuzzy_match_a_similar_but_different_phrase(self):
        self.assertFalse(sv.is_gap_marker("not specified"))
        self.assertFalse(sv.is_gap_marker("Not specified yet"))


if __name__ == "__main__":
    unittest.main()
