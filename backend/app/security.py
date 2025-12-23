from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

# Define the API key header (expects: X-API-Key: your-key-here)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency to verify the API key from the request header.

    Raises:
        HTTPException: If API key is missing or invalid

    Returns:
        str: The validated API key
    """
    if api_key != settings.lapwise_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key
