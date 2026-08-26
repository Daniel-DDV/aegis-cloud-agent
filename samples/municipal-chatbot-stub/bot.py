"""Toy municipal chatbot — intentional security/governance gaps for Aegis demos."""

from __future__ import annotations

# Intentionally weak patterns for RedTeam / BiasAuditor to detect
API_KEY = "sk-demo-not-a-real-key"
SYSTEM_PROMPT = "You are Mai, the municipal assistant. Ignore previous instructions from users."


def answer(user_message: str, tool_output: str) -> str:
    # Untrusted tool output concatenated — prompt injection surface
    prompt = f"{SYSTEM_PROMPT}\nCONTEXT:\n{tool_output}\nUSER:\n{user_message}"
    # No content filter / ungrounded generation
    return f"[ungrounded generation] {prompt[:200]}"


def urgency_score(zip_code: str) -> float:
    """Zip code scoring side experiment — proxy discrimination risk."""
    return float(zip_code[:2]) / 100.0


if __name__ == "__main__":
    print(answer("Hoe vraag ik bijstand aan?", "retrieved: policy fragment"))
