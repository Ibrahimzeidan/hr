# Resume Ranker

AI-powered resume screening and candidate ranking platform built as a production-style full-stack SaaS assessment project.

## Project Overview

Resume Ranker lets HR teams upload resumes, provide a job description, analyze fit, and review candidates ranked from highest to lowest match. The backend parses documents, extracts candidate signals, computes weighted scores, stores resumes in Cloudinary, persists data in PostgreSQL, and exports ranked results.

## Features

- Single and bulk resume upload with PDF, DOC, and DOCX validation
- Job description paste or document upload
- Resume parsing for contact details, skills, education, experience, certifications, and projects
- Weighted scoring: skills 50%, experience 25%, education 15%, keyword similarity 10%
- Semantic similarity via sentence-transformers with TF-IDF fallback
- Ranked dashboard with search, sorting, filtering, pagination, detail modal, and resume preview
- CSV and Excel export
- Responsive light/dark HR SaaS interface
- Rate limiting, sanitization, environment-based configuration, CORS, and Cloudinary storage

## Tech Stack

Frontend: Next.js 15 App Router, TypeScript, TailwindCSS, ShadCN-style UI, Framer Motion, React Hook Form, Zod, Zustand, TanStack Query.

Backend: FastAPI, Python 3.12+, SQLAlchemy, Alembic, PostgreSQL, Pydantic, spaCy, sentence-transformers, scikit-learn, PyMuPDF, python-docx, pandas, openpyxl.

Deployment: Vercel frontend, Render backend, Neon PostgreSQL, Cloudinary resume storage.

## Folder Structure

```text
backend/app
  api/routes          FastAPI endpoints
  ai                  parsing, keywords, semantic matching
  database            SQLAlchemy models and Alembic migrations
  schemas             Pydantic contracts
  services            business logic and exports
  storage             Cloudinary integration
frontend/src
  app                 Next.js routes
  components          UI, layout, dashboard, upload, candidate views
  features            upload, analysis, ranking, export, search
  hooks               TanStack Query hooks
  services            API client
  store               Zustand state
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
```

## Local Setup

```bash
cd backend
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` and set `NEXT_PUBLIC_API_URL` to the FastAPI URL.

## API Documentation

- `POST /upload-resumes`
- `POST /upload-job-description`
- `POST /analyze`
- `GET /candidates`
- `GET /candidate/{id}`
- `GET /download/csv`
- `GET /download/excel`
- `GET /health`

FastAPI interactive docs are available at `/docs`.

## Deployment Guide

1. Create a Neon PostgreSQL database and copy the connection string.
2. Create a Cloudinary account and copy cloud name, API key, and API secret.
3. Deploy `backend/` on Render using `render.yaml` or the included Dockerfile.
4. Set backend env vars on Render, including `FRONTEND_URL`.
5. Deploy `frontend/` on Vercel and set `NEXT_PUBLIC_API_URL` to the Render backend URL.
6. Run Alembic migrations during backend startup; the Dockerfile already does this.

## Tests

```bash
cd backend && python -m pytest
cd frontend && npm run lint && npm run test && npm run build
```

## Screenshots

Add screenshots here after deployment:

- Landing page
- Analysis workspace
- Ranked candidates dashboard
- Candidate details modal

