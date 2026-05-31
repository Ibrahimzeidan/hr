export type AnalysisResult = {
  matching_skills: string[];
  missing_skills: string[];
  semantic_similarity: number;
  keyword_score: number;
  explanation: string;
};

export type Candidate = {
  id: number;
  full_name: string;
  email: string | null;
  phone: string | null;
  resume_url: string;
  score: number;
  rank: number | null;
  created_at: string;
  skills: string[];
  analysis: AnalysisResult | null;
};

export type CandidateList = {
  items: Candidate[];
  total: number;
  page: number;
  limit: number;
};

export type JobDescription = {
  id: number;
  content: string;
  created_at: string;
};

export type UploadResponse = {
  candidates: Candidate[];
};

