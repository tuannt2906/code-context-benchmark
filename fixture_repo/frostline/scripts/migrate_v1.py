"""One-off report comparing v1 and v2 quotes for archived shipments.

Run manually: python -m frostline.scripts.migrate_v1
"""

from frostline.legacy.pricing_v1 import QuoteEngine as V1Engine
from frostline.routing.network import REMOTE_DEPOTS


def compare(shipments, customers, v2_engine):
    v1 = V1Engine(REMOTE_DEPOTS)
    report = []
    for shipment in shipments:
        customer = customers.get(shipment.customer_id)
        report.append((shipment.id, v1.quote(shipment, customer), v2_engine.quote(shipment, customer).total))
    return report
