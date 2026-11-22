"""Money helpers. Always use Decimal for amounts, never float."""
from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

AMOUNT_REGEX = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
CENTS = Decimal("0.01")


def parse_amount(text: str) -> Decimal:
    """Get the amount from text like 'Item total: $45.98' or '₹1,00,000.00'.

    Digits are kept as shown, so '59.980000000000004' stays as is and fails the test.
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
