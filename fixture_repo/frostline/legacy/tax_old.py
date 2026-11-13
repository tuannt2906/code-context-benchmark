"""Pre-2025 VAT table (superseded by tax/policies.py)."""

from decimal import Decimal

OLD_RATES = {"north": Decimal("0.075"), "south": Decimal("0.09"), "central": Decimal("0.09")}


class NorthTax:
    rate = OLD_RATES["north"]

    def tax(self, amount):
        return amount * self.rate


class SouthTax:
    rate = OLD_RATES["south"]

    def tax(self, amount):
        return amount * self.rate
