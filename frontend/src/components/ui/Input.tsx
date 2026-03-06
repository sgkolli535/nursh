"use client";

import { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export default function Input({ className = "", ...props }: InputProps) {
  return (
    <input
      className={`w-full px-4 py-3 bg-[#E8D5C4]/50 rounded-[12px] border border-[#C9A87C] text-[#3E2117] text-[15px] placeholder:text-[#D4B896] focus:bg-[#E8D5C4] focus:border-[#A0674B] focus:border-2 focus:outline-none transition-all duration-200 ${className}`}
      {...props}
    />
  );
}
