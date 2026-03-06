"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import ConfidenceIndicator from "@/components/transparency/ConfidenceIndicator";
import FoodGroupChip from "@/components/food-groups/FoodGroupChip";
import { useAuth } from "@/components/AuthProvider";
import type { FoodGroupId, ParsedFoodItem } from "@/lib/types";
import {
  parseMeal,
  createJournalEntry,
  getRecentItems,
  getFavorites,
  saveFavorite,
} from "@/lib/api";
import Link from "next/link";

export default function LogPage() {
  return (
    <Suspense
      fallback={
        <div className="px-4 pt-8 text-[#C9A87C] max-w-[480px] mx-auto">Loading...</div>
      }
    >
      <LogPageContent />
    </Suspense>
  );
}

interface RecentItem {
  food_name: string;
  food_id: string | null;
  portion: string;
}

interface FavoriteItem {
  id: string;
  label: string;
  items: Record<string, unknown>[];
}

function LogPageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const mealType = searchParams.get("meal") || "lunch";

  const [text, setText] = useState("");
  const [items, setItems] = useState<ParsedFoodItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  // Recent & Favorites
  const [recentItems, setRecentItems] = useState<RecentItem[]>([]);
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [showRecent, setShowRecent] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);

  // Load recent & favorites on mount
  useEffect(() => {
    if (!user) return;
    getRecentItems(user.id)
      .then((data) => setRecentItems(data.items || []))
      .catch(() => {});
    getFavorites(user.id)
      .then((data) => setFavorites(data.favorites || []))
      .catch(() => {});
  }, [user]);

  async function handleParse() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setSaved(false);
    setShowRecent(false);
    setShowFavorites(false);
    try {
      const result = await parseMeal(text, user?.id);
      setItems(result.items || []);
    } catch {
      setError("Could not parse your meal. You can still save it manually.");
      setItems([
        {
          food_name: text,
          raw_text: text,
          portion: "1 serving",
          portion_grams_est: null,
          confidence: 0.5,
          alternatives: [],
          cuisine_hint: null,
          food_id: null,
          food_groups: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleRecentSelect(item: RecentItem) {
    setItems([
      {
        food_name: item.food_name,
        raw_text: item.food_name,
        portion: item.portion,
        portion_grams_est: null,
        confidence: 1.0,
        alternatives: [],
        cuisine_hint: null,
        food_id: item.food_id,
        food_groups: [],
      },
    ]);
    setText(item.food_name);
    setShowRecent(false);
    setShowFavorites(false);
  }

  function handleFavoriteSelect(fav: FavoriteItem) {
    const parsed: ParsedFoodItem[] = fav.items.map((fi) => ({
      food_name: (fi.food_name as string) || (fi.food_name_raw as string) || "",
      raw_text: (fi.food_name as string) || "",
      portion: (fi.portion as string) || (fi.portion_description as string) || "1 serving",
      portion_grams_est: null,
      confidence: 1.0,
      alternatives: [],
      cuisine_hint: null,
      food_id: (fi.food_id as string) || null,
      food_groups: ((fi.food_group_ids as string[]) || []) as FoodGroupId[],
    }));
    setItems(parsed);
    setText(fav.label);
    setShowFavorites(false);
    setShowRecent(false);
  }

  async function handleSave() {
    if (!user || items.length === 0) return;
    setSaving(true);
    setError(null);
    try {
      await createJournalEntry(
        user.id,
        mealType,
        items.map((item) => ({
          food_id: item.food_id,
          food_name_raw: item.food_name,
          portion_description: item.portion,
          portion_grams_est: item.portion_grams_est,
          confidence_score: item.confidence,
          food_group_ids: item.food_groups || [],
        }))
      );
      setSaved(true);
      setTimeout(() => router.push("/"), 1200);
    } catch {
      setError("Could not save. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveAsFavorite() {
    if (!user || items.length === 0) return;
    const label =
      items.length === 1
        ? items[0].food_name
        : items.map((i) => i.food_name).join(", ");
    try {
      await saveFavorite(
        user.id,
        label,
        items.map((item) => ({
          food_name: item.food_name,
          food_id: item.food_id,
          portion: item.portion,
          food_group_ids: item.food_groups || [],
        }))
      );
      // Refresh favorites list
      const data = await getFavorites(user.id);
      setFavorites(data.favorites || []);
    } catch {}
  }

  const mealLabel = mealType.charAt(0).toUpperCase() + mealType.slice(1);

  return (
    <div className="px-4 pt-8 pb-28 max-w-[480px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Link href="/" className="text-[#A0674B] text-[15px]">
          ← Back
        </Link>
        <h1
          className="text-[20px]"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Log {mealLabel}
        </h1>
        <div className="w-12" />
      </div>

      {/* Input */}
      <div className="mb-4">
        <Input
          placeholder="What did you eat? e.g. idli with sambar and chutney"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleParse()}
          autoFocus
        />
        <div className="flex gap-2 mt-3">
          <Button onClick={handleParse} disabled={loading || !text.trim()}>
            {loading ? "Parsing..." : "Parse Meal"}
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              setShowFavorites(!showFavorites);
              setShowRecent(false);
            }}
          >
            Favorites{favorites.length > 0 ? ` (${favorites.length})` : ""}
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              setShowRecent(!showRecent);
              setShowFavorites(false);
            }}
          >
            Recent{recentItems.length > 0 ? ` (${recentItems.length})` : ""}
          </Button>
        </div>
      </div>

      {/* Favorites Panel */}
      {showFavorites && (
        <Card className="mb-4">
          <h3 className="text-[13px] font-semibold text-[#6B4226] mb-2">
            Saved Favorites
          </h3>
          {favorites.length === 0 ? (
            <p className="text-[13px] text-[#C9A87C]">
              No favorites yet. Log a meal and save it as a favorite!
            </p>
          ) : (
            <div className="space-y-2">
              {favorites.map((fav) => (
                <button
                  key={fav.id}
                  onClick={() => handleFavoriteSelect(fav)}
                  className="w-full text-left p-3 bg-[#FAF6F1] rounded-[10px] hover:bg-[#E8D5C4] transition-colors"
                >
                  <p className="text-[14px] font-medium text-[#3E2117]">
                    {fav.label}
                  </p>
                  <p className="text-[11px] text-[#C9A87C]">
                    {fav.items.length} item{fav.items.length !== 1 ? "s" : ""}
                  </p>
                </button>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Recent Panel */}
      {showRecent && (
        <Card className="mb-4">
          <h3 className="text-[13px] font-semibold text-[#6B4226] mb-2">
            Recently Logged
          </h3>
          {recentItems.length === 0 ? (
            <p className="text-[13px] text-[#C9A87C]">
              No recent items yet. Start logging meals!
            </p>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {recentItems.map((item, i) => (
                <button
                  key={i}
                  onClick={() => handleRecentSelect(item)}
                  className="text-[13px] px-3 py-1.5 bg-[#FAF6F1] rounded-full border border-[#E8D5C4] text-[#6B4226] hover:bg-[#E8D5C4] transition-colors"
                >
                  {item.food_name}
                </button>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Error */}
      {error && (
        <p className="text-[13px] text-[#B87358] bg-[#B87358]/10 px-3 py-2 rounded-[8px] mb-4">
          {error}
        </p>
      )}

      {/* Parsed Items */}
      {items.length > 0 && (
        <div className="space-y-3 mb-6">
          <h2
            className="text-[17px] font-semibold"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Recognized Items
          </h2>
          {items.map((item, i) => (
            <Card key={i} hoverable>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-[15px] text-[#3E2117]">
                      {item.food_name}
                    </p>
                    <ConfidenceIndicator confidence={item.confidence} />
                  </div>
                  <p className="text-[13px] text-[#6B5B4E]">
                    {item.portion}
                    {item.cuisine_hint && (
                      <span className="text-[#D4B896]">
                        {" "}
                        · {item.cuisine_hint}
                      </span>
                    )}
                  </p>
                  {item.food_groups.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {item.food_groups.map((fg) => (
                        <FoodGroupChip
                          key={fg}
                          slug={fg as FoodGroupId}
                          name={fg}
                          filled
                        />
                      ))}
                    </div>
                  )}
                  {item.confidence < 0.7 &&
                    item.alternatives.length > 0 && (
                      <div className="mt-2 p-2 bg-[#FAF6F1] rounded-[8px]">
                        <p className="text-[11px] text-[#C49A3C] mb-1">
                          Did you mean one of these?
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {item.alternatives.map((alt, j) => (
                            <button
                              key={j}
                              className="text-[13px] px-2 py-1 bg-white rounded-[8px] border border-[#E8D5C4] text-[#6B4226] hover:bg-[#E8D5C4]"
                              onClick={() => {
                                const updated = [...items];
                                updated[i] = {
                                  ...updated[i],
                                  food_name: alt,
                                  confidence: 0.9,
                                };
                                setItems(updated);
                              }}
                            >
                              {alt}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
                <button className="text-[#D4B896] text-[13px] ml-2">
                  Edit
                </button>
              </div>
            </Card>
          ))}

          {/* Action Buttons */}
          {saved ? (
            <div className="text-center py-4">
              <p className="text-[15px] text-[#7A9E7E] font-semibold">
                Saved to your journal!
              </p>
            </div>
          ) : (
            <div className="space-y-2 mt-4">
              <Button
                className="w-full"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? "Saving..." : `Add to ${mealLabel}`}
              </Button>
              <Button
                variant="ghost"
                className="w-full"
                onClick={handleSaveAsFavorite}
              >
                Save as Favorite
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
