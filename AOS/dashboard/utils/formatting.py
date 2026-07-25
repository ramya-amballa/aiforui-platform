"""
Formatting helpers for the AOS Command Center.

parse_currency/format_amount/MULTIPLIERS/CURRENCY_SYMBOLS below are
reused verbatim from AOS/revenue-hunter/runtime/generate.py (itself
reused verbatim from executive-dashboard/runtime/generate.py) so the
dashboard displays the same currency parsing every runtime already
uses, rather than deriving a second implementation of the same logic.
"""

import re

MULTIPLIERS = {"k": 1_000, "l": 100_000, "lakh": 100_000, "cr": 10_000_000, "crore": 10_000_000, "m": 1_000_000}
CURRENCY_SYMBOLS = {"$": "USD", "₹": "INR", "£": "GBP", "€": "EUR"}


def parse_currency(value):
    if isinstance(value, (int, float)):
        return float(value), None
    if not isinstance(value, str):
        return None, None

    text = value.strip()
    currency = None
    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in text:
            currency = code
            break
    match = re.search(r"[A-Za-z]{3}", text)
    if not currency and match:
        currency = match.group(0).upper()

    numbers = re.findall(r"(\d[\d,]*\.?\d*)\s*(k|l|lakh|cr|crore|m)?", text, flags=re.IGNORECASE)
    numbers = [(n, s) for n, s in numbers if n]
    if not numbers:
        return None, currency

    parsed = []
    for num, suffix in numbers:
        try:
            n = float(num.replace(",", ""))
        except ValueError:
            continue
        n *= MULTIPLIERS.get(suffix.lower(), 1) if suffix else 1
        parsed.append(n)

    if not parsed:
        return None, currency
    return sum(parsed) / len(parsed), currency


def format_amount(value, currency):
    if value is None:
        return "unestimated"
    label = currency or ""
    if value >= 10_000_000:
        return f"{label} {value / 10_000_000:.2f}Cr".strip()
    if value >= 100_000:
        return f"{label} {value / 100_000:.2f}L".strip()
    return f"{label} {value:,.0f}".strip()


def format_currency_field(value):
    """Convenience wrapper for a raw pipeline/schema field: parse then format in one call."""
    amount, currency = parse_currency(value)
    return format_amount(amount, currency)


def format_timestamp(iso_string):
    """Best-effort human-readable rendering of an ISO 8601 timestamp; falls back to the raw string."""
    if not iso_string:
        return "Never"
    try:
        from datetime import datetime
        cleaned = iso_string.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        return dt.strftime("%d %b %Y, %H:%M UTC")
    except (ValueError, TypeError):
        return str(iso_string)
