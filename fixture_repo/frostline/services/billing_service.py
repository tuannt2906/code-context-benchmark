"""Monthly invoicing."""

from frostline.billing.fees import calculate_fee
from frostline.pricing.money import from_cents, round_money_even
from frostline.storage.repositories import ShipmentRepository
from frostline.utils.dates import days_between


class BillingService:
    def __init__(self, container, customers, bus):
        self.settings = container.settings
        self.db = container.db
        self.customers = customers
        self.shipments = ShipmentRepository(container.db)
        self.bus = bus

    def invoice(self, customer_id, as_of):
        customer = self.customers.get(customer_id)
        rows = self.shipments.for_customer(customer.id)
        subtotal = sum((from_cents(r["total_cents"]) for r in rows), from_cents(0))
        oldest = min((r["ship_date"] for r in rows), default=as_of)
        fee = calculate_fee(
            subtotal,
            days_between(oldest, as_of),
            rate=self.settings.get("billing.late_fee_rate", "0.015"),
            grace_days=self.settings.get("billing.grace_days", 10),
        )
        total = round_money_even(subtotal + fee)
        row = self.db.insert("invoices", {
            "customer": customer.id,
            "shipments": len(rows),
            "subtotal": str(subtotal),
            "late_fee": str(round_money_even(fee)),
            "total": str(total),
        })
        self.bus.publish("invoice.issued", {"ref": row["id"], "customer": customer.id})
        return row
