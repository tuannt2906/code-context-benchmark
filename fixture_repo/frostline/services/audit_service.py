"""Event subscribers that write the audit trail."""

from frostline.core.events import subscribe
from frostline.storage.repositories import AuditRepository


@subscribe("quote.created")
def audit_quote(payload, context):
    return AuditRepository(context["db"]).save("quote", payload["ref"])


@subscribe("shipment.booked")
def audit_booking(payload, context):
    return AuditRepository(context["db"]).save("booking", payload["ref"])
