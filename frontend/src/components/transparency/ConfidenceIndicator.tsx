"use client";

interface ConfidenceIndicatorProps {
  confidence: number;
}

export default function ConfidenceIndicator({
  confidence,
}: ConfidenceIndicatorProps) {
  if (confidence >= 0.9) {
    return (
      <span className="text-[#7A9E7E] text-[11px]" title="High confidence match">
        ✓
      </span>
    );
  }
  if (confidence >= 0.7) {
    return (
      <span
        className="text-[#C49A3C] text-[11px] font-medium"
        title="Approximate match — tap to correct"
      >
        ~
      </span>
    );
  }
  return (
    <span
      className="text-[#B87358] text-[11px] font-medium"
      title="Low confidence — please verify"
    >
      ?
    </span>
  );
}
