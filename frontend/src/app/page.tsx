"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import FoodGroupDashboard from "@/components/food-groups/FoodGroupDashboard";
import { useAuth } from "@/components/AuthProvider";
import { getFoodGroupSummary, getJournal } from "@/lib/api";
import type { FoodGroupId, MealType } from "@/lib/types";
import Link from "next/link";

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function getSubGreeting(): string {
  const hour = new Date().getHours();
  const subs = {
    morning: ["What's nourishing you today?", "Ready to explore some flavors?"],
    afternoon: ["How's your day tasting?", "What's been on your plate?"],
    evening: ["Let's reflect on today's meals.", "What made today delicious?"],
  };
  const period = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
  return subs[period][Math.floor(Math.random() * subs[period].length)];
}

function formatDate(): string {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
}

const MEAL_TYPES: {
  type: MealType;
  label: string;
  icon: string;
  time: string;
}[] = [
  { type: "breakfast", label: "Breakfast", icon: "☀️", time: "Morning" },
  { type: "lunch", label: "Lunch", icon: "🌤️", time: "Midday" },
  { type: "dinner", label: "Dinner", icon: "🌙", time: "Evening" },
  { type: "snacks", label: "Snacks", icon: "🫐", time: "Anytime" },
];

export default function JournalPage() {
  const { user } = useAuth();
  const [filledGroups, setFilledGroups] = useState<Set<FoodGroupId>>(new Set());
  const [insightText, setInsightText] = useState<string | null>(null);
  const [todayEntries, setTodayEntries] = useState<Record<string, unknown[]>>({});

  const displayName =
    user?.user_metadata?.display_name || user?.email?.split("@")[0] || "";

  // Fetch today's data when user is available
  useEffect(() => {
    if (!user) return;
    const today = new Date().toISOString().slice(0, 10);

    // Fetch journal entries for today
    getJournal(user.id, today)
      .then((data) => {
        const entries = (data as { entries: { meal_type: string; items: unknown[] }[] }).entries || [];
        const byMeal: Record<string, unknown[]> = {};
        const groups = new Set<FoodGroupId>();
        for (const entry of entries) {
          byMeal[entry.meal_type] = entry.items || [];
          for (const item of (entry.items || []) as { food_groups?: FoodGroupId[] }[]) {
            for (const fg of item.food_groups || []) {
              groups.add(fg);
            }
          }
        }
        setTodayEntries(byMeal);
        setFilledGroups(groups);
      })
      .catch(() => {});

    // Fetch food group summary for insight
    getFoodGroupSummary(user.id, 1)
      .then((data) => {
        const fg = data.food_groups || [];
        const filled = fg.filter(
          (g: { gap_severity: string }) => g.gap_severity === "none"
        ).length;
        setInsightText(
          filled === 0
            ? "Start logging your meals to see your food group coverage!"
            : `You've covered ${filled} of 13 food groups so far today — ${
                filled < 5
                  ? "great start! Keep going."
                  : filled < 10
                    ? "great variety!"
                    : "amazing diversity!"
              }`
        );
      })
      .catch(() =>
        setInsightText("Start logging your meals to track your food groups!")
      );
  }, [user]);

  return (
    <div className="min-h-screen max-w-[480px] mx-auto">
      {/* ===== Header ===== */}
      <header className="px-5 pt-6 pb-5">
        {/* Logo row */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <span
              className="text-[24px] text-[#6B4226] tracking-tight"
              style={{ fontFamily: "var(--font-serif)" }}
            >
              nursh
            </span>
            <span className="text-[10px] font-semibold text-[#A0674B] bg-[#A0674B]/10 px-1.5 py-0.5 rounded-md uppercase tracking-wider">
              journal
            </span>
          </div>
          <span className="text-[12px] text-[#C9A87C] font-medium">
            {formatDate()}
          </span>
        </div>

        {/* Greeting */}
        <h1
          className="text-[26px] text-[#3E2117] leading-snug mb-1"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          {getGreeting()}{displayName ? `, ${displayName}` : ""}.
        </h1>
        <p className="text-[15px] text-[#A0674B]/70">{getSubGreeting()}</p>
      </header>

      {/* ===== Main Content ===== */}
      <main className="px-4 pb-28 space-y-4">
        {/* Food Group Dashboard */}
        <Card className="!p-5">
          <h2
            className="text-[18px] mb-3 text-[#3E2117]"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Today&apos;s Food Groups
          </h2>
          <FoodGroupDashboard filledGroups={filledGroups} />
        </Card>

        {/* Meal Timeline */}
        <div>
          <h2
            className="text-[18px] text-[#3E2117] mb-3 px-1"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Meals
          </h2>
          <div className="space-y-2.5">
            {MEAL_TYPES.map((meal) => (
              <Link key={meal.type} href={`/log?meal=${meal.type}`}>
                <Card hoverable className="!p-0 overflow-hidden cursor-pointer mb-2.5">
                  <div className="flex items-center gap-4 p-4">
                    {/* Icon circle */}
                    <div
                      className="w-11 h-11 rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ background: "#FAF6F1" }}
                    >
                      <span className="text-xl">{meal.icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-[15px] text-[#3E2117]">
                        {meal.label}
                      </p>
                      <p className="text-[12px] text-[#C9A87C]">
                        {(todayEntries[meal.type] as unknown[] | undefined)?.length
                          ? `${(todayEntries[meal.type] as unknown[]).length} item${(todayEntries[meal.type] as unknown[]).length > 1 ? "s" : ""} logged`
                          : `Tap to log your ${meal.label.toLowerCase()}`}
                      </p>
                    </div>
                    {/* Add indicator */}
                    <div className="w-8 h-8 rounded-full border-2 border-dashed border-[#D4B896] flex items-center justify-center flex-shrink-0">
                      <span className="text-[#A0674B] text-lg leading-none font-light">
                        +
                      </span>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Daily Insight */}
        <Card
          className="!p-5 border border-[#7A9E7E]/20"
          style={{ background: "linear-gradient(135deg, #7A9E7E08, #7A9E7E15)" }}
        >
          <div className="flex gap-3">
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
              style={{ background: "#7A9E7E20" }}
            >
              <span className="text-base">✨</span>
            </div>
            <div>
              <p className="text-[13px] font-semibold text-[#7A9E7E] mb-1">
                Today&apos;s Insight
              </p>
              <p className="text-[14px] text-[#3E2117] leading-relaxed">
                {insightText ||
                  "Start logging your meals to see your food group coverage!"}
              </p>
            </div>
          </div>
        </Card>
      </main>

      {/* ===== Bottom Navigation ===== */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-[#E8D5C4]/50 z-20">
        <div className="max-w-[480px] mx-auto flex items-center justify-around px-4 py-3">
          <NavItem label="Journal" active href="/" />
          <NavItem label="Insights" href="/insights" />

          {/* Center log button */}
          <Link
            href="/log"
            className="flex items-center gap-1.5 px-5 py-2.5 bg-[#6B4226] text-white rounded-full shadow-[0_2px_10px_rgba(62,33,23,0.25)] text-[13px] font-semibold active:scale-95 transition-transform"
          >
            <span className="text-base leading-none">+</span>
            Log Meal
          </Link>

          <NavItem label="Discover" href="/discover" />
          <NavItem label="Profile" href="/profile" />
        </div>
      </nav>
    </div>
  );
}

function NavItem({
  label,
  active = false,
  href = "#",
}: {
  label: string;
  active?: boolean;
  href?: string;
}) {
  return (
    <Link
      href={href}
      className={`text-[12px] font-semibold py-2 transition-colors ${
        active ? "text-[#6B4226]" : "text-[#C9A87C] hover:text-[#A0674B]"
      }`}
    >
      {label}
    </Link>
  );
}
