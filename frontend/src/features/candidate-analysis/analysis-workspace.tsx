"use client";

import { motion } from "framer-motion";
import { Play } from "lucide-react";

import { PageHeading } from "@/components/shared/page-heading";
import { Button } from "@/components/ui/button";
import { ResumeUploadPanel } from "@/features/upload/resume-upload-panel";
import { JobDescriptionPanel } from "@/features/upload/job-description-panel";
import { CandidateTable } from "@/features/ranking/candidate-table";
import { useAnalyze } from "@/hooks/use-analyze";

export function AnalysisWorkspace() {
  const analyze = useAnalyze();
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Analysis"
        title="Resume Screening Workspace"
        description="Upload resumes, save a job description, then generate ranked match scores."
        action={<Button disabled={analyze.isPending} onClick={() => analyze.mutate()}><Play className="h-4 w-4" />{analyze.isPending ? "Analyzing..." : "Analyze"}</Button>}
      />
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="grid gap-5 xl:grid-cols-2">
        <ResumeUploadPanel />
        <JobDescriptionPanel />
      </motion.div>
      <CandidateTable />
    </div>
  );
}

