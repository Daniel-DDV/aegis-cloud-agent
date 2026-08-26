"""Deterministic scorers for EU AI Act signals found in target corpora."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .articles import (
    ANNEX_III_SIGNALS,
    ARTICLES,
    PROHIBITED_SIGNALS,
    RiskTier,
)
