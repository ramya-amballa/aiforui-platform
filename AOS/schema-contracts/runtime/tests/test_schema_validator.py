import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import schema_validator as sval  # noqa: E402

SCHEMAS_DIR = RUNTIME_DIR / "schemas"


class ValidateAgainstSchemaTests(unittest.TestCase):
    def test_valid_data_has_no_violations(self):
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
        self.assertEqual(sval.validate_against_schema({"a": "x"}, schema), [])

    def test_missing_required_field_is_flagged(self):
        schema = {"type": "object", "required": ["a", "b"], "properties": {}}
        violations = sval.validate_against_schema({"a": "x"}, schema)
        self.assertEqual(violations, ["missing required field: b"])

    def test_wrong_type_is_flagged(self):
        schema = {"type": "object", "required": [], "properties": {"a": {"type": "string"}}}
        violations = sval.validate_against_schema({"a": 123}, schema)
        self.assertEqual(violations, ["field 'a' expected type string, got int"])

    def test_bool_is_never_silently_accepted_as_number(self):
        schema = {"type": "object", "required": [], "properties": {"a": {"type": "number"}}}
        violations = sval.validate_against_schema({"a": True}, schema)
        self.assertEqual(violations, ["field 'a' expected type number, got boolean"])

    def test_int_and_float_both_satisfy_number(self):
        schema = {"type": "object", "required": [], "properties": {"a": {"type": "number"}}}
        self.assertEqual(sval.validate_against_schema({"a": 5}, schema), [])
        self.assertEqual(sval.validate_against_schema({"a": 5.5}, schema), [])

    def test_non_object_top_level_is_flagged(self):
        schema = {"type": "object", "required": [], "properties": {}}
        violations = sval.validate_against_schema(["not", "an", "object"], schema)
        self.assertEqual(violations, ["expected an object at the top level, got list"])

    def test_extra_undeclared_fields_are_not_flagged(self):
        """A minimal structural check, not a strict schema — an
        employee adding a genuinely new field is not itself a
        violation."""
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
        self.assertEqual(sval.validate_against_schema({"a": "x", "b": "unexpected but fine"}, schema), [])


class RealPilotSchemaTests(unittest.TestCase):
    """The two pilot Schema Contracts shipped with this feature must
    themselves be loadable and must validate their own real,
    already-committed feed shape."""

    def test_account_intelligence_feed_schema_loads_and_validates_a_real_shaped_feed(self):
        schema = sval.load_schema(SCHEMAS_DIR / "account-intelligence-feed.schema.json")
        feed = {"schema": {}, "briefs": [{
            "organisation": "BBVA", "industry": "Banking", "region": "EU",
            "buyingReadinessBand": "High", "outreachStrategy": "Warm intro",
            "overallPriority": 82, "briefPath": "AOS/output/account-intelligence/account-briefs/bbva.md",
        }]}
        self.assertEqual(sval.validate_against_schema(feed, schema), [])

    def test_artifact_index_schema_loads_and_validates_a_real_shaped_index(self):
        schema = sval.load_schema(SCHEMAS_DIR / "artifact-index.schema.json")
        index = {
            "schemaVersion": "1", "generatedAt": "2026-08-02T00:00:00+00:00",
            "artifactCount": 0, "employeeCounts": {}, "validationSummary": {"flaggedCount": 0, "flagCounts": {}},
            "artifacts": [],
        }
        self.assertEqual(sval.validate_against_schema(index, schema), [])

    def test_artifact_index_schema_flags_a_real_regression(self):
        schema = sval.load_schema(SCHEMAS_DIR / "artifact-index.schema.json")
        broken_index = {"schemaVersion": "1", "artifactCount": 0}  # missing several required keys
        violations = sval.validate_against_schema(broken_index, schema)
        self.assertIn("missing required field: generatedAt", violations)
        self.assertIn("missing required field: artifacts", violations)


if __name__ == "__main__":
    unittest.main()
