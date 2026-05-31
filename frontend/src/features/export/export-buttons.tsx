import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { exportUrl } from "@/services/api";

export function ExportButtons() {
  return (
    <div className="flex flex-wrap gap-2">
      <Button asChild variant="outline">
        <a href={exportUrl("csv")}><Download className="h-4 w-4" />CSV</a>
      </Button>
      <Button asChild variant="outline">
        <a href={exportUrl("excel")}><Download className="h-4 w-4" />Excel</a>
      </Button>
    </div>
  );
}

