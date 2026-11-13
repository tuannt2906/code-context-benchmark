from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import PercentageRule


@register("surcharge", "hazmat")
class HazmatRule(PercentageRule):
    """Dangerous goods: percentage of base when any parcel is hazmat."""

    code = "hazmat"
    percent = Decimal("0.15")

    def applies(self, shipment, context):
        return any(p.hazmat for p in shipment.parcels)
