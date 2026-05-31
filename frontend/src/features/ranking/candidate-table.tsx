"use client";

import { FileSearch } from "lucide-react";
import { useState } from "react";

import { CandidateDetailModal } from "@/components/candidate/candidate-detail-modal";
import { CandidateRow } from "@/components/candidate/candidate-row";
import { ResumePreviewModal } from "@/components/candidate/resume-preview-modal";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useCandidates } from "@/hooks/use-candidates";
import { useAppStore } from "@/store/app-store";
import type { Candidate } from "@/types/candidate";

export function CandidateTable() {
  const { data, isLoading, isError } = useCandidates();
  const [details, setDetails] = useState<Candidate | null>(null);
  const [preview, setPreview] = useState<Candidate | null>(null);
  const filters = useAppStore((state) => state.filters);
  const setFilters = useAppStore((state) => state.setFilters);

  if (isLoading) return <Skeleton className="h-72 w-full" />;
  if (isError) return <EmptyState icon={FileSearch} title="Candidates unavailable" text="The API did not return a ranked list." />;
  if (!data?.items.length) return <EmptyState icon={FileSearch} title="No candidates yet" text="Upload resumes and run an analysis." />;

  const maxPage = Math.max(1, Math.ceil(data.total / filters.limit));
  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Candidate</TableHead>
                <TableHead>Score</TableHead>
                <TableHead className="hidden md:table-cell">Matched</TableHead>
                <TableHead className="hidden lg:table-cell">Missing</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((candidate) => <CandidateRow key={candidate.id} candidate={candidate} onDetails={setDetails} onPreview={setPreview} />)}
            </TableBody>
          </Table>
        </div>
        <div className="flex items-center justify-between border-t p-4 text-sm">
          <span className="text-muted-foreground">Page {filters.page} of {maxPage}</span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={filters.page <= 1} onClick={() => setFilters({ page: filters.page - 1 })}>Previous</Button>
            <Button variant="outline" size="sm" disabled={filters.page >= maxPage} onClick={() => setFilters({ page: filters.page + 1 })}>Next</Button>
          </div>
        </div>
      </CardContent>
      <CandidateDetailModal candidate={details} open={Boolean(details)} onOpenChange={(open) => !open && setDetails(null)} />
      <ResumePreviewModal candidate={preview} open={Boolean(preview)} onOpenChange={(open) => !open && setPreview(null)} />
    </Card>
  );
}

