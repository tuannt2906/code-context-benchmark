from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import PercentageRule
from frostline.utils.dates import is_weekend


@register("surcharge", "weekend")
class WeekendRule(PercentageRule):
    """Weekend pickup surcharge. Not enabled in any shipped profile."""

    code = "weekend"
    percent = Decimal("0.20")

    def applies(self, shipment, context):
        return is_weekend(shipment.ship_date)
