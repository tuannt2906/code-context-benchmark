from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.base import SurchargeRule
from frostline.routing.network import REMOTE_DEPOTS


@register("surcharge", "remote")
class RemoteAreaRule(SurchargeRule):
    """Flat fee when the destination depot is in a remote area."""

    code = "remote"
    fee = Decimal("9.00")

    def applies(self, shipment, context):
        return shipment.destination in REMOTE_DEPOTS

    def amount(self, base, shipment, context):
        return self.fee
