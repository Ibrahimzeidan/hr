import { AppShell } from "@/components/layout/app-shell";
import { CandidatesPage } from "@/features/ranking/candidates-page";

export default function CandidatesRoute() {
  return (
    <AppShell>
      <CandidatesPage />
    </AppShell>
  );
}

