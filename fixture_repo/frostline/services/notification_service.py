"""Event subscribers that enqueue customer notifications in the outbox."""

from frostline.core.events import subscribe
from frostline.storage.repositories import OutboxRepository
from frostline.utils.text import normalize, slugify

TEMPLATES = {
    "email": "booking_confirmation_v3",
    "sms": "booking_short_v1",
    "push": "booking_push_v2",
}


@subscribe("shipment.booked")
def notify_booking(payload, context):
    outbox = OutboxRepository(context["db"])
    rows = []
    for channel in context["settings"].get("notify.channels", []):
        channel = normalize(channel)
        recipient = "%s@%s" % (slugify(payload["customer_name"]), channel)
        rows.append(outbox.save(channel, recipient, TEMPLATES[channel], payload["ref"]))
    return rows


@subscribe("invoice.issued")
def notify_invoice(payload, context):
    outbox = OutboxRepository(context["db"])
    return [outbox.save("email", payload["customer"], "invoice_v2", payload["ref"])]
