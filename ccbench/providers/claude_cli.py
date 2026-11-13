"""Claude through the Claude Code CLI in headless mode (``claude -p``).

Uses the user's existing Claude Code login (no API key). All tools are
disabled (``--tools ""``) so the model can only see the prompt - it cannot
open repository files on its own. The process runs inside an empty temporary
working directory owned by the runner. Usage, cost (list-price equivalent
reported by the CLI) and the canonical model id are taken from the JSON result.
The CLI does not expose temperature or seed; they are recorded as unsupported.
"""

import json
import shutil
import subprocess

from ccbench.providers.base import Provider, Response

QUOTA_MARKERS = ("usage limit", "rate limit", "quota", "credit balance", "limit reached", "hit your", "-hour limit", "weekly limit", "resets ")


class ClaudeCLIProvider(Provider):
    name = "claude_cli"
    supports = {"temperature": False, "seed": False, "usage": True, "cost": True}

    def __init__(self, model="haiku", workdir=None, effort=None, binary="claude", **kw):
        super().__init__(model, **kw)
        self.workdir = workdir
        self.effort = effort
        self.binary = shutil.which(binary) or binary

    def effective_params(self):
        p = super().effective_params()
        p["effort"] = self.effort
        return p

    def _call(self, system, prompt, max_tokens, meta):
        cmd = [self.binary, "-p", "--model", self.model, "--output-format", "json", "--tools", "",
               "--system-prompt", system, "--no-session-persistence", "--strict-mcp-config",
               "--setting-sources", "", "--disable-slash-commands"]
        if self.effort:
            cmd += ["--effort", self.effort]
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=self.timeout,
                              cwd=self.workdir)
        out = proc.stdout.strip()
        try:
            data = json.loads(out.splitlines()[-1]) if out else {}
        except ValueError:
            data = {}
        if not data:
            msg = (proc.stderr or out or "empty output")[-500:]
            kind = "quota" if any(m in msg.lower() for m in QUOTA_MARKERS) else "exception"
            return Response(error=msg, error_kind=kind)
        if data.get("is_error"):
            msg = str(data.get("result") or data.get("api_error_status") or data)[-500:]
            kind = "quota" if any(m in msg.lower() for m in QUOTA_MARKERS) else "exception"
            return Response(error=msg, error_kind=kind)
        usage = data.get("usage", {})
        model_usage = data.get("modelUsage", {})
        model_id = next(iter(model_usage), None)
        mu = model_usage.get(model_id, {}) if model_id else {}
        inp = (usage.get("input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0)
        return Response(
            text=data.get("result", ""), model_id=mu.get("canonicalModel", model_id),
            input_tokens=inp, output_tokens=usage.get("output_tokens"),
            cache_read_tokens=usage.get("cache_read_input_tokens"), cache_creation_tokens=usage.get("cache_creation_input_tokens"),
            cost_usd=data.get("total_cost_usd"), cost_source="claude_cli total_cost_usd (list-price equivalent)",
            latency_s=(data.get("duration_ms") or 0) / 1000.0 or None,
            extra={"thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
                   "duration_api_ms": data.get("duration_api_ms"), "stop_reason": data.get("stop_reason")},
        )
