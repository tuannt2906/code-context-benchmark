from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import SurchargeRule


@register("surcharge", "insurance")
class InsuranceRule(SurchargeRule):
    """Declared-value insurance: 1.2% of declared value, minimum 2.00."""

    code = "insurance"
    rate = Decimal("0.012")
    minimum = Decimal("2.00")

    def applies(self, shipment, context):
        return any(p.declared_value > 0 for p in shipment.parcels)

    def amount(self, base, shipment, context):
        declared = sum((p.declared_value for p in shipment.parcels), Decimal("0"))
        return max(self.minimum, declared * self.rate)
