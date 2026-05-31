import { AppShell } from "@/components/layout/app-shell";
import { AnalysisWorkspace } from "@/features/candidate-analysis/analysis-workspace";

export default function AnalysisPage() {
  return (
    <AppShell>
      <AnalysisWorkspace />
    </AppShell>
  );
}

