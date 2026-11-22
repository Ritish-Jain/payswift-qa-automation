"""Money handling for assertions.

Amounts are always compared as Decimal, never float. A float comparison can pass or
fail for the wrong reason (0.1 + 0.2 != 0.3), which is exactly the class of defect a
payments suite should catch rather than hide.
"""
from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

AMOUNT_REGEX = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
CENTS = Decimal("0.01")


def parse_amount(text: str) -> Decimal:
    """Extract the amount from UI text such as 'Item total: $45.98' or '₹1,00,000.00'.

    Keeps every digit the UI shows. A value like '59.980000000000004' is returned as is,
    so a precision bug in the app surfaces as an assertion failure.
    """
    match = AMOUNT_REGEX.search(text or "")
    if not match:
        raise ValueError(f"No amount found in text: {text!r}")
    try:
        return Decimal(match.group(0).replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError(f"Cannot parse amount from {text!r}") from exc


def round_half_up(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def has_two_decimals(value: Decimal) -> bool:
    return value == value.quantize(CENTS)
