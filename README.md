# F1 Analytics

A full-stack web application for visualizing Formula 1 race data, telemetry, and statistics. Personal learning project to master modern web development.

**Current Status:** ✅ Database refactored - Session-based architecture with 2024 race and qualifying data ingested

---

## What It Does

**Currently Working:**
- Fetches and stores 2024 F1 season data from FastF1 3.6.1
- Session-based architecture supporting race, qualifying, sprint, and sprint qualifying
- Complete race results with positions, times, points, laps completed, and fastest lap tracking
- Year-partitioned teams table to track color/name changes between seasons
- Auto-generated API documentation at `/docs`

**Database:**
- PostgreSQL with 5 tables: drivers, teams, circuits, sessions, session_results
- 2024 Season ingested: 24 races + 24 qualifying sessions = 48 sessions
- ~960 session results (48 sessions × ~20 drivers)
- Normalized schema with proper foreign keys and data integrity

**Data Sources:**
- FastF1 3.6.1 (2018+) - Calculates results from F1 live timing data
- Uses official F1 API timing data (Ergast no longer available as of 2024)

---

## Tech Stack

**Frontend:** Next.js 14 (App Router) • TypeScript • Tailwind CSS
**Backend:** FastAPI • Python 3.11 • SQLAlchemy 2.0
**Database:** PostgreSQL 15
**Data:** FastF1 3.6.1 • F1 Live Timing API
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

# Ingest 2024 race and qualifying data (takes ~15 min first time)
PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race,qualifying

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
- Pulls 2024 F1 data from FastF1 3.6.1 using F1 Live Timing API
- Session-based ingestion: races, qualifying, sprints, sprint qualifying
- Idempotent (safe to run multiple times)
- Automatically detects fastest laps from lap data
- Year-partitioned teams handle color/name changes
- Stores times as floats (seconds) for easy frontend conversion

✅ **Database Schema**
- **sessions**: Replaces races table, supports multiple session types per round
- **session_results**: Unified table for race and qualifying results
- **teams**: Year-partitioned (teams.year + teams.name unique constraint)
- **drivers**: Year-independent with driver_code
- **circuits**: Location and country data

✅ **API** (Legacy endpoints, being refactored)
- `GET /api/races/2024` - Returns race winners (old schema)
- Auto-generated Swagger docs at `/docs`
- Pydantic v2 validation

---

## What's Next

**Immediate:**
- `/api/results` endpoint with query parameters (year, round, session_type)
- Update frontend to use new session-based API
- Championship standings calculation

**Phase 2:**
- Ingest sprint and sprint qualifying data for 2024
- Add 2023, 2022 seasons (and earlier back to 2018)
- Lap time visualizations
- Driver/team statistics pages

**Phase 3:**
- Telemetry data visualizations (speed, throttle, brake traces)
- Historical data (1950-2017) from alternative sources
- Driver head-to-head comparisons
- Predictive analytics

---

## How It Works

```
F1 Live Timing API → FastF1 3.6.1 → ingest_season.py → PostgreSQL → FastAPI → Next.js
```

**Data Flow:**
1. FastF1 fetches live timing data from official F1 API
2. Calculates race/qualifying results from timing data (Ergast no longer available)
3. `ingest_season.py` processes and stores in PostgreSQL (session-based schema)
4. FastAPI serves data via REST endpoints
5. Next.js frontend fetches and displays

**Key Files:**
- `backend/scripts/ingest_season.py` - Session data ingestion script
- `backend/app/models/session.py` - Session model (replaces Race)
- `backend/app/models/session_result.py` - Result model (replaces RaceResult)
- `backend/app/schemas/result.py` - Pydantic response schemas

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
# Ingest specific session types for a year
cd backend
PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race
PYTHONPATH=$PWD python scripts/ingest_season.py 2024 qualifying
PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race,qualifying,sprint_race,sprint_qualifying

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# View database
docker exec -it f1-analytics-db psql -U f1admin -d f1_analytics

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

---

**Learning Project** • Not affiliated with Formula 1 • MIT License
