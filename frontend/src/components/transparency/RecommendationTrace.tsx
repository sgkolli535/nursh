"use client";

import { useState } from "react";
import type { RecommendationTrace as TraceType } from "@/lib/types";

interface RecommendationTraceProps {
  trace: TraceType;
}

export default function RecommendationTrace({
  trace,
}: RecommendationTraceProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-[11px] text-[#A0674B] underline cursor-pointer"
      >
        {expanded ? "Hide reasoning" : "Why am I seeing this?"}
      </button>

      {expanded && (
        <div className="mt-2 p-3 bg-[#FAF6F1] rounded-[12px] text-[13px] space-y-2">
          {/* Logic Chain */}
          <div>
            <p className="font-semibold text-[#6B4226] mb-1">Reasoning:</p>
            <ol className="list-decimal list-inside space-y-1 text-[#3E2117]">
              {trace.logic_chain.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </div>

          {/* Data Source */}
          {trace.data_source && trace.data_source.source && (
            <div>
              <p className="font-semibold text-[#6B4226] mb-1">Data source:</p>
              <p className="text-[#3E2117]">
                {trace.data_source.food} —{" "}
                <span className="text-[#A0674B]">
                  {trace.data_source.source}
                  {trace.data_source.source_id &&
                    ` (${trace.data_source.source_id})`}
                </span>
                {trace.data_source.verified_date && (
                  <span className="text-[#D4B896] ml-1">
                    Verified {trace.data_source.verified_date}
                  </span>
                )}
              </p>
              {trace.data_source.source_url && (
                <a
                  href={trace.data_source.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#A0674B] underline text-[11px]"
                >
                  View original source
                </a>
              )}
            </div>
          )}

          {/* Evidence Citation */}
          {trace.evidence && (
            <div>
              <p className="font-semibold text-[#6B4226] mb-1">Research:</p>
              <p className="text-[#3E2117]">{trace.evidence.display_text}</p>
              <p className="text-[11px] text-[#D4B896] mt-1 italic">
                {trace.evidence.citation}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
