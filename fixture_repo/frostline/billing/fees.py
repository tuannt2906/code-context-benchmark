"""Late payment fees for invoices."""

from decimal import Decimal


def calculate_fee(amount, days_late, rate="0.015", grace_days=10):
    """Late fee: ``rate`` per started 30-day period after the grace period."""
    overdue = days_late - grace_days
    if overdue <= 0:
        return Decimal("0")
    periods = (overdue + 29) // 30
    return Decimal(amount) * Decimal(rate) * periods
