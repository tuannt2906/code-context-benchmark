"""HTTP-style handlers. Each receives the app and the request body."""

from frostline.api.router import route
from frostline.api.serializers import parse_shipment, quote_to_dict
from frostline.pricing.money import from_cents
from frostline.reporting.metrics import outbox_by_channel, revenue_by_customer
from frostline.routing.fees import calculate_fee


@route("POST", "/quotes")
def post_quote(app, body):
    quote, row = app.quote_service.create_quote(parse_shipment(body))
    result = quote_to_dict(quote)
    result["quote_id"] = row["id"]
    return result


@route("POST", "/shipments")
def post_shipment(app, body):
    quote, row = app.shipment_service.book(parse_shipment(body))
    return {
        "shipment_id": row["id"],
        "route": row["route"],
        "total": str(from_cents(row["total_cents"])),
    }


@route("GET", "/routes")
def get_route(app, body):
    engine = app.container.route_engine()
    path = engine.path(body["from"], body["to"])
    distance = engine.distance(body["from"], body["to"])
    return {"path": path, "distance_km": distance, "toll": str(calculate_fee(distance))}


@route("POST", "/invoices")
def post_invoice(app, body):
    row = app.billing_service.invoice(body["customer"], body["as_of"])
    return {"invoice_id": row["id"], "total": row["total"], "late_fee": row["late_fee"]}


@route("GET", "/reports/revenue")
def get_revenue(app, body):
    return {"revenue": revenue_by_customer(app.db), "outbox": outbox_by_channel(app.db)}
