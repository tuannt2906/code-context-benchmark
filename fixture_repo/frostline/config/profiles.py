"""Named configuration profiles layered on top of DEFAULTS."""

PROFILES = {
    "default": {},
    "express": {
        "pricing.strategy": "distance",
        "surcharge.enabled": ["fuel", "remote", "fragile", "hazmat", "express"],
        "routing.engine": "greedy",
        "notify.channels": ["email", "sms"],
    },
    "eco": {
        "pricing.strategy": "flat",
        "surcharge.enabled": ["remote"],
        "fuel.index": "1.05",
        "discount.stacking": True,
    },
}
