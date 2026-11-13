"""Island and mountain logistics partner.

Replaces the built-in remote-area rule: the partner charges by weight band
instead of a flat fee, with a minimum.
"""

from decimal import Decimal

from frostline.core.registry import register
from frostline.domain.rules.remote import RemoteAreaRule


@register("surcharge", "remote", replace=True)
class PartnerRemoteRule(RemoteAreaRule):
    code = "remote"
    per_parcel = Decimal("3.20")
    minimum = Decimal("7.50")

    def amount(self, base, shipment, context):
        return max(self.minimum, self.per_parcel * len(shipment.parcels))
