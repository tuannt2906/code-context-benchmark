"""Frostline: a cold-chain parcel dispatch backend.

Layers (top to bottom):
    api       -> request routing, payload parsing, response shaping
    services  -> use cases (quote, booking, billing, notification, audit)
    pricing   -> quote engine, pricing strategies, discounts, money helpers
    domain    -> entities, units, surcharge rules
    routing   -> depot network and route engines
    storage   -> in-memory database and repositories
    core      -> registry, dependency container, event bus, interfaces
"""

__version__ = "2.3.0"
