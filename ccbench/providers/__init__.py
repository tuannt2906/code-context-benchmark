"""Provider registry: add a new model backend by adding an adapter here."""

from ccbench.providers.anthropic_api import AnthropicProvider
from ccbench.providers.claude_cli import ClaudeCLIProvider
from ccbench.providers.mock import MockProvider
from ccbench.providers.openai_compat import OpenAICompatProvider

PROVIDERS = {
    "claude_cli": ClaudeCLIProvider,
    "anthropic": AnthropicProvider,
    "openai_compat": OpenAICompatProvider,
    "mock": MockProvider,
}


def make_provider(spec, **runtime):
    spec = dict(spec)
    kind = spec.pop("provider")
    spec.pop("label", None)
    spec.update(runtime)
    return PROVIDERS[kind](**spec)
