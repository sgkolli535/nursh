"""
Health context rule engine.
Deterministic rules that adjust recommendations based on health conditions.
Every rule links to evidence citations via rule_key.

IMPORTANT: These are informational guidelines, not medical advice.
All rules are authored by referencing published nutrition guidelines.
"""

from dataclasses import dataclass


@dataclass
class HealthRule:
    """A deterministic health rule that maps conditions to food guidance."""
    condition: str
    rule_key: str
    priority_food_groups: list[str]
    suggested_foods: list[str]
    beneficial_pairings: list[tuple[str, str]]  # (food/nutrient, enhancer)
    inhibitor_pairings: list[tuple[str, str]]   # (food/nutrient, inhibitor)
    notes: str


# All health rules for supported conditions
HEALTH_RULES: dict[str, list[HealthRule]] = {
    "iron_deficiency_anemia": [
        HealthRule(
            condition="iron_deficiency_anemia",
            rule_key="anemia_heme_iron",
            priority_food_groups=["iron_rich_proteins", "dark_leafy_greens", "legumes_pulses"],
            suggested_foods=["spinach", "lentils", "red meat", "dark poultry", "tofu"],
            beneficial_pairings=[
                ("iron-rich foods", "vitamin C (lemon, tomato, bell pepper)"),
            ],
            inhibitor_pairings=[
                ("iron-rich foods", "calcium (dairy) at the same meal"),
                ("iron-rich foods", "tannins (tea, coffee) within 1 hour"),
            ],
            notes="Prioritize heme iron sources for higher bioavailability. Pair with vitamin C.",
        ),
    ],
    "pcos": [
        HealthRule(
            condition="pcos",
            rule_key="pcos_anti_inflammatory",
            priority_food_groups=["omega3_sources", "dark_leafy_greens", "nuts_seeds", "herbs_spices"],
            suggested_foods=["salmon", "walnuts", "turmeric", "leafy greens", "berries"],
            beneficial_pairings=[
                ("turmeric", "black pepper (piperine enhances curcumin absorption)"),
            ],
            inhibitor_pairings=[],
            notes="Emphasize anti-inflammatory foods. Magnesium and omega-3 rich options.",
        ),
        HealthRule(
            condition="pcos",
            rule_key="pcos_inositol",
            priority_food_groups=["citrus_berries", "legumes_pulses", "whole_grains"],
            suggested_foods=["oranges", "chickpeas", "buckwheat", "cantaloupe"],
            beneficial_pairings=[],
            inhibitor_pairings=[],
            notes="Inositol-rich foods may support insulin sensitivity.",
        ),
    ],
    "hypothyroidism": [
        HealthRule(
            condition="hypothyroidism",
            rule_key="hypothyroidism_selenium",
            priority_food_groups=["nuts_seeds", "omega3_sources"],
            suggested_foods=["brazil nuts", "fish", "eggs", "sunflower seeds"],
            beneficial_pairings=[],
            inhibitor_pairings=[],
            notes="Selenium supports thyroid hormone metabolism.",
        ),
        HealthRule(
            condition="hypothyroidism",
            rule_key="hypothyroidism_cruciferous",
            priority_food_groups=["cruciferous"],
            suggested_foods=["broccoli (cooked)", "cauliflower (cooked)"],
            beneficial_pairings=[],
            inhibitor_pairings=[],
            notes="Cruciferous vegetables are nutritious. Cooking reduces goitrogen content significantly.",
        ),
    ],
    "pregnancy_t1": [
        HealthRule(
            condition="pregnancy_t1",
            rule_key="pregnancy_folate",
            priority_food_groups=["dark_leafy_greens", "legumes_pulses", "citrus_berries"],
            suggested_foods=["lentils", "spinach", "asparagus", "oranges", "fortified cereals"],
            beneficial_pairings=[
                ("folate-rich foods", "vitamin C for enhanced absorption"),
            ],
            inhibitor_pairings=[],
            notes="Folate is critical for neural tube development in early pregnancy.",
        ),
        HealthRule(
            condition="pregnancy_t1",
            rule_key="pregnancy_mercury_fish",
            priority_food_groups=["omega3_sources"],
            suggested_foods=["sardines", "salmon", "walnuts", "chia seeds"],
            beneficial_pairings=[],
            inhibitor_pairings=[
                ("pregnancy", "high mercury fish (swordfish, king mackerel, tilefish)"),
            ],
            notes="Choose low-mercury fish. DHA is important for fetal brain development.",
        ),
    ],
    "pregnancy_t2": [
        HealthRule(
            condition="pregnancy_t2",
            rule_key="pregnancy_folate",
            priority_food_groups=["iron_rich_proteins", "calcium_sources", "omega3_sources"],
            suggested_foods=["lean red meat", "sardines", "dairy", "tofu", "lentils"],
            beneficial_pairings=[
                ("iron-rich foods", "vitamin C"),
            ],
            inhibitor_pairings=[],
            notes="Iron and calcium needs increase in second trimester.",
        ),
    ],
    "pregnancy_t3": [
        HealthRule(
            condition="pregnancy_t3",
            rule_key="pregnancy_folate",
            priority_food_groups=["calcium_sources", "iron_rich_proteins", "omega3_sources"],
            suggested_foods=["dairy", "sardines", "lean meat", "tofu", "fortified plant milk"],
            beneficial_pairings=[],
            inhibitor_pairings=[],
            notes="Calcium and DHA remain critical in third trimester.",
        ),
    ],
    "perimenopause": [
        HealthRule(
            condition="perimenopause",
            rule_key="perimenopause_phytoestrogen",
            priority_food_groups=["calcium_sources", "legumes_pulses", "nuts_seeds"],
            suggested_foods=["soy products", "flaxseeds", "sesame", "dairy", "fortified plant milk"],
            beneficial_pairings=[],
            inhibitor_pairings=[],
            notes="Phytoestrogens and calcium support comfort during perimenopause.",
        ),
    ],
    "type2_diabetes": [
        HealthRule(
            condition="type2_diabetes",
            rule_key="diabetes_fiber_glycemic",
            priority_food_groups=["legumes_pulses", "whole_grains", "dark_leafy_greens"],
            suggested_foods=["lentils", "chickpeas", "quinoa", "oats", "leafy greens"],
            beneficial_pairings=[
                ("carbohydrates", "fiber and protein (slows glucose absorption)"),
            ],
            inhibitor_pairings=[],
            notes="High-fiber, low-glycemic foods help maintain steady blood sugar.",
        ),
    ],
    "celiac": [
        HealthRule(
            condition="celiac",
            rule_key="celiac_gluten_free",
            priority_food_groups=["whole_grains"],
            suggested_foods=["rice", "quinoa", "millet", "buckwheat", "amaranth", "teff"],
            beneficial_pairings=[],
            inhibitor_pairings=[
                ("celiac", "wheat, barley, rye, regular roti, naan, couscous"),
            ],
            notes="Gluten-free grains are nutritious alternatives. Many cultures have naturally GF grain traditions.",
        ),
    ],
    "vegetarian": [
        HealthRule(
            condition="vegetarian",
            rule_key="anemia_heme_iron",
            priority_food_groups=["legumes_pulses", "nuts_seeds", "dark_leafy_greens"],
            suggested_foods=["lentils", "tofu", "tempeh", "pumpkin seeds", "fortified cereals"],
            beneficial_pairings=[
                ("plant iron", "vitamin C for better absorption"),
                ("incomplete proteins", "grain + legume combinations"),
            ],
            inhibitor_pairings=[],
            notes="Monitor B12, iron, zinc, omega-3. Combine plant proteins for completeness.",
        ),
    ],
    "vegan": [
        HealthRule(
            condition="vegan",
            rule_key="anemia_heme_iron",
            priority_food_groups=["legumes_pulses", "nuts_seeds", "dark_leafy_greens", "fermented_foods"],
            suggested_foods=["lentils", "tofu", "tempeh", "nutritional yeast", "fortified plant milk"],
            beneficial_pairings=[
                ("plant iron", "vitamin C"),
                ("incomplete proteins", "grain + legume combinations"),
            ],
            inhibitor_pairings=[],
            notes="B12 supplementation is essential. Monitor iron, zinc, omega-3, calcium.",
        ),
    ],
}


def get_rules_for_conditions(conditions: list[str]) -> list[HealthRule]:
    """Get all applicable health rules for a user's conditions."""
    rules = []
    for condition in conditions:
        rules.extend(HEALTH_RULES.get(condition, []))
    return rules


def get_priority_food_groups(conditions: list[str]) -> list[str]:
    """Get deduplicated priority food groups across all conditions."""
    groups = []
    seen = set()
    for rule in get_rules_for_conditions(conditions):
        for fg in rule.priority_food_groups:
            if fg not in seen:
                groups.append(fg)
                seen.add(fg)
    return groups


def get_suggested_foods(conditions: list[str]) -> list[str]:
    """Get deduplicated food suggestions across all conditions."""
    foods = []
    seen = set()
    for rule in get_rules_for_conditions(conditions):
        for food in rule.suggested_foods:
            if food not in seen:
                foods.append(food)
                seen.add(food)
    return foods


def get_inhibitors(conditions: list[str]) -> list[tuple[str, str]]:
    """Get all inhibitor pairings for a user's conditions."""
    inhibitors = []
    for rule in get_rules_for_conditions(conditions):
        inhibitors.extend(rule.inhibitor_pairings)
    return inhibitors
