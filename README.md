# Resume Ranker

AI-powered resume screening and candidate ranking platform built as a production-style full-stack SaaS assessment project.

## Project Overview

Resume Ranker lets HR teams upload resumes, provide a job description, analyze fit, and review candidates ranked from highest to lowest match. The backend parses documents, extracts candidate signals, computes weighted scores, enhances analysis with Google Gemini AI, stores resumes in Cloudinary, persists data in PostgreSQL, and exports ranked results.

## Features

- Single and bulk resume upload with PDF, DOC, and DOCX validation
- Job description paste or document upload
- Resume parsing for contact details, skills, education, experience, certifications, and projects
- **Deterministic scoring engine**: skills 50%, experience 25%, education 15%, keyword similarity 10%
- **Google Gemini AI integration** for enhanced candidate insights (with graceful fallback)
- Semantic similarity via sentence-transformers with TF-IDF fallback
- Ranked dashboard with search, sorting, filtering, pagination, detail modal, and resume preview
- CSV and Excel export with AI-enhanced insights
- Responsive light/dark HR SaaS interface
- Rate limiting, sanitization, environment-based configuration, CORS, and Cloudinary storage

## AI Features

### Deterministic Scoring Engine
The scoring system is fully deterministic and transparent:
- **Skills Match (50%)**: Exact skill matching combined with semantic similarity
- **Experience Relevance (25%)**: Years of experience vs requirements
- **Education Alignment (15%)**: Degree/education match with job requirements
- **Keyword Similarity (10%)**: TF-IDF based keyword overlap

### Google Gemini AI Integration
Gemini AI is used ONLY for generating insights, NOT for calculating scores:
- Candidate summaries
- Hiring recommendations (Strong Hire, Hire, Consider, Weak Match, Reject)
- Confidence scores
- Strengths and weaknesses analysis
- Personalized recommendations
- Detailed explanations

**Graceful Fallback**: If `GEMINI_API_KEY` is not configured, the system automatically uses a deterministic local analysis engine that provides consistent, rule-based insights.

## Tech Stack

**Frontend**: Next.js 15 App Router, TypeScript, TailwindCSS, ShadCN-style UI, Framer Motion, React Hook Form, Zod, Zustand, TanStack Query, Vitest, React Testing Library.

**Backend**: FastAPI, Python 3.12+, SQLAlchemy, Alembic, PostgreSQL, Pydantic, spaCy, sentence-transformers, scikit-learn, PyMuPDF, python-docx, pandas, openpyxl, google-generativeai.

**Deployment**: Vercel frontend, Render backend, Supabase PostgreSQL, Cloudinary resume storage.

**CI/CD**: GitHub Actions with automated testing, linting, type checking, and deployment.

## Folder Structure

```text
backend/app
  api/routes          FastAPI endpoints
  ai/                 parsing, keywords, semantic matching, gemini_service.py
  database            SQLAlchemy models and Alembic migrations
  schemas             Pydantic contracts
  services            business logic, scoring, analysis, exports
  storage             Cloudinary integration
  utils               utilities and serializers
frontend/src
  app                 Next.js routes
  components          UI, layout, dashboard, upload, candidate views
  features            upload, analysis, ranking, export, search
  hooks               TanStack Query hooks
  services            API client
  store               Zustand state
  types               TypeScript type definitions
.github/workflows     CI/CD pipeline configuration
```

## Environment Variables

Frontend `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Backend `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
FRONTEND_URL=http://localhost:3000

# AI (Google Gemini) - Optional
# If not set, the system uses deterministic local fallback
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Local Setup

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
# Set DATABASE_URL to your Supabase PostgreSQL connection string
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` and set `NEXT_PUBLIC_API_URL` to the FastAPI URL.

## Running Tests

### Backend Tests

```bash
cd backend
DISABLE_SENTENCE_TRANSFORMERS=1 python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run lint
npm run test
npm run build
```

## API Documentation

- `POST /upload-resumes` - Upload one or more resumes
- `POST /upload-job-description` - Upload or paste a job description
- `POST /analyze` - Analyze candidates against a job description
- `GET /candidates` - List all candidates with pagination
- `GET /candidate/{id}` - Get candidate details
- `GET /download/csv` - Export candidates to CSV
- `GET /download/excel` - Export candidates to Excel
- `GET /health` - Health check endpoint

FastAPI interactive docs are available at `/docs`.

## Output Format

Each candidate analysis returns:

```json
{
  "score": 85.5,
  "rank": 1,
  "matching_skills": ["Python", "React", "PostgreSQL"],
  "missing_skills": ["AWS", "Docker"],
  "strengths": ["Strong technical skill match", "Meets experience requirement"],
  "weaknesses": ["Missing cloud experience"],
  "recommendations": ["Consider upskilling in AWS"],
  "explanation": "Strong alignment across required skills...",
  "candidate_summary": "Experienced developer with 5 years...",
  "hiring_recommendation": "Hire",
  "confidence_score": 85.0
}
```

## Deployment Guide

1. Create a Supabase PostgreSQL database and copy the connection string from Settings > Database.
2. Create a Cloudinary account and copy cloud name, API key, and API secret.
3. (Optional) Get a Google Gemini API key from Google AI Studio.
4. Deploy `backend/` on Render using `render.yaml` or the included Dockerfile.
5. Set backend env vars on Render, including `FRONTEND_URL` and optionally `GEMINI_API_KEY`.
6. Deploy `frontend/` on Vercel and set `NEXT_PUBLIC_API_URL` to the Render backend URL.
7. Run Alembic migrations during backend startup; the Dockerfile already does this.

## CI/CD Pipeline

The GitHub Actions workflow automatically:
- Runs backend tests with pytest
- Runs frontend tests with Vitest
- Performs linting and type checking
- Builds the frontend
- Deploys preview on pull requests
- Deploys to production on main branch

## Production Features

- **Logging**: Comprehensive logging throughout the application
- **Retry Handling**: Automatic retries for API calls with exponential backoff
- **Timeout Handling**: Request timeouts to prevent hanging
- **Rate Limiting**: API rate limiting to prevent abuse
- **Error Monitoring**: Detailed error tracking and reporting
- **Graceful AI Failure Recovery**: Automatic fallback to deterministic analysis
- **Caching**: Response caching to reduce API calls
- **Parallel Processing**: Support for batch analysis of 100+ resumes

## License

MIT