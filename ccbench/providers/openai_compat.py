"""OpenAI-compatible chat completions adapter (free-tier control model).

Works with any endpoint implementing /chat/completions, e.g. OpenRouter,
Groq, Google Gemini (OpenAI-compatible endpoint), Hugging Face router,
Together, DeepSeek, FPT AI. Configure with environment variables in .env:
OPENAI_COMPAT_BASE_URL, OPENAI_COMPAT_API_KEY (or a preset name below).
Free-tier quotas are not assumed: HTTP 429 / quota messages are detected and
the run stops cleanly so it can be resumed.
"""

import os
import time

from ccbench.providers.base import Provider, Response
from ccbench.providers.http import classify_http, post_json

PRESETS = {
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "huggingface": ("https://router.huggingface.co/v1", "HF_TOKEN"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
}


class OpenAICompatProvider(Provider):
    name = "openai_compat"
    supports = {"temperature": True, "seed": True, "usage": True, "cost": False}

    def __init__(self, model, preset=None, base_url=None, api_key_env=None, price_in=0.0, price_out=0.0, **kw):
        super().__init__(model, **kw)
        if preset:
            base_url, api_key_env = PRESETS[preset][0], api_key_env or PRESETS[preset][1]
        self.base_url = (base_url or os.environ.get("OPENAI_COMPAT_BASE_URL", "")).rstrip("/")
        self.api_key_env = api_key_env or "OPENAI_COMPAT_API_KEY"
        self.price_in, self.price_out = price_in, price_out
        self.preset = preset

    def _call(self, system, prompt, max_tokens, meta):
        key = os.environ.get(self.api_key_env)
        if not key or not self.base_url:
            return Response(error="missing %s or base_url" % self.api_key_env, error_kind="fatal")
        payload = {"model": self.model, "max_tokens": max_tokens, "temperature": self.temperature,
                   "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}
        if self.seed is not None:
            payload["seed"] = self.seed
        t0 = time.monotonic()
        status, body = post_json(self.base_url + "/chat/completions", payload, {"Authorization": "Bearer " + key}, self.timeout)
        latency = time.monotonic() - t0
        if status != 200 or "choices" not in body:
            return Response(error=str(body)[:500], error_kind=classify_http(status, body), latency_s=latency)
        text = body["choices"][0]["message"].get("content") or ""
        u = body.get("usage") or {}
        cost = (u.get("prompt_tokens", 0) * self.price_in + u.get("completion_tokens", 0) * self.price_out) / 1e6
        return Response(text=text, model_id=body.get("model", self.model), input_tokens=u.get("prompt_tokens"),
                        output_tokens=u.get("completion_tokens"), cost_usd=cost,
                        cost_source="configured price (free tier = 0)", latency_s=latency)
