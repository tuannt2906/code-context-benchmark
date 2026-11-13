"""Domain entities."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class Parcel:
    weight_kg: Decimal
    length_cm: int
    width_cm: int
    height_cm: int
    fragile: bool = False
    hazmat: bool = False
    declared_value: Decimal = Decimal("0")


@dataclass
class Shipment:
    customer_id: str
    origin: str
    destination: str
    parcels: List[Parcel]
    service: str = "standard"
    promo_code: Optional[str] = None
    ship_date: str = "2026-11-02"
    id: Optional[str] = None


@dataclass
class Customer:
    id: str
    name: str
    level: str = "bronze"
    region: Optional[str] = None
    category: str = "business"


@dataclass
class Quote:
    shipment_id: Optional[str]
    weight_kg: Decimal
    distance_km: int
    base: Decimal
    surcharges: Dict[str, Decimal] = field(default_factory=dict)
    discount: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    currency: str = "EUR"
