"""
Seed data for the 13 food group categories.
Defined in Nursh Product Spec v1.0 Section 5.2.
"""

FOOD_GROUPS = [
    {
        "name": "Dark Leafy Greens",
        "slug": "dark_leafy_greens",
        "key_nutrients": ["iron", "folate", "calcium", "vitamin_k"],
        "color_hex": "#8FA68B",
        "icon_name": "leaf",
    },
    {
        "name": "Orange/Red Vegetables",
        "slug": "orange_red_vegetables",
        "key_nutrients": ["vitamin_a", "beta_carotene", "vitamin_c"],
        "color_hex": "#C17C5E",
        "icon_name": "carrot",
    },
    {
        "name": "Cruciferous Vegetables",
        "slug": "cruciferous",
        "key_nutrients": ["sulforaphane", "vitamin_c", "fiber"],
        "color_hex": "#8FA68B",
        "icon_name": "broccoli",
    },
    {
        "name": "Alliums",
        "slug": "alliums",
        "key_nutrients": ["prebiotic_fiber", "quercetin", "sulfur_compounds"],
        "color_hex": "#D4B896",
        "icon_name": "garlic",
    },
    {
        "name": "Citrus & Berries",
        "slug": "citrus_berries",
        "key_nutrients": ["vitamin_c", "anthocyanins", "flavonoids"],
        "color_hex": "#D4A054",
        "icon_name": "orange",
    },
    {
        "name": "Legumes & Pulses",
        "slug": "legumes_pulses",
        "key_nutrients": ["protein", "iron", "zinc", "b_vitamins", "fiber"],
        "color_hex": "#A0674B",
        "icon_name": "pod",
    },
    {
        "name": "Whole Grains",
        "slug": "whole_grains",
        "key_nutrients": ["b_vitamins", "magnesium", "selenium", "fiber"],
        "color_hex": "#C9A87C",
        "icon_name": "wheat",
    },
    {
        "name": "Nuts & Seeds",
        "slug": "nuts_seeds",
        "key_nutrients": ["vitamin_e", "magnesium", "omega_3", "zinc"],
        "color_hex": "#6B4226",
        "icon_name": "almond",
    },
    {
        "name": "Fermented Foods",
        "slug": "fermented_foods",
        "key_nutrients": ["probiotics", "b12", "bioavailable_minerals"],
        "color_hex": "#D4A69A",
        "icon_name": "jar",
    },
    {
        "name": "Omega-3 Sources",
        "slug": "omega3_sources",
        "key_nutrients": ["epa", "dha", "ala"],
        "color_hex": "#8B7355",
        "icon_name": "fish",
    },
    {
        "name": "Iron-Rich Proteins",
        "slug": "iron_rich_proteins",
        "key_nutrients": ["heme_iron", "b12", "zinc"],
        "color_hex": "#C17C5E",
        "icon_name": "drumstick",
    },
    {
        "name": "Calcium Sources",
        "slug": "calcium_sources",
        "key_nutrients": ["calcium", "vitamin_d"],
        "color_hex": "#E8D5C4",
        "icon_name": "milk",
    },
    {
        "name": "Herbs & Spices",
        "slug": "herbs_spices",
        "key_nutrients": ["antioxidants", "anti_inflammatory_compounds"],
        "color_hex": "#A0674B",
        "icon_name": "mortar",
    },
]
