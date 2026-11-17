# HealthSutra

HealthSutra is a document-grounded public health awareness chatbot.

## What makes this different
- Answers are generated only from approved WHO and Government of India documents.
- If evidence is missing, the system refuses the question instead of guessing.
- Every factual answer includes validated citations.
- Emergency and unsafe prompts are intercepted by safety rules.

## Stack
- Backend: FastAPI, SQLAlchemy, Pydantic, FAISS, Sentence Transformers, Groq API (optional)
- Frontend: React, Vite, Tailwind
- Data: Approved source registry + FAISS metadata + SQLite/PostgreSQL
- Evaluation: Grounded vs ungrounded benchmark over 50 calibrated questions

## Run backend locally
1. Create and activate virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start API:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Run frontend locally
1. Install dependencies:
   - `npm install`
2. Configure API URL:
   - Copy `frontend/.env.example` to `frontend/.env`
3. Start app:
   - `npm run dev`

## Run tests
- Backend tests:
  - `pytest -q`

## Run evaluation benchmark
- `python evaluation/run_benchmark.py`
- Output files:
  - `evaluation/evaluation_summary.json`
  - `evaluation/grounded_results.json`
  - `evaluation/ungrounded_results.json`

## Docker Compose
- Build and run all services:
  - `docker compose up --build`

Services:
- `backend` on `http://localhost:8000`
- `frontend` on `http://localhost:5173`
- `postgres` on `localhost:5432`
