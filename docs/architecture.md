# Architecture

## System Architecture

Resume Ranker is split into an independently deployable Next.js frontend and FastAPI backend. The frontend runs on Vercel and communicates with the API through `NEXT_PUBLIC_API_URL`. The backend runs on Render, stores metadata and analysis in Neon PostgreSQL, and uploads resume files to Cloudinary because Render storage is ephemeral.

```text
Browser -> Vercel Next.js -> Render FastAPI -> Neon PostgreSQL
                                      |
                                      +-> Cloudinary resume files
```

## Backend Design

The API is organized by responsibility:

- `api/routes`: upload, analysis, candidates, and export endpoints
- `services`: orchestration, ranking, scoring, parsing, and export logic
- `ai`: resume/JD parsing, keyword extraction, semantic similarity
- `database`: SQLAlchemy models and Alembic migrations
- `storage`: Cloudinary upload integration

Routes remain thin and delegate business logic to services. Pydantic validates request and response boundaries.

## Frontend Design

The frontend uses App Router pages as small shells that compose feature modules. TanStack Query owns server state, Zustand owns table filters and selected JD state, and React Hook Form with Zod handles JD form validation. ShadCN-style primitives keep the UI consistent while feature components stay below 100 lines.

## AI Scoring Methodology

The final score is normalized to `0-100`:

- Skills match: 50%
- Experience relevance: 25%
- Education alignment: 15%
- Keyword similarity: 10%

Skill matching uses exact controlled-vocabulary extraction plus a semantic adjustment. Experience compares extracted years against JD requirements. Education checks JD degree terms against resume education lines. Keyword similarity uses TF-IDF keyword overlap.

## Semantic Matching

`sentence-transformers/all-MiniLM-L6-v2` is used when available. If the model cannot load, the service falls back to scikit-learn TF-IDF cosine similarity so analysis remains functional in constrained environments and tests.

## Database Design

Tables:

- `candidates`: profile, resume URL, extracted text, score, rank
- `skills`: normalized skills catalog
- `candidate_skills`: many-to-many candidate skill links
- `job_descriptions`: stored JD content
- `analysis_results`: matched skills, missing skills, semantic similarity, keyword score, explanation

Ranks are recalculated after each analysis so dashboard ordering is deterministic.

## Security And Validation

Uploads are limited by extension and size, text inputs are sanitized, CORS is restricted to configured frontend origins, and SlowAPI applies request rate limits. Production resume files are stored in Cloudinary rather than local disk.

## Deployment Assumptions

Render runs the backend Dockerfile and executes `alembic upgrade head` before starting Uvicorn. Vercel builds the frontend with `NEXT_PUBLIC_API_URL` pointing at Render. Neon requires a PostgreSQL URL using SSL. Cloudinary credentials must be present in production.

