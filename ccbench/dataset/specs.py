"""Hand-written item specifications (dataset v1).

Ground truth is NOT written here: every answer is computed by executing the
``oracle`` snippet against the fixture (see ccbench.oracle.worker). Specs only
contain the question, the answer type, the evidence units a correct answer
must rely on, labels, the rubric and an explanation of the derivation.

Oracle snippet environment (worker): D (Decimal), app(profile, overrides),
call(app, method, path, body) -> body, scenario(sid) -> [bodies],
impact(target, mutation) -> sorted scenario ids whose output changes, and the
fixture modules importable as ``frostline.*``. A snippet must set ANSWER and
may set DISTRACTOR (the answer a look-alike component would produce).
"""

from ccbench.dataset.scenarios import describe

DATASET_VERSION = "v1"

P = "frostline/"


def U(path, name="<module>"):
    return "%s%s::%s" % (P, path, name)


RUBRIC = {
    "number": "Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).",
    "string": "Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.",
    "set": "Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.",
    "list": "Correct iff the ordered list equals the ground truth element by element.",
    "json": "Correct iff the JSON value equals the ground truth structurally (numbers compared numerically).",
}

MUT_TEXT = {
    "plus_cent": "returns exactly 0.01 more than it currently returns",
    "plus_one": "returns exactly 1 more than it currently returns",
    "reverse_list": "returns its current result list in reverse order",
    "lower": "returns the lower-cased version of its current result",
    "empty_list": "returns an empty list (after doing nothing)",
}


def item(id, level, qtype, atype, question, oracle, gold, explanation, indirect=False, lookalike=False,
         tags=(), distractor=None, trace=True, static=()):
    return {
        "id": id, "level": level, "qtype": qtype, "answer_type": atype, "question": question,
        "oracle": oracle, "distractor_oracle": distractor, "gold_units": gold,
        "indirect": indirect, "lookalike": lookalike, "tags": list(tags),
        "rubric": RUBRIC[atype], "explanation": explanation, "trace": trace,
        "static_gold": list(static),
    }


def impact_item(id, target, target_desc, mutation, gold, explanation, indirect=True, lookalike=False):
    q = ("Suppose %s is modified so that it %s (nothing else in the repository changes). "
         "Each scenario below is run in a fresh application instance and its observable output is the list "
         "of API response bodies it returns. Which scenarios would return at least one response body that "
         "differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).\n"
         "Scenarios:\n%s") % (target_desc, MUT_TEXT[mutation], describe())
    return item(id, "L5", "impact_analysis", "set", q, "ANSWER = impact(%r, %r)" % (target, mutation),
                gold, explanation, indirect=indirect, lookalike=lookalike, tags=["mutation"], trace=False)


QUOTE_CORE = [
    U("api/handlers.py", "post_quote"), U("api/serializers.py", "parse_shipment"), U("api/serializers.py", "parse_parcel"),
    U("services/quote_service.py", "QuoteService.create_quote"), U("pricing/quote_engine.py", "QuoteEngine.quote"),
    U("pricing/quote_engine.py", "QuoteEngine.chargeable_weight"), U("pricing/quote_engine.py", "QuoteEngine.surcharges"),
    U("domain/units.py", "chargeable_weight"), U("core/container.py", "Container.pricing_strategy"),
    U("core/container.py", "Container.surcharge_rules"), U("core/container.py", "Container.tax_policy"),
    U("pricing/discounts.py", "apply_discount"), U("config/settings.py"),
]
BOOK_CORE = [
    U("api/handlers.py", "post_shipment"), U("services/shipment_service.py", "ShipmentService.book"),
    U("pricing/quote_engine.py", "QuoteEngine.quote"), U("storage/repositories.py", "ShipmentRepository.save"),
    U("core/container.py", "Container.route_engine"),
]

ITEMS = [
    # ------------------------------------------------------------------ L1
    item("L1-01", "L1", "value_lookup", "number",
         "In frostline/pricing/strategies.py, what rate per kg does TieredStrategy.base_rate return for a chargeable weight of exactly 20 kg?",
         "from frostline.pricing.strategies import TieredStrategy\nANSWER = TieredStrategy(None).base_rate(D('20'), 0)",
         [U("pricing/strategies.py", "TieredStrategy"), U("pricing/strategies.py", "TieredStrategy.base_rate")],
         "TIERS upper bounds are inclusive (weight <= upper): 20 kg falls in the second tier.",
         distractor="DISTRACTOR = D('2.05')"),
    item("L1-02", "L1", "value_compute", "number",
         "In frostline/domain/units.py, what does chargeable_weight return (in kg) for a parcel of 2.2 kg measuring 30x30x30 cm when called with its default arguments?",
         "from frostline.domain.units import chargeable_weight, round_up_to_step, volumetric_weight_air\nfrom frostline.domain.models import Parcel\n"
         "p = Parcel(D('2.2'), 30, 30, 30)\nANSWER = chargeable_weight(p)\nDISTRACTOR = round_up_to_step(max(D('2.2'), volumetric_weight_air(p)), '0.5')",
         [U("domain/units.py", "chargeable_weight"), U("domain/units.py", "volumetric_weight"), U("domain/units.py", "round_up_to_step")],
         "Volumetric weight 27000/5000 = 5.4 kg exceeds 2.2 kg and is rounded up to the 0.5 kg step.", lookalike=True),
    item("L1-03", "L1", "value_compute", "number",
         "In frostline/billing/fees.py, what does calculate_fee(200, 45) return with the default rate and grace period?",
         "from frostline.billing.fees import calculate_fee\nANSWER = calculate_fee(200, 45)",
         [U("billing/fees.py", "calculate_fee")],
         "35 days overdue -> 2 started 30-day periods -> 200 * 0.015 * 2.", lookalike=True),
    item("L1-04", "L1", "value_compute", "number",
         "In frostline/routing/fees.py, what does calculate_fee(350) return?",
         "from frostline.routing.fees import calculate_fee\nANSWER = calculate_fee(350)",
         [U("routing/fees.py", "calculate_fee"), U("routing/fees.py")],
         "First 100 km are free; 250 km * 0.035.", lookalike=True),
    item("L1-05", "L1", "value_compute", "string",
         "In frostline/utils/text.py, what string does normalize_code(' cold-10 ') return?",
         "from frostline.utils.text import normalize_code, normalize\nANSWER = normalize_code(' cold-10 ')\nDISTRACTOR = normalize(' cold-10 ')",
         [U("utils/text.py", "normalize_code")],
         "Dashes and spaces removed, then upper-cased.", lookalike=True),
    item("L1-06", "L1", "control_flow", "json",
         "In frostline/warehouse/sensors.py, assume `within(zone, c)` is True exactly when zone.min_c <= c <= zone.max_c, and the zone range is 0..4 C. "
         "What does excursions(zone, readings) return (default min_minutes) for readings = [(0, 2), (5, 6), (12, 7), (20, 8), (22, 3), (40, 9), (45, 3)]? Answer as a JSON list of [start, end] pairs.",
         "from frostline.warehouse.sensors import excursions\nfrom frostline.warehouse.zones import Zone\n"
         "z = Zone('X', D('0'), D('4'), D('1'))\nANSWER = [list(r) for r in excursions(z, [(0, 2), (5, 6), (12, 7), (20, 8), (22, 3), (40, 9), (45, 3)])]",
         [U("warehouse/sensors.py", "excursions")],
         "Runs outside range: 5..20 (15 min, kept) and 40..40 (0 min, dropped)."),
    item("L1-07", "L1", "value_compute", "number",
         "In frostline/pricing/money.py, what does round_money_even(Decimal('2.345')) return?",
         "from frostline.pricing.money import round_money_even, round_money\nANSWER = round_money_even(D('2.345'))\nDISTRACTOR = round_money(D('2.345'))",
         [U("pricing/money.py", "round_money_even"), U("pricing/money.py")],
         "Banker's rounding: half goes to the even cent.", lookalike=True),
    item("L1-08", "L1", "api_semantics", "string",
         "In frostline/core/registry.py, what exception class is raised when the same (kind, name) is registered twice without replace=True? Give the class name.",
         "from frostline.core import registry\nfrom frostline.core.errors import RegistryError\n"
         "try:\n    registry.register('zz_test', 'x')(type('A', (), {}))\n    registry.register('zz_test', 'x')(type('B', (), {}))\n    ANSWER = None\n"
         "except Exception as exc:\n    ANSWER = type(exc).__name__\nfinally:\n    registry._REGISTRY.pop(('zz_test', 'x'), None)",
         [U("core/registry.py", "register")], "register() checks for an existing key unless replace is set."),
    item("L1-09", "L1", "value_compute", "number",
         "In frostline/warehouse/storage_fees.py, what does handling_fee(12) return?",
         "from frostline.warehouse.storage_fees import handling_fee\nANSWER = handling_fee(12)",
         [U("warehouse/storage_fees.py", "handling_fee")], "6.00 per pallet capped at 60.00."),
    item("L1-10", "L1", "value_compute", "number",
         "In frostline/domain/validation.py, what does girth(parcel) return for a parcel measuring length 100, width 30, height 50 cm?",
         "from frostline.domain.validation import girth\nfrom frostline.domain.models import Parcel\nANSWER = girth(Parcel(D('1'), 100, 30, 50))",
         [U("domain/validation.py", "girth")], "Longest side + 2 * (sum of the two shorter sides)."),
    item("L1-11", "L1", "value_compute", "number",
         "In frostline/pricing/discounts.py, what does apply_discount return for a subtotal of 80.00, a customer with level 'gold', promo code 'FREEZE5', "
         "and settings where discount.loyalty_enabled is True and discount.stacking is False?",
         "from frostline.pricing.discounts import apply_discount\nfrom frostline.domain.models import Customer\nfrom frostline.config.settings import Settings\n"
         "s = Settings({'discount.loyalty_enabled': True, 'discount.stacking': False})\nANSWER = apply_discount(D('80.00'), Customer('X', 'x', level='gold'), 'FREEZE5', s)\n"
         "DISTRACTOR = D('80.00') * D('0.07') + D('5.00')",
         [U("pricing/discounts.py", "apply_discount"), U("pricing/discounts.py", "loyalty_discount"),
          U("pricing/discounts.py", "promo_discount"), U("pricing/discounts.py")],
         "Without stacking the larger of loyalty (5.60) and promo (5.00) wins."),
    item("L1-12", "L1", "config_lookup", "set",
         "In frostline/config/profiles.py, which surcharge codes are enabled by the 'express' profile?",
         "from frostline.config.profiles import PROFILES\nANSWER = sorted(PROFILES['express']['surcharge.enabled'])",
         [U("config/profiles.py")], "Read the 'surcharge.enabled' list of the express profile."),
    item("L1-13", "L1", "value_compute", "number",
         "In frostline/pricing/money.py, what integer does to_cents(Decimal('19.995')) return?",
         "from frostline.pricing.money import to_cents\nANSWER = to_cents(D('19.995'))",
         [U("pricing/money.py", "to_cents"), U("pricing/money.py", "round_money")],
         "to_cents first applies round_money (half-up) -> 20.00 -> 2000 cents."),

    # ------------------------------------------------------------------ L2
    item("L2-01", "L2", "value_compute", "number",
         "Under the default settings, what total chargeable weight (kg) does QuoteEngine.chargeable_weight compute for a shipment with a single parcel of 4 kg measuring 41x33x27 cm?",
         "from frostline.pricing.quote_engine import QuoteEngine\nfrom frostline.domain.models import Parcel, Shipment\nfrom frostline.domain.units import round_up_to_step, volumetric_weight_air\n"
         "p = Parcel(D('4'), 41, 33, 27)\nANSWER = QuoteEngine(app().container).chargeable_weight(Shipment('C-101', 'HAN', 'HUE', [p]))\n"
         "DISTRACTOR = round_up_to_step(max(D('4'), volumetric_weight_air(p)), '0.5')",
         [U("pricing/quote_engine.py", "QuoteEngine.chargeable_weight"), U("domain/units.py", "chargeable_weight"),
          U("domain/units.py", "volumetric_weight"), U("domain/units.py", "round_up_to_step"), U("config/settings.py")],
         "Divisor 5000 and step 0.5 come from DEFAULTS; volumetric 36531/5000 = 7.31 -> 7.5.", lookalike=True),
    item("L2-02", "L2", "value_compute", "number",
         "With the default settings, what base price does the pricing strategy registered as 'flat' return for a chargeable weight of 3 kg?",
         "from frostline.pricing.strategies import FlatStrategy\nANSWER = FlatStrategy(app().settings).price(D('3'), 100)\nDISTRACTOR = D('3') * D('2.40')",
         [U("pricing/strategies.py", "FlatStrategy"), U("pricing/strategies.py", "FlatStrategy.price"),
          U("pricing/strategies.py", "FlatStrategy.min_charge"), U("config/settings.py")],
         "3 * 2.40 = 7.20 is below the configured minimum charge of 12.50."),
    item("L2-03", "L2", "value_compute", "number",
         "With the default settings, what does apply_discount return for a subtotal of 50.00, a 'silver' customer and promo code ' icebox '?",
         "from frostline.pricing.discounts import apply_discount\nfrom frostline.domain.models import Customer\n"
         "ANSWER = apply_discount(D('50.00'), Customer('X', 'x', level='silver'), ' icebox ', app().settings)\nDISTRACTOR = D('50.00') * D('0.03')",
         [U("pricing/discounts.py", "apply_discount"), U("pricing/discounts.py", "promo_discount"), U("pricing/discounts.py", "loyalty_discount"),
          U("pricing/discounts.py"), U("utils/text.py", "normalize_code"), U("config/settings.py")],
         "normalize_code maps ' icebox ' to ICEBOX (4% = 2.00), larger than silver loyalty (1.50)."),
    item("L2-04", "L2", "data_flow", "number",
         "What total distance in km does DijkstraEngine compute from depot HAN to depot HUE on the default network?",
         "from frostline.routing.engines import DijkstraEngine\nfrom frostline.routing.network import default_network\nANSWER = DijkstraEngine(default_network()).distance('HAN', 'HUE')",
         [U("routing/engines.py", "DijkstraEngine.path"), U("core/interfaces.py", "RouteEngine.distance"), U("routing/network.py"),
          U("routing/network.py", "Network.edge"), U("routing/network.py", "Network.neighbours")],
         "Shortest path HAN-NDH-THO-VIN-HUE (95+85+140+360) beats THO-HUE direct (520)."),
    item("L2-05", "L2", "control_flow", "list",
         "What path (ordered list of depot codes) does GreedyEngine.path return from HPH to LCU on the default network?",
         "from frostline.routing.engines import GreedyEngine, DijkstraEngine\nfrom frostline.routing.network import default_network\n"
         "ANSWER = GreedyEngine(default_network()).path('HPH', 'LCU')\nDISTRACTOR = DijkstraEngine(default_network()).path('HPH', 'LCU')",
         [U("routing/engines.py", "GreedyEngine.path"), U("routing/network.py"), U("routing/network.py", "Network.neighbours")],
         "Nearest-neighbour walk: from HPH the nearest is NDH (70), then HAN (95), TNG (80), LCU - longer than the shortest path via HAN.", lookalike=True),
    item("L2-06", "L2", "data_flow", "number",
         "What value does POST /storage/estimate return in its 'total' field for the body {\"product\": \"flowers\", \"pallets\": 2, \"days\": 10}?",
         "ANSWER = call(app(), 'POST', '/storage/estimate', {'product': 'flowers', 'pallets': 2, 'days': 10})['total']",
         [U("api/warehouse_handlers.py", "post_storage_estimate"), U("warehouse/storage_fees.py", "calculate_fee"),
          U("warehouse/storage_fees.py", "handling_fee"), U("warehouse/storage_fees.py"), U("warehouse/zones.py"), U("warehouse/zones.py", "zone_for")],
         "Flowers -> CHL (1.35/day); 8 billable days * 2 pallets = 21.60; handling 12.00 counted twice.", lookalike=True),
    item("L2-07", "L2", "data_flow", "number",
         "When a request body uses \"weight_unit\": \"lb\" and a parcel has \"weight\": 11, what weight_kg value ends up in the parsed Parcel?",
         "from frostline.api.serializers import parse_parcel\nANSWER = parse_parcel({'weight': 11, 'dims': [10, 10, 10]}, 'lb').weight_kg",
         [U("api/serializers.py", "parse_parcel"), U("domain/units.py", "to_kg"), U("domain/units.py")],
         "11 / 2.20462 quantized to 0.001."),
    item("L2-08", "L2", "control_flow", "number",
         "What HTTP status does App.handle return for POST /quotes when one parcel has dims [200, 10, 10] (other fields valid: customer C-101, from HAN, to HUE, weight 3)?",
         "r = app().handle('POST', '/quotes', {'customer': 'C-101', 'from': 'HAN', 'to': 'HUE', 'parcels': [{'weight': 3, 'dims': [200, 10, 10]}]})\nANSWER = r['status']",
         [U("api/app.py", "App.handle"), U("api/serializers.py", "parse_shipment"), U("domain/validation.py", "check_parcel"),
          U("domain/validation.py"), U("core/errors.py", "ValidationError")],
         "check_parcel raises ValidationError (status 422) which App.handle converts to the response status."),
    item("L2-09", "L2", "control_flow", "string",
         "What 'status' does POST /storage/compliance return for product 'seafood' with readings [[0, -20], [10, -15], [20, -12], [30, -19]]?",
         "ANSWER = call(app(), 'POST', '/storage/compliance', {'product': 'seafood', 'readings': [[0, -20], [10, -15], [20, -12], [30, -19]]})['status']",
         [U("api/warehouse_handlers.py", "post_compliance"), U("warehouse/sensors.py", "compliance_status"), U("warehouse/sensors.py", "excursions"),
          U("warehouse/zones.py", "within"), U("warehouse/zones.py")],
         "Seafood is FRZ (-25..-18); the out-of-range run 10..20 lasts 10 min < 15, so no excursion."),
    item("L2-10", "L2", "value_compute", "number",
         "What does calculate_fee('vaccine', 3, 40) in frostline/warehouse/storage_fees.py return?",
         "from frostline.warehouse.storage_fees import calculate_fee\nANSWER = calculate_fee('vaccine', 3, 40)",
         [U("warehouse/storage_fees.py", "calculate_fee"), U("warehouse/storage_fees.py"), U("warehouse/zones.py"), U("warehouse/zones.py", "zone_for")],
         "Vaccine -> CHL 1.35; 38 billable days = 28 normal + 10 long-stay at 80%."),

    # ------------------------------------------------------------------ L3
    item("L3-01", "L3", "dispatch_resolution", "number",
         "In the running application, how much tax is charged for customer C-103 on a taxable amount of 150.00?",
         "from frostline.services.customer_service import CustomerService\nfrom frostline.tax.policies import CentralTax\n"
         "ANSWER = app().container.tax_policy(CustomerService().get('C-103')).tax(D('150.00'))\nDISTRACTOR = CentralTax().tax(D('150.00'))",
         [U("core/container.py", "Container.tax_policy"), U("tax/policies.py", "ExemptTax"), U("tax/policies.py", "ExemptTax.tax"),
          U("services/customer_service.py")],
         "C-103 has category 'gov', so the container resolves the 'exempt' policy before looking at its region.", indirect=True, lookalike=True),
    item("L3-02", "L3", "dispatch_resolution", "number",
         "What 'toll' value does GET /routes return for the body {\"from\": \"HAN\", \"to\": \"LCU\"} under the default settings?",
         "ANSWER = call(app(), 'GET', '/routes', {'from': 'HAN', 'to': 'LCU'})['toll']",
         [U("api/handlers.py", "get_route"), U("routing/fees.py", "calculate_fee"), U("routing/fees.py"), U("core/container.py", "Container.route_engine"),
          U("routing/engines.py", "DijkstraEngine.path"), U("core/interfaces.py", "RouteEngine.distance"), U("routing/network.py")],
         "Dijkstra (configured engine) gives HAN-TNG-LCU = 290 km; toll = (290-100) * 0.035.", indirect=True, lookalike=True),
    item("L3-03", "L3", "dispatch_resolution", "number",
         "In the default application, what 'remote' surcharge amount is applied to a shipment from HAN to HGI with 3 parcels (base price 30.00)?",
         "from frostline.pricing.quote_engine import QuoteEngine\nfrom frostline.domain.models import Parcel, Shipment\n"
         "s = Shipment('C-101', 'HAN', 'HGI', [Parcel(D('1'), 10, 10, 10) for _ in range(3)])\n"
         "ANSWER = QuoteEngine(app().container).surcharges(D('30.00'), s)['remote']\nDISTRACTOR = D('9.00')",
         [U("plugins/island.py", "PartnerRemoteRule"), U("plugins/island.py", "PartnerRemoteRule.amount"), U("domain/rules/remote.py", "RemoteAreaRule.applies"),
          U("core/registry.py", "register"), U("api/app.py"), U("plugins/__init__.py"), U("core/container.py", "Container.surcharge_rules")],
         "plugins/island.py re-registers 'remote' with replace=True after the built-ins: max(7.50, 3 * 3.20).", indirect=True, lookalike=True,
         static=[U("core/registry.py", "register")]),
    item("L3-04", "L3", "dispatch_resolution", "string",
         "In the default application, which class (class name only) actually computes the amount of the 'remote' surcharge?",
         "from frostline.core.registry import resolve\nimport frostline.api.app\nANSWER = resolve('surcharge', 'remote').__name__\nDISTRACTOR = 'RemoteAreaRule'",
         [U("plugins/island.py", "PartnerRemoteRule"), U("plugins/island.py", "PartnerRemoteRule.amount"), U("core/registry.py", "register"),
          U("api/app.py"), U("plugins/__init__.py")],
         "Plugins are imported last and PartnerRemoteRule registers with replace=True.", indirect=True, lookalike=True, trace=False),
    item("L3-05", "L3", "dispatch_resolution", "number",
         "Under the 'express' profile, what base price does the configured pricing strategy return for a chargeable weight of 10 kg over 680 km?",
         "from frostline.pricing.strategies import TieredStrategy\nANSWER = app('express').container.pricing_strategy().price(D('10'), 680)\n"
         "DISTRACTOR = TieredStrategy(app().settings).price(D('10'), 680)",
         [U("config/profiles.py"), U("core/container.py", "Container.pricing_strategy"), U("pricing/strategies.py", "DistanceStrategy.price"),
          U("pricing/strategies.py", "DistanceStrategy"), U("pricing/strategies.py", "FlatStrategy.price"), U("pricing/strategies.py", "TieredStrategy.base_rate"),
          U("pricing/strategies.py", "FlatStrategy.min_charge")],
         "express -> 'distance' strategy: tiered price 10 * 2.60 = 26.00 plus 0.012 * 680.", indirect=True),
    item("L3-06", "L3", "config_lookup", "set",
         "With the default profile, which surcharge codes can ever appear in the 'surcharges' of a quote?",
         "ANSWER = sorted(app().settings.get('surcharge.enabled'))\nDISTRACTOR = ['express', 'fragile', 'fuel', 'hazmat', 'insurance', 'remote', 'weekend']",
         [U("config/settings.py"), U("core/container.py", "Container.surcharge_rules"), U("pricing/quote_engine.py", "QuoteEngine.surcharges")],
         "Only rules listed in surcharge.enabled are instantiated; registered-but-disabled rules never run.", indirect=True, lookalike=True, trace=False),
    item("L3-07", "L3", "event_flow", "set",
         "If the application is created with the override notify.channels = ['SMS', 'Email'] and a shipment is booked, which template names appear in the outbox rows created for that booking?",
         "a = app('default', {'notify.channels': ['SMS', 'Email']})\n"
         "call(a, 'POST', '/shipments', {'customer': 'C-101', 'from': 'HAN', 'to': 'HUE', 'parcels': [{'weight': 2, 'dims': [10, 10, 10]}]})\n"
         "ANSWER = sorted({r['template'] for r in a.db.tables['outbox']})\nDISTRACTOR = ['booking_confirmation_v1', 'booking_sms_legacy']",
         [U("services/notification_service.py", "notify_booking"), U("services/notification_service.py"), U("utils/text.py", "normalize"),
          U("services/shipment_service.py", "ShipmentService.book"), U("core/events.py", "EventBus.publish")],
         "notify_booking normalizes channel names to lower case and looks them up in TEMPLATES.", indirect=True, lookalike=True),
    item("L3-08", "L3", "event_flow", "set",
         "When POST /quotes succeeds, which database tables receive new rows?",
         "a = app()\ncall(a, 'POST', '/quotes', {'customer': 'C-101', 'from': 'HAN', 'to': 'HUE', 'parcels': [{'weight': 2, 'dims': [10, 10, 10]}]})\n"
         "ANSWER = sorted(t for t, rows in a.db.tables.items() if rows)",
         [U("services/quote_service.py", "QuoteService.create_quote"), U("storage/repositories.py", "QuoteRepository"),
          U("services/audit_service.py", "audit_quote"), U("storage/repositories.py", "AuditRepository"), U("core/events.py", "EventBus.publish")],
         "QuoteRepository writes 'quotes'; the 'quote.created' event triggers audit_quote which writes 'audit'.", indirect=True),
    item("L3-09", "L3", "event_flow", "set",
         "When POST /shipments succeeds under the default settings, which database tables receive new rows?",
         "a = app()\ncall(a, 'POST', '/shipments', {'customer': 'C-101', 'from': 'HAN', 'to': 'HUE', 'parcels': [{'weight': 2, 'dims': [10, 10, 10]}]})\n"
         "ANSWER = sorted(t for t, rows in a.db.tables.items() if rows)\nDISTRACTOR = ['audit', 'outbox', 'quotes', 'shipments']",
         [U("services/shipment_service.py", "ShipmentService.book"), U("storage/repositories.py", "ShipmentRepository"),
          U("services/notification_service.py", "notify_booking"), U("services/audit_service.py", "audit_booking"),
          U("storage/repositories.py", "OutboxRepository"), U("storage/repositories.py", "AuditRepository")],
         "Booking uses QuoteEngine directly (no quote row); 'shipment.booked' triggers outbox and audit writers.", indirect=True, lookalike=True),
    item("L3-10", "L3", "event_flow", "list",
         "In which order are the event handler functions invoked when the 'shipment.booked' event is published? Give the function names in order.",
         "import frostline.api.app\nfrom frostline.core.events import subscribers\nANSWER = subscribers('shipment.booked')",
         [U("services/__init__.py"), U("core/events.py", "subscribe"), U("core/events.py", "EventBus.publish"),
          U("services/notification_service.py", "notify_booking"), U("services/audit_service.py", "audit_booking")],
         "Handlers run in subscription order; services/__init__ imports notification_service before audit_service.", indirect=True, trace=False),
    item("L3-11", "L3", "dispatch_resolution", "number",
         "Under the 'eco' profile, what fuel surcharge amount is applied to a shipment from HAN to HUE whose base price is 40.00? (Answer 0 if none.)",
         "from frostline.pricing.quote_engine import QuoteEngine\nfrom frostline.domain.models import Parcel, Shipment\n"
         "s = Shipment('C-101', 'HAN', 'HUE', [Parcel(D('1'), 10, 10, 10)])\nANSWER = QuoteEngine(app('eco').container).surcharges(D('40.00'), s).get('fuel', 0)\n"
         "DISTRACTOR = D('40.00') * D('0.05')",
         [U("config/profiles.py"), U("core/container.py", "Container.surcharge_rules"), U("pricing/quote_engine.py", "QuoteEngine.surcharges")],
         "The eco profile enables only the 'remote' rule, so the fuel rule (index 1.05) is never instantiated.", indirect=True, lookalike=True),
    item("L3-12", "L3", "dispatch_resolution", "number",
         "Under the default settings, what VAT rate is applied to quotes for customer C-100?",
         "from frostline.services.customer_service import CustomerService\nANSWER = app().container.tax_policy(CustomerService().get('C-100')).rate\nDISTRACTOR = D('0.08')",
         [U("core/container.py", "Container.tax_policy"), U("services/customer_service.py"), U("tax/policies.py", "SouthTax"), U("config/settings.py")],
         "The customer's own region ('south') takes precedence over the tax.region default ('north').", indirect=True, lookalike=True),
    item("L3-13", "L3", "dispatch_resolution", "number",
         "What 'distance_km' does GET /routes return for the body {\"from\": \"HPH\", \"to\": \"THO\"} under the default settings?",
         "ANSWER = call(app(), 'GET', '/routes', {'from': 'HPH', 'to': 'THO'})['distance_km']",
         [U("api/handlers.py", "get_route"), U("core/container.py", "Container.route_engine"), U("routing/engines.py", "DijkstraEngine.path"),
          U("core/interfaces.py", "RouteEngine.distance"), U("routing/network.py")],
         "The configured engine is dijkstra: HPH-NDH-THO.", indirect=True),

    # ------------------------------------------------------------------ L4
    item("L4-01", "L4", "data_flow", "number",
         "What 'total' does POST /quotes return (default profile) for the body {\"customer\": \"C-101\", \"from\": \"HAN\", \"to\": \"HUE\", \"parcels\": "
         "[{\"weight\": 3.2, \"dims\": [30, 20, 20]}, {\"weight\": 12, \"dims\": [60, 40, 40], \"fragile\": true}]}?",
         "ANSWER = scenario('S1')[0]['total']",
         QUOTE_CORE + [U("pricing/strategies.py", "TieredStrategy.base_rate"), U("pricing/strategies.py", "FlatStrategy.price"),
                       U("domain/rules/fuel.py", "FuelRule.amount"), U("domain/rules/fragile.py", "FragileRule"),
                       U("domain/rules/base.py", "PerParcelRule.amount"), U("pricing/discounts.py", "loyalty_discount"), U("tax/policies.py", "NorthTax")],
         "Per-parcel chargeable weights (volumetric vs actual, rounded to 0.5 kg) are summed and priced by tier; fuel and fragile surcharges; silver loyalty discount; north VAT (C-101 has no region).", indirect=True),
    item("L4-02", "L4", "data_flow", "number",
         "After POST /shipments (default profile) with body {\"customer\": \"C-100\", \"from\": \"HAN\", \"to\": \"HGI\", \"parcels\": [{\"weight\": 8, \"dims\": [40, 30, 30]}], "
         "\"promo\": \"cold-10\"}, what integer value is stored in the 'total_cents' column of the new shipments row?",
         "a = app()\ncall(a, 'POST', '/shipments', {'customer': 'C-100', 'from': 'HAN', 'to': 'HGI', 'parcels': [{'weight': 8, 'dims': [40, 30, 30]}], 'promo': 'cold-10'})\n"
         "ANSWER = a.db.tables['shipments'][0]['total_cents']",
         BOOK_CORE + [U("plugins/island.py", "PartnerRemoteRule.amount"), U("pricing/discounts.py", "promo_discount"), U("utils/text.py", "normalize_code"),
                      U("tax/policies.py", "SouthTax"), U("pricing/money.py", "to_cents"), U("core/container.py", "Container.tax_policy")],
         "Remote partner surcharge, COLD10 (10%) beats gold loyalty (7%), south VAT 10%, stored in cents.", indirect=True, lookalike=True),
    item("L4-03", "L4", "data_flow", "string",
         "After POST /shipments (default profile) with body {\"customer\": \"C-102\", \"from\": \"HPH\", \"to\": \"CTH\", \"parcels\": [{\"weight\": 10, \"dims\": [30, 30, 30]}]}, "
         "what string is stored in the 'route' column of the shipments row?",
         "a = app()\ncall(a, 'POST', '/shipments', {'customer': 'C-102', 'from': 'HPH', 'to': 'CTH', 'parcels': [{'weight': 10, 'dims': [30, 30, 30]}]})\n"
         "ANSWER = a.db.tables['shipments'][0]['route']",
         BOOK_CORE + [U("routing/engines.py", "DijkstraEngine.path"), U("routing/network.py")],
         "Route comes from the configured Dijkstra engine and is joined with '-'.", indirect=True),
    item("L4-04", "L4", "data_flow", "number",
         "What 'tax' does POST /quotes return (default profile) for the body {\"customer\": \"C-104\", \"from\": \"HAN\", \"to\": \"DNG\", \"parcels\": "
         "[{\"weight\": 7, \"dims\": [50, 40, 30]}, {\"weight\": 2, \"dims\": [20, 20, 20]}]}?",
         "ANSWER = call(app(), 'POST', '/quotes', {'customer': 'C-104', 'from': 'HAN', 'to': 'DNG', 'parcels': [{'weight': 7, 'dims': [50, 40, 30]}, {'weight': 2, 'dims': [20, 20, 20]}]})['tax']",
         QUOTE_CORE + [U("tax/policies.py", "CentralTax.tax"), U("tax/policies.py", "CentralTax"), U("services/customer_service.py")],
         "C-104 is in region 'central': 5% on the first 100 of the taxable amount, 10% above.", indirect=True),
    item("L4-05", "L4", "data_flow", "set",
         "Which surcharge codes appear in the 'surcharges' of the POST /quotes response under the 'express' profile for the body {\"customer\": \"C-102\", \"from\": \"HAN\", "
         "\"to\": \"HCM\", \"service\": \"express\", \"parcels\": [{\"weight\": 5, \"dims\": [20, 20, 20], \"hazmat\": true}]}?",
         "ANSWER = sorted(scenario('S6')[0]['surcharges'])",
         QUOTE_CORE + [U("config/profiles.py"), U("plugins/express.py", "ExpressRule.applies"), U("domain/rules/hazmat.py", "HazmatRule.applies"),
                       U("domain/rules/remote.py", "RemoteAreaRule.applies"), U("domain/rules/fragile.py", "FragileRule.matches")],
         "Express enables five rules; remote does not apply (HCM is not remote) and fragile matches no parcel.", indirect=True),
    item("L4-06", "L4", "data_flow", "number",
         "What 'total' does the POST /quotes call of scenario S6 return? S6: profile 'express', body {\"customer\": \"C-102\", \"from\": \"HAN\", \"to\": \"HCM\", "
         "\"service\": \"express\", \"parcels\": [{\"weight\": 5, \"dims\": [20, 20, 20], \"hazmat\": true}]}.",
         "ANSWER = scenario('S6')[0]['total']",
         QUOTE_CORE + [U("config/profiles.py"), U("pricing/strategies.py", "DistanceStrategy.price"), U("routing/engines.py", "GreedyEngine.path"),
                       U("plugins/express.py", "ExpressRule"), U("domain/rules/hazmat.py", "HazmatRule"), U("domain/rules/fuel.py", "FuelRule.amount"),
                       U("tax/policies.py", "SouthTax")],
         "Distance strategy over the greedy route, fuel + hazmat + express surcharges, platinum discount, south VAT.", indirect=True),
    item("L4-07", "L4", "data_flow", "number",
         "Scenario: in a fresh default app, POST /shipments with {\"customer\": \"C-104\", \"from\": \"HPH\", \"to\": \"DNG\", \"parcels\": [{\"weight\": 6, \"dims\": [40, 30, 20]}, "
         "{\"weight\": 1.5, \"dims\": [10, 10, 10], \"fragile\": true}]}, then POST /invoices with {\"customer\": \"C-104\", \"as_of\": \"2026-12-30\"}. What 'late_fee' does the invoice response contain?",
         "ANSWER = scenario('S4')[1]['late_fee']",
         [U("api/handlers.py", "post_invoice"), U("services/billing_service.py", "BillingService.invoice"), U("billing/fees.py", "calculate_fee"),
          U("utils/dates.py", "days_between"), U("domain/models.py", "Shipment"), U("pricing/money.py", "round_money_even"), U("config/settings.py"),
          U("storage/repositories.py", "ShipmentRepository.save")] + BOOK_CORE,
         "Ship date defaults to 2026-11-02: 58 days, 48 overdue after 10 grace days -> 2 periods of 1.5%.", indirect=True, lookalike=True),
    item("L4-08", "L4", "data_flow", "number",
         "What 'weight_kg' does POST /quotes return for {\"customer\": \"C-101\", \"from\": \"HAN\", \"to\": \"NDH\", \"weight_unit\": \"lb\", \"parcels\": [{\"weight\": 22, \"dims\": [20, 20, 20]}]}?",
         "ANSWER = call(app(), 'POST', '/quotes', {'customer': 'C-101', 'from': 'HAN', 'to': 'NDH', 'weight_unit': 'lb', 'parcels': [{'weight': 22, 'dims': [20, 20, 20]}]})['weight_kg']",
         [U("api/serializers.py", "parse_shipment"), U("api/serializers.py", "parse_parcel"), U("domain/units.py", "to_kg"),
          U("pricing/quote_engine.py", "QuoteEngine.chargeable_weight"), U("domain/units.py", "chargeable_weight"), U("domain/units.py", "round_up_to_step"),
          U("api/serializers.py", "quote_to_dict")],
         "22 lb = 9.979 kg, larger than volumetric 1.6 kg, rounded up to the 0.5 kg step."),
    item("L4-09", "L4", "data_flow", "string",
         "Under the 'express' profile, what string is stored in the 'route' column after POST /shipments with {\"customer\": \"C-101\", \"from\": \"HPH\", \"to\": \"LCU\", "
         "\"parcels\": [{\"weight\": 2, \"dims\": [10, 10, 10]}]}?",
         "a = app('express')\ncall(a, 'POST', '/shipments', {'customer': 'C-101', 'from': 'HPH', 'to': 'LCU', 'parcels': [{'weight': 2, 'dims': [10, 10, 10]}]})\n"
         "ANSWER = a.db.tables['shipments'][0]['route']\nDISTRACTOR = '-'.join(app().container.route_engine().path('HPH', 'LCU'))",
         BOOK_CORE + [U("config/profiles.py"), U("routing/engines.py", "GreedyEngine.path"), U("routing/network.py")],
         "The express profile switches routing.engine to 'greedy'.", indirect=True, lookalike=True),
    item("L4-10", "L4", "event_flow", "string",
         "Under the default settings, after POST /shipments with {\"customer\": \"c-103\", \"from\": \"HAN\", \"to\": \"HUE\", \"parcels\": [{\"weight\": 1, \"dims\": [10, 10, 10]}]}, "
         "what value is written to the 'to' column of the outbox row?",
         "a = app()\ncall(a, 'POST', '/shipments', {'customer': 'c-103', 'from': 'HAN', 'to': 'HUE', 'parcels': [{'weight': 1, 'dims': [10, 10, 10]}]})\n"
         "ANSWER = a.db.tables['outbox'][0]['to']",
         [U("services/notification_service.py", "notify_booking"), U("utils/text.py", "slugify"), U("utils/text.py", "normalize"),
          U("services/shipment_service.py", "ShipmentService.book"), U("services/customer_service.py"), U("utils/text.py", "normalize_id"),
          U("config/settings.py")],
         "The customer id is normalized to C-103 (Provincial Health Office); recipient = slug + '@' + channel.", indirect=True),
    item("L4-11", "L4", "data_flow", "number",
         "What 'total' does POST /shipments return (default profile) for {\"customer\": \"C-103\", \"from\": \"HAN\", \"to\": \"LCU\", \"parcels\": [{\"weight\": 2, \"dims\": [20, 20, 20], \"fragile\": true}]}?",
         "ANSWER = scenario('S8')[0]['total']",
         BOOK_CORE + [U("plugins/island.py", "PartnerRemoteRule.amount"), U("tax/policies.py", "ExemptTax.tax"), U("core/container.py", "Container.tax_policy"),
                      U("pricing/strategies.py", "FlatStrategy.min_charge"), U("domain/rules/fragile.py", "FragileRule"), U("domain/rules/fuel.py", "FuelRule.amount")],
         "Minimum charge, fuel, fragile and partner remote surcharges; gov customer is tax exempt.", indirect=True, lookalike=True),
    item("L4-12", "L4", "data_flow", "number",
         "In a fresh default app, two bookings are made with POST /shipments: (1) {\"customer\": \"C-100\", \"from\": \"HAN\", \"to\": \"HGI\", \"parcels\": [{\"weight\": 8, \"dims\": [40, 30, 30]}], \"promo\": \"cold-10\"} and "
         "(2) {\"customer\": \"C-100\", \"from\": \"HAN\", \"to\": \"HPH\", \"parcels\": [{\"weight\": 1, \"dims\": [10, 10, 10]}]}. What revenue value does GET /reports/revenue then report for C-100?",
         "a = app()\ncall(a, 'POST', '/shipments', {'customer': 'C-100', 'from': 'HAN', 'to': 'HGI', 'parcels': [{'weight': 8, 'dims': [40, 30, 30]}], 'promo': 'cold-10'})\n"
         "call(a, 'POST', '/shipments', {'customer': 'C-100', 'from': 'HAN', 'to': 'HPH', 'parcels': [{'weight': 1, 'dims': [10, 10, 10]}]})\n"
         "ANSWER = call(a, 'GET', '/reports/revenue', {})['revenue']['C-100']",
         BOOK_CORE + [U("reporting/metrics.py", "revenue_by_customer"), U("api/handlers.py", "get_revenue"), U("pricing/money.py", "from_cents"),
                      U("plugins/island.py", "PartnerRemoteRule.amount"), U("pricing/discounts.py", "apply_discount"), U("tax/policies.py", "SouthTax")],
         "Sum of the two stored totals (in cents) converted back to EUR.", indirect=True),
]

ITEMS += [
    impact_item("L5-01", "frostline.pricing.money:round_money_even", "the function `round_money_even` in frostline/pricing/money.py", "plus_one",
                [U("pricing/money.py", "round_money_even"), U("services/billing_service.py", "BillingService.invoice"), U("api/handlers.py", "post_invoice")],
                "Only invoicing uses banker's rounding; only S4 issues an invoice.", lookalike=True),
    impact_item("L5-02", "frostline.pricing.money:round_money", "the function `round_money` in frostline/pricing/money.py", "plus_one",
                [U("pricing/money.py", "round_money"), U("pricing/quote_engine.py", "QuoteEngine.quote"), U("warehouse/storage_fees.py", "calculate_fee"),
                 U("pricing/money.py", "to_cents"), U("api/handlers.py", "get_route"), U("routing/fees.py", "calculate_fee")],
                "Quotes/bookings and storage fees use round_money; the route toll uses quantize directly; compliance uses no money.", lookalike=True),
    impact_item("L5-03", "frostline.routing.fees:calculate_fee", "the function `calculate_fee` in frostline/routing/fees.py", "plus_one",
                [U("routing/fees.py", "calculate_fee"), U("api/handlers.py", "get_route")],
                "Only GET /routes imports the routing toll function; billing and storage have their own calculate_fee.", lookalike=True),
    impact_item("L5-04", "frostline.billing.fees:calculate_fee", "the function `calculate_fee` in frostline/billing/fees.py", "plus_one",
                [U("billing/fees.py", "calculate_fee"), U("services/billing_service.py", "BillingService.invoice"), U("api/handlers.py", "post_invoice")],
                "Only invoicing (S4) calls the late-fee function.", lookalike=True),
    impact_item("L5-05", "frostline.warehouse.storage_fees:calculate_fee", "the function `calculate_fee` in frostline/warehouse/storage_fees.py", "plus_one",
                [U("warehouse/storage_fees.py", "calculate_fee"), U("api/warehouse_handlers.py", "post_storage_estimate")],
                "Only the storage estimate endpoint (S5) uses it.", lookalike=True),
    impact_item("L5-06", "frostline.domain.rules.remote:RemoteAreaRule.amount", "the method `RemoteAreaRule.amount` in frostline/domain/rules/remote.py", "plus_one",
                [U("domain/rules/remote.py", "RemoteAreaRule.amount"), U("plugins/island.py", "PartnerRemoteRule"), U("plugins/island.py", "PartnerRemoteRule.amount"),
                 U("api/app.py")],
                "The registered 'remote' rule is PartnerRemoteRule, which overrides amount(); the base method is never called.", lookalike=True),
    impact_item("L5-07", "frostline.plugins.island:PartnerRemoteRule.amount", "the method `PartnerRemoteRule.amount` in frostline/plugins/island.py", "plus_one",
                [U("plugins/island.py", "PartnerRemoteRule.amount"), U("domain/rules/remote.py", "RemoteAreaRule.applies"), U("routing/network.py"),
                 U("config/settings.py"), U("core/container.py", "Container.surcharge_rules")],
                "Applies only to shipments whose destination is remote (HGI in S2, LCU in S8).", lookalike=True),
    impact_item("L5-08", "frostline.pricing.strategies:TieredStrategy.base_rate", "the method `TieredStrategy.base_rate` in frostline/pricing/strategies.py", "plus_one",
                [U("pricing/strategies.py", "TieredStrategy.base_rate"), U("pricing/strategies.py", "DistanceStrategy"), U("pricing/strategies.py", "FlatStrategy.price"),
                 U("config/settings.py"), U("config/profiles.py")],
                "Used by 'tiered' (default) and inherited by 'distance' (express); changes matter only when above the minimum charge."),
    impact_item("L5-09", "frostline.pricing.strategies:FlatStrategy.min_charge", "the method `FlatStrategy.min_charge` in frostline/pricing/strategies.py", "plus_one",
                [U("pricing/strategies.py", "FlatStrategy.min_charge"), U("pricing/strategies.py", "FlatStrategy.price")],
                "Only shipments whose raw price is below the minimum charge change."),
    impact_item("L5-10", "frostline.services.notification_service:notify_booking", "the function `notify_booking` in frostline/services/notification_service.py", "empty_list",
                [U("services/notification_service.py", "notify_booking"), U("core/events.py", "EventBus.publish"), U("services/shipment_service.py", "ShipmentService.book")],
                "Handler results are discarded by book(), but S8's GET /reports/revenue response includes per-channel outbox counts."),
    impact_item("L5-11", "frostline.routing.engines:DijkstraEngine.path", "the method `DijkstraEngine.path` in frostline/routing/engines.py", "reverse_list",
                [U("routing/engines.py", "DijkstraEngine.path"), U("core/interfaces.py", "RouteEngine.distance"), U("api/handlers.py", "get_route"),
                 U("api/handlers.py", "post_shipment"), U("storage/repositories.py", "ShipmentRepository.save")],
                "A reversed path has the same distance, so quotes do not change; responses exposing the path/route do."),
    impact_item("L5-12", "frostline.utils.text:normalize_code", "the function `normalize_code` in frostline/utils/text.py", "lower",
                [U("utils/text.py", "normalize_code"), U("pricing/discounts.py", "promo_discount"), U("pricing/discounts.py", "apply_discount")],
                "Only promo codes are normalized with it; only S2 uses a promo, and COLD10 beats the gold loyalty discount.", lookalike=True),
    impact_item("L5-13", "frostline.tax.policies:ExemptTax.tax", "the method `ExemptTax.tax` in frostline/tax/policies.py", "plus_one",
                [U("tax/policies.py", "ExemptTax.tax"), U("core/container.py", "Container.tax_policy"), U("services/customer_service.py")],
                "Only 'gov' customers (C-103, S8) are exempt."),
    impact_item("L5-14", "frostline.warehouse.storage_fees:handling_fee", "the function `handling_fee` in frostline/warehouse/storage_fees.py", "plus_one",
                [U("warehouse/storage_fees.py", "handling_fee"), U("api/warehouse_handlers.py", "post_storage_estimate")],
                "Only the storage estimate endpoint uses handling fees."),
    impact_item("L5-15", "frostline.routing.engines:GreedyEngine.path", "the method `GreedyEngine.path` in frostline/routing/engines.py", "reverse_list",
                [U("routing/engines.py", "GreedyEngine.path"), U("config/profiles.py"), U("core/interfaces.py", "RouteEngine.distance"),
                 U("api/handlers.py", "post_quote")],
                "Only S6 uses the greedy engine and its quote depends only on the (unchanged) distance."),
    impact_item("L5-16", "frostline.domain.rules.fuel:FuelRule.amount", "the method `FuelRule.amount` in frostline/domain/rules/fuel.py", "plus_one",
                [U("domain/rules/fuel.py", "FuelRule.amount"), U("config/settings.py"), U("config/profiles.py"), U("core/container.py", "Container.surcharge_rules")],
                "Every quote/booking scenario has 'fuel' enabled (default and express profiles)."),
]
