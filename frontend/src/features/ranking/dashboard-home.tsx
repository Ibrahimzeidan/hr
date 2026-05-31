"use client";

import { Award, Gauge, Users } from "lucide-react";

import { ScoreDistribution } from "@/components/charts/score-distribution";
import { CandidateTable } from "@/features/ranking/candidate-table";
import { CandidateFilters } from "@/features/search/candidate-filters";
import { ExportButtons } from "@/features/export/export-buttons";
import { MetricCard } from "@/components/shared/metric-card";
import { PageHeading } from "@/components/shared/page-heading";
import { useCandidates } from "@/hooks/use-candidates";

export function DashboardHome() {
  const { data } = useCandidates();
  const candidates = data?.items ?? [];
  const top = candidates[0];
  const avg = candidates.length
    ? Math.round(candidates.reduce((total, item) => total + item.score, 0) / candidates.length)
    : 0;

  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Screening"
        title="Candidate Ranking Dashboard"
        description="Review ranked candidates, inspect fit signals, and export shortlist data."
        action={<ExportButtons />}
      />
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Candidates" value={String(data?.total ?? 0)} hint="Total resumes indexed" icon={Users} />
        <MetricCard label="Average Score" value={`${avg}/100`} hint="Across visible candidates" icon={Gauge} />
        <MetricCard label="Top Candidate" value={top?.full_name ?? "-"} hint={top ? `${top.score}/100 match` : "Waiting for analysis"} icon={Award} />
      </div>
      <ScoreDistribution candidates={candidates} />
      <CandidateFilters />
      <CandidateTable />
    </div>
  );
}

