"""Request parsing and response shaping."""

from decimal import Decimal

from frostline.core.errors import ValidationError
from frostline.domain.models import Parcel, Shipment
from frostline.domain.validation import check_parcel
from frostline.domain.units import to_kg
from frostline.utils.text import normalize_id


def parse_parcel(data, unit):
    try:
        return Parcel(
            weight_kg=to_kg(data["weight"], unit),
            length_cm=int(data["dims"][0]),
            width_cm=int(data["dims"][1]),
            height_cm=int(data["dims"][2]),
            fragile=bool(data.get("fragile", False)),
            hazmat=bool(data.get("hazmat", False)),
            declared_value=Decimal(str(data.get("declared_value", "0"))),
        )
    except (KeyError, IndexError) as exc:
        raise ValidationError("bad parcel: %s" % exc)


def parse_shipment(body):
    unit = body.get("weight_unit", "kg")
    parcels = [parse_parcel(p, unit) for p in body["parcels"]]
    for parcel in parcels:
        check_parcel(parcel)
    return Shipment(
        customer_id=normalize_id(body["customer"]),
        origin=normalize_id(body["from"]),
        destination=normalize_id(body["to"]),
        parcels=parcels,
        service=body.get("service", "standard"),
        promo_code=body.get("promo"),
        ship_date=body.get("date", "2026-11-02"),
    )


def quote_to_dict(quote):
    return {
        "weight_kg": str(quote.weight_kg),
        "distance_km": quote.distance_km,
        "base": str(quote.base),
        "surcharges": {k: str(v) for k, v in sorted(quote.surcharges.items())},
        "discount": str(quote.discount),
        "tax": str(quote.tax),
        "total": str(quote.total),
        "currency": quote.currency,
    }
