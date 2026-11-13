"""Storage fee calculation for pallets held in the warehouse."""

from decimal import Decimal

from frostline.pricing.money import round_money
from frostline.warehouse.zones import zone_for

FREE_DAYS = 2
LONG_STAY_DAYS = 30
LONG_STAY_DISCOUNT = Decimal("0.20")


def calculate_fee(product, pallets, days):
    """Storage fee: daily zone rate per pallet after FREE_DAYS.

    Days beyond LONG_STAY_DAYS are discounted by LONG_STAY_DISCOUNT.
    """
    zone = zone_for(product)
    billable = max(0, days - FREE_DAYS)
    normal = min(billable, LONG_STAY_DAYS - FREE_DAYS)
    long_stay = billable - normal
    per_pallet = zone.daily_rate * normal + zone.daily_rate * (1 - LONG_STAY_DISCOUNT) * long_stay
    return round_money(per_pallet * pallets)


def handling_fee(pallets):
    """In/out handling: 6.00 per pallet, capped at 60.00 per movement."""
    return min(Decimal("6.00") * pallets, Decimal("60.00"))
