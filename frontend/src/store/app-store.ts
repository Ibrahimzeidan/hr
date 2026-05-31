import { create } from "zustand";

import type { CandidateFilters } from "@/types/api";

type AppState = {
  jobDescriptionId?: number;
  filters: CandidateFilters;
  setJobDescriptionId: (id: number) => void;
  setFilters: (filters: Partial<CandidateFilters>) => void;
};

export const useAppStore = create<AppState>((set) => ({
  filters: { search: "", minScore: 0, sort: "score", page: 1, limit: 10 },
  setJobDescriptionId: (jobDescriptionId) => set({ jobDescriptionId }),
  setFilters: (filters) =>
    set((state) => ({
      filters: { ...state.filters, ...filters, page: filters.page ?? state.filters.page }
    }))
}));

