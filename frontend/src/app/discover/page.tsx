"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { useAuth } from "@/components/AuthProvider";
import { searchFoods, getSimilarFoods } from "@/lib/api";
import type { Food, SimilarFood } from "@/lib/types";
import Link from "next/link";

interface SimilarityResult {
  sourceName: string;
  sourceCuisine: string;
  similar: { name: string; cuisine_region: string; similarity: number }[];
}

export default function DiscoverPage() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Food[]>([]);
  const [searching, setSearching] = useState(false);
  const [similarityResult, setSimilarityResult] =
    useState<SimilarityResult | null>(null);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [featuredFoods, setFeaturedFoods] = useState<Food[]>([]);

  // Load a random set of foods on mount
  useEffect(() => {
    searchFoods("", undefined, undefined)
      .then((data) => {
        // Shuffle and pick 6
        const shuffled = (data.results || []).sort(() => Math.random() - 0.5);
        setFeaturedFoods(shuffled.slice(0, 6));
      })
      .catch(() => {});
  }, []);

  async function handleSearch() {
    if (!searchQuery.trim()) return;
    setSearching(true);
    setSimilarityResult(null);
    try {
      const data = await searchFoods(searchQuery);
      setSearchResults(data.results || []);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  }

  async function handleFindSimilar(food: Food) {
    setLoadingSimilar(true);
    try {
      const data = await getSimilarFoods(food.id, food.cuisine_region);
      setSimilarityResult({
        sourceName: food.name,
        sourceCuisine: food.cuisine_region,
        similar: (data.similar || []).map(
          (s: SimilarFood | { name: string; cuisine_region: string; similarity: number }) => ({
            name: "food" in s ? s.food.name : s.name,
            cuisine_region: "food" in s ? s.food.cuisine_region : s.cuisine_region,
            similarity:
              "similarity_score" in s
                ? (s as SimilarFood).similarity_score
                : (s as { similarity: number }).similarity,
          })
        ),
      });
    } catch {
      setSimilarityResult(null);
    } finally {
      setLoadingSimilar(false);
    }
  }

  const CUISINE_LABELS: Record<string, string> = {
    south_indian: "South Indian",
    north_indian: "North Indian",
    indian: "Indian",
    american: "American",
    east_asian: "East Asian",
    southeast_asian: "Southeast Asian",
    west_african: "West African",
    east_african: "East African",
    latin_american: "Latin American",
    middle_eastern: "Middle Eastern",
    global: "Global",
  };

  return (
    <div className="px-4 pt-8 pb-28 max-w-[480px] mx-auto">
      <div className="flex items-center justify-between mb-6">
        <Link href="/" className="text-[#A0674B] text-[15px]">
          ← Back
        </Link>
        <h1
          className="text-[20px]"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Discover
        </h1>
        <div className="w-12" />
      </div>

      {/* Search */}
      <div className="mb-6">
        <Input
          placeholder="Search foods... e.g. lentils, tofu, millet"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        {searching && (
          <p className="text-[13px] text-[#C9A87C] mt-2">Searching...</p>
        )}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="mb-6">
          <h2
            className="text-[17px] mb-3"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Results
          </h2>
          <div className="space-y-2">
            {searchResults.map((food) => (
              <Card key={food.id} hoverable>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-[15px] text-[#3E2117]">
                      {food.name}
                    </p>
                    <p className="text-[12px] text-[#C9A87C]">
                      {CUISINE_LABELS[food.cuisine_region] ||
                        food.cuisine_region}{" "}
                      · {food.source}
                    </p>
                    {food.tags && food.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {food.tags.slice(0, 4).map((tag) => (
                          <span
                            key={tag}
                            className="text-[10px] px-1.5 py-0.5 bg-[#E8D5C4] rounded text-[#6B4226]"
                          >
                            {tag.replace(/_/g, " ")}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleFindSimilar(food)}
                    className="text-[12px] text-[#A0674B] border border-[#A0674B] px-2.5 py-1.5 rounded-full hover:bg-[#A0674B]/10 transition-colors flex-shrink-0 ml-2"
                  >
                    Find similar
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Cross-Cultural Similarity Results */}
      {loadingSimilar && (
        <Card className="mb-6">
          <p className="text-[14px] text-[#C9A87C] text-center py-4">
            Finding nutritionally similar foods...
          </p>
        </Card>
      )}

      {similarityResult && (
        <Card className="mb-6 border border-[#7A9E7E]/20" style={{ background: "#7A9E7E08" }}>
          <h2
            className="text-[17px] mb-1"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Cross-Cultural Discovery
          </h2>
          <p className="text-[13px] text-[#6B5B4E] mb-3">
            Foods nutritionally similar to{" "}
            <strong>{similarityResult.sourceName}</strong> (
            {CUISINE_LABELS[similarityResult.sourceCuisine] ||
              similarityResult.sourceCuisine}
            ) from other cuisines:
          </p>
          {similarityResult.similar.length > 0 ? (
            <div className="space-y-2">
              {similarityResult.similar.map((food, j) => (
                <div
                  key={j}
                  className="flex items-center justify-between p-3 bg-white rounded-[12px]"
                >
                  <div>
                    <p className="font-semibold text-[15px] text-[#3E2117]">
                      {food.name}
                    </p>
                    <p className="text-[12px] text-[#C9A87C]">
                      {CUISINE_LABELS[food.cuisine_region] ||
                        food.cuisine_region}
                    </p>
                  </div>
                  <span className="text-[13px] text-[#7A9E7E] font-semibold">
                    {Math.round(food.similarity * 100)}% match
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[13px] text-[#C9A87C]">
              No similar foods found from other cuisines yet.
            </p>
          )}
          <p className="text-[11px] text-[#D4B896] mt-3 italic">
            Similarity based on 20-nutrient profile comparison via pgvector
            cosine distance
          </p>
        </Card>
      )}

      {/* Featured Foods */}
      {searchResults.length === 0 && (
        <>
          <h2
            className="text-[18px] mb-3 px-1"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Explore Foods
          </h2>
          <div className="space-y-2.5">
            {featuredFoods.map((food) => (
              <Card key={food.id} hoverable>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-[15px] text-[#3E2117]">
                      {food.name}
                    </p>
                    <p className="text-[12px] text-[#C9A87C]">
                      {CUISINE_LABELS[food.cuisine_region] ||
                        food.cuisine_region}
                    </p>
                  </div>
                  <button
                    onClick={() => handleFindSimilar(food)}
                    className="text-[12px] text-[#A0674B] border border-[#A0674B] px-2.5 py-1.5 rounded-full hover:bg-[#A0674B]/10 transition-colors flex-shrink-0"
                  >
                    Find similar
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
