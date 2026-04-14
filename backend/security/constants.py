import os
import secrets


# JWT token generation and verification constants
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", default=secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_TOKEN_ROUTE = "/token"
# Azure AD configuration constants
TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")  # This will be used for audience validation in OIDC tokens
OPENID_CONFIG_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"
