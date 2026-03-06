"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirmSent, setConfirmSent] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { display_name: displayName || email.split("@")[0] },
          },
        });
        if (error) throw error;
        setConfirmSent(true);
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        router.push("/");
        router.refresh();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (confirmSent) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <Card className="w-full max-w-sm !p-8 text-center">
          <span className="text-4xl mb-4 block">🌱</span>
          <h1
            className="text-[24px] text-[#3E2117] mb-2"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Check your email
          </h1>
          <p className="text-[15px] text-[#A0674B]/70 mb-6">
            We sent a confirmation link to <strong>{email}</strong>. Click it to
            activate your account.
          </p>
          <Button
            variant="secondary"
            className="w-full"
            onClick={() => setConfirmSent(false)}
          >
            Back to login
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-sm !p-8">
        {/* Branding */}
        <div className="text-center mb-8">
          <span className="text-4xl mb-3 block">🌱</span>
          <h1
            className="text-[28px] text-[#3E2117] mb-1"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            nursh
          </h1>
          <p className="text-[14px] text-[#A0674B]/60">
            A smarter way to eat well
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignUp && (
            <div>
              <label className="text-[13px] font-medium text-[#6B4226] mb-1 block">
                Your name
              </label>
              <Input
                type="text"
                placeholder="How should we greet you?"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>
          )}

          <div>
            <label className="text-[13px] font-medium text-[#6B4226] mb-1 block">
              Email
            </label>
            <Input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-[13px] font-medium text-[#6B4226] mb-1 block">
              Password
            </label>
            <Input
              type="password"
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {error && (
            <p className="text-[13px] text-[#B87358] bg-[#B87358]/10 px-3 py-2 rounded-[8px]">
              {error}
            </p>
          )}

          <Button className="w-full" disabled={loading}>
            {loading
              ? "Loading..."
              : isSignUp
                ? "Create Account"
                : "Sign In"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
            }}
            className="text-[13px] text-[#A0674B] hover:underline"
          >
            {isSignUp
              ? "Already have an account? Sign in"
              : "New here? Create an account"}
          </button>
        </div>
      </Card>
    </div>
  );
}
