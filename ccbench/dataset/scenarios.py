"""Scenario catalog used by impact-analysis (L5) questions and some L4 items.

Each scenario runs in a *fresh* app; its observable output is the list of API
responses (bodies), in order. Database side effects that are not returned in a
response are not part of the observable output.
"""

PARCEL_A = {"weight": 3.2, "dims": [30, 20, 20]}
PARCEL_B = {"weight": 12, "dims": [60, 40, 40], "fragile": True}

SCENARIOS = {
    "S1": {"profile": "default", "requests": [
        ("POST", "/quotes", {"customer": "C-101", "from": "HAN", "to": "HUE", "parcels": [PARCEL_A, PARCEL_B]}),
    ]},
    "S2": {"profile": "default", "requests": [
        ("POST", "/shipments", {"customer": "C-100", "from": "HAN", "to": "HGI",
                                "parcels": [{"weight": 8, "dims": [40, 30, 30]}], "promo": "cold-10"}),
    ]},
    "S3": {"profile": "default", "requests": [
        ("GET", "/routes", {"from": "HAN", "to": "LCU"}),
    ]},
    "S4": {"profile": "default", "requests": [
        ("POST", "/shipments", {"customer": "C-104", "from": "HPH", "to": "DNG",
                                "parcels": [{"weight": 6, "dims": [40, 30, 20]},
                                            {"weight": 1.5, "dims": [10, 10, 10], "fragile": True}]}),
        ("POST", "/invoices", {"customer": "C-104", "as_of": "2026-12-30"}),
    ]},
    "S5": {"profile": "default", "requests": [
        ("POST", "/storage/estimate", {"product": "seafood", "pallets": 4, "days": 45}),
    ]},
    "S6": {"profile": "express", "requests": [
        ("POST", "/quotes", {"customer": "C-102", "from": "HAN", "to": "HCM", "service": "express",
                             "parcels": [{"weight": 5, "dims": [20, 20, 20], "hazmat": True}]}),
    ]},
    "S7": {"profile": "default", "requests": [
        ("POST", "/storage/compliance", {"product": "vaccine",
                                         "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}),
    ]},
    "S8": {"profile": "default", "requests": [
        ("POST", "/shipments", {"customer": "C-103", "from": "HAN", "to": "LCU",
                                "parcels": [{"weight": 2, "dims": [20, 20, 20], "fragile": True}]}),
        ("GET", "/reports/revenue", {}),
    ]},
}


def describe(ids=None):
    """Human-readable catalog block embedded in L5 questions."""
    import json
    lines = []
    for sid in ids or sorted(SCENARIOS):
        sc = SCENARIOS[sid]
        reqs = "; then ".join("%s %s %s" % (m, p, json.dumps(b, sort_keys=True)) for m, p, b in sc["requests"])
        lines.append("- %s (profile=%s): %s" % (sid, sc["profile"], reqs))
    return "\n".join(lines)
