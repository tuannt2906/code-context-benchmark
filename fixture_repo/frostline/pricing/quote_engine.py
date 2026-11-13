"""Quote computation: the heart of pricing."""

from decimal import Decimal

from frostline.domain.models import Quote
from frostline.domain.units import chargeable_weight
from frostline.pricing.discounts import apply_discount
from frostline.pricing.money import round_money


class QuoteEngine:
    def __init__(self, container):
        self.container = container
        self.settings = container.settings

    def chargeable_weight(self, shipment):
        divisor = self.settings.get("pricing.volumetric_divisor", 5000)
        step = self.settings.get("pricing.weight_step", "0.5")
        return sum((chargeable_weight(p, divisor, step) for p in shipment.parcels), Decimal("0"))

    def surcharges(self, base, shipment):
        context = {"settings": self.settings}
        result = {}
        for rule in self.container.surcharge_rules():
            amount = round_money(rule.apply(base, shipment, context))
            if amount:
                result[rule.code] = amount
        return result

    def quote(self, shipment, customer):
        weight = self.chargeable_weight(shipment)
        distance = self.container.route_engine().distance(shipment.origin, shipment.destination)
        base = round_money(self.container.pricing_strategy().price(weight, distance))
        surcharges = self.surcharges(base, shipment)
        subtotal = base + sum(surcharges.values(), Decimal("0"))
        discount = round_money(apply_discount(subtotal, customer, shipment.promo_code, self.settings))
        taxable = subtotal - discount
        tax = round_money(self.container.tax_policy(customer).tax(taxable))
        return Quote(
            shipment_id=shipment.id,
            weight_kg=weight,
            distance_km=distance,
            base=base,
            surcharges=surcharges,
            discount=discount,
            tax=tax,
            total=round_money(taxable + tax),
        )
