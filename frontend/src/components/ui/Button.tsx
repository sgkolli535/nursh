"use client";

import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "destructive";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-[#6B4226] text-white shadow-[0_2px_8px_rgba(62,33,23,0.15)] hover:brightness-90",
  secondary: "bg-[#E8D5C4] text-[#6B4226] hover:brightness-95",
  ghost: "bg-transparent text-[#A0674B] hover:bg-[#FAF6F1]",
  destructive: "bg-[#B87358] text-white hover:brightness-90",
};

export default function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`min-h-[48px] px-4 rounded-[12px] font-semibold text-[15px] transition-all duration-200 cursor-pointer ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
