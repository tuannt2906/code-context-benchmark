"""v1 quote engine (deprecated in 2.0, kept for the migration report)."""

from decimal import Decimal

from frostline.pricing.money import round_money

V1_RATE_PER_KG = Decimal("2.90")
V1_MIN_CHARGE = Decimal("10.00")
V1_REMOTE_FEE = Decimal("12.00")
V1_FUEL_INDEX = Decimal("1.22")


def chargeable_weight(parcel):
    volume = parcel.length_cm * parcel.width_cm * parcel.height_cm
    return max(Decimal(parcel.weight_kg), Decimal(volume) / Decimal(4000))


class QuoteEngine:
    """v1 engine: single rate, surcharges hard-coded, VAT 7.5% everywhere."""

    def __init__(self, remote_depots):
        self.remote_depots = remote_depots

    def quote(self, shipment, customer):
        weight = sum(chargeable_weight(p) for p in shipment.parcels)
        base = max(V1_MIN_CHARGE, weight * V1_RATE_PER_KG)
        surcharge = base * (V1_FUEL_INDEX - 1)
        if shipment.destination in self.remote_depots:
            surcharge += V1_REMOTE_FEE
        subtotal = base + surcharge
        return round_money(subtotal * Decimal("1.075"))
