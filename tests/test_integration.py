"""Integration tests: dataset ground truth reproduces; offline mock run end to end."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccbench import paths  # noqa: E402
from ccbench.dataset.build import build, load  # noqa: E402


class TestDataset(unittest.TestCase):
    def test_ground_truth_reproduces(self):
        recs, man = build(write=False)
        with open(os.path.join(paths.DATA_DIR, "manifest.v1.json")) as fh:
            saved = json.load(fh)
        self.assertEqual(man["dataset_sha256"], saved["dataset_sha256"])
        self.assertEqual(len(recs), saved["n_items"])

    def test_every_item_has_required_fields(self):
        need = {"id", "question", "answer", "gold_evidence", "level", "qtype", "rubric", "explanation", "answer_type"}
        for it in load():
            self.assertTrue(need <= set(it), it["id"])
            self.assertTrue(it["gold_evidence"])
        levels = {it["level"] for it in load()}
        self.assertEqual(levels, {"L1", "L2", "L3", "L4", "L5"})


class TestMockRun(unittest.TestCase):
    def test_end_to_end(self):
        from ccbench.report.report import build_report
        from ccbench.runner import Runner, load_records
        tmp = tempfile.mkdtemp(prefix="ccbench-test-")
        try:
            cfg = {"name": "test_mock", "models": [{"provider": "mock", "model": "mock", "label": "mock", "seed": 1}],
                   "conditions": [{"strategy": "none"}, {"strategy": "oracle"}, {"strategy": "bm25", "budgets": [2000]},
                                  {"strategy": "dgc", "budgets": [2000]}],
                   "items": {"ids": ["L1-01", "L3-03", "L5-06"]}, "repeats": 1, "concurrency": 2}
            exp = os.path.join(tmp, "exp")
            os.makedirs(exp)
            r = Runner(cfg, exp_dir=exp, log=lambda *a: None)
            r.run()
            recs = load_records(exp)
            self.assertEqual(len(recs), 12)
            # resume must not duplicate work
            Runner(cfg, exp_dir=exp, log=lambda *a: None).run()
            self.assertEqual(len(load_records(exp)), 12)
            oracle = [x for x in recs if x["strategy"] == "oracle"]
            self.assertTrue(all(x["scores"]["context_recall"] == 1.0 for x in oracle))
            none = [x for x in recs if x["strategy"] == "none"]
            self.assertTrue(all(x["scores"]["context_recall"] == 0.0 for x in none))
            self.assertNotIn("def ", json.dumps(recs[0]["context"]))  # no source code dumped in records
            with open(os.path.join(paths.CONFIG_DIR, "prereg.json")) as fh:
                out = build_report(exp, json.load(fh))
            self.assertTrue(os.path.exists(os.path.join(out, "report.md")))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
