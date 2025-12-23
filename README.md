# lapwise.dev

A full-stack web application for visualizing Formula 1 race data, standings, and statistics.

## Features

- 2025-2018 F1 season standings (drivers and constructors)
- Interactive points progression graphs with team colors
- Race-by-race results with podium finishes
- Sprint race support
- Individual race detail pages
- Auto-generated API documentation

## Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS, Recharts
- **Backend:** FastAPI, Python 3.11, SQLAlchemy
- **Database:** PostgreSQL 15
- **Data Source:** FastF1 (official F1 live timing data)

## Getting Started

### Prerequisites
- Docker
- Node.js 20+
- Python 3.11

### Installation

1. **Start the database**
```bash
docker-compose up -d
```

2. **Set up the backend**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

3. **Ingest F1 data** (optional, takes ~15-20 minutes)
```bash
PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race,qualifying,sprint_race,sprint_qualifying
```

4. **Start the backend server**
```bash
uvicorn app.main:app --reload
```
API will be available at http://localhost:8000 (docs at `/docs`)

5. **Set up the frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```
App will be available at http://localhost:3000

## Project Structure

```
lapwise.dev/
├── frontend/          # Next.js app
│   ├── app/          # Pages and routing
│   ├── components/   # React components
│   └── lib/          # Utilities
├── backend/          # FastAPI app
│   ├── app/          # Application code
│   ├── scripts/      # Data ingestion
│   └── alembic/      # Database migrations
└── docker-compose.yml
```

## License

MIT License - Not affiliated with Formula 1
