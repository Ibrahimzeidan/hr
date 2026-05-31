"use client";

import { Mail, Phone } from "lucide-react";

import { SkillList } from "@/components/candidate/skill-list";
import { ScoreRing } from "@/components/shared/score-ring";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import type { Candidate } from "@/types/candidate";

type Props = {
  candidate: Candidate | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function CandidateDetailModal({ candidate, open, onOpenChange }: Props) {
  if (!candidate) return null;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{candidate.full_name}</DialogTitle>
          <DialogDescription>Rank #{candidate.rank ?? "-"} candidate profile</DialogDescription>
        </DialogHeader>
        <div className="grid gap-5 md:grid-cols-[auto_1fr]">
          <ScoreRing score={candidate.score} />
          <div className="space-y-2 text-sm">
            <p className="flex items-center gap-2"><Mail className="h-4 w-4" />{candidate.email ?? "No email found"}</p>
            <p className="flex items-center gap-2"><Phone className="h-4 w-4" />{candidate.phone ?? "No phone found"}</p>
            <p className="text-muted-foreground">{candidate.analysis?.explanation ?? "No analysis available yet."}</p>
          </div>
        </div>
        <section className="space-y-2">
          <h4 className="text-sm font-semibold">Matching Skills</h4>
          <SkillList skills={candidate.analysis?.matching_skills ?? []} tone="success" />
        </section>
        <section className="space-y-2">
          <h4 className="text-sm font-semibold">Missing Skills</h4>
          <SkillList skills={candidate.analysis?.missing_skills ?? []} tone="danger" />
        </section>
      </DialogContent>
    </Dialog>
  );
}

