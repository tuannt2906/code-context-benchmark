"""Offline mock model - SIMULATION ONLY, never reported as an experimental result.

Answers correctly with probability  base + gain * context_recall  (deterministic
per job), otherwise returns the distractor answer (if any) or a wrong value.
Used for unit/integration tests, the no-API demo, and to check that the
analysis pipeline recovers an effect of known size.
"""

import hashlib
import json
import random

from ccbench.providers.base import Provider, Response


class MockProvider(Provider):
    name = "mock"
    supports = {"temperature": False, "seed": True, "usage": False, "cost": False}

    def __init__(self, model="mock-recall", base=0.15, gain=0.7, **kw):
        super().__init__(model, **kw)
        self.base, self.gain = base, gain

    def _call(self, system, prompt, max_tokens, meta):
        item = meta.get("item") or {}
        recall = meta.get("context_recall", 0.0)
        h = int(hashlib.sha256(("%s|%s|%s" % (meta.get("job_key"), self.seed, self.model)).encode()).hexdigest(), 16)
        rng = random.Random(h)
        correct = rng.random() < self.base + self.gain * recall
        if correct:
            ans = item.get("answer")
        elif item.get("distractor_answer") is not None and rng.random() < 0.6:
            ans = item["distractor_answer"]
        else:
            ans = [] if item.get("answer_type") in ("set", "list") else "unknown"
        ev = []
        if correct and item.get("gold_evidence"):
            g = item["gold_evidence"][0]
            ev = ["%s:%d" % (g["path"], g["start"])]
        text = json.dumps({"answer": ans, "evidence": ev, "explanation": "simulated"})
        return Response(text=text, model_id="mock/%s" % self.model, input_tokens=None, output_tokens=None,
                        cost_usd=0.0, cost_source="mock", latency_s=0.0)
