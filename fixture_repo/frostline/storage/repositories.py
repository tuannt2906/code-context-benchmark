"""Repositories map entities to MemoryDB rows."""

from frostline.core.interfaces import Repository
from frostline.pricing.money import to_cents


class QuoteRepository(Repository):
    table = "quotes"

    def save(self, quote, customer_id):
        return self.db.insert(self.table, {
            "customer": customer_id,
            "total_cents": to_cents(quote.total),
            "tax_cents": to_cents(quote.tax),
            "surcharges": sorted(quote.surcharges),
        })


class ShipmentRepository(Repository):
    table = "shipments"

    def save(self, shipment, quote, path):
        row = self.db.insert(self.table, {
            "customer": shipment.customer_id,
            "route": "-".join(path),
            "parcels": len(shipment.parcels),
            "total_cents": to_cents(quote.total),
            "ship_date": shipment.ship_date,
            "status": "booked",
        })
        shipment.id = row["id"]
        return row

    def for_customer(self, customer_id):
        return self.db.select(self.table, customer=customer_id)


class OutboxRepository(Repository):
    table = "outbox"

    def save(self, channel, recipient, template, ref):
        return self.db.insert(self.table, {
            "channel": channel,
            "to": recipient,
            "template": template,
            "ref": ref,
        })


class AuditRepository(Repository):
    table = "audit"

    def save(self, action, ref):
        return self.db.insert(self.table, {"action": action, "ref": ref})
