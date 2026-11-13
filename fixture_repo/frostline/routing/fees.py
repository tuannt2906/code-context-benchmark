"""Road toll estimation for routes."""

from decimal import Decimal

TOLL_PER_KM = Decimal("0.035")
TOLL_FREE_KM = 100


def calculate_fee(distance_km):
    """Toll fee for a route: free for the first TOLL_FREE_KM kilometres."""
    billable = max(0, distance_km - TOLL_FREE_KM)
    return (Decimal(billable) * TOLL_PER_KM).quantize(Decimal("0.01"))
