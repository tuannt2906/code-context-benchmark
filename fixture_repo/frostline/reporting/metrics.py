"""Operational metrics computed from stored rows."""

from frostline.pricing.money import from_cents


def revenue_by_customer(db):
    totals = {}
    for row in db.select("shipments"):
        totals[row["customer"]] = totals.get(row["customer"], 0) + row["total_cents"]
    return {k: str(from_cents(v)) for k, v in sorted(totals.items())}


def outbox_by_channel(db):
    counts = {}
    for row in db.select("outbox"):
        counts[row["channel"]] = counts.get(row["channel"], 0) + 1
    return counts
