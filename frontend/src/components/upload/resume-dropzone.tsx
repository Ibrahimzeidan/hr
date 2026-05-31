"use client";

import { Eye, FileText, UploadCloud, X } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const allowed = [".pdf", ".doc", ".docx"];
const maxBytes = 8 * 1024 * 1024;

type Props = {
  files: File[];
  onFiles: (files: File[]) => void;
  progress: number;
  uploading: boolean;
};

export function ResumeDropzone({ files, onFiles, progress, uploading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function accept(next: FileList | File[]) {
    const valid = Array.from(next).filter(
      (file) => allowed.some((ext) => file.name.toLowerCase().endsWith(ext)) && file.size <= maxBytes
    );
    if (valid.length !== next.length) toast.error("Use PDF, DOC, or DOCX files under 8 MB");
    onFiles([...files, ...valid]);
  }

  return (
    <div
      onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => { event.preventDefault(); setDragging(false); accept(event.dataTransfer.files); }}
      className={cn("rounded-lg border border-dashed bg-card p-6 transition", dragging && "border-primary bg-primary/5")}
    >
      <input ref={inputRef} type="file" multiple accept={allowed.join(",")} hidden onChange={(event) => accept(event.target.files ?? [])} />
      <div className="grid place-items-center gap-3 text-center">
        <UploadCloud className="h-9 w-9 text-primary" />
        <div>
          <p className="font-medium">Drop resumes here</p>
          <p className="text-sm text-muted-foreground">PDF, DOC, or DOCX</p>
        </div>
        <Button type="button" variant="outline" onClick={() => inputRef.current?.click()}>Select files</Button>
      </div>
      {files.length ? (
        <div className="mt-5 space-y-2">
          {files.map((file, index) => (
            <div key={`${file.name}-${index}`} className="flex items-center gap-3 rounded-md border p-3">
              <FileText className="h-4 w-4 text-primary" />
              <span className="min-w-0 flex-1 truncate text-sm">{file.name}</span>
              <Button type="button" size="icon" variant="ghost" onClick={() => window.open(URL.createObjectURL(file))}>
                <Eye className="h-4 w-4" />
              </Button>
              <Button type="button" size="icon" variant="ghost" onClick={() => onFiles(files.filter((_, item) => item !== index))}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      ) : null}
      {uploading ? <Progress className="mt-5" value={progress} /> : null}
    </div>
  );
}
