import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

export function EmptyState({ icon: Icon, title, text }: { icon: LucideIcon; title: string; text: string }) {
  return (
    <Card>
      <CardContent className="grid place-items-center gap-3 py-12 text-center">
        <div className="rounded-md bg-muted p-3 text-muted-foreground">
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{text}</p>
        </div>
      </CardContent>
    </Card>
  );
}

