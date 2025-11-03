"""
Season Data Ingestion Script

Ingests session data (races, qualifying, sprints) for a given F1 season.
Safe to run multiple times (idempotent) - skips existing data.

Requirements:
    - FastF1 3.6.1+ (calculates results from F1 Live Timing API)
    - PYTHONPATH must include backend directory

Usage:
    PYTHONPATH=$PWD python scripts/ingest_season.py
    PYTHONPATH=$PWD python scripts/ingest_season.py 2023  # Specific year
    PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race,qualifying  # Specific session types

Schema:
    - sessions: year, round, session_type, event_name, date, circuit_id
    - session_results: Universal fields (position, status) + session-specific fields
      * Race/Sprint: grid_position, points, time_seconds, laps_completed, fastest_lap
      * Qualifying: q1_time_seconds, q2_time_seconds, q3_time_seconds
    - teams: Year-partitioned (unique constraint on year + name)
    - drivers: Year-independent (driver_code unique)

Note:
    FastF1 3.6.1+ calculates results from live timing data since Ergast API
    shutdown in 2024. Earlier versions (3.2.0) will result in NULL values.
"""

import fastf1
import sys
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Import our models and config
from app.models import Driver, Team, Circuit, Session, SessionResult
from app.config import settings


# Session types to ingest (configurable)
DEFAULT_SESSION_TYPES = ['race', 'qualifying', 'sprint', 'sprint_qualifying']


def get_db_session():
    """Create a synchronous database session for ingestion."""
    # Convert async URL to sync URL for script usage
    database_url = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql://"
    )
    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def ingest_circuit(db, event):
    """
    Ingest circuit if it doesn't exist.

    Returns: circuit_id
    """
    circuit_name = event.get("Location")  # Circuit location (e.g., "Bahrain International Circuit")
    location = event.get("Location")
    country = event.get("Country")

    # Check if circuit exists by name
    circuit = db.execute(
        select(Circuit).where(Circuit.name == circuit_name)
    ).scalar_one_or_none()

    if circuit:
        print(f"  ✓ Circuit exists: {circuit_name}")
        return circuit.id
    else:
        print(f"  + Creating circuit: {circuit_name}")
        circuit = Circuit(
            name=circuit_name,
            location=location,
            country=country,
            track_length_km=None  # FastF1 doesn't provide this directly
        )
        db.add(circuit)
        db.commit()
        db.refresh(circuit)
        return circuit.id


def ingest_session_metadata(db, event, circuit_id, year, session_type, session_date):
    """
    Ingest session metadata if it doesn't exist.

    Returns: (session_id, should_process_results)
    """
    round_num = event["RoundNumber"]
    event_name = event["EventName"]

    # Check if session exists
    existing_session = db.execute(
        select(Session).where(
            Session.year == year,
            Session.round == round_num,
            Session.session_type == session_type
        )
    ).scalar_one_or_none()

    if existing_session:
        print(f"  ✓ Session exists: {year} R{round_num} {session_type}")
        return existing_session.id, False  # Don't process results
    else:
        print(f"  + Creating session: {year} R{round_num} {session_type} - {event_name}")
        session = Session(
            year=year,
            round=round_num,
            session_type=session_type,
            event_name=event_name,
            date=session_date.date() if hasattr(session_date, "date") else session_date,
            circuit_id=circuit_id,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session.id, True  # Process results


def ingest_driver(db, driver_data):
    """
    Ingest or update driver.

    Args:
        driver_data: Row from session.results DataFrame

    Returns: driver_id
    """
    driver_code = driver_data["Abbreviation"]

    # Check if driver exists by code
    driver = db.execute(
        select(Driver).where(Driver.driver_code == driver_code)
    ).scalar_one_or_none()

    if driver:
        return driver.id
    else:
        print(f"    + New driver: {driver_data['FullName']} ({driver_code})")
        driver = Driver(
            full_name=driver_data["FullName"],
            driver_code=driver_code,
            driver_number=(
                int(driver_data["DriverNumber"])
                if driver_data["DriverNumber"]
                else None
            ),
            country_code=driver_data.get("CountryCode"),
        )
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver.id


def ingest_team(db, team_data, year):
    """
    Ingest team for a specific year if it doesn't exist.

    Args:
        team_data: Row from session.results DataFrame
        year: Season year

    Returns: team_id
    """
    team_name = team_data["TeamName"]
    team_color = team_data.get("TeamColor", "")

    # Remove '#' from color if present
    if team_color and team_color.startswith('#'):
        team_color = team_color[1:]

    # Check if team exists for this year
    team = db.execute(
        select(Team).where(Team.year == year, Team.name == team_name)
    ).scalar_one_or_none()

    if team:
        return team.id
    else:
        print(f"    + New team for {year}: {team_name}")
        team = Team(
            year=year,
            name=team_name,
            team_color=team_color if team_color else None
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        return team.id


def safe_float(val):
    """Convert value to float, handling NaN and None"""
    import pandas as pd
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_int(val):
    """Convert value to int, handling NaN and None"""
    import pandas as pd
    if pd.isna(val):
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def timedelta_to_seconds(td):
    """Convert pandas Timedelta to seconds (float)"""
    if td is None:
        return None
    try:
        return td.total_seconds()
    except (AttributeError, TypeError):
        return None


def ingest_race_results(db, fastf1_session, session_id, year):
    """
    Ingest race or sprint race results.

    Args:
        db: Database session
        fastf1_session: FastF1 session object (already loaded)
        session_id: ID of the session in our database
        year: Season year
    """
    results = fastf1_session.results
    print(f"  📊 Processing {len(results)} driver results...")

    # Get fastest lap info from laps data
    try:
        laps = fastf1_session.laps
        fastest_lap = laps.pick_fastest()
        fastest_lap_driver = fastest_lap['Driver'] if fastest_lap is not None else None
    except Exception as e:
        print(f"    ⚠️  Could not determine fastest lap: {e}")
        fastest_lap_driver = None

    new_results = 0
    for idx, driver_result in results.iterrows():
        # Get or create driver
        driver_id = ingest_driver(db, driver_result)

        # Get or create team (year-specific)
        team_id = ingest_team(db, driver_result, year)

        # Check if result already exists
        existing_result = db.execute(
            select(SessionResult).where(
                SessionResult.session_id == session_id,
                SessionResult.driver_id == driver_id
            )
        ).scalar_one_or_none()

        if existing_result:
            continue  # Skip existing result

        # Create new result
        new_results += 1

        # Check if this driver had the fastest lap
        driver_code = driver_result["Abbreviation"]
        had_fastest_lap = (fastest_lap_driver == driver_code) if fastest_lap_driver else False

        # Convert time to seconds
        time_seconds = timedelta_to_seconds(driver_result.get("Time"))

        result = SessionResult(
            session_id=session_id,
            driver_id=driver_id,
            team_id=team_id,
            position=safe_int(driver_result.get("Position")),
            status=str(driver_result.get("Status", "Unknown")),
            headshot_url=driver_result.get("HeadshotUrl"),
            grid_position=safe_int(driver_result.get("GridPosition")),
            points=safe_float(driver_result.get("Points")),
            laps_completed=safe_int(driver_result.get("Laps")),  # Available in FastF1 3.6+
            time_seconds=time_seconds,
            fastest_lap=had_fastest_lap,
        )
        db.add(result)

    db.commit()
    print(f"  ✓ Added {new_results} new results")


def ingest_qualifying_results(db, fastf1_session, session_id, year):
    """
    Ingest qualifying or sprint qualifying results.

    Args:
        db: Database session
        fastf1_session: FastF1 session object (already loaded)
        session_id: ID of the session in our database
        year: Season year
    """
    results = fastf1_session.results
    print(f"  📊 Processing {len(results)} qualifying results...")

    new_results = 0
    for idx, driver_result in results.iterrows():
        # Get or create driver
        driver_id = ingest_driver(db, driver_result)

        # Get or create team (year-specific)
        team_id = ingest_team(db, driver_result, year)

        # Check if result already exists
        existing_result = db.execute(
            select(SessionResult).where(
                SessionResult.session_id == session_id,
                SessionResult.driver_id == driver_id
            )
        ).scalar_one_or_none()

        if existing_result:
            continue

        new_results += 1

        # Convert qualifying times to seconds
        q1_time = timedelta_to_seconds(driver_result.get("Q1"))
        q2_time = timedelta_to_seconds(driver_result.get("Q2"))
        q3_time = timedelta_to_seconds(driver_result.get("Q3"))

        result = SessionResult(
            session_id=session_id,
            driver_id=driver_id,
            team_id=team_id,
            position=safe_int(driver_result.get("Position")),
            status=str(driver_result.get("Status", "Unknown")),
            headshot_url=driver_result.get("HeadshotUrl"),
            q1_time_seconds=q1_time,
            q2_time_seconds=q2_time,
            q3_time_seconds=q3_time,
        )
        db.add(result)

    db.commit()
    print(f"  ✓ Added {new_results} new qualifying results")


def ingest_session(db, year, round_num, event, session_type_name, fastf1_session_name):
    """
    Ingest a single session (race, qualifying, sprint, etc.).

    Args:
        db: Database session
        year: Season year
        round_num: Round number
        event: Event data from schedule
        session_type_name: Our session type ('race', 'qualifying', 'sprint_race', 'sprint_qualifying')
        fastf1_session_name: FastF1 session name ('Race', 'Qualifying', 'Sprint', 'Sprint Qualifying')
    """
    # Ingest circuit
    circuit_id = ingest_circuit(db, event)

    # Load FastF1 session data
    print(f"  📥 Loading {fastf1_session_name} data from FastF1...")
    try:
        fastf1_sess = fastf1.get_session(year, round_num, fastf1_session_name)
        fastf1_sess.load()

        # Ingest session metadata
        session_date = fastf1_sess.date if hasattr(fastf1_sess, 'date') else event.get("EventDate")
        session_id, should_process = ingest_session_metadata(
            db, event, circuit_id, year, session_type_name, session_date
        )

        if should_process:
            # Ingest results based on session type
            if session_type_name in ['race', 'sprint_race']:
                ingest_race_results(db, fastf1_sess, session_id, year)
            elif session_type_name in ['qualifying', 'sprint_qualifying']:
                ingest_qualifying_results(db, fastf1_sess, session_id, year)
        else:
            print(f"  ⏭️  Results already exist, skipping")

    except Exception as e:
        print(f"  ❌ Error loading {fastf1_session_name} data: {e}")


def ingest_season(season_year, session_types=None):
    """
    Main function: Ingest all sessions for a given season.

    Args:
        season_year: Year to ingest (e.g., 2024)
        session_types: List of session types to ingest (defaults to all)
    """
    if session_types is None:
        session_types = DEFAULT_SESSION_TYPES

    print(f"\n{'='*60}")
    print(f"INGESTING {season_year} SEASON")
    print(f"Session types: {', '.join(session_types)}")
    print(f"{'='*60}\n")

    # Enable FastF1 cache
    cache_dir = "../cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)

    # Get database session
    db = get_db_session()

    # Mapping of our session types to FastF1 session names
    SESSION_TYPE_MAP = {
        'race': 'Race',
        'qualifying': 'Qualifying',
        'sprint_race': 'Sprint',
        'sprint_qualifying': 'Sprint Qualifying',
    }

    try:
        # Get season schedule
        print(f"📅 Fetching {season_year} schedule...")
        schedule = fastf1.get_event_schedule(season_year)
        print(f"   Found {len(schedule)} events\n")

        # Process each race weekend
        for index, event in schedule.iterrows():
            round_num = event["RoundNumber"]
            event_name = event["EventName"]

            # Skip testing events
            if round_num == 0:
                print(f"⏭️  Skipping: {event_name}\n")
                continue

            print(f"🏁 Round {round_num}: {event_name}")

            # Ingest each requested session type
            for session_type in session_types:
                if session_type not in SESSION_TYPE_MAP:
                    print(f"  ⚠️  Unknown session type: {session_type}, skipping")
                    continue

                fastf1_session_name = SESSION_TYPE_MAP[session_type]
                print(f"\n  🔹 {session_type.upper()}")

                try:
                    ingest_session(db, season_year, round_num, event, session_type, fastf1_session_name)
                except Exception as e:
                    print(f"  ❌ Failed to ingest {session_type}: {e}")
                    continue

            print()  # Blank line between events

        print(f"{'='*60}")
        print(f"✅ INGESTION COMPLETE!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Parse command line arguments
    season = int(sys.argv[1]) if len(sys.argv) > 1 else 2024

    # Optional: specify session types (e.g., python ingest_season.py 2024 race,qualifying)
    if len(sys.argv) > 2:
        session_types = sys.argv[2].split(',')
    else:
        session_types = ['race', 'qualifying']  # Default: just race and qualifying

    ingest_season(season, session_types)
