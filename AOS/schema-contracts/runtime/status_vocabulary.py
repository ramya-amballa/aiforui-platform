"""
Schema Contracts — shared honest-gap vocabulary (AOS Architecture
Constitution, Schema Contracts NOW item)

Formalizes a vocabulary that already exists, informally, across the
codebase: a grep across every employee's own code found these exact
seven phrases already in use 131 times combined, expressing "this
field genuinely has no value" in place of an implicit null or zero.
This module gives that vocabulary one canonical name each, so a future
employee (or the Artifact Registry's own validation layer) can check
"is this value an honest, declared gap" without guessing from string
content.

Deliberately stdlib only — `GapMarker` subclasses both `str` and
`Enum`, so `GapMarker.NOT_SPECIFIED == "Not specified"` is True. An
employee migrated to use the enum writes the exact same string to
disk as before; an employee that never migrates keeps working
unchanged, because the two are interchangeable. No employee is
required to adopt this to keep functioning — it is available for
incremental use, never a breaking rename of an existing field or
value.

This is intentionally not a Pydantic model. Every AOS employee runtime
has been dependency-free stdlib Python since day one, with exactly one
demonstrated exception (spaCy, for offline NER an employee genuinely
cannot do in pure stdlib — see demand-intelligence/runtime/
requirements.txt). A shared enum plus a small hand-written validator
(schema_validator.py, alongside this file) meets the same real need
— explicit states over implicit defaults — without introducing a new
dependency every one of AOS's 22 employee runtimes would then require.
See adr/0002-schema-contracts-stdlib-not-pydantic.md for the full
reasoning and the alternative considered.
"""

from enum import Enum


class GapMarker(str, Enum):
    """One canonical name per honest-gap phrase already in real use.
    Ordered by how often each already appears in this codebase today —
    NOT_SPECIFIED is overwhelmingly the general-purpose one; the rest
    are more specific to a particular kind of gap."""

    NOT_SPECIFIED = "Not specified"
    NOT_STARTED = "Not started"
    INSUFFICIENT_SIGNAL = "Not enough signal yet"
    NOT_YET_ESTIMATED = "Not yet estimated"
    NOT_TRACKED = "Not tracked"
    NONE_YET = "None yet"
    NOT_SET = "Not set"


_VALUES = {marker.value for marker in GapMarker}


def is_gap_marker(value):
    """True if this value is one of the declared honest-gap phrases —
    i.e. a field that explicitly says it has nothing to report, as
    opposed to a real (even if falsy, like 0 or "") answer. Exact
    string match only, deliberately: a value that merely *resembles*
    one of these phrases without matching exactly is not assumed to
    mean the same thing."""
    return value in _VALUES
