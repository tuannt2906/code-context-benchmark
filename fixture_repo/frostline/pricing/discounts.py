"""Customer discounts: loyalty levels and promo codes."""

from decimal import Decimal

from frostline.utils.text import normalize_code

LOYALTY_RATES = {
    "bronze": Decimal("0"),
    "silver": Decimal("0.03"),
    "gold": Decimal("0.07"),
    "platinum": Decimal("0.10"),
}

PROMOS = {
    "COLD10": ("percent", Decimal("0.10")),
    "FREEZE5": ("fixed", Decimal("5.00")),
    "ICEBOX": ("percent", Decimal("0.04")),
}


def loyalty_discount(subtotal, customer, settings):
    if not settings.get("discount.loyalty_enabled", True):
        return Decimal("0")
    return subtotal * LOYALTY_RATES.get(customer.level, Decimal("0"))


def promo_discount(subtotal, promo_code):
    if not promo_code:
        return Decimal("0")
    kind, value = PROMOS.get(normalize_code(promo_code), (None, Decimal("0")))
    if kind == "percent":
        return subtotal * value
    if kind == "fixed":
        return min(value, subtotal)
    return Decimal("0")


def apply_discount(subtotal, customer, promo_code, settings):
    """Loyalty and promo discounts do not stack by default: the larger wins."""
    loyalty = loyalty_discount(subtotal, customer, settings)
    promo = promo_discount(subtotal, promo_code)
    if settings.get("discount.stacking", False):
        return loyalty + promo
    return max(loyalty, promo)
