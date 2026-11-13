"""Deterministic identifier generation (per table counters)."""

PREFIXES = {
    "shipments": "SHP",
    "quotes": "QTE",
    "outbox": "MSG",
    "audit": "AUD",
    "invoices": "INV",
}


class IdGenerator:
    def __init__(self, start=1000):
        self._start = start
        self._counters = {}

    def next_id(self, table):
        value = self._counters.get(table, self._start) + 1
        self._counters[table] = value
        return "%s-%d" % (PREFIXES.get(table, "ROW"), value)
