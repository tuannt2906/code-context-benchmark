"""Application wiring.

Import order matters: built-in components register first, plugins last, so a
plugin that registers with ``replace=True`` overrides the built-in one.
"""

import frostline.domain.rules  # noqa: F401  (registers surcharge rules)
import frostline.pricing  # noqa: F401  (registers pricing strategies)
import frostline.routing  # noqa: F401  (registers route engines)
import frostline.tax  # noqa: F401  (registers tax policies)
import frostline.services  # noqa: F401  (subscribes event handlers)
import frostline.plugins  # noqa: F401  (plugins last)
import frostline.api.handlers  # noqa: F401  (registers routes)
import frostline.api.warehouse_handlers  # noqa: F401

from frostline.api.router import dispatch
from frostline.config.settings import load_settings
from frostline.core.container import Container
from frostline.core.errors import FrostlineError
from frostline.core.events import EventBus
from frostline.services.billing_service import BillingService
from frostline.services.customer_service import CustomerService
from frostline.services.quote_service import QuoteService
from frostline.services.shipment_service import ShipmentService
from frostline.storage.memory_db import MemoryDB


class App:
    def __init__(self, profile="default", overrides=None):
        self.settings = load_settings(profile, overrides)
        self.db = MemoryDB()
        self.container = Container(self.settings, self.db)
        self.bus = EventBus({"db": self.db, "settings": self.settings})
        customers = CustomerService()
        self.quote_service = QuoteService(self.container, customers, self.bus)
        self.shipment_service = ShipmentService(self.container, customers, self.bus)
        self.billing_service = BillingService(self.container, customers, self.bus)

    def handle(self, method, path, body=None):
        try:
            return {"status": 200, "body": dispatch(method, path)(self, body or {})}
        except FrostlineError as exc:
            return {"status": exc.status, "error": str(exc)}


def create_app(profile="default", **overrides):
    return App(profile, {k.replace("__", "."): v for k, v in overrides.items()})
