"""Temperature excursion detection from sensor logs.

A reading log is a list of (minute, celsius) tuples sorted by minute. An
excursion is a maximal run of consecutive readings outside the zone range.
Short blips are tolerated: only runs lasting at least ``min_minutes`` count.
"""

from decimal import Decimal

from frostline.warehouse.zones import within


def excursions(zone, readings, min_minutes=15):
    runs, start, last = [], None, None
    for minute, celsius in readings:
        if not within(zone, celsius):
            if start is None:
                start = minute
            last = minute
        elif start is not None:
            runs.append((start, last))
            start = None
    if start is not None:
        runs.append((start, last))
    return [(a, b) for a, b in runs if b - a >= min_minutes]


def worst_reading(zone, readings):
    """The reading furthest outside the zone range (0 if all within)."""
    worst = Decimal("0")
    for _, celsius in readings:
        c = Decimal(str(celsius))
        gap = max(zone.min_c - c, c - zone.max_c, Decimal("0"))
        worst = max(worst, gap)
    return worst


def compliance_status(zone, readings):
    found = excursions(zone, readings)
    if not found:
        return "ok"
    if worst_reading(zone, readings) > Decimal("5"):
        return "quarantine"
    return "review"
