"""Temperature zones of a cold-storage warehouse."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Zone:
    code: str
    min_c: Decimal
    max_c: Decimal
    daily_rate: Decimal  # EUR per pallet per day


ZONES = {
    "FRZ": Zone("FRZ", Decimal("-25"), Decimal("-18"), Decimal("1.90")),
    "CHL": Zone("CHL", Decimal("0"), Decimal("4"), Decimal("1.35")),
    "CRT": Zone("CRT", Decimal("15"), Decimal("25"), Decimal("0.80")),
}

PRODUCT_ZONES = {
    "seafood": "FRZ",
    "icecream": "FRZ",
    "dairy": "CHL",
    "vaccine": "CHL",
    "flowers": "CHL",
    "medicine": "CRT",
}


def zone_for(product):
    try:
        return ZONES[PRODUCT_ZONES[product]]
    except KeyError:
        raise KeyError("no zone configured for product %r" % product)


def within(zone, reading_c):
    return zone.min_c <= Decimal(str(reading_c)) <= zone.max_c
