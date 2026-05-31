"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { uploadJobDescription, uploadResumes } from "@/services/api";
import { useAppStore } from "@/store/app-store";

export function useResumeUpload() {
  const [progress, setProgress] = useState(0);
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (files: File[]) => uploadResumes(files, setProgress),
    onMutate: () => setProgress(0),
    onSuccess: async (data) => {
      await queryClient.invalidateQueries({ queryKey: ["candidates"] });
      toast.success(`${data.candidates.length} resume${data.candidates.length > 1 ? "s" : ""} uploaded`);
      setProgress(100);
    },
    onError: (error) => toast.error(error.message)
  });
  return { ...mutation, progress };
}

export function useJobDescriptionUpload() {
  const setJobDescriptionId = useAppStore((state) => state.setJobDescriptionId);
  return useMutation({
    mutationFn: ({ content, file }: { content: string; file?: File }) => uploadJobDescription(content, file),
    onSuccess: (data) => {
      setJobDescriptionId(data.id);
      toast.success("Job description saved");
    },
    onError: (error) => toast.error(error.message)
  });
}
