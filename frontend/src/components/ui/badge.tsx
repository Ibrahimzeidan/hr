import * as React from "react";

import { cn } from "@/lib/utils";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & { tone?: "default" | "success" | "warning" | "danger" };

export function Badge({ className, tone = "default", ...props }: BadgeProps) {
  const tones = {
    default: "bg-muted text-muted-foreground",
    success: "bg-emerald-500/10 text-emerald-600",
    warning: "bg-amber-500/10 text-amber-600",
    danger: "bg-rose-500/10 text-rose-600"
  };
  return <span className={cn("inline-flex rounded-md px-2 py-1 text-xs font-medium", tones[tone], className)} {...props} />;
}

