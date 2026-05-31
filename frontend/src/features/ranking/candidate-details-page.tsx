"use client";

import { SkillList } from "@/components/candidate/skill-list";
import { PageHeading } from "@/components/shared/page-heading";
import { ScoreRing } from "@/components/shared/score-ring";
import { Card, CardContent } from "@/components/ui/card";
import { useCandidate } from "@/hooks/use-candidate";

export function CandidateDetailsPage({ id }: { id: number }) {
  const { data, isLoading, isError } = useCandidate(id);
  if (isError) return <div className="text-sm text-muted-foreground">Candidate not found.</div>;
  if (isLoading || !data) return <div className="text-sm text-muted-foreground">Loading candidate...</div>;
  return (
    <div className="space-y-6">
      <PageHeading eyebrow={`Rank #${data.rank ?? "-"}`} title={data.full_name} description={data.analysis?.explanation ?? "Candidate profile"} />
      <Card>
        <CardContent className="grid gap-6 p-6 md:grid-cols-[auto_1fr]">
          <ScoreRing score={data.score} />
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">{data.email ?? "No email"} · {data.phone ?? "No phone"}</p>
            <SkillList skills={data.analysis?.matching_skills ?? data.skills} tone="success" />
            <SkillList skills={data.analysis?.missing_skills ?? []} tone="danger" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
