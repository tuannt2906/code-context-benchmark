"""Runtime settings.

Settings are a flat mapping of dotted keys. Values come from three layers,
applied in order: DEFAULTS, then the selected profile (see profiles.py),
then explicit overrides passed by the caller.
"""

from frostline.config.profiles import PROFILES

DEFAULTS = {
    "pricing.strategy": "tiered",
    "pricing.min_charge": "12.50",
    "pricing.volumetric_divisor": 5000,
    "pricing.weight_step": "0.5",
    "tax.region": "north",
    "routing.engine": "dijkstra",
    "surcharge.enabled": ["fuel", "remote", "fragile"],
    "fuel.index": "1.18",
    "discount.loyalty_enabled": True,
    "discount.stacking": False,
    "notify.channels": ["email"],
    "storage.backend": "memory",
    "billing.late_fee_rate": "0.015",
    "billing.grace_days": 10,
    "booking.max_parcel_kg": 70,
}


class Settings:
    """Read-only view over the merged configuration layers."""

    def __init__(self, values, profile="default"):
        self._values = dict(values)
        self.profile = profile

    def get(self, key, default=None):
        return self._values.get(key, default)

    def require(self, key):
        if key not in self._values:
            raise KeyError("missing setting: %s" % key)
        return self._values[key]

    def with_overrides(self, **overrides):
        merged = dict(self._values)
        for key, value in overrides.items():
            merged[key.replace("__", ".")] = value
        return Settings(merged, self.profile)

    def as_dict(self):
        return dict(self._values)


def load_settings(profile="default", overrides=None):
    """Merge DEFAULTS <- PROFILES[profile] <- overrides."""
    values = dict(DEFAULTS)
    values.update(PROFILES.get(profile, {}))
    if overrides:
        values.update(overrides)
    return Settings(values, profile)
