# BookDiscoverAI

BookDiscoverAI is a lightweight proof-of-concept for a mobile-first, swipeable book discovery experience. It includes a FastAPI backend for managing settings, demo recommendation data, and structured logging as well as a Vite + React frontend for browsing recommendations, configuring integrations, and reviewing logs.

## Features

- **Mobile-focused UI** – Vertical card layout inspired by swipe feeds, implemented with React.
- **Settings Console** – Configure Audiobookshelf connectivity, metadata providers, and AI engines.
- **Logging Dashboard** – View backend events and simulated client logs directly in the app.
- **Demo Recommendation Engine** – Seed romantasy titles and explanations to showcase the experience without external APIs.
- **Trope Discovery Feed** – Parallel trope-tag pipeline that powers a toggleable recommendations feed with trope matches and explanations.
- **Dockerized Development** – Compose file starts the backend and frontend with a single command.

## Getting Started

### Prerequisites

- Docker and Docker Compose (v2+ recommended)
- Node.js 18+ and pnpm/npm (optional for running the frontend locally without Docker)
- Python 3.11 (optional for running the backend locally without Docker)

### Environment

Copy the example environment file and adjust settings as needed:

```bash
cp .env.example .env
```

All configuration values are optional for the demo. When you provide real API keys or ABS credentials they are persisted in the backend database.

### Run with Docker

```bash
docker compose up --build
```

Services:

- Frontend → http://localhost:5173
- Backend → http://localhost:8000

The backend stores data in a SQLite database inside the container volume `backend_data`.

### Run Backend Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

By default the Vite dev server proxies API requests to `http://localhost:8000`.

### Tests

Backend unit tests are available via pytest:

```bash
cd backend
pytest
```

### Trope Discovery Demo

1. Open the **Settings** tab and queue the trope extraction job.
2. Switch to the **Discover** tab and toggle to the **Trope Feed** to browse trope-matched cards.
3. Use the log viewer to confirm trope-engine events and scores are being recorded.

## Project Structure

```
BookDiscoverAI/
├── backend/          # FastAPI application and tests
├── frontend/         # Vite + React mobile-first UI
├── docker-compose.yml
├── README.md
└── .env.example
```

## Next Steps

- Integrate the Audiobookshelf API for real library ingestion.
- Add Google Books/Open Library enrichment calls.
- Connect embeddings/LLM providers and persist computed vectors.
- Expand the logging console with streaming updates.
- Implement swipe gestures and offline caching for the PWA experience.
