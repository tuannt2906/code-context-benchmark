"""Token estimation.

No provider-specific tokenizer is available offline, so budgets are enforced
with a character-based estimate. The ratio is calibrated after a run against
provider-reported input tokens (see analysis.aggregate.token_calibration) and
both numbers are always reported side by side.
"""

import math

CHARS_PER_TOKEN = 2.35  # calibrated on claude-haiku-5-5 usage (smoke run 2026-11-13: slope 1.36 at 3.2)


def estimate(text):
    if not text:
        return 0
    return int(math.ceil(len(text) / CHARS_PER_TOKEN))
