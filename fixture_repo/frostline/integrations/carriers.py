"""Partner carriers quote their own price; we add a brokerage margin.

These adapters mimic the partners' public tariff sheets. They are used by the
overflow planner only, never by the main quote path.
"""

from decimal import Decimal

from frostline.domain.units import volumetric_weight_air
from frostline.pricing.money import round_money

BROKER_MARGIN = Decimal("0.12")


class Carrier:
    name = "carrier"
    rate_per_kg = Decimal("0")
    min_charge = Decimal("0")

    def chargeable_weight(self, parcels):
        return sum((max(Decimal(p.weight_kg), volumetric_weight_air(p)) for p in parcels), Decimal("0"))

    def quote(self, parcels, distance_km):
        raw = max(self.min_charge, self.chargeable_weight(parcels) * self.rate_per_kg)
        return round_money(raw * (1 + BROKER_MARGIN))


class SkyFreeze(Carrier):
    """Air partner for long-haul perishables."""

    name = "skyfreeze"
    rate_per_kg = Decimal("4.75")
    min_charge = Decimal("35.00")


class RoadChill(Carrier):
    """Road partner; charges per km on top of weight."""

    name = "roadchill"
    rate_per_kg = Decimal("1.95")
    min_charge = Decimal("18.00")
    per_km = Decimal("0.010")

    def quote(self, parcels, distance_km):
        base = super().quote(parcels, distance_km)
        return round_money(base + self.per_km * distance_km)


PARTNERS = [SkyFreeze(), RoadChill()]


def cheapest_partner(parcels, distance_km):
    offers = sorted((c.quote(parcels, distance_km), c.name) for c in PARTNERS)
    return offers[0]
