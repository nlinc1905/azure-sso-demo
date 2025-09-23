from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import httpx, os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
bearer_scheme = HTTPBearer()

# CORS settings to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")
OPENID_CONFIG_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"


async def get_jwks() -> dict:
    """
    Fetch the JSON Web Key Set (JWKS) from Azure AD.

    :return: The JWKS as a dictionary.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPENID_CONFIG_URL)
        jwks_uri = resp.json()["jwks_uri"]
        jwks = (await client.get(jwks_uri)).json()
        return jwks


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Verify the JWT token from Azure AD.

    :param credentials: The HTTP authorization credentials.

    :return: The decoded token payload if valid.
    :raises HTTPException: If the token is invalid or verification fails.
    """
    token = credentials.credentials
    jwks = await get_jwks()

    try:
        # Decode the token header to get the key ID
        header = jwt.get_unverified_header(token)
        key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
        if not key:
            raise HTTPException(status_code=401, detail="Key not found")

        # Verify the token with the public key and validate the claims in the payload
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            # audience=CLIENT_ID, # Use for Oauth2 but not for OIDC
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            options={"verify_aud": False}  # Disable audience verification for OIDC
        )

        # Manually check the 'aud' claim for OIDC tokens
        if payload.get("aud") != CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid audience")

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/protected")
async def protected(user=Depends(verify_token)) -> dict:
    """A sample protected endpoint that requires a valid JWT token."""
    return {"message": "You are authenticated!", "user": user}
