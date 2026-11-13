"""Provider adapter interface + shared retry / rate-limit / quota handling."""

import random
import threading
import time


class QuotaExhausted(Exception):
    """Raised when a provider reports that the quota is used up; the runner stops
    scheduling new jobs for that model and the run can be resumed later."""


class Response:
    def __init__(self, text="", model_id=None, provider=None, input_tokens=None, output_tokens=None,
                 cache_read_tokens=None, cache_creation_tokens=None, cost_usd=None, cost_source=None,
                 latency_s=None, error=None, error_kind=None, attempts=1, extra=None):
        self.text = text
        self.model_id = model_id
        self.provider = provider
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_tokens = cache_read_tokens
        self.cache_creation_tokens = cache_creation_tokens
        self.cost_usd = cost_usd
        self.cost_source = cost_source
        self.latency_s = latency_s
        self.error = error
        self.error_kind = error_kind
        self.attempts = attempts
        self.extra = extra or {}

    @property
    def ok(self):
        return self.error is None

    def to_dict(self):
        return dict(self.__dict__)


class RateLimiter:
    """Minimum spacing between request starts (requests per minute)."""

    def __init__(self, rpm=None):
        self.interval = 60.0 / rpm if rpm else 0.0
        self.lock = threading.Lock()
        self.next_at = 0.0

    def wait(self):
        if not self.interval:
            return
        with self.lock:
            now = time.monotonic()
            delay = max(0.0, self.next_at - now)
            self.next_at = max(now, self.next_at) + self.interval
        if delay:
            time.sleep(delay)


class Provider:
    name = "base"
    supports = {"temperature": False, "seed": False, "usage": False, "cost": False}

    def __init__(self, model, temperature=0.0, seed=None, timeout=180, max_retries=4, rpm=None, **kwargs):
        self.model = model
        self.temperature = temperature
        self.seed = seed
        self.timeout = timeout
        self.max_retries = max_retries
        self.limiter = RateLimiter(rpm)
        self.options = kwargs

    def effective_params(self):
        """Parameters actually honoured by this provider (recorded per run)."""
        return {
            "model": self.model,
            "temperature": self.temperature if self.supports["temperature"] else None,
            "seed": self.seed if self.supports["seed"] else None,
            "unsupported": [k for k in ("temperature", "seed") if not self.supports[k]],
        }

    def _call(self, system, prompt, max_tokens, meta):
        raise NotImplementedError

    def generate(self, system, prompt, max_tokens=1024, meta=None):
        attempt, last = 0, None
        while attempt <= self.max_retries:
            attempt += 1
            self.limiter.wait()
            t0 = time.monotonic()
            try:
                resp = self._call(system, prompt, max_tokens, meta or {})
            except QuotaExhausted:
                raise
            except Exception as exc:  # network / subprocess errors are retryable
                resp = Response(error="%s: %s" % (type(exc).__name__, exc), error_kind="exception")
            if resp.latency_s is None:
                resp.latency_s = time.monotonic() - t0
            resp.attempts = attempt
            resp.provider = self.name
            if resp.ok or resp.error_kind in ("fatal",):
                return resp
            if resp.error_kind == "quota":
                raise QuotaExhausted(resp.error)
            last = resp
            time.sleep(min(60, (2 ** attempt) + random.random()))
        return last
