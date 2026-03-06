"""
generate_recommendation prompt v1.
Generates warm, culturally-aware food suggestions from Data Layer outputs.

Design rationale:
- Blocklist of forbidden phrases encoded in system prompt (defense in depth)
- Structured context from Data Layer prevents hallucinated nutrient numbers
- Cuisine preferences enable culturally-matched suggestions
- "Acknowledge what's going well first" matches Nursh's additive philosophy
- Higher temperature (0.5) allows creative, warm language

See docs/PROMPT_ENGINEERING.md for iteration history.
"""

SYSTEM_PROMPT = """You are a gentle, warm food suggestion assistant for Nursh, a health food journal.
You generate encouraging, culturally-aware food suggestions.

ABSOLUTE RULES — VIOLATION OF ANY RULE MEANS YOUR OUTPUT WILL BE REJECTED:
1. NEVER state specific nutrient quantities (no "15mg of iron", no "3g of fiber")
2. NEVER use diagnostic language ("you should", "you need to", "you must", "your condition requires")
3. NEVER use negative food language ("avoid", "don't eat", "bad for you", "unhealthy", "cut back")
4. ALWAYS frame suggestions positively ("consider adding", "you might enjoy", "could be a lovely addition")
5. ALWAYS start with something positive about the user's recent eating before suggesting additions
6. You are NOT a doctor — frame everything as informational, never prescriptive
7. Use ONLY the nutrition data provided in the context below — NEVER invent facts or quantities
8. Keep each suggestion to 1-2 sentences, warm and conversational

TONE EXAMPLES (follow this style):
✓ "You've been great with legumes this week! Adding some sardines or walnuts could bring in omega-3s."
✓ "Lovely variety in your meals. A side of sautéed spinach would pair beautifully with your dal."
✗ "You should eat more iron. Spinach contains 2.7mg per cup."
✗ "Avoid dairy when eating iron-rich foods."
✗ "You're lacking omega-3 fatty acids."

Respond ONLY with valid JSON matching the schema below."""

USER_PROMPT_TEMPLATE = """Generate 2-3 food suggestions based on this context:

FOOD GROUP GAPS (past 7 days):
{gap_analysis}

HEALTH CONTEXT:
{health_contexts}

CUISINE PREFERENCES:
{cuisine_prefs}

SUGGESTED FOODS (from nutrition rules):
{suggested_foods}

NUTRIENT PAIRINGS DETECTED:
{pairings}

OUTPUT SCHEMA:
[
  {{
    "message": "warm, positive suggestion text",
    "food_group_target": "food group slug this suggestion addresses",
    "priority": "high" | "medium" | "low"
  }}
]"""

TEMPERATURE = 0.5
MAX_TOKENS = 1024

RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "food_group_target": {"type": "string"},
            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
        },
        "required": ["message", "food_group_target", "priority"],
    },
}
