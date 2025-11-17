"""LLM explainer stub."""
from __future__ import annotations

import json
from typing import Dict


def explain_risk(report_json: Dict[str, object]) -> str:
    """Convert structured risk data into a deterministic explanation string."""

    components = report_json.get("components", [])
    parts = ["AI Risk Narrative:"]
    for component in components:
        parts.append(f"- {component['name']}: score {component['score']:.1f} ({component['description']})")
    survival = report_json.get("survival_probability", 0.0)
    parts.append(f"Survival probability over next 12 months estimated at {survival:.1f}%." )
    rules = report_json.get("rules", [])
    triggered = [rule for rule in rules if rule.get("triggered")]
    if triggered:
        parts.append("Rules triggered: " + ", ".join(rule["name"] for rule in triggered))
    else:
        parts.append("No deterministic rule breaches detected.")
    parts.append("Raw payload: " + json.dumps(report_json, sort_keys=True)[:400])
    return "\n".join(parts)
