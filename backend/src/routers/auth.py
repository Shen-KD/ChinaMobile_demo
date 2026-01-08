from fastapi import APIRouter, Request, Response, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import logging

from src.config import settings
from src.utils.cas_client import cas_client
from src.utils.security import security

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

class ValidateTicketRequest(BaseModel):
    ticket: str
    service: str

@router.get("/login")
async def login(request: Request, service: str = settings.FRONTEND_URL):
    """
    Redirect to CAS login with the service parameter set to the provided service URL (frontend).
    """
    # The service URL is where CAS will redirect back to after login (the frontend)
    cas_login_url = cas_client.get_login_url(service)
    return RedirectResponse(cas_login_url)

@router.post("/validate")
async def validate_ticket(req: ValidateTicketRequest, response: Response):
    """
    Validate the CAS ticket provided by the frontend.
    """
    # Validate ticket with CAS using the same service URL that was used for login
    is_valid, username, attributes = await cas_client.validate_ticket(req.ticket, req.service)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="CAS Authentication failed")
    
    # Create session/token
    user_data = {
        "sub": username,
        "username": username,
        **attributes
    }
    
    access_token = security.create_access_token(user_data)
    
    # Set HTTPOnly cookie
    response.set_cookie(
        key="xunyuan_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    logger.info(f"validate_ticket user_data: {user_data}")
    return {"success": True, "user": user_data}

@router.get("/logout")
async def logout(request: Request, service: str = settings.FRONTEND_URL):
    """
    Log the user out locally and then from CAS.
    """
    response = RedirectResponse(url=cas_client.get_logout_url(service))
    response.delete_cookie(key="xunyuan_token", path="/", httponly=True)
    return response

@router.get("/user")
async def get_user(request: Request):
    """
    Get the current logged-in user.
    """
    user = security.get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"success": True, "user": user}
