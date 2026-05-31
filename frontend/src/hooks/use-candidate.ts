"use client";

import { useQuery } from "@tanstack/react-query";

import { getCandidate } from "@/services/api";

export function useCandidate(id: number) {
  return useQuery({
    queryKey: ["candidate", id],
    queryFn: () => getCandidate(id),
    enabled: Number.isFinite(id)
  });
}

