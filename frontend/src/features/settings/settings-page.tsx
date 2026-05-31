import { CheckCircle2 } from "lucide-react";

import { PageHeading } from "@/components/shared/page-heading";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const items = ["Vercel frontend", "Render FastAPI backend", "Neon PostgreSQL", "Cloudinary resume storage", "Strict validation", "Rate limiting"];

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeading eyebrow="Operations" title="Settings" description="Production configuration checklist for the screening platform." />
      <Card>
        <CardHeader><CardTitle>Deployment Readiness</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {items.map((item) => (
            <div key={item} className="flex items-center gap-3 rounded-md border p-3 text-sm">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              {item}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

