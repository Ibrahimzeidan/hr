"use client";

import { useQuery } from "@tanstack/react-query";

import { listCandidates } from "@/services/api";
import { useAppStore } from "@/store/app-store";

export function useCandidates() {
  const filters = useAppStore((state) => state.filters);
  return useQuery({
    queryKey: ["candidates", filters],
    queryFn: () => listCandidates(filters)
  });
}

