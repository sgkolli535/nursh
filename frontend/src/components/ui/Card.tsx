import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export default function Card({
  hoverable = false,
  className = "",
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={`bg-white rounded-[16px] p-4 shadow-[0_1px_4px_rgba(62,33,23,0.08)] ${
        hoverable
          ? "transition-shadow duration-200 hover:shadow-[0_4px_12px_rgba(62,33,23,0.12)]"
          : ""
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
