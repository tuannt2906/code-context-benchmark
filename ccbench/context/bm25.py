"""Okapi BM25 over code units (lexical retrieval baseline)."""

import math
import re
from collections import Counter

_SPLIT = re.compile(r"[A-Za-z][a-z0-9]*|[A-Z]+(?![a-z])|\d+")
STOP = {"the", "a", "an", "of", "to", "in", "is", "and", "or", "for", "what", "which", "does", "with",
        "self", "return", "def", "class", "import", "from", "if", "else", "none", "true", "false", "it",
        "be", "by", "on", "as", "at", "are", "this", "that", "when", "would", "under", "value"}


def tokenize(text):
    out = []
    for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?", text):
        parts = [p for chunk in word.split("_") for p in _SPLIT.findall(chunk)] or [word]
        for p in parts:
            p = p.lower()
            if p not in STOP and len(p) > 1:
                out.append(p)
    return out


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        """docs: list of (doc_id, text)."""
        self.ids = [d for d, _ in docs]
        self.tfs = [Counter(tokenize(t)) for _, t in docs]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avg = sum(self.lens) / max(1, len(self.lens))
        df = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.k1, self.b = k1, b

    def scores(self, query):
        q = tokenize(query)
        out = []
        for i, tf in enumerate(self.tfs):
            s = 0.0
            for t in q:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg))
            out.append((s, self.ids[i]))
        return out

    def rank(self, query):
        return [d for s, d in sorted(self.scores(query), key=lambda x: (-x[0], x[1]))]
