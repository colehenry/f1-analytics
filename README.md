# F1 Analytics

A full-stack web application for visualizing Formula 1 race data, telemetry, and statistics. Personal learning project to master modern web development.

**Current Status:** ✅ Working MVP - Season podium display with year selector (2022-2024 data)

---

## What It Does

**Currently Working:**
- Fetches and stores 2022-2024 F1 season data from FastF1 API
- Home page: Displays 2024 race winners
- `/seasons` page: Shows top 3 finishers for each race with year selector
- Team colors, driver photos, fastest lap indicators
- Auto-generated API documentation at `/docs`

**Database:**
- PostgreSQL with 5 tables: drivers, teams, circuits, races, race_results
- ~1,440 race results (3 seasons × 20 drivers × 24 races)
- Proper foreign key relationships and data integrity

**Data Sources:**
- FastF1 library (2018+) for modern telemetry and race data
- Jolpica F1 API (1950+) for historical data (planned)

---

## Tech Stack

**Frontend:** Next.js 14 (App Router) • TypeScript • Tailwind CSS
**Backend:** FastAPI • Python 3.11 • SQLAlchemy
**Database:** PostgreSQL 15
**Infrastructure:** Docker • Alembic migrations

---

## Quick Start

**Prerequisites:** Docker, Node.js 20, Python 3.11

```bash
# Start PostgreSQL
docker-compose up -d

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.ingest_season  # Takes 10-20 min first time

# Start backend
uvicorn app.main:app --reload
# → http://localhost:8000 (API docs at /docs)

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## Current Features

✅ **Data Ingestion**
- Script pulls 2024 F1 data from FastF1
- Idempotent (safe to run multiple times)
- Automatically detects fastest laps
- Handles mid-season driver/team changes

✅ **API**
- `GET /api/races/2024` - Returns race winners
- Auto-generated Swagger docs
- Pydantic validation

✅ **Frontend**
- Responsive race winner cards
- Server-side rendering
- Tailwind CSS styling

---

## What's Next

**Immediate:**
- Full race results (all 20 drivers per race)
- Qualifying results
- Championship standings

**Phase 2:**
- Lap time visualizations
- Driver/team statistics
- Multiple seasons (2023, 2022, etc.)
- Telemetry data (speed, throttle, brake)

**Phase 3:**
- Historical data (1950-2017)
- Driver comparisons
- Predictive analytics

---

## How It Works

```
FastF1 API → ingest_season.py → PostgreSQL → FastAPI → Next.js → Browser
```

**Data Flow:**
1. `ingest_season.py` fetches race data from FastF1
2. Stores in PostgreSQL (normalized schema)
3. FastAPI serves data via REST endpoints
4. Next.js frontend fetches and displays

**Key Files:**
- `backend/scripts/ingest_season.py` - Data ingestion
- `backend/app/routers/races.py` - API endpoints
- `frontend/app/page.tsx` - Home page

---

## Development

```bash
# Start all services
docker-compose up -d                    # PostgreSQL
cd backend && uvicorn app.main:app --reload  # Backend
cd frontend && npm run dev               # Frontend
```

**Useful Commands:**
```bash
# Re-ingest data
cd backend && python -m scripts.ingest_season

# Database migrations
cd backend && alembic upgrade head

# View database
docker exec -it f1-analytics-db psql -U f1admin -d f1_analytics
```

---

**Learning Project** • Not affiliated with Formula 1 • MIT License
