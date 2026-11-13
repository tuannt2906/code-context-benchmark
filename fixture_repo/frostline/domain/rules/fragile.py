from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import PerParcelRule


@register("surcharge", "fragile")
class FragileRule(PerParcelRule):
    """Handling fee per fragile parcel."""

    code = "fragile"
    fee = Decimal("4.50")

    def matches(self, parcel):
        return parcel.fragile
