"""Money helpers. All amounts are Decimal; never use float for money."""

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

CENT = Decimal("0.01")


def to_decimal(value):
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_money(value):
    """Commercial rounding to cents (half away from zero)."""
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def round_money_even(value):
    """Banker's rounding to cents (half to even). Used for accounting totals."""
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_EVEN)


def to_cents(value):
    return int((round_money(value) * 100).to_integral_value())


def from_cents(cents):
    return (Decimal(cents) / 100).quantize(CENT)


def clamp(value, low, high):
    return max(low, min(high, value))
