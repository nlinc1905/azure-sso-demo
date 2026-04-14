from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware

from security import create_access_token, get_current_user, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, verify_azure_token


app = FastAPI()

# CORS settings to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/token")
async def token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """
    Generates an Oauth2 token for users to programmatically access the API.
    
    :param form_data: The Oauth2 password request form data.

    :return: A dictionary containing the access token and token type.
    """
    # In a real application, you would validate the username and password here
    if form_data.username != "testuser" or form_data.password != "testpassword":
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token
    token_data = {
        "sub": form_data.username,
        "user_id": "1",              # Would get this from a DB in a real application
        "scopes": ["read", "write"]  # Would get this from a DB in a real application
    }
    access_token = create_access_token(
        data=token_data, 
        expires_delta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected-a")
async def protected_by_azure(user=Depends(verify_azure_token)) -> dict:
    """A sample protected endpoint that requires a valid JWT token. Verifies with Azure."""
    return {"message": "You are authenticated!", "user": user}


@app.get("/protected-b")
async def protected_by_token(user=Depends(get_current_user)) -> dict:
    """A sample protected endpoint that requires a valid JWT token. Verifies with custom."""
    return {"message": "You are authenticated!", "user": user}


@app.get("/unprotected")
async def unprotected() -> dict:
    """A sample unprotected endpoint that does not require authentication."""
    return {"message": "This endpoint is unprotected."}
