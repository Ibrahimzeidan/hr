"use client";

import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import { useAppStore } from "@/store/app-store";

export function CandidateFilters() {
  const filters = useAppStore((state) => state.filters);
  const setFilters = useAppStore((state) => state.setFilters);
  return (
    <div className="grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-[1fr_160px_160px]">
      <label className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Search candidates"
          value={filters.search}
          onChange={(event) => setFilters({ search: event.target.value, page: 1 })}
        />
      </label>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        value={filters.sort}
        onChange={(event) => setFilters({ sort: event.target.value as typeof filters.sort, page: 1 })}
      >
        <option value="score">Sort by score</option>
        <option value="name">Sort by name</option>
        <option value="created">Newest first</option>
      </select>
      <label className="flex items-center gap-3 rounded-md border bg-background px-3">
        <span className="text-xs text-muted-foreground">Min</span>
        <input
          type="range"
          min={0}
          max={100}
          value={filters.minScore}
          onChange={(event) => setFilters({ minScore: Number(event.target.value), page: 1 })}
          className="min-w-0 flex-1"
        />
        <span className="w-7 text-right text-sm">{filters.minScore}</span>
      </label>
    </div>
  );
}

