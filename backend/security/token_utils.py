from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer


from .constants import JWT_ALGORITHM, JWT_SECRET_KEY, JWT_TOKEN_ROUTE


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=JWT_TOKEN_ROUTE, auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Helper function to create the JWT token with the expiration timestamp.

    :param data: The data to include in the token payload.
    :param expires_delta: Optional timedelta for token expiration.

    :return: The encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return str(encoded_jwt)


async def get_current_user(request: Request) -> dict:
    """
    Helper function to authenticate the user by decoding the JWT token and validating its claims. 

    :param request: The incoming HTTP request.

    :return: The decoded token payload if valid, else None.
    """
    token = await oauth2_scheme(request)  # returns None if missing
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        # Additional claim checks can be added here (e.g. issuer, audience) if needed
        return dict(payload)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
