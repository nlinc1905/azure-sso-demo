from .azure_utils import AzureTokenVerifier, bearer_scheme, verify_azure_token
from .constants import JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from .token_utils import create_access_token, get_current_user


from fastapi import Depends, HTTPException, Request


azure_verifier = AzureTokenVerifier()


async def authenticate_user(
    request: Request,
    token_user=Depends(get_current_user)
) -> dict:
    """
    Authenticate the user using either Azure SSO or FastAPI's token-based authentication. 

    Note: FastAPI resolves Depends() before the function body runs, so if we use the parameter 
    azure_user = Depends(verify_azure_token) in this function, and the Azure token is invalid or missing,
    it will raise an HTTPException before we have a chance to fall back to token-based auth.
    To work around this, we manually call the Azure verifier on the request, 
    and catch any exceptions to allow fallback to token-based auth.

    :param request: The incoming HTTP request.
    :param token_user: User authenticated via FastAPI's token-based authentication.

    :return: The authenticated user.
    :raises HTTPException: If both authentication methods fail.
    """
    try:
        # Try Azure SSO authentication first
        # Manually extract the credentials from the request and call the Azure verifier
        credentials = await bearer_scheme(request)
        if credentials:
            return await azure_verifier(credentials)
        raise HTTPException(status_code=401, detail="No credentials provided for Azure SSO")
    except (HTTPException, Exception):
        pass  # Azure auth failed, fall through to token auth

    # Fall back to token-based auth (already resolved via Depends)
    if token_user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed for both Azure SSO and API token."
        )

    return token_user


__all__ = [
    "authenticate_user",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 
    "create_access_token", 
    "get_current_user",
    "verify_azure_token"
]
