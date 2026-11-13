"""Business validation helpers used by the API layer."""

from decimal import Decimal

from frostline.core.errors import ValidationError

MAX_DIM_CM = 180
MAX_GIRTH_CM = 400


def girth(parcel):
    dims = sorted([parcel.length_cm, parcel.width_cm, parcel.height_cm])
    return dims[2] + 2 * (dims[0] + dims[1])


def check_parcel(parcel):
    if max(parcel.length_cm, parcel.width_cm, parcel.height_cm) > MAX_DIM_CM:
        raise ValidationError("dimension above %d cm" % MAX_DIM_CM)
    if girth(parcel) > MAX_GIRTH_CM:
        raise ValidationError("girth above %d cm" % MAX_GIRTH_CM)
    if parcel.weight_kg <= Decimal("0"):
        raise ValidationError("weight must be positive")
