import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function scoreTone(score?: number) {
  if ((score ?? 0) >= 80) return "text-emerald-600";
  if ((score ?? 0) >= 60) return "text-amber-600";
  return "text-rose-600";
}

