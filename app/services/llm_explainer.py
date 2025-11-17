"""LLM explainer services and provider implementations."""
from __future__ import annotations

import json
import os
from textwrap import dedent
from typing import Dict, Protocol, runtime_checkable

try:  # pragma: no cover - imported at runtime when dependency is installed
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - fallback when Anthropic is unavailable
    Anthropic = None  # type: ignore[assignment]


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol describing a generic LLM explanation provider."""

    def explain(self, prompt: str) -> str:
        """Return a human-readable explanation generated from the prompt."""


class AnthropicExplainer:
    """Concrete provider backed by the Anthropic Messages API."""

    def __init__(
        self,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 700,
        temperature: float = 0.2,
    ) -> None:
        if Anthropic is None:
            raise RuntimeError(
                "anthropic library is not installed. Ensure requirements are installed to use AnthropicExplainer."
            )
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not configured.")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def explain(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text_blocks = [block.text for block in response.content if getattr(block, "text", None)]
        return "\n".join(text_blocks).strip()


def _fallback_summary(report_json: Dict[str, object]) -> str:
    """Deterministic summary used when an LLM provider is unavailable."""

    components = report_json.get("components", [])
    parts = ["AI Risk Narrative:"]
    for component in components:
        parts.append(
            f"- {component['name']}: score {component['score']:.1f} ({component['description']})"
        )
    survival = report_json.get("survival_probability", 0.0)
    parts.append(f"Survival probability over next 12 months estimated at {survival:.1f}%.")
    rules = report_json.get("rules", [])
    triggered = [rule for rule in rules if rule.get("triggered")]
    if triggered:
        parts.append("Rules triggered: " + ", ".join(rule["name"] for rule in triggered))
    else:
        parts.append("No deterministic rule breaches detected.")
    parts.append("Raw payload: " + json.dumps(report_json, sort_keys=True)[:400])
    return "\n".join(parts)


def _build_prompt(report_json: Dict[str, object]) -> str:
    """Create a prompt that guides the LLM to narrate the risk report."""

    components = report_json.get("components", [])
    rules = report_json.get("rules", [])
    survival = report_json.get("survival_probability", 0.0)
    metadata = report_json.get("metadata", {})
    component_lines = "\n".join(
        f"- {component['name']}: score={component['score']} context={component['description']}"
        for component in components
    )
    rule_lines = "\n".join(
        f"- {rule['name']} => triggered={rule.get('triggered')} rationale={rule.get('description', '')}"
        for rule in rules
    )
    metadata_line = json.dumps(metadata) if metadata else "{}"
    structured = json.dumps(report_json, indent=2, sort_keys=True)

    prompt = dedent(
        f"""
        You are a senior financial risk analyst. Using the structured risk metrics, rules, and metadata
        supplied below, write a concise executive briefing that covers:
        1. Overall financial resilience and survival probability ({survival:.1f}%).
        2. The top drivers of risk taken from the component list.
        3. Any policy or rules violations plus recommended follow-up questions.

        Company metadata: {metadata_line}
        Risk components:\n{component_lines or '- None provided'}
        Rule evaluations:\n{rule_lines or '- No rules evaluated'}

        Respond with 2-3 paragraphs plus a final bullet list of actionable next steps (max 3 bullets).
        Reference the numeric inputs directly where relevant and avoid inventing data not present in the JSON.

        Full JSON payload for reference:
        {structured}
        """
    ).strip()
    return prompt


def explain_risk(report_json: Dict[str, object], provider: LLMProvider | None = None) -> str:
    """Convert structured risk data into an explanation provided by the LLM provider."""

    prompt = _build_prompt(report_json)
    active_provider: LLMProvider | None = provider
    if active_provider is None:
        try:
            active_provider = AnthropicExplainer()
        except RuntimeError:
            active_provider = None

    if active_provider is None:
        return _fallback_summary(report_json)
    return active_provider.explain(prompt)


__all__ = ["LLMProvider", "AnthropicExplainer", "explain_risk"]

