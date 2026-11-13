"""Dependency container: turns settings into concrete components."""

from frostline.core.registry import resolve
from frostline.routing.network import default_network


class Container:
    def __init__(self, settings, db):
        self.settings = settings
        self.db = db
        self._network = default_network()

    def pricing_strategy(self):
        cls = resolve("pricing", self.settings.get("pricing.strategy"))
        return cls(self.settings)

    def tax_policy(self, customer):
        if customer.category == "gov":
            return resolve("tax", "exempt")()
        region = customer.region or self.settings.get("tax.region")
        return resolve("tax", region)()

    def route_engine(self):
        cls = resolve("routing", self.settings.get("routing.engine"))
        return cls(self._network)

    def surcharge_rules(self):
        enabled = self.settings.get("surcharge.enabled", [])
        return [resolve("surcharge", code)(self.settings) for code in enabled]

    def network(self):
        return self._network
