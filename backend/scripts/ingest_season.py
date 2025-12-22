"""
Season Data Ingestion Script

Ingests session data (races, qualifying, sprints) for a given F1 season.
Safe to run multiple times (idempotent) - checks database first, skips existing data.

Requirements:
    - FastF1 3.6.1+ (calculates results from F1 Live Timing API)
    - PYTHONPATH must include backend directory

Usage:
    PYTHONPATH=$PWD python scripts/ingest_season.py
    PYTHONPATH=$PWD python scripts/ingest_season.py 2023  # Specific year
    PYTHONPATH=$PWD python scripts/ingest_season.py 2024 race,qualifying  # Specific session types
    PYTHONPATH=$PWD python scripts/ingest_season.py 2024 --strict  # Fail fast on errors

Features:
    - ⚡ Database-first approach: Checks DB before making expensive FastF1 API calls
    - Automatic retry with exponential backoff for network failures
    - Detailed error reporting and success/failure tracking
    - Absolute cache path for consistent caching
    - Session availability detection (skips non-existent sprint sessions)
    - Optional strict mode (--strict) to fail immediately on errors

Schema:
    - sessions: year, round, session_type, event_name, date, circuit_id
    - session_results: Universal fields (position, status) + session-specific fields
      * Race/Sprint: grid_position, points, time_seconds, laps_completed, fastest_lap
      * Qualifying: q1_time_seconds, q2_time_seconds, q3_time_seconds
    - teams: Year-partitioned (unique constraint on year + name)
    - drivers: Year-independent (driver_code unique)

Session Types:
    - race: Main race
    - qualifying: Qualifying session
    - sprint_race: Sprint race (not all events)
    - sprint_qualifying: Sprint qualifying (not all events)

Note:
    FastF1 3.6.1+ calculates results from live timing data since Ergast API
    shutdown in 2024. Earlier versions (3.2.0) will result in NULL values.
"""

import fastf1
import sys
import os
import time
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Import our models and config
from app.models import Driver, Team, Circuit, Session, SessionResult
from app.config import settings


# Session types to ingest (configurable)
DEFAULT_SESSION_TYPES = ['race', 'qualifying', 'sprint_race', 'sprint_qualifying']


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


def load_session_with_retry(year, round_num, session_name, max_retries=3):
    """
    Load a FastF1 session with retry logic and exponential backoff.

    Args:
        year: Season year
        round_num: Round number
        session_name: FastF1 session name ('Race', 'Qualifying', etc.)
        max_retries: Maximum number of retry attempts

    Returns:
        Loaded FastF1 session object, or None if session doesn't exist

    Raises:
        Exception: If loading fails after all retries
    """
    for attempt in range(max_retries):
        try:
            fastf1_sess = fastf1.get_session(year, round_num, session_name)
            fastf1_sess.load()
            return fastf1_sess
        except Exception as e:
            error_msg = str(e).lower()

            # Check if this is a "session doesn't exist" error (not a real failure)
            if "no session" in error_msg or "not found" in error_msg or "invalid session" in error_msg:
                return None

            # Real error - retry with exponential backoff
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"    ⚠️  Load failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"    ⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Final attempt failed
                raise

    return None


def session_exists(event, session_type_name):
    """
    Check if a session type is available for this event.

    Args:
        event: Event data from FastF1 schedule
        session_type_name: Our session type ('sprint_race' or 'sprint_qualifying')

    Returns:
        bool: True if session should exist, False otherwise
    """
    # Sprint sessions only exist at certain events
    if session_type_name in ['sprint_race', 'sprint_qualifying']:
        # Check if event has sprint (look for 'Sprint' in session names)
        # FastF1 event objects have session info in their attributes
        try:
            # The event object should have a Session5Name or similar indicating a sprint
            return hasattr(event, 'Session5Name') and event.get('Session5Name') is not None
        except Exception:
            # If we can't determine, assume it might exist and let FastF1 tell us
            return True

    # Race and qualifying exist at all events
    return True


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


def check_session_in_db(db, year, round_num, session_type_name):
    """
    Check if session and its results already exist in database.

    Args:
        db: Database session
        year: Season year
        round_num: Round number
        session_type_name: Our session type ('race', 'qualifying', 'sprint_race', 'sprint_qualifying')

    Returns:
        tuple: (session_exists: bool, has_results: bool, session_id: int or None)
    """
    # Check if session exists
    existing_session = db.execute(
        select(Session).where(
            Session.year == year,
            Session.round == round_num,
            Session.session_type == session_type_name
        )
    ).scalar_one_or_none()

    if not existing_session:
        return False, False, None

    # Session exists - check if it has results
    result_count = db.execute(
        select(SessionResult).where(
            SessionResult.session_id == existing_session.id
        )
    ).scalars().all()

    has_results = len(result_count) > 0

    return True, has_results, existing_session.id


def ingest_session(db, year, round_num, event, session_type_name, fastf1_session_name, strict_mode=False):
    """
    Ingest a single session (race, qualifying, sprint, etc.).

    IMPORTANT: Checks database FIRST before loading from FastF1 to avoid unnecessary API calls.

    Args:
        db: Database session
        year: Season year
        round_num: Round number
        event: Event data from schedule
        session_type_name: Our session type ('race', 'qualifying', 'sprint_race', 'sprint_qualifying')
        fastf1_session_name: FastF1 session name ('Race', 'Qualifying', 'Sprint', 'Sprint Qualifying')
        strict_mode: If True, raise exceptions instead of continuing

    Returns:
        bool: True if successful, False if failed/skipped
    """
    # STEP 1: Check if data already exists in database
    session_exists, has_results, session_id = check_session_in_db(db, year, round_num, session_type_name)

    if session_exists and has_results:
        print(f"  ✓ Session and results already exist in database, skipping FastF1 load")
        return True  # Success - already have the data

    if session_exists and not has_results:
        print(f"  ⚠️  Session exists but has no results, will reload from FastF1")

    # STEP 2: Ingest circuit (fast database operation)
    circuit_id = ingest_circuit(db, event)

    # STEP 3: Load from FastF1 only if needed
    print(f"  📥 Loading {fastf1_session_name} data from FastF1...")
    try:
        fastf1_sess = load_session_with_retry(year, round_num, fastf1_session_name)

        if fastf1_sess is None:
            # Session doesn't exist (e.g., no sprint at this event)
            print(f"  ⏭️  {fastf1_session_name} not available for this event")
            return False

        # STEP 4: Create/update session metadata if needed
        if not session_exists:
            session_date = fastf1_sess.date if hasattr(fastf1_sess, 'date') else event.get("EventDate")
            session_id, should_process = ingest_session_metadata(
                db, event, circuit_id, year, session_type_name, session_date
            )
        else:
            # Session exists but had no results
            should_process = True

        # STEP 5: Ingest results
        if should_process:
            if session_type_name in ['race', 'sprint_race']:
                ingest_race_results(db, fastf1_sess, session_id, year)
            elif session_type_name in ['qualifying', 'sprint_qualifying']:
                ingest_qualifying_results(db, fastf1_sess, session_id, year)
        else:
            print(f"  ⏭️  Results already exist, skipping")

        return True

    except Exception as e:
        print(f"  ❌ Error loading {fastf1_session_name} data: {e}")
        if strict_mode:
            raise
        return False


def ingest_season(season_year, session_types=None, strict_mode=False):
    """
    Main function: Ingest all sessions for a given season.

    Args:
        season_year: Year to ingest (e.g., 2024)
        session_types: List of session types to ingest (defaults to all)
        strict_mode: If True, fail fast on any error instead of continuing
    """
    if session_types is None:
        session_types = DEFAULT_SESSION_TYPES

    print(f"\n{'='*60}")
    print(f"INGESTING {season_year} SEASON")
    print(f"Session types: {', '.join(session_types)}")
    if strict_mode:
        print(f"Mode: STRICT (fail fast on errors)")
    print(f"{'='*60}\n")

    # Enable FastF1 cache (use absolute path for consistency)
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cache"))
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)
    print(f"📁 Using cache directory: {cache_dir}\n")

    # Get database session
    db = get_db_session()

    # Mapping of our session types to FastF1 session names
    SESSION_TYPE_MAP = {
        'race': 'Race',
        'qualifying': 'Qualifying',
        'sprint_race': 'Sprint',
        'sprint_qualifying': 'Sprint Qualifying',
    }

    # Track success/failure
    stats = {
        'total_sessions_attempted': 0,
        'successful': 0,
        'already_exists': 0,  # Already in database
        'not_available': 0,   # Session doesn't exist (e.g., no sprint)
        'failed': 0,
        'failures': []  # List of (round, session_type, error) tuples
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

                stats['total_sessions_attempted'] += 1

                # Check if already exists BEFORE calling ingest_session
                session_exists, has_results, _ = check_session_in_db(db, season_year, round_num, session_type)

                if session_exists and has_results:
                    # Quick check - data already in DB, don't even try to load
                    print(f"  ✓ Already in database")
                    stats['already_exists'] += 1
                    continue

                try:
                    success = ingest_session(
                        db, season_year, round_num, event,
                        session_type, fastf1_session_name,
                        strict_mode=strict_mode
                    )
                    if success:
                        stats['successful'] += 1
                    else:
                        # Session doesn't exist (e.g., no sprint at this event)
                        stats['not_available'] += 1
                except Exception as e:
                    stats['failed'] += 1
                    stats['failures'].append((round_num, event_name, session_type, str(e)))
                    print(f"  ❌ Failed to ingest {session_type}: {e}")
                    if strict_mode:
                        raise
                    continue

            print()  # Blank line between events

        # Print summary
        print(f"{'='*60}")
        print(f"✅ INGESTION COMPLETE!")
        print(f"{'='*60}")
        print(f"📊 Summary:")
        print(f"   Total sessions checked: {stats['total_sessions_attempted']}")
        print(f"   ✓ Newly ingested: {stats['successful']}")
        print(f"   ✓ Already in database: {stats['already_exists']}")
        print(f"   ⏭️  Not available (no sprint): {stats['not_available']}")
        print(f"   ❌ Failed: {stats['failed']}")

        if stats['failures']:
            print(f"\n⚠️  Failed sessions:")
            for round_num, event_name, session_type, error in stats['failures']:
                print(f"   - R{round_num} {event_name} ({session_type}): {error}")

        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
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
    # Changed default to match DEFAULT_SESSION_TYPES
    if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
        session_types = sys.argv[2].split(',')
    else:
        session_types = ['race', 'qualifying', 'sprint_race', 'sprint_qualifying']

    # Optional: strict mode flag (--strict)
    strict_mode = '--strict' in sys.argv

    ingest_season(season, session_types, strict_mode=strict_mode)
