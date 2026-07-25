"""
Optional extraction backend — wraps claude_client.py's existing Claude
API call behind the same extract(title, summary, model=None) interface
deterministic_extractor.py implements, so collectors/demand_signals.py
can select either without caring which one is running.

Not the default. AOS Sprint 7 made Demand Intelligence fully
functional offline (deterministic_extractor.py, no paid API, no
network call beyond RSS) — this plugin exists for anyone who wants
Claude's stronger language understanding instead, opted into
explicitly via config/sources.json's demandSignals.extractionBackend:
"claude", and still requires ANTHROPIC_API_KEY to actually run.
"""

from .. import claude_client


def model_available():
    return claude_client.api_key_configured()


def extract(title, summary, model=None):
    return claude_client.extract_demand_signal(title, summary, model=model)
