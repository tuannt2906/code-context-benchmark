from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import SurchargeRule


@register("surcharge", "fuel")
class FuelRule(SurchargeRule):
    """Fuel surcharge indexed on ``fuel.index`` (1.00 means no surcharge)."""

    code = "fuel"

    def amount(self, base, shipment, context):
        index = Decimal(self.settings.get("fuel.index", "1.00"))
        return base * (index - Decimal("1"))
