"use client";

import { Eye, UserRound } from "lucide-react";

import { SkillList } from "@/components/candidate/skill-list";
import { ScoreRing } from "@/components/shared/score-ring";
import { Button } from "@/components/ui/button";
import { TableCell, TableRow } from "@/components/ui/table";
import type { Candidate } from "@/types/candidate";

type Props = {
  candidate: Candidate;
  onDetails: (candidate: Candidate) => void;
  onPreview: (candidate: Candidate) => void;
};

export function CandidateRow({ candidate, onDetails, onPreview }: Props) {
  return (
    <TableRow>
      <TableCell className="font-medium">#{candidate.rank ?? "-"}</TableCell>
      <TableCell>
        <div className="font-medium">{candidate.full_name}</div>
        <div className="text-xs text-muted-foreground">{candidate.email ?? "Email unavailable"}</div>
      </TableCell>
      <TableCell><ScoreRing score={candidate.score} /></TableCell>
      <TableCell className="hidden min-w-56 md:table-cell">
        <SkillList skills={candidate.analysis?.matching_skills ?? candidate.skills} tone="success" />
      </TableCell>
      <TableCell className="hidden min-w-48 lg:table-cell">
        <SkillList skills={candidate.analysis?.missing_skills ?? []} tone="danger" />
      </TableCell>
      <TableCell className="text-right">
        <div className="flex justify-end gap-2">
          <Button variant="ghost" size="icon" onClick={() => onPreview(candidate)}><Eye className="h-4 w-4" /></Button>
          <Button variant="outline" size="sm" onClick={() => onDetails(candidate)}><UserRound className="h-4 w-4" />Details</Button>
        </div>
      </TableCell>
    </TableRow>
  );
}

