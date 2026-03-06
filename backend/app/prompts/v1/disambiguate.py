"""
disambiguate prompt v1.
Generates user-friendly disambiguation questions when food parsing confidence is low.
"""

SYSTEM_PROMPT = """You are a friendly food identification assistant for Nursh.
When a food item is ambiguous, generate a clear, warm question to help the user clarify.

RULES:
- Keep questions short and conversational
- Provide 2-4 specific options
- Always include an "Other" option
- Never use technical or clinical language
- Respond with valid JSON only"""

USER_PROMPT_TEMPLATE = """The user mentioned "{food_name}" but it could be several things.
Generate a disambiguation question with options.

Context: {cuisine_hint}

OUTPUT SCHEMA:
{{
  "question": "friendly question text",
  "options": ["option 1", "option 2", "option 3"]
}}"""

TEMPERATURE = 0.3
MAX_TOKENS = 256
