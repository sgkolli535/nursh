"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useAuth } from "@/components/AuthProvider";
import {
  getProfile,
  updateHealthContext,
  updatePreferences,
} from "@/lib/api";
import Link from "next/link";

const HEALTH_CONDITIONS = [
  { id: "pcos", label: "PCOS" },
  { id: "iron_deficiency_anemia", label: "Iron-Deficiency Anemia" },
  { id: "hypothyroidism", label: "Hypothyroidism" },
  { id: "pregnancy_t1", label: "Pregnancy (1st Trimester)" },
  { id: "pregnancy_t2", label: "Pregnancy (2nd Trimester)" },
  { id: "pregnancy_t3", label: "Pregnancy (3rd Trimester)" },
  { id: "perimenopause", label: "Perimenopause" },
  { id: "type2_diabetes", label: "Type 2 Diabetes" },
  { id: "celiac", label: "Celiac / Gluten Sensitivity" },
];

const DIETARY_PREFS = [
  { id: "vegetarian", label: "Vegetarian" },
  { id: "vegan", label: "Vegan" },
  { id: "gluten_free", label: "Gluten-Free" },
  { id: "dairy_free", label: "Dairy-Free" },
];

const CUISINES = [
  { id: "south_indian", label: "South Indian" },
  { id: "north_indian", label: "North Indian" },
  { id: "american", label: "American" },
  { id: "east_asian", label: "East Asian" },
  { id: "west_african", label: "West African" },
  { id: "latin_american", label: "Latin American" },
  { id: "middle_eastern", label: "Middle Eastern" },
];

export default function ProfilePage() {
  const { user, signOut } = useAuth();
  const [selectedConditions, setSelectedConditions] = useState<Set<string>>(new Set());
  const [selectedDiet, setSelectedDiet] = useState<Set<string>>(new Set());
  const [selectedCuisines, setSelectedCuisines] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  // Load profile on mount
  useEffect(() => {
    if (!user) return;
    getProfile(user.id)
      .then((profile) => {
        setSelectedConditions(new Set(profile.health_contexts || []));
        setSelectedDiet(new Set(profile.dietary_preferences || []));
        setSelectedCuisines(
          new Set(
            (profile.cuisine_preferences || []).map(
              (c: string | { cuisine_region: string }) =>
                typeof c === "string" ? c : c.cuisine_region
            )
          )
        );
      })
      .catch(() => {});
  }, [user]);

  function toggleItem(set: Set<string>, item: string): Set<string> {
    const next = new Set(set);
    if (next.has(item)) next.delete(item);
    else next.add(item);
    return next;
  }

  async function handleSave() {
    if (!user) return;
    setSaving(true);
    setSaveStatus(null);
    try {
      await updateHealthContext(user.id, Array.from(selectedConditions));
      await updatePreferences(
        user.id,
        Array.from(selectedDiet),
        Array.from(selectedCuisines)
      );
      setSaveStatus("Saved!");
      setTimeout(() => setSaveStatus(null), 2000);
    } catch {
      setSaveStatus("Could not save. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="px-4 pt-8 pb-32 max-w-[480px] mx-auto">
      <div className="flex items-center justify-between mb-6">
        <Link href="/" className="text-[#A0674B] text-[15px]">
          ← Back
        </Link>
        <h1
          className="text-[20px]"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Profile
        </h1>
        <div className="w-12" />
      </div>

      {/* Health Context */}
      <Card className="mb-4">
        <h2
          className="text-[17px] mb-1"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Health Context
        </h2>
        <p className="text-[13px] text-[#D4B896] mb-3">
          Optional — helps personalize your food suggestions
        </p>
        <div className="flex flex-wrap gap-2">
          {HEALTH_CONDITIONS.map((cond) => (
            <button
              key={cond.id}
              onClick={() =>
                setSelectedConditions(toggleItem(selectedConditions, cond.id))
              }
              className={`px-3 py-1.5 rounded-full text-[13px] border transition-all ${
                selectedConditions.has(cond.id)
                  ? "bg-[#A0674B] text-white border-[#A0674B]"
                  : "bg-white text-[#6B4226] border-[#E8D5C4]"
              }`}
            >
              {cond.label}
            </button>
          ))}
        </div>
        <p className="text-[11px] text-[#D4B896] mt-3 italic">
          This information stays on your device. Nursh provides nutritional
          information, not medical advice.
        </p>
      </Card>

      {/* Dietary Preferences */}
      <Card className="mb-4">
        <h2
          className="text-[17px] mb-3"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Dietary Preferences
        </h2>
        <div className="flex flex-wrap gap-2">
          {DIETARY_PREFS.map((pref) => (
            <button
              key={pref.id}
              onClick={() =>
                setSelectedDiet(toggleItem(selectedDiet, pref.id))
              }
              className={`px-3 py-1.5 rounded-full text-[13px] border transition-all ${
                selectedDiet.has(pref.id)
                  ? "bg-[#6B4226] text-white border-[#6B4226]"
                  : "bg-white text-[#6B4226] border-[#E8D5C4]"
              }`}
            >
              {pref.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Cuisine Preferences */}
      <Card className="mb-4">
        <h2
          className="text-[17px] mb-3"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Cuisine Preferences
        </h2>
        <div className="flex flex-wrap gap-2">
          {CUISINES.map((cuisine) => (
            <button
              key={cuisine.id}
              onClick={() =>
                setSelectedCuisines(toggleItem(selectedCuisines, cuisine.id))
              }
              className={`px-3 py-1.5 rounded-full text-[13px] border transition-all ${
                selectedCuisines.has(cuisine.id)
                  ? "bg-[#C9A87C] text-white border-[#C9A87C]"
                  : "bg-white text-[#6B4226] border-[#E8D5C4]"
              }`}
            >
              {cuisine.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Privacy */}
      <Card className="mb-4">
        <h2
          className="text-[17px] mb-3"
          style={{ fontFamily: "var(--font-serif)" }}
        >
          Privacy & Data
        </h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[15px]">Journal entries</span>
            <span className="text-[13px] text-[#7A9E7E]">Stored securely</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[15px]">Health profile</span>
            <span className="text-[13px] text-[#7A9E7E]">Encrypted</span>
          </div>
          <div className="pt-2 space-y-2">
            <Button variant="secondary" className="w-full">
              Export My Data (JSON)
            </Button>
            <Button variant="destructive" className="w-full">
              Delete All My Data
            </Button>
          </div>
        </div>
      </Card>

      <Button className="w-full" onClick={handleSave} disabled={saving}>
        {saving ? "Saving..." : "Save Profile"}
      </Button>

      {saveStatus && (
        <p
          className={`text-center text-[13px] mt-3 ${
            saveStatus === "Saved!" ? "text-[#7A9E7E]" : "text-[#B87358]"
          }`}
        >
          {saveStatus}
        </p>
      )}

      {/* Sign Out */}
      <div className="mt-8 mb-4">
        <button
          onClick={signOut}
          className="w-full text-center text-[13px] text-[#C9A87C] hover:text-[#A0674B] py-2"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
