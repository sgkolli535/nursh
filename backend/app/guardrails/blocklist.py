"""
Blocklist patterns for LLM output validation.
Defense in depth: these patterns are ALSO in system prompts,
but regex validation catches anything that slips through.
"""

import re

# Diagnostic / prescriptive language (never appropriate for a food journal)
DIAGNOSTIC_PATTERNS = [
    r"\b(you should|you need to|you must|your condition requires)\b",
    r"\b(you have to|it is essential that you|make sure you)\b",
    r"\b(consult your doctor about|see a specialist for)\b",
]

# Negative food language (contradicts Nursh's additive philosophy)
NEGATIVE_FOOD_PATTERNS = [
    r"\b(avoid|don't eat|do not eat|stop eating|never eat)\b",
    r"\b(bad for you|unhealthy|dangerous|harmful|toxic)\b",
    r"\b(you're lacking|you're deficient|you're missing)\b",
    r"\b(too much|excessive|overeat|cut back on|reduce your)\b",
]

# Medical language (Nursh is not a medical provider)
MEDICAL_PATTERNS = [
    r"\b(treat|cure|diagnose|prescription|medication|supplement)\b",
    r"\b(disease|disorder|syndrome|pathology|clinical)\b",
    r"\b(symptoms|therapy|treatment plan|medical advice)\b",
]

# Invented nutrient quantities (AI must never state specific amounts)
NUTRIENT_QUANTITY_PATTERNS = [
    r"\b\d+\.?\d*\s*(mg|mcg|ug|µg|IU)\b",  # "15mg", "400mcg"
    r"\b\d+\.?\d*\s*(grams?|g)\s+of\s+\w+\b",  # "3g of iron"
    r"\b\d+\.?\d*\s*%\s*(daily value|DV|RDA)\b",  # "20% DV"
    r"\bcontains?\s+\d+\.?\d*\s*(mg|mcg|g)\b",  # "contains 2.7mg"
    r"\bprovides?\s+\d+\.?\d*\s*(mg|mcg|g)\b",  # "provides 15mg"
]

ALL_BLOCKLIST = (
    DIAGNOSTIC_PATTERNS
    + NEGATIVE_FOOD_PATTERNS
    + MEDICAL_PATTERNS
    + NUTRIENT_QUANTITY_PATTERNS
)

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in ALL_BLOCKLIST]


def check_blocklist(text: str) -> list[str]:
    """Check text against all blocklist patterns.

    Returns list of matched pattern descriptions. Empty list = safe.
    """
    violations = []
    for pattern, raw in zip(_compiled_patterns, ALL_BLOCKLIST):
        match = pattern.search(text)
        if match:
            violations.append(f"Matched '{match.group()}' (pattern: {raw})")
    return violations
