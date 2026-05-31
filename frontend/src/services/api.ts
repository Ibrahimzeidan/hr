import type { AnalyzePayload, CandidateFilters } from "@/types/api";
import type { Candidate, CandidateList, JobDescription, UploadResponse } from "@/types/candidate";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ErrorBody = { detail?: string | { msg: string }[] };

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers
  });
  if (!response.ok) throw new Error(await errorMessage(response));
  return response.json() as Promise<T>;
}

async function errorMessage(response: Response) {
  const body = (await response.json().catch(() => null)) as ErrorBody | null;
  if (typeof body?.detail === "string") return body.detail;
  return `Request failed with status ${response.status}`;
}

export function listCandidates(filters: CandidateFilters) {
  const params = new URLSearchParams({
    search: filters.search,
    min_score: String(filters.minScore),
    sort: filters.sort,
    page: String(filters.page),
    limit: String(filters.limit)
  });
  return requestJson<CandidateList>(`/candidates?${params.toString()}`);
}

export function getCandidate(id: number) {
  return requestJson<Candidate>(`/candidate/${id}`);
}

export function uploadJobDescription(content: string, file?: File) {
  const form = new FormData();
  if (content) form.append("content", content);
  if (file) form.append("file", file);
  return fetch(`${API_URL}/upload-job-description`, { method: "POST", body: form }).then(async (res) => {
    if (!res.ok) throw new Error(await errorMessage(res));
    return res.json() as Promise<JobDescription>;
  });
}

export function analyze(payload: AnalyzePayload) {
  return requestJson<{ candidates: Candidate[] }>("/analyze", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function uploadResumes(files: File[], onProgress: (value: number) => void) {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  return new Promise<UploadResponse>((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/upload-resumes`);
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress(Math.round((event.loaded / event.total) * 100));
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText) as UploadResponse);
      else reject(new Error(xhr.responseText || "Upload failed"));
    };
    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(form);
  });
}

export const exportUrl = (format: "csv" | "excel") => `${API_URL}/download/${format}`;
