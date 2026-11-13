"""Base class for surcharge rules."""

from abc import ABC, abstractmethod
from decimal import Decimal


class SurchargeRule(ABC):
    code = "base"

    def __init__(self, settings):
        self.settings = settings

    def applies(self, shipment, context):
        return True

    @abstractmethod
    def amount(self, base, shipment, context):
        """Surcharge amount (Decimal) given the base price."""

    def apply(self, base, shipment, context):
        if not self.applies(shipment, context):
            return Decimal("0")
        return self.amount(base, shipment, context)


class PercentageRule(SurchargeRule):
    """A rule charging a percentage of the base price."""

    percent = Decimal("0")

    def amount(self, base, shipment, context):
        return base * self.percent


class PerParcelRule(SurchargeRule):
    """A rule charging a fixed fee for every parcel that matches."""

    fee = Decimal("0")

    def matches(self, parcel):
        return True

    def amount(self, base, shipment, context):
        count = sum(1 for p in shipment.parcels if self.matches(p))
        return self.fee * count
