"use client";

import { foodGroupColors } from "@/styles/design-tokens";
import type { FoodGroupId } from "@/lib/types";

interface FoodGroupChipProps {
  slug: FoodGroupId;
  name: string;
  filled?: boolean;
  onClick?: () => void;
}

const FOOD_GROUP_META: Record<string, { label: string; icon: string }> = {
  dark_leafy_greens: { label: "Leafy Greens", icon: "🥬" },
  orange_red_vegetables: { label: "Orange/Red Veg", icon: "🥕" },
  cruciferous: { label: "Cruciferous", icon: "🥦" },
  alliums: { label: "Alliums", icon: "🧄" },
  citrus_berries: { label: "Citrus & Berries", icon: "🍊" },
  legumes_pulses: { label: "Legumes", icon: "🫘" },
  whole_grains: { label: "Whole Grains", icon: "🌾" },
  nuts_seeds: { label: "Nuts & Seeds", icon: "🥜" },
  fermented_foods: { label: "Fermented", icon: "🫙" },
  omega3_sources: { label: "Omega-3", icon: "🐟" },
  iron_rich_proteins: { label: "Iron-Rich Protein", icon: "🍖" },
  calcium_sources: { label: "Calcium", icon: "🥛" },
  herbs_spices: { label: "Herbs & Spices", icon: "🌿" },
};

export default function FoodGroupChip({
  slug,
  name,
  filled = false,
  onClick,
}: FoodGroupChipProps) {
  const color = foodGroupColors[slug] || "#C9A87C";
  const meta = FOOD_GROUP_META[slug] || { label: name, icon: "🍽️" };

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 py-1.5 px-3 rounded-full transition-all duration-300 cursor-default"
      style={{
        background: filled ? `${color}25` : "transparent",
        border: filled ? `1.5px solid ${color}` : "1.5px dashed #D4B89680",
        opacity: filled ? 1 : 0.55,
      }}
    >
      <span className="text-sm leading-none" style={{ filter: filled ? "none" : "grayscale(1)" }}>
        {meta.icon}
      </span>
      <span
        className="text-[11px] font-semibold leading-tight whitespace-nowrap"
        style={{ color: filled ? "#3E2117" : "#C9A87C" }}
      >
        {meta.label}
      </span>
    </button>
  );
}
