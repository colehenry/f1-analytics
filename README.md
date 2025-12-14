# F1 Analytics

A full-stack web application for visualizing Formula 1 race data, standings, and statistics. Personal learning project to master modern web development.

**Current Status:** ✅ Full 2024 season data ingested | Results page with championships and race summaries live

---

## What It Does

**Currently Working:**
- Complete 2024 F1 season results from FastF1 3.6.1
- Season standings page with driver and constructor championships
- Championship cards showing top 5 (expandable to full list)
- Drivers listed under each constructor team
- Race-by-race podium displays with driver photos
- Individual race detail pages for all 24 rounds
- Sprint race support with separate detail pages
- Dark mode UI with team color coding
- Auto-generated API documentation at `/docs`

**Frontend Pages:**
- `/` - Home page
- `/results/[season]` - Season standings and race summaries (e.g., `/results/2024`)
- `/results/[season]/[round]` - Individual race details (e.g., `/results/2024/1`)
- `/results/[season]/[round]/sprint` - Sprint race details
- `/about` - About page (in progress)
- `/analyze` - Analysis page (in progress)

**Database:**
- PostgreSQL with session-based architecture
- 2024 Season: 24 races + 24 qualifying + 6 sprints + 6 sprint qualifying = 60 sessions
- ~1,200 session results (60 sessions × ~20 drivers)
- Tables: drivers, teams, circuits, sessions, session_results

**Data Sources:**
- FastF1 3.6.1 (2018+) - Uses official F1 live timing data
- Session-based architecture supporting: race, qualifying, sprint_race, sprint_qualifying

---

## Tech Stack

**Frontend:** Next.js 14 (App Router) • React 18 • TypeScript • Tailwind CSS • Biome.js
**Backend:** FastAPI • Python 3.11 • SQLAlchemy 2.0 • Pydantic v2
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

# Ingest 2024 data (takes ~15-20 min first time)
PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race,qualifying,sprint_race,sprint_qualifying

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

### ✅ Data Ingestion
- Pulls 2024 F1 data from FastF1 3.6.1 using F1 Live Timing API
- Session-based ingestion: races, qualifying, sprints, sprint qualifying
- Idempotent (safe to run multiple times)
- Automatically detects fastest laps from lap data
- Year-partitioned teams handle color/name changes
- Stores times as floats (seconds) for easy frontend conversion

### ✅ API Endpoints
All endpoints prefixed with `/api/results`:
- `GET /api/results/seasons` - Get all available seasons
- `GET /api/results/{season}/standings` - Driver and constructor championships
- `GET /api/results/{season}` - All rounds with podium finishers
- `GET /api/results/{season}/{round}` - Individual race details
- `GET /api/results/{season}/{round}/sprint` - Sprint race details

Auto-generated Swagger docs at http://localhost:8000/docs

### ✅ Frontend Features
- **Season standings view** with driver and constructor championships
- **Compact layout** to minimize scrolling
- **Championship cards** showing top 5 by default, expandable to full list
- **Team driver lists** under each constructor with points
- **Modern year selector** for switching seasons
- **Race summaries** with podium finishers and team colors
- **Driver headshots** from F1 official sources
- **Fastest lap indicators** on race results
- **Sprint race badges** to distinguish sprint weekends
- **Responsive design** with Tailwind CSS
- **Dark mode** UI theme

### ✅ Database Schema
- **sessions**: Supports multiple session types per round (race, qualifying, sprint, etc.)
- **session_results**: Unified table for all session results
- **teams**: Year-partitioned (teams can change colors/names between seasons)
- **drivers**: Year-independent with driver_code and headshot URLs
- **circuits**: Track information with location and length

---

## What's Next

**Immediate Improvements:**
- Add qualifying results page
- Performance optimization for large datasets
- Error boundaries and loading states
- Add more seasons (2023, 2022, etc.)

**Phase 2:**
- Lap time visualizations (line charts)
- Driver comparison tools
- Circuit-specific statistics
- Head-to-head driver comparisons

**Phase 3:**
- Telemetry data visualizations (speed, throttle, brake traces)
- Historical data (1950-2017) from alternative sources
- Advanced analytics and insights
- Predictive features

---

## How It Works

```
F1 Live Timing API → FastF1 3.6.1 → ingest_season.py → PostgreSQL → FastAPI → Next.js
```

**Data Flow:**
1. FastF1 fetches live timing data from official F1 API
2. Calculates session results from timing data
3. `ingest_season.py` processes and stores in PostgreSQL (session-based schema)
4. FastAPI serves data via REST endpoints
5. Next.js frontend fetches and displays with React components

**Key Files:**
- `backend/scripts/ingest_season.py` - Session data ingestion script
- `backend/app/models/session.py` - Session model
- `backend/app/models/session_result.py` - Result model
- `backend/app/routers/season_results.py` - API endpoints
- `frontend/app/results/[season]/page.tsx` - Main results page
- `frontend/app/results/[season]/[round]/page.tsx` - Race detail page

---

## Development

```bash
# Start all services
docker-compose up -d                           # PostgreSQL
cd backend && uvicorn app.main:app --reload    # Backend (port 8000)
cd frontend && npm run dev                      # Frontend (port 3000)
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

# Frontend linting
cd frontend
npx biome check .
npx biome check --apply .  # Auto-fix
```

---

## Project Structure

```
f1-analytics/
├── frontend/              # Next.js app (TypeScript + Tailwind)
│   ├── app/              # App Router (file-based routing)
│   │   ├── page.tsx      # Home page (/)
│   │   ├── layout.tsx    # Root layout with navigation
│   │   ├── results/      # Results pages
│   │   │   ├── page.tsx                  # /results (redirects to /results/2024)
│   │   │   └── [season]/                 # /results/2024
│   │   │       ├── page.tsx              # Season standings + race list
│   │   │       └── [round]/              # /results/2024/1
│   │   │           ├── page.tsx          # Race details
│   │   │           └── sprint/
│   │   │               └── page.tsx      # Sprint details
│   │   ├── about/        # About page
│   │   └── analyze/      # Analysis page
│   ├── components/       # React components
│   │   └── Navigation.tsx
│   ├── lib/              # Utilities, API client
│   └── package.json
├── backend/              # FastAPI app (Python 3.11)
│   ├── app/
│   │   ├── main.py      # FastAPI entrypoint
│   │   ├── models/      # SQLAlchemy models
│   │   │   ├── session.py
│   │   │   ├── session_result.py
│   │   │   ├── driver.py
│   │   │   ├── team.py
│   │   │   └── circuit.py
│   │   ├── schemas/     # Pydantic schemas
│   │   │   └── result.py
│   │   ├── routers/     # API endpoints
│   │   │   └── season_results.py
│   │   └── database.py  # DB connection
│   ├── scripts/         # Data ingestion scripts
│   │   └── ingest_season.py
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── docs/                # Documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── SETUP.md
│   ├── FEATURES.md
│   ├── API_DESIGN.md
│   └── LEARNING_LOG.md
└── docker-compose.yml   # PostgreSQL container
```

---

## API Examples

**Get available seasons:**
```bash
curl http://localhost:8000/api/results/seasons
# [2024, 2023, 2022]
```

**Get 2024 season standings:**
```bash
curl http://localhost:8000/api/results/2024/standings
```

**Get all 2024 races with podiums:**
```bash
curl http://localhost:8000/api/results/2024
```

**Get specific race details:**
```bash
curl http://localhost:8000/api/results/2024/1
```

---

## Environment Variables

### Backend `.env` (NEVER commit this file!)
```bash
DATABASE_URL=postgresql://f1admin:f1password@localhost:5432/f1_analytics
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Frontend `.env.local` (NEVER commit this file!)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

**Learning Project** • Not affiliated with Formula 1 • MIT License
