"""Regional VAT policies registered under kind "tax"."""

from decimal import Decimal

from frostline.core.interfaces import TaxPolicy
from frostline.core.registry import register


class FlatRateTax(TaxPolicy):
    def tax(self, amount):
        return amount * self.rate


@register("tax", "north")
class NorthTax(FlatRateTax):
    rate = Decimal("0.08")


@register("tax", "south")
class SouthTax(FlatRateTax):
    rate = Decimal("0.10")


@register("tax", "central")
class CentralTax(FlatRateTax):
    """Central region: reduced rate on the first 100 EUR."""

    rate = Decimal("0.10")
    reduced_rate = Decimal("0.05")
    threshold = Decimal("100")

    def tax(self, amount):
        low = min(amount, self.threshold)
        high = max(Decimal("0"), amount - self.threshold)
        return low * self.reduced_rate + high * self.rate


@register("tax", "exempt")
class ExemptTax(TaxPolicy):
    rate = Decimal("0")

    def tax(self, amount):
        return Decimal("0")
