/**
 * Nursh API Client — typed fetch wrapper for all backend endpoints.
 *
 * When NEXT_PUBLIC_DEMO_MODE is "true", all functions delegate to the
 * mock-api layer so the app runs without a backend or Supabase.
 */

import type {
  Food,
  FoodGroupSummary,
  ParseResult,
  Recommendation,
  SimilarFood,
  UserProfile,
  WeeklyInsight,
} from "./types";

import * as mockApi from "@/demo/mock-api";

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

// Parse
export async function parseMeal(text: string, userId?: string): Promise<ParseResult> {
  if (DEMO_MODE) return mockApi.parseMeal(text, userId);
  return fetchJSON("/parse/", {
    method: "POST",
    body: JSON.stringify({ text, user_id: userId }),
  });
}

// Journal
export async function getJournal(userId: string, date?: string) {
  if (DEMO_MODE) return mockApi.getJournal(userId, date);
  const params = new URLSearchParams({ user_id: userId });
  if (date) params.set("date", date);
  return fetchJSON(`/journal/?${params}`);
}

export async function createJournalEntry(
  userId: string,
  mealType: string,
  items: Record<string, unknown>[]
) {
  if (DEMO_MODE) return mockApi.createJournalEntry(userId, mealType, items);
  return fetchJSON("/journal/", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, meal_type: mealType, items }),
  });
}

// Recent Items
export async function getRecentItems(
  userId: string,
  limit = 10
): Promise<{ items: { food_name: string; food_id: string | null; portion: string }[] }> {
  if (DEMO_MODE) return mockApi.getRecentItems(userId, limit);
  return fetchJSON(`/journal/recent?user_id=${userId}&limit=${limit}`);
}

// Favorites
export async function getFavorites(
  userId: string
): Promise<{ favorites: { id: string; label: string; items: Record<string, unknown>[] }[] }> {
  if (DEMO_MODE) return mockApi.getFavorites(userId);
  return fetchJSON(`/journal/favorites?user_id=${userId}`);
}

export async function saveFavorite(
  userId: string,
  label: string,
  items: Record<string, unknown>[]
) {
  if (DEMO_MODE) return mockApi.saveFavorite(userId, label, items);
  return fetchJSON("/journal/favorites", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, label, items }),
  });
}

export async function deleteFavorite(favoriteId: string) {
  if (DEMO_MODE) return mockApi.deleteFavorite(favoriteId);
  return fetchJSON(`/journal/favorites/${favoriteId}`, { method: "DELETE" });
}

// Food Search
export async function searchFoods(
  query: string,
  cuisine?: string,
  tags?: string
): Promise<{ results: Food[] }> {
  if (DEMO_MODE) return mockApi.searchFoods(query, cuisine, tags);
  const params = new URLSearchParams({ query });
  if (cuisine) params.set("cuisine", cuisine);
  if (tags) params.set("tags", tags);
  return fetchJSON(`/food/search?${params}`);
}

export async function getFood(foodId: string): Promise<Food> {
  if (DEMO_MODE) return mockApi.getFood(foodId);
  return fetchJSON(`/food/${foodId}`);
}

export async function getSimilarFoods(
  foodId: string,
  excludeCuisine?: string
): Promise<{ similar: SimilarFood[] }> {
  if (DEMO_MODE) return mockApi.getSimilarFoods(foodId, excludeCuisine);
  const params = excludeCuisine ? `?exclude_cuisine=${excludeCuisine}` : "";
  return fetchJSON(`/food/${foodId}/similar${params}`);
}

// Recommendations
export async function getRecommendations(
  userId: string
): Promise<{ recommendations: Recommendation[] }> {
  if (DEMO_MODE) return mockApi.getRecommendations(userId);
  return fetchJSON(`/recommendations/?user_id=${userId}`);
}

// Profile
export async function getProfile(userId: string): Promise<UserProfile> {
  if (DEMO_MODE) return mockApi.getProfile(userId);
  return fetchJSON(`/profile/${userId}`);
}

export async function updateHealthContext(userId: string, conditions: string[]) {
  if (DEMO_MODE) return mockApi.updateHealthContext(userId, conditions);
  return fetchJSON(`/profile/${userId}/health-context`, {
    method: "PUT",
    body: JSON.stringify({ conditions }),
  });
}

export async function updatePreferences(
  userId: string,
  dietary?: string[],
  cuisines?: string[]
) {
  if (DEMO_MODE) return mockApi.updatePreferences(userId, dietary, cuisines);
  return fetchJSON(`/profile/${userId}/preferences`, {
    method: "PUT",
    body: JSON.stringify({ dietary, cuisines }),
  });
}

// Insights
export async function getWeeklyInsights(userId: string): Promise<WeeklyInsight> {
  if (DEMO_MODE) return mockApi.getWeeklyInsights(userId);
  return fetchJSON(`/insights/weekly?user_id=${userId}`);
}

export async function getFoodGroupSummary(
  userId: string,
  days = 7
): Promise<{ food_groups: FoodGroupSummary[] }> {
  if (DEMO_MODE) return mockApi.getFoodGroupSummary(userId, days);
  return fetchJSON(`/insights/food-groups?user_id=${userId}&days=${days}`);
}
