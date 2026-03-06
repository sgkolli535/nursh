/**
 * Drop-in replacements for every function in lib/api.ts.
 * Returns mock data with realistic delays — no backend needed.
 */

import type {
  Food,
  FoodGroupSummary,
  JournalEntry,
  ParseResult,
  Recommendation,
  SimilarFood,
  UserProfile,
  WeeklyInsight,
} from "@/lib/types";

import {
  DEMO_USER_ID,
  mockFavorites,
  mockFoodGroupSummary,
  mockFoods,
  mockJournalEntries,
  mockParseResult,
  mockProfile,
  mockRecentItems,
  mockRecommendations,
  mockSearchResults,
  mockSimilarFoods,
  mockWeeklyInsight,
} from "./mock-data";

// Simulate network latency
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// In-memory state for mutations during the demo session
let journalEntries = [...mockJournalEntries];
let favorites: { id: string; label: string; items: Record<string, unknown>[] }[] = [
  ...mockFavorites,
];
let profile = { ...mockProfile };

// ============ Parse ============

export async function parseMeal(
  text: string,
  _userId?: string
): Promise<ParseResult> {
  await delay(800); // LLM parse feels slower
  // Return the pre-built parse result regardless of input
  return mockParseResult;
}

// ============ Journal ============

export async function getJournal(
  _userId: string,
  date?: string
): Promise<{ entries: JournalEntry[] }> {
  await delay(200);
  const targetDate = date || new Date().toISOString().slice(0, 10);
  return {
    entries: journalEntries.filter((e) => e.date === targetDate),
  };
}

export async function createJournalEntry(
  _userId: string,
  mealType: string,
  items: Record<string, unknown>[]
) {
  await delay(300);
  const newEntry: JournalEntry = {
    id: `entry-demo-${Date.now()}`,
    user_id: DEMO_USER_ID,
    date: new Date().toISOString().slice(0, 10),
    meal_type: mealType as JournalEntry["meal_type"],
    items: items.map((item, i) => ({
      id: `item-demo-${Date.now()}-${i}`,
      food_id: (item.food_id as string) || null,
      food_name_raw: (item.food_name as string) || "Unknown",
      portion_description: (item.portion as string) || "1 serving",
      portion_grams_est: (item.portion_grams_est as number) || null,
      confidence_score: (item.confidence as number) || 0.9,
      food_groups: (item.food_groups as JournalEntry["items"][0]["food_groups"]) || [],
    })),
    created_at: new Date().toISOString(),
  };
  journalEntries = [newEntry, ...journalEntries];
  return { entry: newEntry };
}

// ============ Recent Items ============

export async function getRecentItems(
  _userId: string,
  limit = 10
): Promise<{ items: { food_name: string; food_id: string | null; portion: string }[] }> {
  await delay(150);
  return { items: mockRecentItems.slice(0, limit) };
}

// ============ Favorites ============

export async function getFavorites(
  _userId: string
): Promise<{ favorites: { id: string; label: string; items: Record<string, unknown>[] }[] }> {
  await delay(150);
  return { favorites };
}

export async function saveFavorite(
  _userId: string,
  label: string,
  items: Record<string, unknown>[]
) {
  await delay(200);
  const newFav = { id: `fav-demo-${Date.now()}`, label, items };
  favorites = [...favorites, newFav];
  return { favorite: newFav };
}

export async function deleteFavorite(favoriteId: string) {
  await delay(200);
  favorites = favorites.filter((f) => f.id !== favoriteId);
  return { success: true };
}

// ============ Food Search ============

export async function searchFoods(
  query: string,
  _cuisine?: string,
  _tags?: string
): Promise<{ results: Food[] }> {
  await delay(300);
  // Fuzzy match against our mock foods
  const q = query.toLowerCase();
  const results = Object.values(mockFoods).filter(
    (f) =>
      f.name.toLowerCase().includes(q) ||
      f.aliases.some((a) => a.toLowerCase().includes(q)) ||
      f.tags.some((t) => t.toLowerCase().includes(q)) ||
      f.cuisine_region.toLowerCase().includes(q)
  );
  return { results: results.length > 0 ? results : mockSearchResults.default };
}

export async function getFood(foodId: string): Promise<Food> {
  await delay(150);
  const food = mockFoods[foodId];
  if (!food) throw new Error(`Food not found: ${foodId}`);
  return food;
}

export async function getSimilarFoods(
  foodId: string,
  excludeCuisine?: string
): Promise<{ similar: SimilarFood[] }> {
  await delay(400);
  let similar = mockSimilarFoods[foodId] || [];
  if (excludeCuisine) {
    similar = similar.filter(
      (s) => s.food.cuisine_region.toLowerCase() !== excludeCuisine.toLowerCase()
    );
  }
  return { similar };
}

// ============ Recommendations ============

export async function getRecommendations(
  _userId: string
): Promise<{ recommendations: Recommendation[] }> {
  await delay(600); // Recommendations feel like they take a moment
  return { recommendations: mockRecommendations };
}

// ============ Profile ============

export async function getProfile(_userId: string): Promise<UserProfile> {
  await delay(150);
  return profile;
}

export async function updateHealthContext(_userId: string, conditions: string[]) {
  await delay(200);
  profile = { ...profile, health_contexts: conditions as UserProfile["health_contexts"] };
  return { success: true };
}

export async function updatePreferences(
  _userId: string,
  dietary?: string[],
  cuisines?: string[]
) {
  await delay(200);
  if (dietary) profile = { ...profile, dietary_preferences: dietary };
  if (cuisines) profile = { ...profile, cuisine_preferences: cuisines };
  return { success: true };
}

// ============ Insights ============

export async function getWeeklyInsights(_userId: string): Promise<WeeklyInsight> {
  await delay(500);
  return mockWeeklyInsight;
}

export async function getFoodGroupSummary(
  _userId: string,
  _days = 7
): Promise<{ food_groups: FoodGroupSummary[] }> {
  await delay(200);
  return { food_groups: mockFoodGroupSummary };
}
