/**
 * Mock data for demo mode — self-contained, no backend needed.
 *
 * Persona: Priya, a South Indian woman managing PCOS + iron-deficiency anemia.
 * She's been using Nursh for a week and has logged 3 days of meals.
 */

import type {
  Food,
  FoodGroupId,
  FoodGroupSummary,
  JournalEntry,
  ParseResult,
  Recommendation,
  SimilarFood,
  UserProfile,
  WeeklyInsight,
} from "@/lib/types";

// ============ Helpers ============

const today = new Date().toISOString().slice(0, 10);
const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
const twoDaysAgo = new Date(Date.now() - 2 * 86400000).toISOString().slice(0, 10);

export const DEMO_USER_ID = "demo-user-priya";

// ============ User Profile ============

export const mockProfile: UserProfile = {
  id: DEMO_USER_ID,
  display_name: "Priya",
  health_contexts: ["pcos", "iron_deficiency_anemia"],
  dietary_preferences: ["vegetarian"],
  cuisine_preferences: ["south_indian", "north_indian"],
};

// ============ Foods Database ============

export const mockFoods: Record<string, Food> = {
  "food-idli": {
    id: "food-idli",
    name: "Idli",
    aliases: ["steamed rice cake"],
    tags: ["breakfast", "south_indian", "steamed"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-A065",
    source_url: "https://ifct2017.com/food/A065",
    verified_date: "2024-11-15",
    food_groups: ["fermented_foods", "whole_grains"],
  },
  "food-sambar": {
    id: "food-sambar",
    name: "Sambar",
    aliases: ["lentil vegetable stew"],
    tags: ["south_indian", "stew", "comfort"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-C012",
    source_url: "https://ifct2017.com/food/C012",
    verified_date: "2024-11-15",
    food_groups: ["legumes_pulses", "alliums", "herbs_spices"],
  },
  "food-coconut-chutney": {
    id: "food-coconut-chutney",
    name: "Coconut Chutney",
    aliases: ["thengai chutney"],
    tags: ["south_indian", "condiment"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-D034",
    source_url: "https://ifct2017.com/food/D034",
    verified_date: "2024-11-15",
    food_groups: ["nuts_seeds", "herbs_spices"],
  },
  "food-dal": {
    id: "food-dal",
    name: "Toor Dal",
    aliases: ["arhar dal", "pigeon pea dal"],
    tags: ["staple", "protein", "comfort"],
    cuisine_region: "Indian",
    source: "IFCT 2017",
    source_id: "IFCT-B001",
    source_url: "https://ifct2017.com/food/B001",
    verified_date: "2024-11-15",
    food_groups: ["legumes_pulses", "iron_rich_proteins"],
  },
  "food-rice": {
    id: "food-rice",
    name: "Steamed Rice",
    aliases: ["white rice", "chawal"],
    tags: ["staple", "grain"],
    cuisine_region: "Global",
    source: "USDA FoodData Central",
    source_id: "FDC-169756",
    source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/169756",
    verified_date: "2024-10-01",
    food_groups: ["whole_grains"],
  },
  "food-raita": {
    id: "food-raita",
    name: "Cucumber Raita",
    aliases: ["raitha", "yogurt salad"],
    tags: ["condiment", "cooling", "probiotic"],
    cuisine_region: "Indian",
    source: "IFCT 2017",
    source_id: "IFCT-D045",
    source_url: "https://ifct2017.com/food/D045",
    verified_date: "2024-11-15",
    food_groups: ["fermented_foods", "calcium_sources"],
  },
  "food-dosa": {
    id: "food-dosa",
    name: "Masala Dosa",
    aliases: ["crispy crepe with potato"],
    tags: ["south_indian", "breakfast", "crispy"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-A070",
    source_url: "https://ifct2017.com/food/A070",
    verified_date: "2024-11-15",
    food_groups: ["fermented_foods", "whole_grains", "alliums"],
  },
  "food-spinach-dal": {
    id: "food-spinach-dal",
    name: "Palak Dal",
    aliases: ["spinach lentil curry"],
    tags: ["north_indian", "iron_rich", "comfort"],
    cuisine_region: "North Indian",
    source: "IFCT 2017",
    source_id: "IFCT-C030",
    source_url: "https://ifct2017.com/food/C030",
    verified_date: "2024-11-15",
    food_groups: ["dark_leafy_greens", "legumes_pulses", "iron_rich_proteins"],
  },
  "food-curd-rice": {
    id: "food-curd-rice",
    name: "Curd Rice",
    aliases: ["thayir sadam", "yogurt rice"],
    tags: ["south_indian", "comfort", "cooling"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-A080",
    source_url: "https://ifct2017.com/food/A080",
    verified_date: "2024-11-15",
    food_groups: ["fermented_foods", "calcium_sources", "whole_grains"],
  },
  "food-ragi-porridge": {
    id: "food-ragi-porridge",
    name: "Ragi Porridge",
    aliases: ["finger millet porridge", "ragi kanji"],
    tags: ["south_indian", "breakfast", "iron_rich"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-A015",
    source_url: "https://ifct2017.com/food/A015",
    verified_date: "2024-11-15",
    food_groups: ["whole_grains", "calcium_sources", "iron_rich_proteins"],
  },
  "food-amla": {
    id: "food-amla",
    name: "Amla (Indian Gooseberry)",
    aliases: ["nellikai", "amalaki"],
    tags: ["fruit", "vitamin_c", "traditional"],
    cuisine_region: "Indian",
    source: "IFCT 2017",
    source_id: "IFCT-F020",
    source_url: "https://ifct2017.com/food/F020",
    verified_date: "2024-11-15",
    food_groups: ["citrus_berries"],
  },
  "food-moringa": {
    id: "food-moringa",
    name: "Drumstick Leaves (Moringa)",
    aliases: ["murungai keerai", "moringa oleifera"],
    tags: ["south_indian", "superfood", "iron_rich"],
    cuisine_region: "South Indian",
    source: "IFCT 2017",
    source_id: "IFCT-G010",
    source_url: "https://ifct2017.com/food/G010",
    verified_date: "2024-11-15",
    food_groups: ["dark_leafy_greens", "iron_rich_proteins", "calcium_sources"],
  },
  // Cross-cultural similar foods
  "food-tempeh": {
    id: "food-tempeh",
    name: "Tempeh",
    aliases: ["fermented soybean cake"],
    tags: ["indonesian", "fermented", "protein"],
    cuisine_region: "Indonesian",
    source: "USDA FoodData Central",
    source_id: "FDC-174272",
    source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/174272",
    verified_date: "2024-10-01",
    food_groups: ["legumes_pulses", "fermented_foods", "iron_rich_proteins"],
  },
  "food-black-beans": {
    id: "food-black-beans",
    name: "Black Beans",
    aliases: ["frijoles negros"],
    tags: ["mexican", "latin_american", "protein"],
    cuisine_region: "Latin American",
    source: "USDA FoodData Central",
    source_id: "FDC-173735",
    source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/173735",
    verified_date: "2024-10-01",
    food_groups: ["legumes_pulses", "iron_rich_proteins"],
  },
  "food-hummus": {
    id: "food-hummus",
    name: "Hummus",
    aliases: ["chickpea dip"],
    tags: ["middle_eastern", "dip", "protein"],
    cuisine_region: "Middle Eastern",
    source: "USDA FoodData Central",
    source_id: "FDC-172421",
    source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/172421",
    verified_date: "2024-10-01",
    food_groups: ["legumes_pulses", "nuts_seeds"],
  },
  "food-miso": {
    id: "food-miso",
    name: "Miso Paste",
    aliases: ["fermented soybean paste"],
    tags: ["japanese", "fermented", "umami"],
    cuisine_region: "Japanese",
    source: "USDA FoodData Central",
    source_id: "FDC-172442",
    source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/172442",
    verified_date: "2024-10-01",
    food_groups: ["fermented_foods", "legumes_pulses"],
  },
  "food-kimchi": {
    id: "food-kimchi",
    name: "Kimchi",
    aliases: ["fermented cabbage"],
    tags: ["korean", "fermented", "probiotic"],
    cuisine_region: "Korean",
    source: "USDA FoodData Central",
    source_id: "FDC-325871",
    source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/325871",
    verified_date: "2024-10-01",
    food_groups: ["fermented_foods", "cruciferous"],
  },
};

// ============ Journal Entries ============

export const mockJournalEntries: JournalEntry[] = [
  // --- Today ---
  {
    id: "entry-today-breakfast",
    user_id: DEMO_USER_ID,
    date: today,
    meal_type: "breakfast",
    items: [
      {
        id: "item-1",
        food_id: "food-idli",
        food_name_raw: "idli",
        portion_description: "3 pieces",
        portion_grams_est: 120,
        confidence_score: 0.95,
        food_groups: ["fermented_foods", "whole_grains"],
      },
      {
        id: "item-2",
        food_id: "food-sambar",
        food_name_raw: "sambar",
        portion_description: "1 bowl",
        portion_grams_est: 200,
        confidence_score: 0.92,
        food_groups: ["legumes_pulses", "alliums", "herbs_spices"],
      },
      {
        id: "item-3",
        food_id: "food-coconut-chutney",
        food_name_raw: "coconut chutney",
        portion_description: "2 tbsp",
        portion_grams_est: 30,
        confidence_score: 0.88,
        food_groups: ["nuts_seeds", "herbs_spices"],
      },
    ],
    created_at: new Date(new Date().setHours(8, 30)).toISOString(),
  },
  {
    id: "entry-today-lunch",
    user_id: DEMO_USER_ID,
    date: today,
    meal_type: "lunch",
    items: [
      {
        id: "item-4",
        food_id: "food-dal",
        food_name_raw: "dal",
        portion_description: "1 bowl",
        portion_grams_est: 200,
        confidence_score: 0.90,
        food_groups: ["legumes_pulses", "iron_rich_proteins"],
      },
      {
        id: "item-5",
        food_id: "food-rice",
        food_name_raw: "rice",
        portion_description: "1 cup",
        portion_grams_est: 180,
        confidence_score: 0.97,
        food_groups: ["whole_grains"],
      },
      {
        id: "item-6",
        food_id: "food-raita",
        food_name_raw: "raita",
        portion_description: "1 small bowl",
        portion_grams_est: 100,
        confidence_score: 0.85,
        food_groups: ["fermented_foods", "calcium_sources"],
      },
    ],
    created_at: new Date(new Date().setHours(13, 0)).toISOString(),
  },

  // --- Yesterday ---
  {
    id: "entry-yesterday-breakfast",
    user_id: DEMO_USER_ID,
    date: yesterday,
    meal_type: "breakfast",
    items: [
      {
        id: "item-7",
        food_id: "food-dosa",
        food_name_raw: "masala dosa",
        portion_description: "1 large",
        portion_grams_est: 150,
        confidence_score: 0.93,
        food_groups: ["fermented_foods", "whole_grains", "alliums"],
      },
      {
        id: "item-8",
        food_id: "food-coconut-chutney",
        food_name_raw: "coconut chutney",
        portion_description: "2 tbsp",
        portion_grams_est: 30,
        confidence_score: 0.88,
        food_groups: ["nuts_seeds", "herbs_spices"],
      },
    ],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "entry-yesterday-lunch",
    user_id: DEMO_USER_ID,
    date: yesterday,
    meal_type: "lunch",
    items: [
      {
        id: "item-9",
        food_id: "food-spinach-dal",
        food_name_raw: "palak dal",
        portion_description: "1 bowl",
        portion_grams_est: 220,
        confidence_score: 0.91,
        food_groups: ["dark_leafy_greens", "legumes_pulses", "iron_rich_proteins"],
      },
      {
        id: "item-10",
        food_id: "food-rice",
        food_name_raw: "steamed rice",
        portion_description: "1 cup",
        portion_grams_est: 180,
        confidence_score: 0.97,
        food_groups: ["whole_grains"],
      },
    ],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: "entry-yesterday-dinner",
    user_id: DEMO_USER_ID,
    date: yesterday,
    meal_type: "dinner",
    items: [
      {
        id: "item-11",
        food_id: "food-curd-rice",
        food_name_raw: "curd rice",
        portion_description: "1 plate",
        portion_grams_est: 250,
        confidence_score: 0.94,
        food_groups: ["fermented_foods", "calcium_sources", "whole_grains"],
      },
    ],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },

  // --- Two days ago ---
  {
    id: "entry-2daysago-breakfast",
    user_id: DEMO_USER_ID,
    date: twoDaysAgo,
    meal_type: "breakfast",
    items: [
      {
        id: "item-12",
        food_id: "food-ragi-porridge",
        food_name_raw: "ragi porridge with jaggery",
        portion_description: "1 bowl",
        portion_grams_est: 250,
        confidence_score: 0.89,
        food_groups: ["whole_grains", "calcium_sources", "iron_rich_proteins"],
      },
    ],
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
  {
    id: "entry-2daysago-lunch",
    user_id: DEMO_USER_ID,
    date: twoDaysAgo,
    meal_type: "lunch",
    items: [
      {
        id: "item-13",
        food_id: "food-sambar",
        food_name_raw: "sambar",
        portion_description: "1 bowl",
        portion_grams_est: 200,
        confidence_score: 0.92,
        food_groups: ["legumes_pulses", "alliums", "herbs_spices"],
      },
      {
        id: "item-14",
        food_id: "food-rice",
        food_name_raw: "rice",
        portion_description: "1 cup",
        portion_grams_est: 180,
        confidence_score: 0.97,
        food_groups: ["whole_grains"],
      },
    ],
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
];

// ============ Parse Results ============

/** Returned when user types "ragi dosa with peanut chutney and filter coffee" */
export const mockParseResult: ParseResult = {
  items: [
    {
      food_name: "Ragi Dosa",
      raw_text: "ragi dosa",
      portion: "1 piece",
      portion_grams_est: 120,
      confidence: 0.91,
      alternatives: ["Ragi Adai", "Plain Dosa"],
      cuisine_hint: "South Indian",
      food_id: null,
      food_groups: ["whole_grains", "fermented_foods", "iron_rich_proteins"],
    },
    {
      food_name: "Peanut Chutney",
      raw_text: "peanut chutney",
      portion: "2 tbsp",
      portion_grams_est: 30,
      confidence: 0.87,
      alternatives: ["Groundnut Chutney"],
      cuisine_hint: "South Indian",
      food_id: null,
      food_groups: ["nuts_seeds", "herbs_spices"],
    },
    {
      food_name: "Filter Coffee",
      raw_text: "filter coffee",
      portion: "1 cup",
      portion_grams_est: 150,
      confidence: 0.94,
      alternatives: [],
      cuisine_hint: "South Indian",
      food_id: null,
      food_groups: ["calcium_sources"],
    },
  ],
  meal_context: "breakfast",
  needs_disambiguation: false,
};

// ============ Recommendations ============

export const mockRecommendations: Recommendation[] = [
  {
    message:
      "Add moringa (drumstick leaves) to your sambar — it's one of the richest plant sources of iron and calcium, both critical for managing iron-deficiency anemia alongside PCOS.",
    food_group_target: "dark_leafy_greens",
    priority: "high",
    recommendation_type: "rule_based",
    trace: {
      logic_chain: [
        "Health context: iron_deficiency_anemia + pcos",
        "Gap analysis: dark_leafy_greens present 1/7 days (high gap)",
        "Rule: iron_deficiency_anemia → prioritize iron-rich greens",
        "Food match: moringa (murungai keerai) — iron: 28mg/100g, calcium: 185mg/100g",
        "Cuisine fit: South Indian (matches user preference)",
      ],
      data_source: {
        food: "Drumstick Leaves (Moringa)",
        source: "IFCT 2017",
        source_id: "IFCT-G010",
        source_url: "https://ifct2017.com/food/G010",
        verified_date: "2024-11-15",
      },
      evidence: {
        claim:
          "Moringa leaves contain 28mg iron per 100g, making them one of the highest plant-based iron sources.",
        citation: "Gopalakrishnan et al., Journal of Food Science & Technology, 2016",
        display_text:
          "Moringa oleifera leaves are exceptionally rich in bioavailable iron (28mg/100g) and have been shown to improve hemoglobin levels in iron-deficient populations.",
      },
    },
  },
  {
    message:
      "Pair your dal with amla (Indian gooseberry) or lemon — vitamin C can increase iron absorption by up to 6x from plant sources.",
    food_group_target: "citrus_berries",
    priority: "high",
    recommendation_type: "rule_based",
    trace: {
      logic_chain: [
        "Health context: iron_deficiency_anemia",
        "Gap analysis: citrus_berries present 0/7 days (high gap)",
        "Rule: iron_deficiency_anemia → pair iron foods with vitamin C",
        "User eats dal regularly (legumes_pulses present 3/7 days)",
        "Food match: amla — vitamin C: 600mg/100g",
      ],
      data_source: {
        food: "Amla (Indian Gooseberry)",
        source: "IFCT 2017",
        source_id: "IFCT-F020",
        source_url: "https://ifct2017.com/food/F020",
        verified_date: "2024-11-15",
      },
      evidence: {
        claim:
          "Vitamin C enhances non-heme iron absorption by 2-6x by reducing ferric iron to the more absorbable ferrous form.",
        citation: "Hallberg et al., American Journal of Clinical Nutrition, 1989",
        display_text:
          "Co-consumption of 50mg+ vitamin C with iron-rich meals significantly enhances non-heme iron absorption, particularly important for vegetarians.",
      },
    },
  },
  {
    message:
      "Your fermented food intake is great! Idli, dosa, and curd rice are excellent choices — fermented foods support gut health, which is linked to better PCOS symptom management.",
    food_group_target: "fermented_foods",
    priority: "low",
    recommendation_type: "ai_generated",
    trace: {
      logic_chain: [
        "Health context: pcos",
        "Gap analysis: fermented_foods present 3/7 days (no gap)",
        "Pattern: user consistently includes fermented foods",
        "AI insight: positive reinforcement for good habits",
      ],
      data_source: {
        food: "Idli",
        source: "IFCT 2017",
        source_id: "IFCT-A065",
        source_url: "https://ifct2017.com/food/A065",
        verified_date: "2024-11-15",
      },
      evidence: {
        claim:
          "Fermented foods improve gut microbiome diversity, which may help regulate hormonal balance in PCOS.",
        citation: "Giampaolino et al., Nutrients, 2021",
        display_text:
          "Emerging research suggests gut microbiome modulation through fermented foods may improve insulin sensitivity and hormonal balance in women with PCOS.",
      },
    },
  },
  {
    message:
      "Try adding pumpkin seeds or sesame seeds to your meals — they're rich in zinc and magnesium, both important for PCOS management.",
    food_group_target: "nuts_seeds",
    priority: "medium",
    recommendation_type: "rule_based",
    trace: {
      logic_chain: [
        "Health context: pcos",
        "Gap analysis: nuts_seeds present 2/7 days (medium gap)",
        "Rule: pcos → recommend zinc and magnesium-rich foods",
        "Food match: pumpkin seeds — zinc: 7.6mg/100g, magnesium: 550mg/100g",
      ],
      data_source: {
        food: "Pumpkin Seeds",
        source: "USDA FoodData Central",
        source_id: "FDC-170556",
        source_url: "https://fdc.nal.usda.gov/fdc-app.html#/food-details/170556",
        verified_date: "2024-10-01",
      },
      evidence: null,
    },
  },
];

// ============ Food Group Summary ============

export const mockFoodGroupSummary: FoodGroupSummary[] = [
  { food_group_id: "dark_leafy_greens", food_group_slug: "dark-leafy-greens", food_group_name: "Dark Leafy Greens", days_present: 1, target_days: 7, gap: 6, gap_severity: "high" },
  { food_group_id: "orange_red_vegetables", food_group_slug: "orange-red-vegetables", food_group_name: "Orange & Red Vegetables", days_present: 0, target_days: 5, gap: 5, gap_severity: "high" },
  { food_group_id: "cruciferous", food_group_slug: "cruciferous", food_group_name: "Cruciferous Vegetables", days_present: 0, target_days: 5, gap: 5, gap_severity: "high" },
  { food_group_id: "alliums", food_group_slug: "alliums", food_group_name: "Alliums", days_present: 3, target_days: 5, gap: 2, gap_severity: "low" },
  { food_group_id: "citrus_berries", food_group_slug: "citrus-berries", food_group_name: "Citrus & Berries", days_present: 0, target_days: 7, gap: 7, gap_severity: "high" },
  { food_group_id: "legumes_pulses", food_group_slug: "legumes-pulses", food_group_name: "Legumes & Pulses", days_present: 3, target_days: 5, gap: 2, gap_severity: "low" },
  { food_group_id: "whole_grains", food_group_slug: "whole-grains", food_group_name: "Whole Grains", days_present: 3, target_days: 7, gap: 4, gap_severity: "medium" },
  { food_group_id: "nuts_seeds", food_group_slug: "nuts-seeds", food_group_name: "Nuts & Seeds", days_present: 2, target_days: 5, gap: 3, gap_severity: "medium" },
  { food_group_id: "fermented_foods", food_group_slug: "fermented-foods", food_group_name: "Fermented Foods", days_present: 3, target_days: 5, gap: 2, gap_severity: "low" },
  { food_group_id: "omega3_sources", food_group_slug: "omega3-sources", food_group_name: "Omega-3 Sources", days_present: 0, target_days: 3, gap: 3, gap_severity: "medium" },
  { food_group_id: "iron_rich_proteins", food_group_slug: "iron-rich-proteins", food_group_name: "Iron-Rich Proteins", days_present: 2, target_days: 7, gap: 5, gap_severity: "high" },
  { food_group_id: "calcium_sources", food_group_slug: "calcium-sources", food_group_name: "Calcium Sources", days_present: 2, target_days: 5, gap: 3, gap_severity: "medium" },
  { food_group_id: "herbs_spices", food_group_slug: "herbs-spices", food_group_name: "Herbs & Spices", days_present: 3, target_days: 5, gap: 2, gap_severity: "low" },
];

// ============ Similar Foods (Cross-Cultural Discovery) ============

export const mockSimilarFoods: Record<string, SimilarFood[]> = {
  "food-dal": [
    { food: mockFoods["food-black-beans"], similarity_score: 0.89 },
    { food: mockFoods["food-hummus"], similarity_score: 0.84 },
    { food: mockFoods["food-tempeh"], similarity_score: 0.78 },
  ],
  "food-idli": [
    { food: mockFoods["food-tempeh"], similarity_score: 0.82 },
    { food: mockFoods["food-miso"], similarity_score: 0.71 },
    { food: mockFoods["food-kimchi"], similarity_score: 0.65 },
  ],
};

// ============ Weekly Insights ============

export const mockWeeklyInsight: WeeklyInsight = {
  narrative:
    "You've had a strong week for fermented foods and legumes, Priya — your South Indian staples like idli, dosa, and sambar are doing double duty for gut health and plant protein. The biggest opportunity is adding more dark leafy greens and vitamin C-rich foods, which will directly support your iron absorption given your anemia. Even a small daily addition like moringa in sambar or amla with meals could make a meaningful difference.",
  highlights: [
    "Fermented foods in 3 of 3 logged days — great for PCOS gut health",
    "Legumes & pulses showing consistently — strong plant protein intake",
    "Iron-rich proteins need a boost — try ragi, moringa, or sesame seeds",
  ],
  spotlight_text:
    "This week's spotlight: Iron + Vitamin C synergy. Your vegetarian diet is rich in non-heme iron from dal and ragi. Pairing these with vitamin C sources like amla, lemon, or tomato can increase iron absorption by up to 6x — a simple change with big impact for iron-deficiency anemia.",
  nutrient_spotlight: {
    nutrient: "Iron (non-heme)",
    description:
      "Plant-based iron absorption is enhanced 2-6x when consumed with vitamin C. Your dal and ragi are great iron sources — pair them with citrus for maximum benefit.",
    food_sources: ["Ragi (finger millet)", "Moringa leaves", "Toor dal", "Sesame seeds", "Amla"],
  },
  error: null,
};

// ============ Favorites ============

export const mockFavorites = [
  {
    id: "fav-1",
    label: "Morning Idli Plate",
    items: [
      { food_name: "idli", portion: "3 pieces", food_id: "food-idli" },
      { food_name: "sambar", portion: "1 bowl", food_id: "food-sambar" },
      { food_name: "coconut chutney", portion: "2 tbsp", food_id: "food-coconut-chutney" },
    ],
  },
  {
    id: "fav-2",
    label: "Dal Rice Combo",
    items: [
      { food_name: "dal", portion: "1 bowl", food_id: "food-dal" },
      { food_name: "rice", portion: "1 cup", food_id: "food-rice" },
      { food_name: "raita", portion: "1 small bowl", food_id: "food-raita" },
    ],
  },
];

// ============ Recent Items ============

export const mockRecentItems = [
  { food_name: "idli", food_id: "food-idli", portion: "3 pieces" },
  { food_name: "sambar", food_id: "food-sambar", portion: "1 bowl" },
  { food_name: "coconut chutney", food_id: "food-coconut-chutney", portion: "2 tbsp" },
  { food_name: "dal", food_id: "food-dal", portion: "1 bowl" },
  { food_name: "rice", food_id: "food-rice", portion: "1 cup" },
  { food_name: "raita", food_id: "food-raita", portion: "1 small bowl" },
  { food_name: "masala dosa", food_id: "food-dosa", portion: "1 large" },
  { food_name: "curd rice", food_id: "food-curd-rice", portion: "1 plate" },
];

// ============ Search Results ============

export const mockSearchResults: Record<string, Food[]> = {
  default: [
    mockFoods["food-moringa"],
    mockFoods["food-ragi-porridge"],
    mockFoods["food-amla"],
    mockFoods["food-spinach-dal"],
    mockFoods["food-tempeh"],
  ],
};
