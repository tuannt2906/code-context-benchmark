"""Prompt template (version p1). Identical for every strategy and model."""

import hashlib

from ccbench import PROMPT_VERSION

SYSTEM = ("You are an expert software engineer answering questions about a Python code repository named "
          "`frostline`. Base your answer only on the code you are given and on careful reasoning about how it "
          "executes. Respond with a single JSON object and nothing else.")

FORMAT_HINT = {
    "number": "a JSON number or numeric string (e.g. 12.5)",
    "string": "a JSON string",
    "set": "a JSON list of strings; order does not matter",
    "list": "a JSON list, in order",
    "json": "a JSON value",
}


def build_prompt(item, context_text):
    q = item["question"]
    if context_text:
        ctx = ("Repository context (excerpts of the repository; each line is prefixed with its line number; "
               "'...' marks omitted bodies):\n<context>\n%s\n</context>\n\n" % context_text)
    else:
        ctx = "No repository code is provided for this question. Give your best answer.\n\n"
    return ("Question: %s\n\n%sQuestion (repeated): %s\n\n"
            "Answer format: %s.\n"
            "Respond with JSON only, exactly in this shape:\n"
            "{\"answer\": <answer>, \"evidence\": [\"<file path>:<line>\", ...], \"explanation\": \"<at most two sentences>\"}\n"
            "In \"evidence\" cite 1-6 code lines (path:line or path:start-end) that justify the answer."
            % (q, ctx, q, FORMAT_HINT[item["answer_type"]]))


def prompt_sha(system, prompt):
    return hashlib.sha256((PROMPT_VERSION + "\0" + system + "\0" + prompt).encode()).hexdigest()[:16]
