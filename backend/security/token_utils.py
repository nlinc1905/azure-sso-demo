from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer


from .constants import JWT_ALGORITHM, JWT_SECRET_KEY, JWT_TOKEN_ROUTE


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=JWT_TOKEN_ROUTE)


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


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    """
    Helper function to authenticate the user by decoding the JWT token and validating its claims. 

    :param request: The incoming HTTP request.
    :param token: The JWT token extracted from the Authorization header.

    :return: The decoded token payload if valid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return dict(payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
