"use client";

import { ExportButtons } from "@/features/export/export-buttons";
import { CandidateTable } from "@/features/ranking/candidate-table";
import { CandidateFilters } from "@/features/search/candidate-filters";
import { PageHeading } from "@/components/shared/page-heading";

export function CandidatesPage() {
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Talent Pool"
        title="Candidates"
        description="Search, filter, sort, inspect, and export ranked applicants."
        action={<ExportButtons />}
      />
      <CandidateFilters />
      <CandidateTable />
    </div>
  );
}

