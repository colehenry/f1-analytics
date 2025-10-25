from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from env variables.

    Pydantic will automatically:
    1. Read the .env file
    2. Validate the types (str, bool, etc.)
    3. Raise errors if required variables are missing
    """

    # Database
    database_url: str

    # Application
    debug: bool = False
    secret_key: str

    # FastF1
    fastf1_cache_dir: str = "./cache"

    class Config:
        # Tell Pydantic where to find the .env file
        env_file = ".env"
        # Make it case-insensitive (DATABASE_URL = database_url)
        case_sensitive = False


# Create a single instance to use throughout the app
settings = Settings()
