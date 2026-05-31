import { AppShell } from "@/components/layout/app-shell";
import { CandidateDetailsPage } from "@/features/ranking/candidate-details-page";

export default async function CandidateRoute({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell>
      <CandidateDetailsPage id={Number(id)} />
    </AppShell>
  );
}

