# Dataset catalog v1 (auto-generated from data/items.v1.jsonl)

Ground truth = executed by the oracle (`verified_by`). `I` = indirect dependency, `LA` = look-alike distractor present.

| ID | Level | Type | I | LA | Answer (ground truth) | Look-alike answer | Gold evidence units | Verified by |
|---|---|---|---|---|---|---|---|---|
| L1-01 | L1 | value_lookup |  |  | `"2.60"` | `"2.05"` | 2 | execution+trace |
| L1-02 | L1 | value_compute |  | x | `"5.5"` | `"4.5"` | 3 | execution+trace |
| L1-03 | L1 | value_compute |  | x | `"6.000"` |  | 1 | execution+trace |
| L1-04 | L1 | value_compute |  | x | `"8.75"` |  | 2 | execution+trace |
| L1-05 | L1 | value_compute |  | x | `"COLD10"` | `"cold-10"` | 1 | execution+trace |
| L1-06 | L1 | control_flow |  |  | `[[5, 20]]` |  | 1 | execution+trace |
| L1-07 | L1 | value_compute |  | x | `"2.34"` | `"2.35"` | 2 | execution+trace |
| L1-08 | L1 | api_semantics |  |  | `"RegistryError"` |  | 1 | execution+trace |
| L1-09 | L1 | value_compute |  |  | `"60.00"` |  | 1 | execution+trace |
| L1-10 | L1 | value_compute |  |  | `260` |  | 1 | execution+trace |
| L1-11 | L1 | value_compute |  |  | `"5.6000"` | `"10.6000"` | 4 | execution+trace |
| L1-12 | L1 | config_lookup |  |  | `["express", "fragile", "fuel", "hazmat", "remote"]` |  | 1 | execution+trace |
| L1-13 | L1 | value_compute |  |  | `2000` |  | 2 | execution+trace |
| L2-01 | L2 | value_compute |  | x | `"7.5"` | `"6.5"` | 5 | execution+trace |
| L2-02 | L2 | value_compute |  |  | `"12.50"` | `"7.20"` | 4 | execution+trace |
| L2-03 | L2 | value_compute |  |  | `"2.0000"` | `"1.5000"` | 6 | execution+trace |
| L2-04 | L2 | data_flow |  |  | `680` |  | 5 | execution+trace |
| L2-05 | L2 | control_flow |  | x | `["HPH", "NDH", "HAN", "TNG", "LCU"]` | `["HPH", "HAN", "TNG", "LCU"]` | 3 | execution+trace |
| L2-06 | L2 | data_flow |  | x | `"45.60"` |  | 6 | execution+trace |
| L2-07 | L2 | data_flow |  |  | `"4.990"` |  | 3 | execution+trace |
| L2-08 | L2 | control_flow |  |  | `422` |  | 5 | execution+trace |
| L2-09 | L2 | control_flow |  |  | `"ok"` |  | 5 | execution+trace |
| L2-10 | L2 | value_compute |  |  | `"145.80"` |  | 4 | execution+trace |
| L3-01 | L3 | dispatch_resolution | x | x | `"0"` | `"10.0000"` | 4 | execution+trace |
| L3-02 | L3 | dispatch_resolution | x | x | `"6.65"` |  | 7 | execution+trace |
| L3-03 | L3 | dispatch_resolution | x | x | `"9.60"` | `"9.00"` | 7 | execution+trace |
| L3-04 | L3 | dispatch_resolution | x | x | `"PartnerRemoteRule"` | `"RemoteAreaRule"` | 5 | execution |
| L3-05 | L3 | dispatch_resolution | x |  | `"34.160"` | `"26.00"` | 7 | execution+trace |
| L3-06 | L3 | config_lookup | x | x | `["fragile", "fuel", "remote"]` | `["express", "fragile", "fuel", "hazmat", "insurance", "remote", "weekend"]` | 3 | execution |
| L3-07 | L3 | event_flow | x | x | `["booking_confirmation_v3", "booking_short_v1"]` | `["booking_confirmation_v1", "booking_sms_legacy"]` | 5 | execution+trace |
| L3-08 | L3 | event_flow | x |  | `["audit", "quotes"]` |  | 5 | execution+trace |
| L3-09 | L3 | event_flow | x | x | `["audit", "outbox", "shipments"]` | `["audit", "outbox", "quotes", "shipments"]` | 6 | execution+trace |
| L3-10 | L3 | event_flow | x |  | `["notify_booking", "audit_booking"]` |  | 5 | execution |
| L3-11 | L3 | dispatch_resolution | x | x | `0` | `"2.0000"` | 3 | execution+trace |
| L3-12 | L3 | dispatch_resolution | x | x | `"0.10"` | `"0.08"` | 4 | execution+trace |
| L3-13 | L3 | dispatch_resolution | x |  | `155` |  | 5 | execution+trace |
| L4-01 | L4 | data_flow | x |  | `"63.01"` |  | 20 | execution+trace |
| L4-02 | L4 | data_flow | x | x | `3172` |  | 11 | execution+trace |
| L4-03 | L4 | data_flow | x |  | `"HPH-NDH-THO-VIN-HUE-DNG-QNH-HCM-CTH"` |  | 7 | execution+trace |
| L4-04 | L4 | data_flow | x |  | `"2.15"` |  | 16 | execution+trace |
| L4-05 | L4 | data_flow | x |  | `["express", "fuel", "hazmat"]` |  | 18 | execution+trace |
| L4-06 | L4 | data_flow | x |  | `"56.63"` |  | 20 | execution+trace |
| L4-07 | L4 | data_flow | x | x | `"0.87"` |  | 13 | execution+trace |
| L4-08 | L4 | data_flow |  |  | `"10.0"` |  | 7 | execution+trace |
| L4-09 | L4 | data_flow | x | x | `"HPH-NDH-HAN-TNG-LCU"` | `"HPH-HAN-TNG-LCU"` | 8 | execution+trace |
| L4-10 | L4 | event_flow | x |  | `"provincial-health-office@email"` |  | 7 | execution+trace |
| L4-11 | L4 | data_flow | x | x | `"26.75"` |  | 11 | execution+trace |
| L4-12 | L4 | data_flow | x |  | `"46.81"` |  | 11 | execution+trace |
| L5-01 | L5 | impact_analysis | x | x | `["S4"]` |  | 3 | mutation |
| L5-02 | L5 | impact_analysis | x | x | `["S1", "S2", "S4", "S5", "S6", "S8"]` |  | 6 | mutation |
| L5-03 | L5 | impact_analysis | x | x | `["S3"]` |  | 2 | mutation |
| L5-04 | L5 | impact_analysis | x | x | `["S4"]` |  | 3 | mutation |
| L5-05 | L5 | impact_analysis | x | x | `["S5"]` |  | 2 | mutation |
| L5-06 | L5 | impact_analysis | x | x | `[]` |  | 4 | mutation |
| L5-07 | L5 | impact_analysis | x | x | `["S2", "S8"]` |  | 5 | mutation |
| L5-08 | L5 | impact_analysis | x |  | `["S1", "S2", "S4", "S6"]` |  | 5 | mutation |
| L5-09 | L5 | impact_analysis | x |  | `["S8"]` |  | 2 | mutation |
| L5-10 | L5 | impact_analysis | x |  | `["S8"]` |  | 3 | mutation |
| L5-11 | L5 | impact_analysis | x |  | `["S2", "S3", "S4", "S8"]` |  | 5 | mutation |
| L5-12 | L5 | impact_analysis | x | x | `["S2"]` |  | 3 | mutation |
| L5-13 | L5 | impact_analysis | x |  | `["S8"]` |  | 3 | mutation |
| L5-14 | L5 | impact_analysis | x |  | `["S5"]` |  | 2 | mutation |
| L5-15 | L5 | impact_analysis | x |  | `[]` |  | 4 | mutation |
| L5-16 | L5 | impact_analysis | x |  | `["S1", "S2", "S4", "S6", "S8"]` |  | 4 | mutation |

## Full questions

### L1-01 (L1, value_lookup)

In frostline/pricing/strategies.py, what rate per kg does TieredStrategy.base_rate return for a chargeable weight of exactly 20 kg?

- **Ground truth:** `"2.60"`
- **Evidence:** `frostline/pricing/strategies.py::TieredStrategy` (L28-35), `frostline/pricing/strategies.py::TieredStrategy.base_rate` (L37-41)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** TIERS upper bounds are inclusive (weight <= upper): 20 kg falls in the second tier.

### L1-02 (L1, value_compute)

In frostline/domain/units.py, what does chargeable_weight return (in kg) for a parcel of 2.2 kg measuring 30x30x30 cm when called with its default arguments?

- **Ground truth:** `"5.5"`
- **Evidence:** `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/domain/units.py::volumetric_weight` (L19-22), `frostline/domain/units.py::round_up_to_step` (L31-33)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Volumetric weight 27000/5000 = 5.4 kg exceeds 2.2 kg and is rounded up to the 0.5 kg step.

### L1-03 (L1, value_compute)

In frostline/billing/fees.py, what does calculate_fee(200, 45) return with the default rate and grace period?

- **Ground truth:** `"6.000"`
- **Evidence:** `frostline/billing/fees.py::calculate_fee` (L6-12)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** 35 days overdue -> 2 started 30-day periods -> 200 * 0.015 * 2.

### L1-04 (L1, value_compute)

In frostline/routing/fees.py, what does calculate_fee(350) return?

- **Ground truth:** `"8.75"`
- **Evidence:** `frostline/routing/fees.py::calculate_fee` (L9-12), `frostline/routing/fees.py::<module>` (L1-6)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** First 100 km are free; 250 km * 0.035.

### L1-05 (L1, value_compute)

In frostline/utils/text.py, what string does normalize_code(' cold-10 ') return?

- **Ground truth:** `"COLD10"`
- **Evidence:** `frostline/utils/text.py::normalize_code` (L9-11)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** Dashes and spaces removed, then upper-cased.

### L1-06 (L1, control_flow)

In frostline/warehouse/sensors.py, assume `within(zone, c)` is True exactly when zone.min_c <= c <= zone.max_c, and the zone range is 0..4 C. What does excursions(zone, readings) return (default min_minutes) for readings = [(0, 2), (5, 6), (12, 7), (20, 8), (22, 3), (40, 9), (45, 3)]? Answer as a JSON list of [start, end] pairs.

- **Ground truth:** `[[5, 20]]`
- **Evidence:** `frostline/warehouse/sensors.py::excursions` (L13-25)
- **Rubric:** Correct iff the JSON value equals the ground truth structurally (numbers compared numerically).
- **Explanation:** Runs outside range: 5..20 (15 min, kept) and 40..40 (0 min, dropped).

### L1-07 (L1, value_compute)

In frostline/pricing/money.py, what does round_money_even(Decimal('2.345')) return?

- **Ground truth:** `"2.34"`
- **Evidence:** `frostline/pricing/money.py::round_money_even` (L19-21), `frostline/pricing/money.py::<module>` (L1-5)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Banker's rounding: half goes to the even cent.

### L1-08 (L1, api_semantics)

In frostline/core/registry.py, what exception class is raised when the same (kind, name) is registered twice without replace=True? Give the class name.

- **Ground truth:** `"RegistryError"`
- **Evidence:** `frostline/core/registry.py::register` (L14-23)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** register() checks for an existing key unless replace is set.

### L1-09 (L1, value_compute)

In frostline/warehouse/storage_fees.py, what does handling_fee(12) return?

- **Ground truth:** `"60.00"`
- **Evidence:** `frostline/warehouse/storage_fees.py::handling_fee` (L26-28)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** 6.00 per pallet capped at 60.00.

### L1-10 (L1, value_compute)

In frostline/domain/validation.py, what does girth(parcel) return for a parcel measuring length 100, width 30, height 50 cm?

- **Ground truth:** `260`
- **Evidence:** `frostline/domain/validation.py::girth` (L11-13)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Longest side + 2 * (sum of the two shorter sides).

### L1-11 (L1, value_compute)

In frostline/pricing/discounts.py, what does apply_discount return for a subtotal of 80.00, a customer with level 'gold', promo code 'FREEZE5', and settings where discount.loyalty_enabled is True and discount.stacking is False?

- **Ground truth:** `"5.6000"`
- **Evidence:** `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/pricing/discounts.py::loyalty_discount` (L21-24), `frostline/pricing/discounts.py::promo_discount` (L27-35), `frostline/pricing/discounts.py::<module>` (L1-18)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Without stacking the larger of loyalty (5.60) and promo (5.00) wins.

### L1-12 (L1, config_lookup)

In frostline/config/profiles.py, which surcharge codes are enabled by the 'express' profile?

- **Ground truth:** `["express", "fragile", "fuel", "hazmat", "remote"]`
- **Evidence:** `frostline/config/profiles.py::<module>` (L1-17)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Read the 'surcharge.enabled' list of the express profile.

### L1-13 (L1, value_compute)

In frostline/pricing/money.py, what integer does to_cents(Decimal('19.995')) return?

- **Ground truth:** `2000`
- **Evidence:** `frostline/pricing/money.py::to_cents` (L24-25), `frostline/pricing/money.py::round_money` (L14-16)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** to_cents first applies round_money (half-up) -> 20.00 -> 2000 cents.

### L2-01 (L2, value_compute)

Under the default settings, what total chargeable weight (kg) does QuoteEngine.chargeable_weight compute for a shipment with a single parcel of 4 kg measuring 41x33x27 cm?

- **Ground truth:** `"7.5"`
- **Evidence:** `frostline/pricing/quote_engine.py::QuoteEngine.chargeable_weight` (L16-19), `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/domain/units.py::volumetric_weight` (L19-22), `frostline/domain/units.py::round_up_to_step` (L31-33), `frostline/config/settings.py::<module>` (L1-26)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Divisor 5000 and step 0.5 come from DEFAULTS; volumetric 36531/5000 = 7.31 -> 7.5.

### L2-02 (L2, value_compute)

With the default settings, what base price does the pricing strategy registered as 'flat' return for a chargeable weight of 3 kg?

- **Ground truth:** `"12.50"`
- **Evidence:** `frostline/pricing/strategies.py::FlatStrategy` (L13-15), `frostline/pricing/strategies.py::FlatStrategy.price` (L23-25), `frostline/pricing/strategies.py::FlatStrategy.min_charge` (L20-21), `frostline/config/settings.py::<module>` (L1-26)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** 3 * 2.40 = 7.20 is below the configured minimum charge of 12.50.

### L2-03 (L2, value_compute)

With the default settings, what does apply_discount return for a subtotal of 50.00, a 'silver' customer and promo code ' icebox '?

- **Ground truth:** `"2.0000"`
- **Evidence:** `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/pricing/discounts.py::promo_discount` (L27-35), `frostline/pricing/discounts.py::loyalty_discount` (L21-24), `frostline/pricing/discounts.py::<module>` (L1-18), `frostline/utils/text.py::normalize_code` (L9-11), `frostline/config/settings.py::<module>` (L1-26)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** normalize_code maps ' icebox ' to ICEBOX (4% = 2.00), larger than silver loyalty (1.50).

### L2-04 (L2, data_flow)

What total distance in km does DijkstraEngine compute from depot HAN to depot HUE on the default network?

- **Ground truth:** `680`
- **Evidence:** `frostline/routing/engines.py::DijkstraEngine.path` (L14-29), `frostline/core/interfaces.py::RouteEngine.distance` (L31-33), `frostline/routing/network.py::<module>` (L1-21), `frostline/routing/network.py::Network.edge` (L31-32), `frostline/routing/network.py::Network.neighbours` (L34-35)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Shortest path HAN-NDH-THO-VIN-HUE (95+85+140+360) beats THO-HUE direct (520).

### L2-05 (L2, control_flow)

What path (ordered list of depot codes) does GreedyEngine.path return from HPH to LCU on the default network?

- **Ground truth:** `["HPH", "NDH", "HAN", "TNG", "LCU"]`
- **Evidence:** `frostline/routing/engines.py::GreedyEngine.path` (L39-53), `frostline/routing/network.py::<module>` (L1-21), `frostline/routing/network.py::Network.neighbours` (L34-35)
- **Rubric:** Correct iff the ordered list equals the ground truth element by element.
- **Explanation:** Nearest-neighbour walk: from HPH the nearest is NDH (70), then HAN (95), TNG (80), LCU - longer than the shortest path via HAN.

### L2-06 (L2, data_flow)

What value does POST /storage/estimate return in its 'total' field for the body {"product": "flowers", "pallets": 2, "days": 10}?

- **Ground truth:** `"45.60"`
- **Evidence:** `frostline/api/warehouse_handlers.py::post_storage_estimate` (L9-18), `frostline/warehouse/storage_fees.py::calculate_fee` (L13-23), `frostline/warehouse/storage_fees.py::handling_fee` (L26-28), `frostline/warehouse/storage_fees.py::<module>` (L1-10), `frostline/warehouse/zones.py::<module>` (L1-28), `frostline/warehouse/zones.py::zone_for` (L31-35)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Flowers -> CHL (1.35/day); 8 billable days * 2 pallets = 21.60; handling 12.00 counted twice.

### L2-07 (L2, data_flow)

When a request body uses "weight_unit": "lb" and a parcel has "weight": 11, what weight_kg value ends up in the parsed Parcel?

- **Ground truth:** `"4.990"`
- **Evidence:** `frostline/api/serializers.py::parse_parcel` (L12-24), `frostline/domain/units.py::to_kg` (L8-16), `frostline/domain/units.py::<module>` (L1-5)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** 11 / 2.20462 quantized to 0.001.

### L2-08 (L2, control_flow)

What HTTP status does App.handle return for POST /quotes when one parcel has dims [200, 10, 10] (other fields valid: customer C-101, from HAN, to HUE, weight 3)?

- **Ground truth:** `422`
- **Evidence:** `frostline/api/app.py::App.handle` (L39-43), `frostline/api/serializers.py::parse_shipment` (L27-40), `frostline/domain/validation.py::check_parcel` (L16-22), `frostline/domain/validation.py::<module>` (L1-8), `frostline/core/errors.py::ValidationError` (L7-8)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** check_parcel raises ValidationError (status 422) which App.handle converts to the response status.

### L2-09 (L2, control_flow)

What 'status' does POST /storage/compliance return for product 'seafood' with readings [[0, -20], [10, -15], [20, -12], [30, -19]]?

- **Ground truth:** `"ok"`
- **Evidence:** `frostline/api/warehouse_handlers.py::post_compliance` (L21-25), `frostline/warehouse/sensors.py::compliance_status` (L38-44), `frostline/warehouse/sensors.py::excursions` (L13-25), `frostline/warehouse/zones.py::within` (L38-39), `frostline/warehouse/zones.py::<module>` (L1-28)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** Seafood is FRZ (-25..-18); the out-of-range run 10..20 lasts 10 min < 15, so no excursion.

### L2-10 (L2, value_compute)

What does calculate_fee('vaccine', 3, 40) in frostline/warehouse/storage_fees.py return?

- **Ground truth:** `"145.80"`
- **Evidence:** `frostline/warehouse/storage_fees.py::calculate_fee` (L13-23), `frostline/warehouse/storage_fees.py::<module>` (L1-10), `frostline/warehouse/zones.py::<module>` (L1-28), `frostline/warehouse/zones.py::zone_for` (L31-35)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Vaccine -> CHL 1.35; 38 billable days = 28 normal + 10 long-stay at 80%.

### L3-01 (L3, dispatch_resolution)

In the running application, how much tax is charged for customer C-103 on a taxable amount of 150.00?

- **Ground truth:** `"0"`
- **Evidence:** `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/tax/policies.py::ExemptTax` (L38-40), `frostline/tax/policies.py::ExemptTax.tax` (L42-43), `frostline/services/customer_service.py::<module>` (L1-13)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** C-103 has category 'gov', so the container resolves the 'exempt' policy before looking at its region.

### L3-02 (L3, dispatch_resolution)

What 'toll' value does GET /routes return for the body {"from": "HAN", "to": "LCU"} under the default settings?

- **Ground truth:** `"6.65"`
- **Evidence:** `frostline/api/handlers.py::get_route` (L28-33), `frostline/routing/fees.py::calculate_fee` (L9-12), `frostline/routing/fees.py::<module>` (L1-6), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/routing/engines.py::DijkstraEngine.path` (L14-29), `frostline/core/interfaces.py::RouteEngine.distance` (L31-33), `frostline/routing/network.py::<module>` (L1-21)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Dijkstra (configured engine) gives HAN-TNG-LCU = 290 km; toll = (290-100) * 0.035.

### L3-03 (L3, dispatch_resolution)

In the default application, what 'remote' surcharge amount is applied to a shipment from HAN to HGI with 3 parcels (base price 30.00)?

- **Ground truth:** `"9.60"`
- **Evidence:** `frostline/plugins/island.py::PartnerRemoteRule` (L13-17), `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/domain/rules/remote.py::RemoteAreaRule.applies` (L15-16), `frostline/core/registry.py::register` (L14-23), `frostline/api/app.py::<module>` (L1-25), `frostline/plugins/__init__.py::<module>` (L1-7), `frostline/core/container.py::Container.surcharge_rules` (L27-29)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** plugins/island.py re-registers 'remote' with replace=True after the built-ins: max(7.50, 3 * 3.20).

### L3-04 (L3, dispatch_resolution)

In the default application, which class (class name only) actually computes the amount of the 'remote' surcharge?

- **Ground truth:** `"PartnerRemoteRule"`
- **Evidence:** `frostline/plugins/island.py::PartnerRemoteRule` (L13-17), `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/core/registry.py::register` (L14-23), `frostline/api/app.py::<module>` (L1-25), `frostline/plugins/__init__.py::<module>` (L1-7)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** Plugins are imported last and PartnerRemoteRule registers with replace=True.

### L3-05 (L3, dispatch_resolution)

Under the 'express' profile, what base price does the configured pricing strategy return for a chargeable weight of 10 kg over 680 km?

- **Ground truth:** `"34.160"`
- **Evidence:** `frostline/config/profiles.py::<module>` (L1-17), `frostline/core/container.py::Container.pricing_strategy` (L13-15), `frostline/pricing/strategies.py::DistanceStrategy.price` (L48-49), `frostline/pricing/strategies.py::DistanceStrategy` (L44-46), `frostline/pricing/strategies.py::FlatStrategy.price` (L23-25), `frostline/pricing/strategies.py::TieredStrategy.base_rate` (L37-41), `frostline/pricing/strategies.py::FlatStrategy.min_charge` (L20-21)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** express -> 'distance' strategy: tiered price 10 * 2.60 = 26.00 plus 0.012 * 680.

### L3-06 (L3, config_lookup)

With the default profile, which surcharge codes can ever appear in the 'surcharges' of a quote?

- **Ground truth:** `["fragile", "fuel", "remote"]`
- **Evidence:** `frostline/config/settings.py::<module>` (L1-26), `frostline/core/container.py::Container.surcharge_rules` (L27-29), `frostline/pricing/quote_engine.py::QuoteEngine.surcharges` (L21-28)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only rules listed in surcharge.enabled are instantiated; registered-but-disabled rules never run.

### L3-07 (L3, event_flow)

If the application is created with the override notify.channels = ['SMS', 'Email'] and a shipment is booked, which template names appear in the outbox rows created for that booking?

- **Ground truth:** `["booking_confirmation_v3", "booking_short_v1"]`
- **Evidence:** `frostline/services/notification_service.py::notify_booking` (L14-22), `frostline/services/notification_service.py::<module>` (L1-11), `frostline/utils/text.py::normalize` (L4-6), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/core/events.py::EventBus.publish` (L24-29)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** notify_booking normalizes channel names to lower case and looks them up in TEMPLATES.

### L3-08 (L3, event_flow)

When POST /quotes succeeds, which database tables receive new rows?

- **Ground truth:** `["audit", "quotes"]`
- **Evidence:** `frostline/services/quote_service.py::QuoteService.create_quote` (L14-19), `frostline/storage/repositories.py::QuoteRepository` (L7-8), `frostline/services/audit_service.py::audit_quote` (L7-9), `frostline/storage/repositories.py::AuditRepository` (L50-51), `frostline/core/events.py::EventBus.publish` (L24-29)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** QuoteRepository writes 'quotes'; the 'quote.created' event triggers audit_quote which writes 'audit'.

### L3-09 (L3, event_flow)

When POST /shipments succeeds under the default settings, which database tables receive new rows?

- **Ground truth:** `["audit", "outbox", "shipments"]`
- **Evidence:** `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/storage/repositories.py::ShipmentRepository` (L19-20), `frostline/services/notification_service.py::notify_booking` (L14-22), `frostline/services/audit_service.py::audit_booking` (L12-14), `frostline/storage/repositories.py::OutboxRepository` (L38-39), `frostline/storage/repositories.py::AuditRepository` (L50-51)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Booking uses QuoteEngine directly (no quote row); 'shipment.booked' triggers outbox and audit writers.

### L3-10 (L3, event_flow)

In which order are the event handler functions invoked when the 'shipment.booked' event is published? Give the function names in order.

- **Ground truth:** `["notify_booking", "audit_booking"]`
- **Evidence:** `frostline/services/__init__.py::<module>` (L1-3), `frostline/core/events.py::subscribe` (L11-16), `frostline/core/events.py::EventBus.publish` (L24-29), `frostline/services/notification_service.py::notify_booking` (L14-22), `frostline/services/audit_service.py::audit_booking` (L12-14)
- **Rubric:** Correct iff the ordered list equals the ground truth element by element.
- **Explanation:** Handlers run in subscription order; services/__init__ imports notification_service before audit_service.

### L3-11 (L3, dispatch_resolution)

Under the 'eco' profile, what fuel surcharge amount is applied to a shipment from HAN to HUE whose base price is 40.00? (Answer 0 if none.)

- **Ground truth:** `0`
- **Evidence:** `frostline/config/profiles.py::<module>` (L1-17), `frostline/core/container.py::Container.surcharge_rules` (L27-29), `frostline/pricing/quote_engine.py::QuoteEngine.surcharges` (L21-28)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** The eco profile enables only the 'remote' rule, so the fuel rule (index 1.05) is never instantiated.

### L3-12 (L3, dispatch_resolution)

Under the default settings, what VAT rate is applied to quotes for customer C-100?

- **Ground truth:** `"0.10"`
- **Evidence:** `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/services/customer_service.py::<module>` (L1-13), `frostline/tax/policies.py::SouthTax` (L19-21), `frostline/config/settings.py::<module>` (L1-26)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** The customer's own region ('south') takes precedence over the tax.region default ('north').

### L3-13 (L3, dispatch_resolution)

What 'distance_km' does GET /routes return for the body {"from": "HPH", "to": "THO"} under the default settings?

- **Ground truth:** `155`
- **Evidence:** `frostline/api/handlers.py::get_route` (L28-33), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/routing/engines.py::DijkstraEngine.path` (L14-29), `frostline/core/interfaces.py::RouteEngine.distance` (L31-33), `frostline/routing/network.py::<module>` (L1-21)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** The configured engine is dijkstra: HPH-NDH-THO.

### L4-01 (L4, data_flow)

What 'total' does POST /quotes return (default profile) for the body {"customer": "C-101", "from": "HAN", "to": "HUE", "parcels": [{"weight": 3.2, "dims": [30, 20, 20]}, {"weight": 12, "dims": [60, 40, 40], "fragile": true}]}?

- **Ground truth:** `"63.01"`
- **Evidence:** `frostline/api/handlers.py::post_quote` (L10-15), `frostline/api/serializers.py::parse_shipment` (L27-40), `frostline/api/serializers.py::parse_parcel` (L12-24), `frostline/services/quote_service.py::QuoteService.create_quote` (L14-19), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/pricing/quote_engine.py::QuoteEngine.chargeable_weight` (L16-19), `frostline/pricing/quote_engine.py::QuoteEngine.surcharges` (L21-28), `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/core/container.py::Container.pricing_strategy` (L13-15), `frostline/core/container.py::Container.surcharge_rules` (L27-29), `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/config/settings.py::<module>` (L1-26), `frostline/pricing/strategies.py::TieredStrategy.base_rate` (L37-41), `frostline/pricing/strategies.py::FlatStrategy.price` (L23-25), `frostline/domain/rules/fuel.py::FuelRule.amount` (L13-15), `frostline/domain/rules/fragile.py::FragileRule` (L7-12), `frostline/domain/rules/base.py::PerParcelRule.amount` (L43-45), `frostline/pricing/discounts.py::loyalty_discount` (L21-24), `frostline/tax/policies.py::NorthTax` (L14-16)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Per-parcel chargeable weights (volumetric vs actual, rounded to 0.5 kg) are summed and priced by tier; fuel and fragile surcharges; silver loyalty discount; north VAT (C-101 has no region).

### L4-02 (L4, data_flow)

After POST /shipments (default profile) with body {"customer": "C-100", "from": "HAN", "to": "HGI", "parcels": [{"weight": 8, "dims": [40, 30, 30]}], "promo": "cold-10"}, what integer value is stored in the 'total_cents' column of the new shipments row?

- **Ground truth:** `3172`
- **Evidence:** `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/pricing/discounts.py::promo_discount` (L27-35), `frostline/utils/text.py::normalize_code` (L9-11), `frostline/tax/policies.py::SouthTax` (L19-21), `frostline/pricing/money.py::to_cents` (L24-25), `frostline/core/container.py::Container.tax_policy` (L17-21)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Remote partner surcharge, COLD10 (10%) beats gold loyalty (7%), south VAT 10%, stored in cents.

### L4-03 (L4, data_flow)

After POST /shipments (default profile) with body {"customer": "C-102", "from": "HPH", "to": "CTH", "parcels": [{"weight": 10, "dims": [30, 30, 30]}]}, what string is stored in the 'route' column of the shipments row?

- **Ground truth:** `"HPH-NDH-THO-VIN-HUE-DNG-QNH-HCM-CTH"`
- **Evidence:** `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/routing/engines.py::DijkstraEngine.path` (L14-29), `frostline/routing/network.py::<module>` (L1-21)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** Route comes from the configured Dijkstra engine and is joined with '-'.

### L4-04 (L4, data_flow)

What 'tax' does POST /quotes return (default profile) for the body {"customer": "C-104", "from": "HAN", "to": "DNG", "parcels": [{"weight": 7, "dims": [50, 40, 30]}, {"weight": 2, "dims": [20, 20, 20]}]}?

- **Ground truth:** `"2.15"`
- **Evidence:** `frostline/api/handlers.py::post_quote` (L10-15), `frostline/api/serializers.py::parse_shipment` (L27-40), `frostline/api/serializers.py::parse_parcel` (L12-24), `frostline/services/quote_service.py::QuoteService.create_quote` (L14-19), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/pricing/quote_engine.py::QuoteEngine.chargeable_weight` (L16-19), `frostline/pricing/quote_engine.py::QuoteEngine.surcharges` (L21-28), `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/core/container.py::Container.pricing_strategy` (L13-15), `frostline/core/container.py::Container.surcharge_rules` (L27-29), `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/config/settings.py::<module>` (L1-26), `frostline/tax/policies.py::CentralTax.tax` (L32-35), `frostline/tax/policies.py::CentralTax` (L24-30), `frostline/services/customer_service.py::<module>` (L1-13)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** C-104 is in region 'central': 5% on the first 100 of the taxable amount, 10% above.

### L4-05 (L4, data_flow)

Which surcharge codes appear in the 'surcharges' of the POST /quotes response under the 'express' profile for the body {"customer": "C-102", "from": "HAN", "to": "HCM", "service": "express", "parcels": [{"weight": 5, "dims": [20, 20, 20], "hazmat": true}]}?

- **Ground truth:** `["express", "fuel", "hazmat"]`
- **Evidence:** `frostline/api/handlers.py::post_quote` (L10-15), `frostline/api/serializers.py::parse_shipment` (L27-40), `frostline/api/serializers.py::parse_parcel` (L12-24), `frostline/services/quote_service.py::QuoteService.create_quote` (L14-19), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/pricing/quote_engine.py::QuoteEngine.chargeable_weight` (L16-19), `frostline/pricing/quote_engine.py::QuoteEngine.surcharges` (L21-28), `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/core/container.py::Container.pricing_strategy` (L13-15), `frostline/core/container.py::Container.surcharge_rules` (L27-29), `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/config/settings.py::<module>` (L1-26), `frostline/config/profiles.py::<module>` (L1-17), `frostline/plugins/express.py::ExpressRule.applies` (L14-15), `frostline/domain/rules/hazmat.py::HazmatRule.applies` (L14-15), `frostline/domain/rules/remote.py::RemoteAreaRule.applies` (L15-16), `frostline/domain/rules/fragile.py::FragileRule.matches` (L14-15)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Express enables five rules; remote does not apply (HCM is not remote) and fragile matches no parcel.

### L4-06 (L4, data_flow)

What 'total' does the POST /quotes call of scenario S6 return? S6: profile 'express', body {"customer": "C-102", "from": "HAN", "to": "HCM", "service": "express", "parcels": [{"weight": 5, "dims": [20, 20, 20], "hazmat": true}]}.

- **Ground truth:** `"56.63"`
- **Evidence:** `frostline/api/handlers.py::post_quote` (L10-15), `frostline/api/serializers.py::parse_shipment` (L27-40), `frostline/api/serializers.py::parse_parcel` (L12-24), `frostline/services/quote_service.py::QuoteService.create_quote` (L14-19), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/pricing/quote_engine.py::QuoteEngine.chargeable_weight` (L16-19), `frostline/pricing/quote_engine.py::QuoteEngine.surcharges` (L21-28), `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/core/container.py::Container.pricing_strategy` (L13-15), `frostline/core/container.py::Container.surcharge_rules` (L27-29), `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/config/settings.py::<module>` (L1-26), `frostline/config/profiles.py::<module>` (L1-17), `frostline/pricing/strategies.py::DistanceStrategy.price` (L48-49), `frostline/routing/engines.py::GreedyEngine.path` (L39-53), `frostline/plugins/express.py::ExpressRule` (L7-12), `frostline/domain/rules/hazmat.py::HazmatRule` (L7-12), `frostline/domain/rules/fuel.py::FuelRule.amount` (L13-15), `frostline/tax/policies.py::SouthTax` (L19-21)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Distance strategy over the greedy route, fuel + hazmat + express surcharges, platinum discount, south VAT.

### L4-07 (L4, data_flow)

Scenario: in a fresh default app, POST /shipments with {"customer": "C-104", "from": "HPH", "to": "DNG", "parcels": [{"weight": 6, "dims": [40, 30, 20]}, {"weight": 1.5, "dims": [10, 10, 10], "fragile": true}]}, then POST /invoices with {"customer": "C-104", "as_of": "2026-12-30"}. What 'late_fee' does the invoice response contain?

- **Ground truth:** `"0.87"`
- **Evidence:** `frostline/api/handlers.py::post_invoice` (L36-39), `frostline/services/billing_service.py::BillingService.invoice` (L17-37), `frostline/billing/fees.py::calculate_fee` (L6-12), `frostline/utils/dates.py::days_between` (L10-11), `frostline/domain/models.py::Shipment` (L19-28), `frostline/pricing/money.py::round_money_even` (L19-21), `frostline/config/settings.py::<module>` (L1-26), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/core/container.py::Container.route_engine` (L23-25)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Ship date defaults to 2026-11-02: 58 days, 48 overdue after 10 grace days -> 2 periods of 1.5%.

### L4-08 (L4, data_flow)

What 'weight_kg' does POST /quotes return for {"customer": "C-101", "from": "HAN", "to": "NDH", "weight_unit": "lb", "parcels": [{"weight": 22, "dims": [20, 20, 20]}]}?

- **Ground truth:** `"10.0"`
- **Evidence:** `frostline/api/serializers.py::parse_shipment` (L27-40), `frostline/api/serializers.py::parse_parcel` (L12-24), `frostline/domain/units.py::to_kg` (L8-16), `frostline/pricing/quote_engine.py::QuoteEngine.chargeable_weight` (L16-19), `frostline/domain/units.py::chargeable_weight` (L36-40), `frostline/domain/units.py::round_up_to_step` (L31-33), `frostline/api/serializers.py::quote_to_dict` (L43-53)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** 22 lb = 9.979 kg, larger than volumetric 1.6 kg, rounded up to the 0.5 kg step.

### L4-09 (L4, data_flow)

Under the 'express' profile, what string is stored in the 'route' column after POST /shipments with {"customer": "C-101", "from": "HPH", "to": "LCU", "parcels": [{"weight": 2, "dims": [10, 10, 10]}]}?

- **Ground truth:** `"HPH-NDH-HAN-TNG-LCU"`
- **Evidence:** `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/config/profiles.py::<module>` (L1-17), `frostline/routing/engines.py::GreedyEngine.path` (L39-53), `frostline/routing/network.py::<module>` (L1-21)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** The express profile switches routing.engine to 'greedy'.

### L4-10 (L4, event_flow)

Under the default settings, after POST /shipments with {"customer": "c-103", "from": "HAN", "to": "HUE", "parcels": [{"weight": 1, "dims": [10, 10, 10]}]}, what value is written to the 'to' column of the outbox row?

- **Ground truth:** `"provincial-health-office@email"`
- **Evidence:** `frostline/services/notification_service.py::notify_booking` (L14-22), `frostline/utils/text.py::slugify` (L19-23), `frostline/utils/text.py::normalize` (L4-6), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/services/customer_service.py::<module>` (L1-13), `frostline/utils/text.py::normalize_id` (L14-16), `frostline/config/settings.py::<module>` (L1-26)
- **Rubric:** Correct iff the normalized string (trimmed, case-insensitive, quotes removed) equals the ground truth.
- **Explanation:** The customer id is normalized to C-103 (Provincial Health Office); recipient = slug + '@' + channel.

### L4-11 (L4, data_flow)

What 'total' does POST /shipments return (default profile) for {"customer": "C-103", "from": "HAN", "to": "LCU", "parcels": [{"weight": 2, "dims": [20, 20, 20], "fragile": true}]}?

- **Ground truth:** `"26.75"`
- **Evidence:** `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/tax/policies.py::ExemptTax.tax` (L42-43), `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/pricing/strategies.py::FlatStrategy.min_charge` (L20-21), `frostline/domain/rules/fragile.py::FragileRule` (L7-12), `frostline/domain/rules/fuel.py::FuelRule.amount` (L13-15)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Minimum charge, fuel, fragile and partner remote surcharges; gov customer is tax exempt.

### L4-12 (L4, data_flow)

In a fresh default app, two bookings are made with POST /shipments: (1) {"customer": "C-100", "from": "HAN", "to": "HGI", "parcels": [{"weight": 8, "dims": [40, 30, 30]}], "promo": "cold-10"} and (2) {"customer": "C-100", "from": "HAN", "to": "HPH", "parcels": [{"weight": 1, "dims": [10, 10, 10]}]}. What revenue value does GET /reports/revenue then report for C-100?

- **Ground truth:** `"46.81"`
- **Evidence:** `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32), `frostline/core/container.py::Container.route_engine` (L23-25), `frostline/reporting/metrics.py::revenue_by_customer` (L6-10), `frostline/api/handlers.py::get_revenue` (L42-44), `frostline/pricing/money.py::from_cents` (L28-29), `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/pricing/discounts.py::apply_discount` (L38-44), `frostline/tax/policies.py::SouthTax` (L19-21)
- **Rubric:** Correct iff the numeric value equals the ground truth exactly (formatting such as trailing zeros ignored).
- **Explanation:** Sum of the two stored totals (in cents) converted back to EUR.

### L5-01 (L5, impact_analysis)

Suppose the function `round_money_even` in frostline/pricing/money.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S4"]`
- **Evidence:** `frostline/pricing/money.py::round_money_even` (L19-21), `frostline/services/billing_service.py::BillingService.invoice` (L17-37), `frostline/api/handlers.py::post_invoice` (L36-39)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only invoicing uses banker's rounding; only S4 issues an invoice.

### L5-02 (L5, impact_analysis)

Suppose the function `round_money` in frostline/pricing/money.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S1", "S2", "S4", "S5", "S6", "S8"]`
- **Evidence:** `frostline/pricing/money.py::round_money` (L14-16), `frostline/pricing/quote_engine.py::QuoteEngine.quote` (L30-48), `frostline/warehouse/storage_fees.py::calculate_fee` (L13-23), `frostline/pricing/money.py::to_cents` (L24-25), `frostline/api/handlers.py::get_route` (L28-33), `frostline/routing/fees.py::calculate_fee` (L9-12)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Quotes/bookings and storage fees use round_money; the route toll uses quantize directly; compliance uses no money.

### L5-03 (L5, impact_analysis)

Suppose the function `calculate_fee` in frostline/routing/fees.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S3"]`
- **Evidence:** `frostline/routing/fees.py::calculate_fee` (L9-12), `frostline/api/handlers.py::get_route` (L28-33)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only GET /routes imports the routing toll function; billing and storage have their own calculate_fee.

### L5-04 (L5, impact_analysis)

Suppose the function `calculate_fee` in frostline/billing/fees.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S4"]`
- **Evidence:** `frostline/billing/fees.py::calculate_fee` (L6-12), `frostline/services/billing_service.py::BillingService.invoice` (L17-37), `frostline/api/handlers.py::post_invoice` (L36-39)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only invoicing (S4) calls the late-fee function.

### L5-05 (L5, impact_analysis)

Suppose the function `calculate_fee` in frostline/warehouse/storage_fees.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S5"]`
- **Evidence:** `frostline/warehouse/storage_fees.py::calculate_fee` (L13-23), `frostline/api/warehouse_handlers.py::post_storage_estimate` (L9-18)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only the storage estimate endpoint (S5) uses it.

### L5-06 (L5, impact_analysis)

Suppose the method `RemoteAreaRule.amount` in frostline/domain/rules/remote.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `[]`
- **Evidence:** `frostline/domain/rules/remote.py::RemoteAreaRule.amount` (L18-19), `frostline/plugins/island.py::PartnerRemoteRule` (L13-17), `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/api/app.py::<module>` (L1-25)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** The registered 'remote' rule is PartnerRemoteRule, which overrides amount(); the base method is never called.

### L5-07 (L5, impact_analysis)

Suppose the method `PartnerRemoteRule.amount` in frostline/plugins/island.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S2", "S8"]`
- **Evidence:** `frostline/plugins/island.py::PartnerRemoteRule.amount` (L19-20), `frostline/domain/rules/remote.py::RemoteAreaRule.applies` (L15-16), `frostline/routing/network.py::<module>` (L1-21), `frostline/config/settings.py::<module>` (L1-26), `frostline/core/container.py::Container.surcharge_rules` (L27-29)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Applies only to shipments whose destination is remote (HGI in S2, LCU in S8).

### L5-08 (L5, impact_analysis)

Suppose the method `TieredStrategy.base_rate` in frostline/pricing/strategies.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S1", "S2", "S4", "S6"]`
- **Evidence:** `frostline/pricing/strategies.py::TieredStrategy.base_rate` (L37-41), `frostline/pricing/strategies.py::DistanceStrategy` (L44-46), `frostline/pricing/strategies.py::FlatStrategy.price` (L23-25), `frostline/config/settings.py::<module>` (L1-26), `frostline/config/profiles.py::<module>` (L1-17)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Used by 'tiered' (default) and inherited by 'distance' (express); changes matter only when above the minimum charge.

### L5-09 (L5, impact_analysis)

Suppose the method `FlatStrategy.min_charge` in frostline/pricing/strategies.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S8"]`
- **Evidence:** `frostline/pricing/strategies.py::FlatStrategy.min_charge` (L20-21), `frostline/pricing/strategies.py::FlatStrategy.price` (L23-25)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only shipments whose raw price is below the minimum charge change.

### L5-10 (L5, impact_analysis)

Suppose the function `notify_booking` in frostline/services/notification_service.py is modified so that it returns an empty list (after doing nothing) (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S8"]`
- **Evidence:** `frostline/services/notification_service.py::notify_booking` (L14-22), `frostline/core/events.py::EventBus.publish` (L24-29), `frostline/services/shipment_service.py::ShipmentService.book` (L26-38)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Handler results are discarded by book(), but S8's GET /reports/revenue response includes per-channel outbox counts.

### L5-11 (L5, impact_analysis)

Suppose the method `DijkstraEngine.path` in frostline/routing/engines.py is modified so that it returns its current result list in reverse order (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S2", "S3", "S4", "S8"]`
- **Evidence:** `frostline/routing/engines.py::DijkstraEngine.path` (L14-29), `frostline/core/interfaces.py::RouteEngine.distance` (L31-33), `frostline/api/handlers.py::get_route` (L28-33), `frostline/api/handlers.py::post_shipment` (L18-25), `frostline/storage/repositories.py::ShipmentRepository.save` (L22-32)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** A reversed path has the same distance, so quotes do not change; responses exposing the path/route do.

### L5-12 (L5, impact_analysis)

Suppose the function `normalize_code` in frostline/utils/text.py is modified so that it returns the lower-cased version of its current result (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S2"]`
- **Evidence:** `frostline/utils/text.py::normalize_code` (L9-11), `frostline/pricing/discounts.py::promo_discount` (L27-35), `frostline/pricing/discounts.py::apply_discount` (L38-44)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only promo codes are normalized with it; only S2 uses a promo, and COLD10 beats the gold loyalty discount.

### L5-13 (L5, impact_analysis)

Suppose the method `ExemptTax.tax` in frostline/tax/policies.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S8"]`
- **Evidence:** `frostline/tax/policies.py::ExemptTax.tax` (L42-43), `frostline/core/container.py::Container.tax_policy` (L17-21), `frostline/services/customer_service.py::<module>` (L1-13)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only 'gov' customers (C-103, S8) are exempt.

### L5-14 (L5, impact_analysis)

Suppose the function `handling_fee` in frostline/warehouse/storage_fees.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S5"]`
- **Evidence:** `frostline/warehouse/storage_fees.py::handling_fee` (L26-28), `frostline/api/warehouse_handlers.py::post_storage_estimate` (L9-18)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only the storage estimate endpoint uses handling fees.

### L5-15 (L5, impact_analysis)

Suppose the method `GreedyEngine.path` in frostline/routing/engines.py is modified so that it returns its current result list in reverse order (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `[]`
- **Evidence:** `frostline/routing/engines.py::GreedyEngine.path` (L39-53), `frostline/config/profiles.py::<module>` (L1-17), `frostline/core/interfaces.py::RouteEngine.distance` (L31-33), `frostline/api/handlers.py::post_quote` (L10-15)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Only S6 uses the greedy engine and its quote depends only on the (unchanged) distance.

### L5-16 (L5, impact_analysis)

Suppose the method `FuelRule.amount` in frostline/domain/rules/fuel.py is modified so that it returns exactly 1 more than it currently returns (nothing else in the repository changes). Each scenario below is run in a fresh application instance and its observable output is the list of API response bodies it returns. Which scenarios would return at least one response body that differs from the current behaviour? Answer with the list of scenario IDs (an empty list if none).  
Scenarios:  
- S1 (profile=default): POST /quotes {"customer": "C-101", "from": "HAN", "parcels": [{"dims": [30, 20, 20], "weight": 3.2}, {"dims": [60, 40, 40], "fragile": true, "weight": 12}], "to": "HUE"}  
- S2 (profile=default): POST /shipments {"customer": "C-100", "from": "HAN", "parcels": [{"dims": [40, 30, 30], "weight": 8}], "promo": "cold-10", "to": "HGI"}  
- S3 (profile=default): GET /routes {"from": "HAN", "to": "LCU"}  
- S4 (profile=default): POST /shipments {"customer": "C-104", "from": "HPH", "parcels": [{"dims": [40, 30, 20], "weight": 6}, {"dims": [10, 10, 10], "fragile": true, "weight": 1.5}], "to": "DNG"}; then POST /invoices {"as_of": "2026-12-30", "customer": "C-104"}  
- S5 (profile=default): POST /storage/estimate {"days": 45, "pallets": 4, "product": "seafood"}  
- S6 (profile=express): POST /quotes {"customer": "C-102", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "hazmat": true, "weight": 5}], "service": "express", "to": "HCM"}  
- S7 (profile=default): POST /storage/compliance {"product": "vaccine", "readings": [[0, 3], [10, 6], [20, 7], [30, 5.5], [40, 3]]}  
- S8 (profile=default): POST /shipments {"customer": "C-103", "from": "HAN", "parcels": [{"dims": [20, 20, 20], "fragile": true, "weight": 2}], "to": "LCU"}; then GET /reports/revenue {}

- **Ground truth:** `["S1", "S2", "S4", "S6", "S8"]`
- **Evidence:** `frostline/domain/rules/fuel.py::FuelRule.amount` (L13-15), `frostline/config/settings.py::<module>` (L1-26), `frostline/config/profiles.py::<module>` (L1-17), `frostline/core/container.py::Container.surcharge_rules` (L27-29)
- **Rubric:** Correct iff the set equals the ground truth; partial credit reported as set precision/recall/F1.
- **Explanation:** Every quote/booking scenario has 'fuel' enabled (default and express profiles).
