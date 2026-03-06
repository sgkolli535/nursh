"use client";

import FoodGroupChip from "./FoodGroupChip";
import type { FoodGroupId } from "@/lib/types";

interface FoodGroupDashboardProps {
  filledGroups: Set<FoodGroupId>;
}

const ALL_GROUPS: { slug: FoodGroupId; name: string }[] = [
  { slug: "dark_leafy_greens", name: "Dark Leafy Greens" },
  { slug: "orange_red_vegetables", name: "Orange/Red Vegetables" },
  { slug: "cruciferous", name: "Cruciferous" },
  { slug: "alliums", name: "Alliums" },
  { slug: "citrus_berries", name: "Citrus & Berries" },
  { slug: "legumes_pulses", name: "Legumes & Pulses" },
  { slug: "whole_grains", name: "Whole Grains" },
  { slug: "nuts_seeds", name: "Nuts & Seeds" },
  { slug: "fermented_foods", name: "Fermented Foods" },
  { slug: "omega3_sources", name: "Omega-3 Sources" },
  { slug: "iron_rich_proteins", name: "Iron-Rich Proteins" },
  { slug: "calcium_sources", name: "Calcium Sources" },
  { slug: "herbs_spices", name: "Herbs & Spices" },
];

export default function FoodGroupDashboard({
  filledGroups,
}: FoodGroupDashboardProps) {
  const filledCount = filledGroups.size;

  return (
    <div>
      {/* Progress ring */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative w-12 h-12 flex-shrink-0">
          <svg viewBox="0 0 48 48" className="w-full h-full -rotate-90">
            <circle
              cx="24"
              cy="24"
              r="20"
              fill="none"
              stroke="#E8D5C4"
              strokeWidth="4"
            />
            <circle
              cx="24"
              cy="24"
              r="20"
              fill="none"
              stroke="#7A9E7E"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${(filledCount / 13) * 125.6} 125.6`}
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-[13px] font-bold text-[#3E2117]">
            {filledCount}
          </span>
        </div>
        <div>
          <p className="text-[15px] font-semibold text-[#3E2117]">
            {filledCount} of 13 groups
          </p>
          <p className="text-[12px] text-[#C9A87C]">
            {filledCount === 0
              ? "Start logging to fill your groups"
              : filledCount < 5
                ? "Good start — keep going!"
                : filledCount < 10
                  ? "Great variety today!"
                  : "Amazing diversity!"}
          </p>
        </div>
      </div>

      {/* Chips grid */}
      <div className="flex flex-wrap gap-1.5">
        {ALL_GROUPS.map((group) => (
          <FoodGroupChip
            key={group.slug}
            slug={group.slug}
            name={group.name}
            filled={filledGroups.has(group.slug)}
          />
        ))}
      </div>
    </div>
  );
}
