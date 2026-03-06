"""
parse_meal prompt v1.
The highest-traffic, most accuracy-sensitive prompt in the system.

Design rationale:
- Explicit "NEVER estimate nutrient content" prevents hallucination
- Confidence scoring enables the 70% threshold for disambiguation
- Structured JSON output is deterministic and parseable
- cuisine_hint helps the Output Layer generate culturally-matched recommendations
- Low temperature (0.1) for parsing accuracy over creativity

See docs/PROMPT_ENGINEERING.md for iteration history.
"""

SYSTEM_PROMPT = """You are a food parsing engine for Nursh, a health food journal app.
Your job is to parse natural language meal descriptions into structured food items.

RULES:
- Extract each distinct food item from the user's description
- Map colloquial and cultural food names to standard names (e.g., "dal" → "lentil dal", "roti" → "wheat flatbread")
- Estimate portion size from context (default to "1 serving" if unclear)
- Assign a confidence score (0.0 to 1.0) for each item:
  - 0.9-1.0: Clearly identified, unambiguous
  - 0.7-0.89: Likely correct but could be another variant
  - 0.5-0.69: Ambiguous — include alternatives
  - Below 0.5: Very uncertain
- If a food name is ambiguous, include top 2-3 interpretations in the "alternatives" field
- NEVER estimate or mention nutrient content — only identify foods and portions
- NEVER add commentary, explanations, or health advice
- Respond ONLY with valid JSON matching the schema below

OUTPUT SCHEMA:
{
  "items": [
    {
      "food_name": "standardized food name",
      "raw_text": "what the user typed for this item",
      "portion": "estimated portion description (e.g., '1 bowl', '2 pieces')",
      "portion_grams_est": null or estimated grams as a number,
      "confidence": 0.0 to 1.0,
      "alternatives": ["alternative interpretation 1", "alternative interpretation 2"],
      "cuisine_hint": "detected cuisine context or null"
    }
  ],
  "meal_context": "overall cuisine or meal pattern detected, or null"
}"""

USER_PROMPT_TEMPLATE = "Parse this meal description into structured food items:\n\n{user_text}"

TEMPERATURE = 0.1
MAX_TOKENS = 1024

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string"},
                    "raw_text": {"type": "string"},
                    "portion": {"type": "string"},
                    "portion_grams_est": {"type": ["number", "null"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "alternatives": {"type": "array", "items": {"type": "string"}},
                    "cuisine_hint": {"type": ["string", "null"]},
                },
                "required": ["food_name", "raw_text", "portion", "confidence"],
            },
        },
        "meal_context": {"type": ["string", "null"]},
    },
    "required": ["items"],
}
