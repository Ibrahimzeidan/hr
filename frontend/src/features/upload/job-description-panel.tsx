"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { FileUp } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useJobDescriptionUpload } from "@/hooks/use-upload";

const schema = z.object({ content: z.string().min(0) });
type FormValues = z.infer<typeof schema>;

export function JobDescriptionPanel() {
  const [file, setFile] = useState<File | undefined>();
  const mutation = useJobDescriptionUpload();
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { content: "" } });

  function submit(values: FormValues) {
    mutation.mutate({ content: values.content, file });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Description</CardTitle>
        <CardDescription>Paste the JD or attach a document.</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
          <Textarea placeholder="Paste job description..." {...form.register("content")} />
          <label className="flex cursor-pointer items-center gap-3 rounded-md border p-3 text-sm hover:bg-muted">
            <FileUp className="h-4 w-4 text-primary" />
            <span className="min-w-0 flex-1 truncate">{file?.name ?? "Attach PDF, DOC, or DOCX"}</span>
            <input type="file" accept=".pdf,.doc,.docx" hidden onChange={(event) => setFile(event.target.files?.[0])} />
          </label>
          <Button disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Saving..." : "Save job description"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

