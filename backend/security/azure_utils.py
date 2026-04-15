from jose import jwt
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .constants import CLIENT_ID, OPENID_CONFIG_URL, TENANT_ID


bearer_scheme = HTTPBearer()


async def get_jwks() -> dict:
    """
    Fetch the JSON Web Key Set (JWKS) from Azure AD's OIDC metadata endpoint.

    :return: The JWKS as a dictionary.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPENID_CONFIG_URL)
        jwks_uri = resp.json()["jwks_uri"]
        jwks = (await client.get(jwks_uri)).json()
        return jwks


async def verify_azure_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Verify the JWT token from Azure AD.

    :param credentials: The HTTP authorization credentials.

    :return: The decoded token payload if valid.
    :raises HTTPException: If the token is invalid or verification fails.
    """
    token = credentials.credentials
    jwks = await get_jwks()
    jwks_keys = jwks.get("keys")
    if not isinstance(jwks_keys, list):
        raise HTTPException(status_code=401, detail="Invalid JWKS format")

    try:
        # Decode the token header to get the key ID
        header = jwt.get_unverified_header(token)
        if "kid" not in header:
            raise HTTPException(status_code=401, detail="Missing key ID in token header")
        key = next((k for k in jwks_keys if k["kid"] == header["kid"]), None)
        if not key:
            raise HTTPException(status_code=401, detail="The key provided in the header was not found in the JWKS")

        # Decode the token with the public key, 
        # and verify the token's issuer and expiration date. 
        # Do not verify the audience claim.
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            # audience=CLIENT_ID, # Use for Oauth2 but not for OIDC
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            options={"verify_aud": False}  # Disable audience verification for OIDC
        )

        # Manually check the 'aud' claim for OIDC tokens using the client ID of the registered Azure app
        if payload.get("aud") != CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid audience")

        return dict(payload)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


class AzureTokenVerifier:
    """
    A callable class wrapper for verify_azure_token, so it can be used both 
    as a dependency and called manually.
    """

    async def __call__(
        self, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ) -> dict:
        return await verify_azure_token(credentials)
