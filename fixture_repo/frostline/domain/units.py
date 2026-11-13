"""Unit conversion and weight rules."""

from decimal import Decimal, ROUND_CEILING

LB_PER_KG = Decimal("2.20462")


def to_kg(value, unit="kg"):
    value = Decimal(str(value))
    if unit == "kg":
        return value
    if unit == "lb":
        return (value / LB_PER_KG).quantize(Decimal("0.001"))
    if unit == "g":
        return value / Decimal(1000)
    raise ValueError("unknown unit %s" % unit)


def volumetric_weight(parcel, divisor=5000):
    """Road freight volumetric weight in kg (cm^3 / divisor)."""
    volume = parcel.length_cm * parcel.width_cm * parcel.height_cm
    return Decimal(volume) / Decimal(divisor)


def volumetric_weight_air(parcel):
    """Air freight volumetric weight in kg (IATA divisor 6000)."""
    volume = parcel.length_cm * parcel.width_cm * parcel.height_cm
    return Decimal(volume) / Decimal(6000)


def round_up_to_step(value, step):
    step = Decimal(step)
    return (value / step).to_integral_value(rounding=ROUND_CEILING) * step


def chargeable_weight(parcel, divisor=5000, step="0.5"):
    """The larger of actual and volumetric weight, rounded up to ``step`` kg."""
    actual = Decimal(parcel.weight_kg)
    volumetric = volumetric_weight(parcel, divisor)
    return round_up_to_step(max(actual, volumetric), step)
