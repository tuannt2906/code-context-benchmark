"""String helpers shared across layers."""


def normalize(value):
    """Lower-case and trim free text (names, notes, channel names)."""
    return (value or "").strip().lower()


def normalize_code(value):
    """Canonical form of promo codes: upper-case, no dashes or spaces."""
    return (value or "").replace("-", "").replace(" ", "").upper()


def normalize_id(value):
    """Canonical form of customer and depot identifiers."""
    return (value or "").strip().upper()


def slugify(value):
    out = []
    for ch in normalize(value):
        out.append(ch if ch.isalnum() else "-")
    return "-".join(part for part in "".join(out).split("-") if part)
