"""Unit tests (stdlib unittest, no API, no network). Run: python3 -m unittest discover -s tests"""

import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccbench import tokens  # noqa: E402
from ccbench.analysis.stats import holm, mcnemar_exact, paired_bootstrap, wilson  # noqa: E402
from ccbench.context.bm25 import BM25, tokenize  # noqa: E402
from ccbench.context.strategies import ContextBuilder  # noqa: E402
from ccbench.eval.parse import parse_citations, parse_response  # noqa: E402
from ccbench.eval.scoring import answer_matches, context_recall, evidence_scores  # noqa: E402
from ccbench.paths import FIXTURE_PKG, FIXTURE_ROOT  # noqa: E402
from ccbench.repo.graph import NameGraph, ProgramGraph  # noqa: E402
from ccbench.repo.index import RepoIndex  # noqa: E402

INDEX = RepoIndex(FIXTURE_ROOT, FIXTURE_PKG)


class TestIndex(unittest.TestCase):
    def test_units_cover_methods_and_classes(self):
        self.assertIn("frostline/pricing/strategies.py::TieredStrategy.base_rate", INDEX.units)
        self.assertIn("frostline/pricing/strategies.py::TieredStrategy", INDEX.units)
        self.assertIn("frostline/config/settings.py::<module>", INDEX.units)

    def test_units_do_not_overlap(self):
        seen = {}
        for u in INDEX.units.values():
            for ln in u.lines:
                key = (u.path, ln)
                self.assertNotIn(key, seen, "line %s owned by %s and %s" % (key, seen.get(key), u.id))
                seen[key] = u.id

    def test_repo_bigger_than_largest_budget(self):
        self.assertGreater(INDEX.total_tokens(), 16000)


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = ProgramGraph(INDEX)

    def test_registry_edges_follow_config(self):
        kinds = {e.dst: e.kind for e in self.g.out["frostline/core/container.py::Container.pricing_strategy"]}
        self.assertEqual(kinds["frostline/pricing/strategies.py::TieredStrategy"], "registry")
        self.assertEqual(kinds["frostline/pricing/strategies.py::DistanceStrategy"], "registry_profile")

    def test_event_edges(self):
        dst = {e.dst for e in self.g.out["frostline/services/shipment_service.py::ShipmentService.book"]}
        self.assertIn("frostline/services/notification_service.py::notify_booking", dst)

    def test_no_dispatch_graph_has_no_dispatch_edges(self):
        g = ProgramGraph(INDEX, dispatch=False)
        self.assertFalse(any(e.family == "dispatch" for es in g.out.values() for e in es))

    def test_super_and_cha(self):
        dst = {e.dst for e in self.g.out["frostline/pricing/strategies.py::DistanceStrategy.price"]}
        self.assertIn("frostline/pricing/strategies.py::FlatStrategy.price", dst)
        dst = {e.dst for e in self.g.out["frostline/domain/rules/base.py::SurchargeRule.apply"]}
        self.assertIn("frostline/plugins/island.py::PartnerRemoteRule.amount", dst)

    def test_namegraph_links_lookalikes(self):
        ng = NameGraph(INDEX)
        callees = ng.callees("frostline/api/handlers.py::get_route")
        self.assertIn("frostline/billing/fees.py::calculate_fee", callees)  # naive by design


class TestContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = ContextBuilder(INDEX)

    def test_budgets_respected(self):
        q = "What 'toll' value does GET /routes return from HAN to LCU?"
        for s in ("full", "fixed", "bm25", "bm25_namegraph", "dgc", "dgc_no_dispatch", "dgc_no_ranking"):
            for b in (2000, 4000, 8000):
                ctx = self.b.build(s, q, b)
                self.assertLessEqual(ctx.est_tokens, b, (s, b))
                self.assertGreater(ctx.est_tokens, 0)

    def test_none_and_oracle(self):
        self.assertEqual(self.b.build("none", "x", 4000).text, "")
        gold = ["frostline/routing/fees.py::calculate_fee"]
        self.assertEqual(self.b.build("oracle", "x", None, gold).full, gold)

    def test_dgc_finds_route_handler(self):
        ctx = self.b.build("dgc", "What 'toll' value does GET /routes return?", 2000)
        self.assertIn("frostline/api/handlers.py::get_route", ctx.full)

    def test_deterministic(self):
        q = "Which tables receive rows when POST /shipments succeeds?"
        self.assertEqual(self.b.build("dgc", q, 4000).text, self.b.build("dgc", q, 4000).text)


class TestScoring(unittest.TestCase):
    def test_numbers(self):
        self.assertTrue(answer_matches("number", "34.16", "34.160")[0])
        self.assertTrue(answer_matches("number", 60, "60.00")[0])
        self.assertFalse(answer_matches("number", "9.00", "9.60")[0])

    def test_sets_and_lists(self):
        ok, p, r, f1 = answer_matches("set", ["S2", "S4"], ["S4"])
        self.assertFalse(ok)
        self.assertAlmostEqual(f1, 2 / 3)
        self.assertTrue(answer_matches("set", [], [])[0])
        self.assertFalse(answer_matches("list", ["a", "b"], ["b", "a"])[0])

    def test_strings(self):
        self.assertTrue(answer_matches("string", "`PartnerRemoteRule`", "PartnerRemoteRule")[0])
        self.assertTrue(answer_matches("string", "frostline.plugins.island.PartnerRemoteRule", "PartnerRemoteRule")[0])

    def test_parse(self):
        obj, err = parse_response("Sure!\n```json\n{\"answer\": [\"S1\"], \"evidence\": [\"api/handlers.py:12\"]}\n```")
        self.assertIsNone(err)
        self.assertEqual(obj["answer"], ["S1"])
        self.assertEqual(parse_response("no json")[1], "no_json_answer")
        self.assertEqual(parse_citations(["pricing/money.py:3-5"]), [("frostline/pricing/money.py", 3, 5)])

    def test_evidence_and_context_recall(self):
        gold = [{"unit": "u1", "path": "frostline/a.py", "start": 10, "end": 20, "lines": list(range(10, 21))}]
        s = evidence_scores([("frostline/a.py", 12, 12), ("frostline/b.py", 1, 1)], gold)
        self.assertEqual(s["evidence_precision"], 0.5)
        self.assertEqual(s["evidence_recall"], 1.0)
        self.assertEqual(context_recall(gold, ["u1"], []), (1.0, 1.0))
        self.assertEqual(context_recall(gold, [], ["u1"]), (0.0, 0.5))


class TestStats(unittest.TestCase):
    def test_wilson(self):
        lo, hi = wilson(50, 100)
        self.assertAlmostEqual(lo, 0.404, places=2)
        self.assertAlmostEqual(hi, 0.596, places=2)

    def test_mcnemar(self):
        a = {i: True for i in range(12)}
        b = {i: i < 2 for i in range(12)}
        n10, n01, p = mcnemar_exact(a, b)
        self.assertEqual((n10, n01), (10, 0))
        self.assertLess(p, 0.01)

    def test_bootstrap_and_holm(self):
        a = {i: 1.0 for i in range(40)}
        b = {i: 0.0 if i < 20 else 1.0 for i in range(40)}
        d, lo, hi, p = paired_bootstrap(a, b, n_boot=2000)
        self.assertAlmostEqual(d, 0.5)
        self.assertGreater(lo, 0.3)
        adj = holm({"x": 0.01, "y": 0.04})
        self.assertAlmostEqual(adj["x"], 0.02)
        self.assertAlmostEqual(adj["y"], 0.04)


class TestMisc(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(tokens.estimate(""), 0)
        self.assertGreater(tokens.estimate("x" * 100), 0)

    def test_bm25(self):
        bm = BM25([("a", "round money cents"), ("b", "route toll fee")])
        self.assertEqual(bm.rank("toll for route")[0], "b")
        self.assertIn("money", tokenize("round_money"))


if __name__ == "__main__":
    unittest.main()


class TestRecovery(unittest.TestCase):
    def test_near_json_recovered(self):
        raw = '{"answer": 4.99, "evidence": ["frostline/a.py:3"], "explanation": "returns row["x"] here"}'
        obj, err = parse_response(raw)
        self.assertIsNone(err)
        self.assertEqual(obj["answer"], 4.99)
        self.assertEqual(obj["evidence"], ["frostline/a.py:3"])
