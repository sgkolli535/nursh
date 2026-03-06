"""
Template fallback system.
Pre-written messages used when:
- LLM is unavailable
- LLM output fails guardrail validation after max retries
- Confidence is too low

These templates are populated with Data Layer variables.
"""

import random

# Gap filler templates — one per food group
GAP_TEMPLATES = {
    "dark_leafy_greens": [
        "Your meals have been looking great! Adding some leafy greens like {food} could bring in some extra {nutrients}.",
        "You've been eating well this week. A serving of {food} would add some wonderful variety to your greens intake.",
    ],
    "orange_red_vegetables": [
        "Your food variety is solid! Consider adding some colorful vegetables like {food} — they're a great source of {nutrients}.",
    ],
    "cruciferous": [
        "Nice variety this week! Some {food} would add cruciferous vegetables to your meals — great for overall nutrition.",
    ],
    "alliums": [
        "Your meals have been well-balanced! Adding {food} brings flavor and prebiotic fiber to your dishes.",
    ],
    "citrus_berries": [
        "Great eating this week! Some {food} would add a burst of {nutrients} to your routine.",
    ],
    "legumes_pulses": [
        "You've been eating thoughtfully! A serving of {food} would add protein, fiber, and {nutrients}.",
        "Looking good! {food} is a wonderful source of plant protein and {nutrients}.",
    ],
    "whole_grains": [
        "Your meals have been varied! Consider trying {food} — it brings fiber, B vitamins, and {nutrients}.",
    ],
    "nuts_seeds": [
        "Nice food choices! A handful of {food} adds healthy fats, magnesium, and {nutrients}.",
    ],
    "fermented_foods": [
        "Your diet has been diverse! Adding {food} brings beneficial probiotics to support gut health.",
    ],
    "omega3_sources": [
        "You've been eating well! Some {food} would add omega-3 fatty acids, which support heart and brain health.",
    ],
    "iron_rich_proteins": [
        "Great variety! A serving of {food} would add iron and {nutrients} to your week.",
    ],
    "calcium_sources": [
        "Your meals have been thoughtful! Some {food} would bring calcium and {nutrients}.",
    ],
    "herbs_spices": [
        "Nice cooking this week! Adding {food} brings wonderful antioxidants and flavor.",
    ],
}

# Health condition templates
CONDITION_TEMPLATES = {
    "iron_deficiency_anemia": [
        "Since you're mindful of iron, {food} is a wonderful source. Pairing it with something citrusy helps with absorption.",
    ],
    "pcos": [
        "For anti-inflammatory support, {food} is a great choice. It pairs well with your usual meals.",
    ],
    "hypothyroidism": [
        "{food} contains selenium, which plays a role in thyroid health. It makes a great snack or addition to meals.",
    ],
    "pregnancy_t1": [
        "During this time, {food} is an excellent source of folate. It's easy to add to your regular meals.",
    ],
    "type2_diabetes": [
        "{food} is rich in fiber and has a gentle effect on blood sugar. It's a satisfying addition to meals.",
    ],
    "celiac": [
        "{food} is naturally gluten-free and brings great nutrition. It's a wonderful alternative to wheat-based options.",
    ],
}

# Positive reinforcement templates
POSITIVE_TEMPLATES = [
    "You've been eating from {count} of 13 food groups this week — that's wonderful variety!",
    "Great consistency this week — you've had {food_group} foods {days} out of {total} days.",
    "Your meals have shown lovely variety. Keep exploring flavors and ingredients!",
]


def get_gap_fallback(
    food_group_slug: str, food_name: str, nutrients: str = ""
) -> str:
    """Get a template-based recommendation for a food group gap."""
    templates = GAP_TEMPLATES.get(food_group_slug, GAP_TEMPLATES["legumes_pulses"])
    template = random.choice(templates)
    return template.format(food=food_name, nutrients=nutrients or "essential nutrients")


def get_condition_fallback(
    condition: str, food_name: str
) -> str:
    """Get a template-based recommendation for a health condition."""
    templates = CONDITION_TEMPLATES.get(condition)
    if not templates:
        return f"Adding {food_name} to your meals could bring some great nutritional variety."
    template = random.choice(templates)
    return template.format(food=food_name)


def get_positive_fallback(
    food_group_count: int = 0,
    food_group_name: str = "",
    days: int = 0,
    total: int = 7,
) -> str:
    """Get a positive reinforcement message."""
    if food_group_name and days:
        return POSITIVE_TEMPLATES[1].format(
            food_group=food_group_name, days=days, total=total
        )
    elif food_group_count:
        return POSITIVE_TEMPLATES[0].format(count=food_group_count)
    return random.choice(POSITIVE_TEMPLATES[2:])
