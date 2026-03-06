interface RecommendationTypeLabelProps {
  type: "rule_based" | "ai_generated";
}

export default function RecommendationTypeLabel({
  type,
}: RecommendationTypeLabelProps) {
  if (type === "rule_based") {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] text-[#7A9E7E] bg-[#7A9E7E]/10 px-2 py-0.5 rounded-full">
        <span>✓</span> Based on established nutrition research
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-[11px] text-[#C49A3C] bg-[#C49A3C]/10 px-2 py-0.5 rounded-full">
      <span>✦</span> Personalized suggestion — tap to see why
    </span>
  );
}
