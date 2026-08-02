"""
Schema Contracts — a minimal, hand-written structural validator
(AOS Architecture Constitution, Schema Contracts NOW item)

Deliberately not a JSON Schema spec implementation, and deliberately
not the `jsonschema` package (a second new dependency, no more
justified than Pydantic for AOS's actual schema complexity today).
This checks exactly two things — every required top-level key is
present, and each declared field's Python type matches — because
that is the whole of what has actually gone wrong in this codebase so
far (a field silently renamed, a feed's shape drifting from its own
documented comment). Extend this only when a real, demonstrated need
appears; do not build in $ref, pattern, enum, or nested-schema support
speculatively.

Advisory only, exactly like registry_validation.py's own checks:
returns a list of violation strings, never raises, never blocks
anything from being indexed or read.
"""

_TYPE_MAP = {
    "string": str,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def load_schema(path):
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_against_schema(data, schema):
    """schema shape: {"type": "object", "required": [...],
    "properties": {"field": {"type": "string"|"number"|"boolean"|
    "array"|"object"}, ...}}. Returns a list of violation strings;
    an empty list means every checked constraint held."""
    violations = []

    if not isinstance(data, dict):
        return [f"expected an object at the top level, got {type(data).__name__}"]

    for field in schema.get("required", []):
        if field not in data:
            violations.append(f"missing required field: {field}")

    properties = schema.get("properties", {})
    for field, field_schema in properties.items():
        if field not in data:
            continue
        declared_type = field_schema.get("type")
        python_type = _TYPE_MAP.get(declared_type)
        if python_type is None:
            continue
        value = data[field]
        # bool is a subclass of int in Python — exclude it explicitly
        # so a real boolean is never silently accepted as a number.
        if declared_type == "number" and isinstance(value, bool):
            violations.append(f"field '{field}' expected type number, got boolean")
        elif not isinstance(value, python_type):
            violations.append(f"field '{field}' expected type {declared_type}, got {type(value).__name__}")

    return violations
