from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import PercentageRule


@register("surcharge", "express")
class ExpressRule(PercentageRule):
    """Next-day service surcharge."""

    code = "express"
    percent = Decimal("0.25")

    def applies(self, shipment, context):
        return shipment.service == "express"
