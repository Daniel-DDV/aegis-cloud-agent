"""EU AI Act article references used by Aegis agents.

These are curated excerpts for demonstration and evaluation.
They are not a substitute for the Official Journal text or legal advice.
"""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


class RiskTier(str, Enum):
    PROHIBITED = "prohibited"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    UNCLASSIFIED = "unclassified"


class ArticleRef(TypedDict):
    id: str
    title: str
    summary: str
    relevance: list[str]


ARTICLES: dict[str, ArticleRef] = {
    "art5": {
        "id": "Article 5",
        "title": "Prohibited AI practices",
        "summary": (
            "Bans subliminal manipulation, social scoring by public authorities, "
            "untargeted facial scraping, emotion recognition in workplaces/education "
            "(with exceptions), and biometric categorisation for sensitive attributes."
        ),
        "relevance": ["prohibited", "biometric", "social_scoring", "emotion"],
    },
    "art6": {
        "id": "Article 6",
        "title": "Classification rules for high-risk AI systems",
        "summary": (
            "Defines when an AI system is high-risk, including Annex III use cases "
            "(biometrics, critical infrastructure, education, employment, essential "
            "public services, law enforcement, migration, justice)."
        ),
        "relevance": ["high_risk", "annex_iii", "public_services", "employment"],
    },
    "art9": {
        "id": "Article 9",
        "title": "Risk management system",
        "summary": (
            "High-risk systems require a continuous risk management system covering "
            "identification, estimation, evaluation, and mitigation of risks."
        ),
        "relevance": ["risk_management", "high_risk", "mitigation"],
    },
    "art10": {
        "id": "Article 10",
        "title": "Data and data governance",
        "summary": (
            "Training, validation and testing data for high-risk systems must meet "
            "quality criteria, including relevance, representativeness, and bias examination."
        ),
        "relevance": ["data_governance", "bias", "training_data"],
    },
    "art11": {
        "id": "Article 11",
        "title": "Technical documentation",
        "summary": (
            "Providers must draw up technical documentation demonstrating compliance "
            "(Annex IV elements: system description, design, data, metrics, oversight)."
        ),
        "relevance": ["documentation", "annex_iv", "conformity"],
    },
    "art13": {
        "id": "Article 13",
        "title": "Transparency and provision of information to deployers",
        "summary": (
            "High-risk systems must be designed for transparency so deployers can "
            "interpret outputs and use the system appropriately."
        ),
        "relevance": ["transparency", "instructions", "deployer"],
    },
    "art14": {
        "id": "Article 14",
        "title": "Human oversight",
        "summary": (
            "High-risk systems must be designed so natural persons can oversee them, "
            "including ability to intervene, interrupt, or decide not to use the system."
        ),
        "relevance": ["human_oversight", "kill_switch", "intervention"],
    },
    "art15": {
        "id": "Article 15",
        "title": "Accuracy, robustness and cybersecurity",
        "summary": (
            "High-risk systems must achieve appropriate levels of accuracy, robustness "
            "and cybersecurity, and be resilient against attempts to alter use or performance."
        ),
        "relevance": ["robustness", "cybersecurity", "accuracy", "red_team"],
    },
    "art50": {
        "id": "Article 50",
        "title": "Transparency obligations for providers and deployers",
        "summary": (
            "Certain AI systems (e.g. interacting with humans, generating synthetic "
            "content) must disclose that users are interacting with AI or that content is AI-generated."
        ),
        "relevance": ["limited_risk", "chatbot", "deepfake", "disclosure"],
    },
    "art52_legacy": {
        "id": "Article 52 (legacy numbering in some guides)",
        "title": "Transparency for certain AI systems",
        "summary": (
            "Pre-final numbering often referenced transparency for chatbots and emotion "
            "recognition; mapped to Article 50 in the final AI Act text."
        ),
        "relevance": ["transparency", "chatbot", "limited_risk"],
    },
}

# Annex III high-risk signal keywords (simplified for demo/evals)
ANNEX_III_SIGNALS: dict[str, list[str]] = {
    "biometrics": ["facial recognition", "biometric", "face match", "fingerprint", "iris"],
    "critical_infrastructure": ["scada", "grid", "water treatment", "traffic control"],
    "education": ["student assessment", "exam scoring", "admission ranking"],
    "employment": ["cv screening", "hiring score", "employee monitoring", "recruitment"],
    "essential_services": [
        "social benefits",
        "welfare eligibility",
        "credit scoring",
        "public service chatbot",
        "municipal chatbot",
        "citizen portal",
    ],
    "law_enforcement": ["predictive policing", "risk assessment offender", "crime prediction"],
    "migration": ["asylum", "border control", "visa application scoring"],
    "justice": ["judicial decision", "case outcome prediction", "sentencing"],
}

PROHIBITED_SIGNALS: list[str] = [
    "social scoring",
    "citizen score",
    "untargeted facial scraping",
    "emotion recognition workplace",
    "subliminal manipulation",
    "real-time remote biometric identification public",
]
