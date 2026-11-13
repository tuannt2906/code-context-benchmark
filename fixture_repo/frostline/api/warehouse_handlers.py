"""Warehouse endpoints."""

from frostline.api.router import route
from frostline.warehouse.sensors import compliance_status, excursions
from frostline.warehouse.storage_fees import calculate_fee, handling_fee
from frostline.warehouse.zones import zone_for


@route("POST", "/storage/estimate")
def post_storage_estimate(app, body):
    storage = calculate_fee(body["product"], body["pallets"], body["days"])
    handling = handling_fee(body["pallets"]) * 2
    return {
        "zone": zone_for(body["product"]).code,
        "storage": str(storage),
        "handling": str(handling),
        "total": str(storage + handling),
    }


@route("POST", "/storage/compliance")
def post_compliance(app, body):
    zone = zone_for(body["product"])
    readings = [tuple(r) for r in body["readings"]]
    return {"status": compliance_status(zone, readings), "excursions": excursions(zone, readings)}
