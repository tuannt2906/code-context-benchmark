"""Booking use case: validate, price, route and persist a shipment."""

from decimal import Decimal

from frostline.core.errors import ValidationError
from frostline.pricing.quote_engine import QuoteEngine
from frostline.storage.repositories import ShipmentRepository


class ShipmentService:
    def __init__(self, container, customers, bus):
        self.container = container
        self.engine = QuoteEngine(container)
        self.customers = customers
        self.shipments = ShipmentRepository(container.db)
        self.bus = bus

    def validate(self, shipment):
        limit = Decimal(self.container.settings.get("booking.max_parcel_kg", 70))
        for parcel in shipment.parcels:
            if parcel.weight_kg > limit:
                raise ValidationError("parcel exceeds %s kg" % limit)
        if shipment.origin == shipment.destination:
            raise ValidationError("origin equals destination")

    def book(self, shipment):
        self.validate(shipment)
        customer = self.customers.get(shipment.customer_id)
        quote = self.engine.quote(shipment, customer)
        path = self.container.route_engine().path(shipment.origin, shipment.destination)
        row = self.shipments.save(shipment, quote, path)
        self.bus.publish("shipment.booked", {
            "ref": row["id"],
            "customer": customer.id,
            "customer_name": customer.name,
            "total_cents": row["total_cents"],
        })
        return quote, row
