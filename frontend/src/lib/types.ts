/**
 * Shared types between frontend and backend.
 */

// ============ Food Groups ============

export type FoodGroupId =
  | "dark_leafy_greens"
  | "orange_red_vegetables"
  | "cruciferous"
  | "alliums"
  | "citrus_berries"
  | "legumes_pulses"
  | "whole_grains"
  | "nuts_seeds"
  | "fermented_foods"
  | "omega3_sources"
  | "iron_rich_proteins"
  | "calcium_sources"
  | "herbs_spices";

export interface FoodGroup {
  id: string;
  name: string;
  key_nutrients: string[];
  color_hex: string;
  icon_name: string;
}

// ============ Foods ============

export interface Food {
  id: string;
  name: string;
  aliases: string[];
  tags: string[];
  cuisine_region: string;
  source: string;
  source_id: string;
  source_url: string;
  verified_date: string;
  food_groups: FoodGroupId[];
}

export interface SimilarFood {
  food: Food;
  similarity_score: number;
}

// ============ Parsing ============

export interface ParsedFoodItem {
  food_name: string;
  raw_text: string;
  portion: string;
  portion_grams_est: number | null;
  confidence: number;
  alternatives: string[];
  cuisine_hint: string | null;
  food_id: string | null; // matched DB food, if found
  food_groups: FoodGroupId[];
}

export interface ParseResult {
  items: ParsedFoodItem[];
  meal_context: string | null;
  needs_disambiguation: boolean;
}

// ============ Journal ============

export type MealType = "breakfast" | "lunch" | "dinner" | "snacks";

export interface JournalEntry {
  id: string;
  user_id: string;
  date: string;
  meal_type: MealType;
  items: JournalItem[];
  created_at: string;
}

export interface JournalItem {
  id: string;
  food_id: string | null;
  food_name_raw: string;
  portion_description: string;
  portion_grams_est: number | null;
  confidence_score: number;
  food_groups: FoodGroupId[];
}

// ============ Health Context ============

export type HealthCondition =
  | "pcos"
  | "iron_deficiency_anemia"
  | "hypothyroidism"
  | "pregnancy_t1"
  | "pregnancy_t2"
  | "pregnancy_t3"
  | "perimenopause"
  | "type2_diabetes"
  | "celiac"
  | "vegetarian"
  | "vegan";

export interface UserProfile {
  id: string;
  display_name: string;
  health_contexts: HealthCondition[];
  dietary_preferences: string[];
  cuisine_preferences: string[];
}

// ============ Recommendations ============

export interface Recommendation {
  message: string;
  food_group_target: FoodGroupId;
  priority: "high" | "medium" | "low";
  recommendation_type: "rule_based" | "ai_generated";
  trace: RecommendationTrace;
}

export interface RecommendationTrace {
  logic_chain: string[];
  data_source: {
    food: string;
    source: string;
    source_id: string;
    source_url: string;
    verified_date: string;
  };
  evidence: {
    claim: string;
    citation: string;
    display_text: string;
  } | null;
}

// ============ Insights ============

export interface FoodGroupSummary {
  food_group_id: FoodGroupId;
  food_group_slug: string;
  food_group_name: string;
  days_present: number;
  target_days: number;
  gap: number;
  gap_severity: "none" | "low" | "medium" | "high";
}

export interface WeeklyInsight {
  narrative: string;
  highlights: string[];
  spotlight_text: string;
  nutrient_spotlight: {
    nutrient: string;
    description: string;
    food_sources: string[];
  } | null;
  error: string | null;
}

// ============ Evidence ============

export interface EvidenceCitation {
  claim: string;
  citation_text: string;
  doi: string | null;
  display_text: string;
}
