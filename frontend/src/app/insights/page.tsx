"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import RecommendationTrace from "@/components/transparency/RecommendationTrace";
import RecommendationTypeLabel from "@/components/transparency/RecommendationTypeLabel";
import { useAuth } from "@/components/AuthProvider";
import {
  getRecommendations,
  getWeeklyInsights,
  getFoodGroupSummary,
} from "@/lib/api";
import type { Recommendation, FoodGroupSummary } from "@/lib/types";
import { foodGroupColors } from "@/styles/design-tokens";
import Link from "next/link";

export default function InsightsPage() {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [narrative, setNarrative] = useState<string | null>(null);
  const [spotlightText, setSpotlightText] = useState<string | null>(null);
  const [spotlightNutrient, setSpotlightNutrient] = useState<string | null>(null);
  const [foodGroups, setFoodGroups] = useState<FoodGroupSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    async function fetchData() {
      setLoading(true);
      try {
        // Fetch all three in parallel
        const [recsData, insightsData, fgData] = await Promise.allSettled([
          getRecommendations(user!.id),
          getWeeklyInsights(user!.id),
          getFoodGroupSummary(user!.id, 7),
        ]);

        if (recsData.status === "fulfilled") {
          setRecommendations(recsData.value.recommendations || []);
        }

        if (insightsData.status === "fulfilled") {
          const insights = insightsData.value;
          setNarrative(insights.narrative || null);
          setSpotlightText(insights.spotlight_text || null);
          setSpotlightNutrient(
            insights.nutrient_spotlight?.nutrient || null
          );
        }

        if (fgData.status === "fulfilled") {
          setFoodGroups(fgData.value.food_groups || []);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [user]);

  // Build heatmap data: 7 columns (days) x 13 rows (food groups)
  const coveredCount = foodGroups.filter(
    (g) => g.gap_severity === "none"
  ).length;

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
          Weekly Insights
        </h1>
        <div className="w-12" />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-[15px] text-[#C9A87C]">
            Loading your insights...
          </p>
        </div>
      ) : (
        <>
          {/* Weekly Narrative */}
          <Card className="mb-5" style={{ background: "#7A9E7E10" }}>
            <h2
              className="text-[17px] mb-2"
              style={{ fontFamily: "var(--font-serif)" }}
            >
              This Week
            </h2>
            <p className="text-[15px] text-[#3E2117] leading-relaxed">
              {narrative ||
                `You covered ${coveredCount} of 13 food groups this week. ${
                  coveredCount < 5
                    ? "There's room to explore more variety!"
                    : coveredCount < 10
                      ? "Great variety — keep it up!"
                      : "Amazing food diversity this week!"
                }`}
            </p>
          </Card>

          {/* Food Group Heatmap */}
          {foodGroups.length > 0 && (
            <Card className="mb-5">
              <h2
                className="text-[17px] mb-3"
                style={{ fontFamily: "var(--font-serif)" }}
              >
                Food Group Coverage
              </h2>
              <div className="space-y-1.5">
                {foodGroups.map((fg) => {
                  const color =
                    foodGroupColors[fg.food_group_slug] || "#C9A87C";
                  const pct = Math.min(
                    100,
                    (fg.days_present / Math.max(fg.target_days, 1)) * 100
                  );
                  return (
                    <div key={fg.food_group_slug} className="flex items-center gap-2">
                      <span className="text-[11px] text-[#6B5B4E] w-28 text-right truncate">
                        {fg.food_group_name}
                      </span>
                      <div className="flex-1 h-3 bg-[#E8D5C4] rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${pct}%`,
                            background: color,
                            opacity: pct > 0 ? 0.7 : 0,
                          }}
                        />
                      </div>
                      <span className="text-[11px] text-[#C9A87C] w-10">
                        {fg.days_present}/{fg.target_days}d
                      </span>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <>
              <h2
                className="text-[18px] mb-3 px-1"
                style={{ fontFamily: "var(--font-serif)" }}
              >
                Suggestions for You
              </h2>
              <div className="space-y-3 mb-5">
                {recommendations.map((rec, i) => (
                  <Card key={i}>
                    <RecommendationTypeLabel
                      type={rec.recommendation_type}
                    />
                    <p className="text-[15px] text-[#3E2117] leading-relaxed mt-2">
                      {rec.message}
                    </p>
                    {rec.trace && <RecommendationTrace trace={rec.trace} />}
                  </Card>
                ))}
              </div>
            </>
          )}

          {recommendations.length === 0 && (
            <Card className="mb-5">
              <p className="text-[14px] text-[#C9A87C] text-center py-4">
                Log a few days of meals to get personalized suggestions.
              </p>
            </Card>
          )}

          {/* Nutrient Spotlight */}
          <Card className="mb-8" style={{ background: "#D4A05415" }}>
            <h3 className="text-[17px] font-semibold text-[#6B4226] mb-2">
              Nutrient Spotlight{spotlightNutrient ? `: ${spotlightNutrient}` : ""}
            </h3>
            <p className="text-[15px] text-[#3E2117] leading-relaxed">
              {spotlightText ||
                "Iron helps carry oxygen through your blood to all parts of your body. Great sources include lentils, spinach, tofu, and pumpkin seeds. Pairing iron-rich foods with vitamin C helps your body absorb it better."}
            </p>
          </Card>
        </>
      )}
    </div>
  );
}
