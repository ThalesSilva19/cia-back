from typing import Optional

from fastapi import Header, HTTPException

from src.utils.jwt import decode_access_token


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Extract and validate the current user from the Authorization header.

    Args:
        authorization: The Authorization header value (Bearer token)

    Returns:
        dict: User information from the decoded token

    Raises:
        HTTPException: If the token is invalid or missing
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token = authorization.split(" ")[1]
    try:
        user = decode_access_token(token)
        user_identifier = user.get("email")
        if not user_identifier:
            raise HTTPException(
                status_code=401, detail="Invalid token payload: missing user identifier"
            )
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
