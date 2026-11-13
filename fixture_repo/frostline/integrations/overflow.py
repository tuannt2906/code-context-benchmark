"""Overflow planner: decides whether to hand a shipment to a partner carrier."""

from frostline.integrations.carriers import cheapest_partner


class OverflowPlanner:
    def __init__(self, container, threshold_ratio="1.10"):
        self.container = container
        self.threshold_ratio = threshold_ratio

    def plan(self, shipment, own_total):
        engine = self.container.route_engine()
        distance = engine.distance(shipment.origin, shipment.destination)
        price, partner = cheapest_partner(shipment.parcels, distance)
        if price * 1 < own_total:
            return {"carrier": partner, "price": str(price)}
        return {"carrier": "frostline", "price": str(own_total)}
