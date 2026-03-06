/**
 * Nursh Design Tokens
 * Programmatic access to design system values from the Design Spec v1.0
 */

export const colors = {
  // Primary
  espresso: "#3E2117",
  walnut: "#6B4226",
  terracotta: "#A0674B",

  // Neutral & Background
  caramel: "#C9A87C",
  sand: "#D4B896",
  linen: "#E8D5C4",
  cream: "#F5EDE3",
  parchment: "#FAF6F1",

  // Accent (food groups)
  mutedSage: "#8FA68B",
  softClay: "#C17C5E",
  warmAmber: "#D4A054",
  blush: "#D4A69A",
  softBrown: "#8B7355",

  // Semantic
  warmSuccess: "#7A9E7E",
  gentleAmber: "#C49A3C",
  softAlert: "#B87358",

  // Dark mode
  darkCocoa: "#1E1410",
  warmCharcoal: "#2A1F18",
  darkWalnut: "#342318",
} as const;

export const foodGroupColors: Record<string, string> = {
  dark_leafy_greens: colors.mutedSage,
  orange_red_vegetables: colors.softClay,
  cruciferous: colors.mutedSage,
  alliums: colors.sand,
  citrus_berries: colors.warmAmber,
  legumes_pulses: colors.terracotta,
  whole_grains: colors.caramel,
  nuts_seeds: colors.walnut,
  fermented_foods: colors.blush,
  omega3_sources: colors.softBrown,
  iron_rich_proteins: colors.softClay,
  calcium_sources: colors.linen,
  herbs_spices: colors.terracotta,
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  "2xl": 48,
} as const;

export const radius = {
  button: 12,
  card: 16,
  modal: 20,
  chip: 999,
  input: 12,
} as const;

export const typography = {
  displayTitle: { font: "DM Serif Display", size: 32, weight: 400 },
  h1: { font: "DM Serif Display", size: 26, weight: 400 },
  h2: { font: "DM Serif Display", size: 20, weight: 400 },
  h3: { font: "Plus Jakarta Sans", size: 17, weight: 600 },
  body: { font: "Plus Jakarta Sans", size: 15, weight: 400 },
  bodySmall: { font: "Plus Jakarta Sans", size: 13, weight: 400 },
  caption: { font: "Plus Jakarta Sans", size: 11, weight: 500 },
  button: { font: "Plus Jakarta Sans", size: 15, weight: 600 },
} as const;
