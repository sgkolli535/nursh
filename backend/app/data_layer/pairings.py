"""
Nutrient pairing logic.
Detects beneficial and inhibiting nutrient pairings in meals.
Deterministic — based on published nutrition science.
"""


# Beneficial pairings: consuming these together enhances absorption
BENEFICIAL_PAIRINGS = [
    {
        "nutrient_a": "iron",
        "nutrient_b": "vitamin_c",
        "effect": "enhanced_absorption",
        "rule_key": "pairing_iron_vitamin_c",
        "food_groups_a": ["iron_rich_proteins", "dark_leafy_greens", "legumes_pulses"],
        "food_groups_b": ["citrus_berries"],
        "message_template": "Great combination — the {food_b} helps your body absorb more iron from the {food_a}.",
    },
    {
        "nutrient_a": "turmeric",
        "nutrient_b": "black_pepper",
        "effect": "enhanced_absorption",
        "rule_key": "pcos_anti_inflammatory",
        "food_groups_a": ["herbs_spices"],
        "food_groups_b": ["herbs_spices"],
        "message_template": "Nice pairing — black pepper enhances your body's ability to use the curcumin in turmeric.",
    },
    {
        "nutrient_a": "vitamin_d",
        "nutrient_b": "calcium",
        "effect": "enhanced_absorption",
        "rule_key": "perimenopause_phytoestrogen",
        "food_groups_a": ["omega3_sources"],  # Fatty fish = vitamin D
        "food_groups_b": ["calcium_sources"],
        "message_template": "Good combination — vitamin D helps your body absorb calcium more effectively.",
    },
]

# Inhibiting pairings: consuming these together reduces absorption
INHIBITOR_PAIRINGS = [
    {
        "nutrient_a": "iron",
        "nutrient_b": "calcium",
        "effect": "inhibited_absorption",
        "rule_key": "pairing_calcium_iron_inhibitor",
        "food_groups_a": ["iron_rich_proteins", "dark_leafy_greens", "legumes_pulses"],
        "food_groups_b": ["calcium_sources"],
        "message_template": "Tip: spacing out your {food_a} and {food_b} across different meals helps both nutrients work better.",
    },
    {
        "nutrient_a": "iron",
        "nutrient_b": "tannins",
        "effect": "inhibited_absorption",
        "rule_key": "pairing_tannin_iron_inhibitor",
        "food_groups_a": ["iron_rich_proteins", "dark_leafy_greens", "legumes_pulses"],
        "food_groups_b": [],  # Tea/coffee not in food groups
        "message_template": "Tip: waiting about an hour before or after your {food_a} to have tea or coffee helps with iron absorption.",
    },
]


def detect_pairings_in_meal(
    food_group_slugs: list[str],
) -> list[dict]:
    """Detect beneficial and inhibiting nutrient pairings in a single meal.

    Args:
        food_group_slugs: List of food group slugs present in the meal.

    Returns:
        List of detected pairing dicts with type, rule_key, and message_template.
    """
    detected = []
    slug_set = set(food_group_slugs)

    for pairing in BENEFICIAL_PAIRINGS:
        has_a = bool(slug_set & set(pairing["food_groups_a"]))
        has_b = bool(slug_set & set(pairing["food_groups_b"]))
        if has_a and has_b:
            detected.append({
                "type": "beneficial",
                "rule_key": pairing["rule_key"],
                "effect": pairing["effect"],
                "message_template": pairing["message_template"],
                "nutrients": (pairing["nutrient_a"], pairing["nutrient_b"]),
            })

    for pairing in INHIBITOR_PAIRINGS:
        has_a = bool(slug_set & set(pairing["food_groups_a"]))
        has_b = bool(slug_set & set(pairing["food_groups_b"]))
        if has_a and has_b:
            detected.append({
                "type": "inhibitor",
                "rule_key": pairing["rule_key"],
                "effect": pairing["effect"],
                "message_template": pairing["message_template"],
                "nutrients": (pairing["nutrient_a"], pairing["nutrient_b"]),
            })

    return detected
