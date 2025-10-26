"""
Season Data Ingestion Script

Ingests all race data for a given F1 season into the database.
Safe to run multiple times (idempotent) - skips existing data.

Usage:
    python ingest_season.py
    python ingest_season.py 2023  # Specific year
"""

import fastf1
import sys
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Import our models and config
from app.models import Driver, Team, Circuit, Race, RaceResult
from app.config import settings


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
    circuit_name = event["EventName"]
    location = event["Location"]
    country = event["Country"]

    # Check if circuit exists by name
    circuit = db.execute(
        select(Circuit).where(Circuit.name == circuit_name)
    ).scalar_one_or_none()

    if circuit:
        print(f"  ✓ Circuit exists: {circuit_name}")
        return circuit.id
    else:
        print(f"  + Creating circuit: {circuit_name}")
        circuit = Circuit(name=circuit_name, location=location, country=country)
        db.add(circuit)
        db.commit()
        db.refresh(circuit)
        return circuit.id


def ingest_race(db, event, circuit_id, season_year):
    """
    Ingest race if it doesn't exist.

    Returns: (race_id, should_process_results)
    """
    round_num = event["RoundNumber"]
    race_name = event["EventName"]
    race_date = event["EventDate"]

    # Check if race exists
    race = db.execute(
        select(Race).where(Race.season == season_year, Race.round == round_num)
    ).scalar_one_or_none()

    if race:
        print(f"  ✓ Race exists: {season_year} R{round_num}")
        return race.id, False  # Don't process results
    else:
        print(f"  + Creating race: {season_year} R{round_num} - {race_name}")
        race = Race(
            season=season_year,
            round=round_num,
            name=race_name,
            date=race_date.date() if hasattr(race_date, "date") else race_date,
            event_date=race_date,
            circuit_id=circuit_id,
        )
        db.add(race)
        db.commit()
        db.refresh(race)
        return race.id, True  # Process results


def ingest_driver(db, driver_data):
    """
    Ingest or update driver.

    Args:
        driver_data: Row from session.results DataFrame

    Returns: driver_id
    """
    abbr = driver_data["Abbreviation"]

    # Check if driver exists by abbreviation
    driver = db.execute(
        select(Driver).where(Driver.abbreviation == abbr)
    ).scalar_one_or_none()

    if driver:
        # Update headshot URL to keep it fresh
        driver.default_headshot_url = driver_data["HeadshotUrl"]
        db.commit()
        return driver.id
    else:
        print(f"    + New driver: {driver_data['FullName']}")
        driver = Driver(
            full_name=driver_data["FullName"],
            abbreviation=abbr,
            driver_number=(
                int(driver_data["DriverNumber"])
                if driver_data["DriverNumber"]
                else None
            ),
            country_code=driver_data["CountryCode"],
            default_headshot_url=driver_data["HeadshotUrl"],
        )
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver.id


def ingest_team(db, team_data):
    """
    Ingest team if it doesn't exist.

    Args:
        team_data: Row from session.results DataFrame

    Returns: team_id
    """
    team_name = team_data["TeamName"]

    # Check if team exists by name
    team = db.execute(select(Team).where(Team.name == team_name)).scalar_one_or_none()

    if team:
        return team.id
    else:
        print(f"    + New team: {team_name}")
        team = Team(name=team_name, team_color=team_data["TeamColor"])
        db.add(team)
        db.commit()
        db.refresh(team)
        return team.id


def ingest_race_results(db, session, race_id, season_year, round_num):
    """
    Ingest all race results for a race.

    Args:
        db: Database session
        session: FastF1 session object (already loaded)
        race_id: ID of the race
        season_year: Year
        round_num: Round number
    """
    results = session.results
    print(f"  📊 Processing {len(results)} driver results...")

    # Get fastest lap info from laps data
    laps = session.laps
    fastest_lap = laps.pick_fastest()
    fastest_lap_driver = fastest_lap['Driver'] if fastest_lap is not None else None

    new_results = 0
    for idx, driver_result in results.iterrows():
        # Get or create driver
        driver_id = ingest_driver(db, driver_result)

        # Get or create team
        team_id = ingest_team(db, driver_result)

        # Check if result already exists
        existing_result = db.execute(
            select(RaceResult).where(
                RaceResult.race_id == race_id, RaceResult.driver_id == driver_id
            )
        ).scalar_one_or_none()

        if existing_result:
            continue  # Skip existing result

        # Create new result
        new_results += 1

        # Helper to safely convert, handling NaN
        import pandas as pd

        def safe_int(val):
            if pd.isna(val):
                return None
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        def safe_float(val):
            if pd.isna(val):
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        # Check if this driver had the fastest lap
        driver_abbr = driver_result["Abbreviation"]
        had_fastest_lap = (fastest_lap_driver == driver_abbr) if fastest_lap_driver else False

        result = RaceResult(
            race_id=race_id,
            driver_id=driver_id,
            team_id=team_id,
            position=safe_int(driver_result["Position"]),
            grid_position=safe_int(driver_result["GridPosition"]),
            points=safe_float(driver_result["Points"]),
            status=(
                str(driver_result["Status"])
                if not pd.isna(driver_result["Status"])
                else "Unknown"
            ),
            time=(
                str(driver_result["Time"])
                if not pd.isna(driver_result["Time"])
                else None
            ),
            fastest_lap=had_fastest_lap,
            headshot_url=(
                driver_result["HeadshotUrl"]
                if not pd.isna(driver_result["HeadshotUrl"])
                else None
            ),
        )
        db.add(result)

    db.commit()
    print(f"  ✓ Added {new_results} new results")


def ingest_season(season_year):
    """
    Main function: Ingest all races for a given season.
    """
    print(f"\n{'='*60}")
    print(f"INGESTING {season_year} SEASON")
    print(f"{'='*60}\n")

    # Enable FastF1 cache
    cache_dir = "../cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)

    # Get database session
    db = get_db_session()

    try:
        # Get season schedule
        print(f"📅 Fetching {season_year} schedule...")
        schedule = fastf1.get_event_schedule(season_year)
        print(f"   Found {len(schedule)} events\n")

        # Process each race
        for index, event in schedule.iterrows():
            round_num = event["RoundNumber"]
            event_name = event["EventName"]

            # Skip testing events
            if round_num == 0:
                print(f"⏭️  Skipping: {event_name}\n")
                continue

            print(f"🏁 Round {round_num}: {event_name}")

            # Ingest circuit
            circuit_id = ingest_circuit(db, event)

            # Ingest race
            race_id, should_process = ingest_race(db, event, circuit_id, season_year)

            if should_process:
                # Load race session data
                print(f"  📥 Loading race data from FastF1...")
                try:
                    session = fastf1.get_session(season_year, round_num, "Race")
                    session.load()

                    # Ingest results
                    ingest_race_results(db, session, race_id, season_year, round_num)

                except Exception as e:
                    print(f"  ❌ Error loading race data: {e}")
                    print(f"     Skipping results for this race\n")
                    continue
            else:
                print(f"  ⏭️  Results already exist, skipping")

            print()  # Blank line

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
    # Default to 2024, or take from command line
    season = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    ingest_season(season)
