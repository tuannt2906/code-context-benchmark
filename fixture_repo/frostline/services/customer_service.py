"""Customer directory (seeded, read-only in this version)."""

from frostline.core.errors import NotFound
from frostline.domain.models import Customer
from frostline.utils.text import normalize_id

SEED_CUSTOMERS = [
    Customer("C-100", "Lotus Seafood", level="gold", region="south"),
    Customer("C-101", "Hanoi Dairy Co", level="silver"),
    Customer("C-102", "Mekong Pharma", level="platinum", region="south"),
    Customer("C-103", "Provincial Health Office", level="bronze", region="central", category="gov"),
    Customer("C-104", "Highland Flowers", level="bronze", region="central"),
]


class CustomerService:
    def __init__(self, customers=None):
        self._by_id = {c.id: c for c in (customers or SEED_CUSTOMERS)}

    def get(self, customer_id):
        key = normalize_id(customer_id)
        if key not in self._by_id:
            raise NotFound("customer %s" % key)
        return self._by_id[key]
