export type CandidateFilters = {
  search: string;
  minScore: number;
  sort: "score" | "name" | "created";
  page: number;
  limit: number;
};

export type AnalyzePayload = {
  job_description_id?: number;
  candidate_ids?: number[];
};

