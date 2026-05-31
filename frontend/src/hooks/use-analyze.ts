"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { analyze } from "@/services/api";
import { useAppStore } from "@/store/app-store";

export function useAnalyze() {
  const jobDescriptionId = useAppStore((state) => state.jobDescriptionId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => analyze({ job_description_id: jobDescriptionId }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["candidates"] });
      toast.success("Ranking refreshed");
    },
    onError: (error) => toast.error(error.message)
  });
}

