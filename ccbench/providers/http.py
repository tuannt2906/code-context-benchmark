"""Tiny JSON-over-HTTP helper (urllib, stdlib only)."""

import json
import urllib.error
import urllib.request


def post_json(url, payload, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers=dict({"Content-Type": "application/json"}, **headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            return exc.code, json.loads(body)
        except ValueError:
            return exc.code, {"error": body[:500]}


def classify_http(status, body):
    text = json.dumps(body).lower()
    if status == 429 or "quota" in text or "rate limit" in text or "insufficient" in text:
        # 429 can be transient rate limiting or exhausted daily quota; daily quota is fatal for the run
        if any(k in text for k in ("quota", "daily", "per day", "exceeded your", "insufficient", "credits")):
            return "quota"
        return "rate_limit"
    if status in (400, 401, 403, 404):
        return "fatal"
    return "http"
