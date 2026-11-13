"""In-memory relational-ish store used by every repository."""

from frostline.utils.ids import IdGenerator


class MemoryDB:
    def __init__(self):
        self.tables = {}
        self.ids = IdGenerator()

    def insert(self, table, row):
        row = dict(row)
        row.setdefault("id", self.ids.next_id(table))
        self.tables.setdefault(table, []).append(row)
        return row

    def select(self, table, **where):
        rows = self.tables.get(table, [])
        return [r for r in rows if all(r.get(k) == v for k, v in where.items())]

    def update(self, table, row_id, **changes):
        for row in self.tables.get(table, []):
            if row["id"] == row_id:
                row.update(changes)
                return row
        return None

    def count(self, table):
        return len(self.tables.get(table, []))
