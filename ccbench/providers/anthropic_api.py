"""Anthropic Messages API adapter (needs ANTHROPIC_API_KEY in .env)."""

import os
import time

from ccbench.providers.base import Provider, Response
from ccbench.providers.http import classify_http, post_json

# USD per million tokens (input, output). Only used for cost estimation; edit if prices change.
PRICES = {"claude-haiku-5-5": (1.0, 5.0), "claude-sonnet-5-5": (3.0, 15.0), "claude-opus-5-5": (5.0, 25.0)}


class AnthropicProvider(Provider):
    name = "anthropic"
    supports = {"temperature": True, "seed": False, "usage": True, "cost": True}

    def _call(self, system, prompt, max_tokens, meta):
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return Response(error="ANTHROPIC_API_KEY not set", error_kind="fatal")
        t0 = time.monotonic()
        status, body = post_json("https://api.anthropic.com/v1/messages", {
            "model": self.model, "max_tokens": max_tokens, "temperature": self.temperature,
            "system": system, "messages": [{"role": "user", "content": prompt}],
        }, {"x-api-key": key, "anthropic-version": "2023-06-01"}, self.timeout)
        latency = time.monotonic() - t0
        if status != 200:
            return Response(error=str(body)[:500], error_kind=classify_http(status, body), latency_s=latency)
        text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
        u = body.get("usage", {})
        mid = body.get("model", self.model)
        pin, pout = PRICES.get(mid, (None, None))
        cost = None if pin is None else (u.get("input_tokens", 0) * pin + u.get("output_tokens", 0) * pout) / 1e6
        return Response(text=text, model_id=mid, input_tokens=u.get("input_tokens"), output_tokens=u.get("output_tokens"),
                        cost_usd=cost, cost_source="price table estimate" if cost is not None else None, latency_s=latency)
