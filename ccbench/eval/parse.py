"""Extract the JSON answer object from a raw model response."""

import json
import re

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def _first_object(text):
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except ValueError:
                        break
        start = text.find("{", start + 1)
    return None


def parse_response(text):
    """Return (obj, error). obj has keys answer, evidence, explanation."""
    if not text:
        return None, "empty"
    candidates = [m.group(1) for m in FENCE.finditer(text)] + [text]
    for c in candidates:
        obj = _first_object(c)
        if isinstance(obj, dict) and "answer" in obj:
            ev = obj.get("evidence") or []
            if isinstance(ev, str):
                ev = [ev]
            obj["evidence"] = [e if isinstance(e, str) else json.dumps(e) for e in ev]
            return obj, None
    # fallback: the object is almost JSON (e.g. unescaped quotes inside "explanation");
    # recover only the "answer" and "evidence" fields, which are what we score
    m = re.search(r'"answer"\s*:\s*(.*?)\s*,\s*"evidence"\s*:\s*(\[.*?\])', text, re.S)
    if m:
        try:
            ans = json.loads(m.group(1))
            ev = json.loads(m.group(2))
            return {"answer": ans, "evidence": [e if isinstance(e, str) else json.dumps(e) for e in ev],
                    "explanation": None, "_recovered": True}, None
        except ValueError:
            pass
    return None, "no_json_answer"


CITE = re.compile(r"((?:[\w.\-]+/)*[\w.\-]+\.py)\s*[:#L ]*\s*(\d+)(?:\s*[-–]\s*L?(\d+))?")


def parse_citations(evidence):
    """['frostline/a.py:12', 'pricing/x.py:3-9'] -> [(path, start, end)]"""
    out = []
    for e in evidence:
        for m in CITE.finditer(e):
            path = m.group(1).lstrip("./")
            if not path.startswith("frostline/"):
                path = "frostline/" + path
            a = int(m.group(2))
            b = int(m.group(3)) if m.group(3) else a
            out.append((path, min(a, b), max(a, b)))
    return out
