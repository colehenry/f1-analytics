# F1 Analytics

A full-stack web application for visualizing Formula 1 telemetry, race data, and historical statistics. Built as a learning project to master modern web development while creating something useful for F1 fans.

**Current Status:** 🚧 In Development - Database schema implemented, data ingestion in progress

---

## Tech Stack

**Frontend:**
- React 18 + Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Plotly.js/Recharts for visualizations
- React Query for data fetching

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL 15+
- Alembic (migrations)
- APScheduler (automated updates)

**Data Sources:**
- FastF1 library (telemetry, 2018+)
- Jolpica F1 API (historical data, 1950+)

**Infrastructure:**
- Docker (PostgreSQL container)
- VS Code + Biome.js + Black

---

## Project Structure

```
f1-analytics/
├── frontend/           # Next.js React app
├── backend/            # FastAPI Python app
├── docs/               # Documentation
│   ├── PROJECT_OVERVIEW.md    # Architecture & tech explanations
│   ├── SETUP.md               # Installation guide
│   ├── FEATURES.md            # Feature roadmap
│   ├── TIMELINE.md            # Learning timeline
│   ├── API_DESIGN.md          # API endpoints & database schema
│   ├── SCHEMA_DESIGN.md       # Database schema design decisions
│   └── LEARNING_LOG.md        # Personal learning notes
├── docker-compose.yml  # PostgreSQL config
└── README.md           # This file
```

---

## Getting Started

### Prerequisites

- macOS (instructions are Mac-specific)
- Docker Desktop
- Node.js 20 LTS (via nvm)
- Python 3.11
- VS Code

### Setup Instructions

**Complete setup guide**: See [`docs/SETUP.md`](docs/SETUP.md)

1. **Install tools** (Docker, Node.js, Python - see SETUP.md)
2. **Clone repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/f1-analytics.git
   cd f1-analytics
   ```

3. **Start PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

4. **Set up backend**:
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

5. **Set up frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Visit**:
   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

---

## Current Progress

### ✅ Completed
- PostgreSQL database running in Docker
- FastAPI backend structure with health endpoint
- SQLAlchemy ORM models for all core entities
- Alembic migrations configured and applied
- Database schema with 5 tables: `drivers`, `teams`, `circuits`, `races`, `race_results`
- Foreign key relationships with referential integrity
- FastF1 exploration script for understanding data structure

### 🚧 In Progress
- Data ingestion scripts to populate database with FastF1 data

### 📋 Next Up
- First API endpoint: `/api/races/{season}`
- Frontend Next.js setup
- Race results visualization

---

## Documentation

This project is heavily documented as a learning resource:

- **[PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)**: Explains architecture, tech choices, data flow
- **[SETUP.md](docs/SETUP.md)**: Step-by-step environment setup with explanations
- **[FEATURES.md](docs/FEATURES.md)**: Feature roadmap with checkboxes
- **[TIMELINE.md](docs/TIMELINE.md)**: Month-by-month learning plan
- **[API_DESIGN.md](docs/API_DESIGN.md)**: API endpoints and database schema
- **[SCHEMA_DESIGN.md](docs/SCHEMA_DESIGN.md)**: Database schema design decisions (NEW!)
- **[LEARNING_LOG.md](docs/LEARNING_LOG.md)**: Space for personal notes and learnings

---

## Features

### MVP (Phase 1) - In Progress
- [x] Database schema designed and implemented
- [ ] Ingest race data from FastF1
- [ ] Display race results for 2024 season
- [ ] Show lap times for each race
- [ ] Basic data visualizations (line charts)

### Planned Features
- [ ] Telemetry visualization (speed, throttle, brake)
- [ ] Driver comparison tool
- [ ] Historical race data (1950-2024)
- [ ] Championship standings
- [ ] Automated weekly data updates
- [ ] Machine learning predictions

See [`docs/FEATURES.md`](docs/FEATURES.md) for complete roadmap.

---

## Development

### Running locally

**Start all services:**
```bash
# Terminal 1: PostgreSQL
docker-compose up

# Terminal 2: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend && npm run dev
```

### Running tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

---

## Learning Goals

This project is designed to teach:
- Full-stack web development
- React + Next.js with TypeScript
- FastAPI + SQLAlchemy
- PostgreSQL database design
- Docker basics
- API design and consumption
- Data visualization
- Working with external APIs

See [`docs/TIMELINE.md`](docs/TIMELINE.md) for the complete learning roadmap.

---

## Data Sources

**FastF1** - F1 telemetry and timing data (2018+)
- Lap times
- Speed, throttle, brake telemetry
- Qualifying results
- Practice sessions
- Sprint races

**Jolpica F1 API** - Historical race data (1950+)
- Race results
- Championship standings
- Driver/team information

---

## License

MIT

---

## Acknowledgments

- FastF1 library maintainers
- Jolpica F1 API
- F1 community for data access

---

**Status**: Active development | Learning project | Not affiliated with Formula 1
