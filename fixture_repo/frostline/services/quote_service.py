"""Quote use case: price a shipment without booking it."""

from frostline.pricing.quote_engine import QuoteEngine
from frostline.storage.repositories import QuoteRepository


class QuoteService:
    def __init__(self, container, customers, bus):
        self.engine = QuoteEngine(container)
        self.customers = customers
        self.quotes = QuoteRepository(container.db)
        self.bus = bus

    def create_quote(self, shipment):
        customer = self.customers.get(shipment.customer_id)
        quote = self.engine.quote(shipment, customer)
        row = self.quotes.save(quote, customer.id)
        self.bus.publish("quote.created", {"ref": row["id"], "customer": customer.id})
        return quote, row
