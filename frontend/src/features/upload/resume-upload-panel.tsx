"use client";

import { useState } from "react";

import { ResumeDropzone } from "@/components/upload/resume-dropzone";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useResumeUpload } from "@/hooks/use-upload";

export function ResumeUploadPanel() {
  const [files, setFiles] = useState<File[]>([]);
  const upload = useResumeUpload();

  async function submit() {
    await upload.mutateAsync(files);
    setFiles([]);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resume Intake</CardTitle>
        <CardDescription>Upload one or many candidate resumes.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <ResumeDropzone files={files} onFiles={setFiles} progress={upload.progress} uploading={upload.isPending} />
        <Button disabled={!files.length || upload.isPending} onClick={submit}>
          {upload.isPending ? "Uploading..." : "Upload resumes"}
        </Button>
      </CardContent>
    </Card>
  );
}

