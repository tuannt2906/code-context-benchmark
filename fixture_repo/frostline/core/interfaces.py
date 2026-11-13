"""Abstract interfaces implemented by pluggable components."""

from abc import ABC, abstractmethod


class PricingStrategy(ABC):
    def __init__(self, settings):
        self.settings = settings

    @abstractmethod
    def price(self, weight_kg, distance_km):
        """Return the base price (Decimal) for a chargeable weight and distance."""


class TaxPolicy(ABC):
    rate = None

    @abstractmethod
    def tax(self, amount):
        """Return the tax (Decimal) owed on a taxable amount."""


class RouteEngine(ABC):
    def __init__(self, network):
        self.network = network

    @abstractmethod
    def path(self, origin, destination):
        """Return the list of depot codes from origin to destination."""

    def distance(self, origin, destination):
        hops = self.path(origin, destination)
        return sum(self.network.edge(a, b) for a, b in zip(hops, hops[1:]))


class Repository(ABC):
    table = None

    def __init__(self, db):
        self.db = db

    @abstractmethod
    def save(self, *args, **kwargs):
        """Persist an entity and return its stored row."""
