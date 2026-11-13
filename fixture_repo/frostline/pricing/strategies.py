"""Pricing strategies registered under kind "pricing".

The class hierarchy is Flat <- Tiered <- Distance: each subclass only
overrides the part of the computation that differs.
"""

from decimal import Decimal

from frostline.core.interfaces import PricingStrategy
from frostline.core.registry import register


@register("pricing", "flat")
class FlatStrategy(PricingStrategy):
    RATE_PER_KG = Decimal("2.40")

    def base_rate(self, weight_kg, distance_km):
        return self.RATE_PER_KG

    def min_charge(self):
        return Decimal(self.settings.get("pricing.min_charge", "0"))

    def price(self, weight_kg, distance_km):
        raw = self.base_rate(weight_kg, distance_km) * weight_kg
        return max(self.min_charge(), raw)


@register("pricing", "tiered")
class TieredStrategy(FlatStrategy):
    # (upper bound in kg inclusive, rate per kg); None means "and above"
    TIERS = [
        (Decimal("5"), Decimal("3.10")),
        (Decimal("20"), Decimal("2.60")),
        (None, Decimal("2.05")),
    ]

    def base_rate(self, weight_kg, distance_km):
        for upper, rate in self.TIERS:
            if upper is None or weight_kg <= upper:
                return rate
        raise AssertionError("unreachable")


@register("pricing", "distance")
class DistanceStrategy(TieredStrategy):
    PER_KM = Decimal("0.012")

    def price(self, weight_kg, distance_km):
        return super().price(weight_kg, distance_km) + self.PER_KM * distance_km
