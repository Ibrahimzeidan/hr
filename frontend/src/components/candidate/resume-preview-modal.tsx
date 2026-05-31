"use client";

import { ExternalLink } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import type { Candidate } from "@/types/candidate";

type Props = {
  candidate: Candidate | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function ResumePreviewModal({ candidate, open, onOpenChange }: Props) {
  if (!candidate) return null;
  const canEmbed = candidate.resume_url.startsWith("http");
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{candidate.full_name} Resume</DialogTitle>
          <DialogDescription>Uploaded resume source</DialogDescription>
        </DialogHeader>
        {canEmbed ? (
          <iframe title={`${candidate.full_name} resume`} src={candidate.resume_url} className="h-[65vh] w-full rounded-md border" />
        ) : (
          <div className="rounded-md border bg-muted p-6 text-sm text-muted-foreground">Cloudinary credentials are not configured for this local upload.</div>
        )}
        <Button asChild variant="outline"><a href={candidate.resume_url} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4" />Open source</a></Button>
      </DialogContent>
    </Dialog>
  );
}

