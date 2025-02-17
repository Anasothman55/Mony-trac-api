from typing import Annotated, List
from fastapi import  APIRouter, Body, status, HTTPException, Form,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import  EmailStr, ValidationError
from ..schema.user_auth import GetFullUser, CreateIUserDict,CreateUser
from ..db.index import get_db
from ..services.user_auth import AuthenticationServices
from ..email.user_auth import UserAuthEmail



route = APIRouter(tags=["auth"])




@route.post("/signup", status_code= status.HTTP_201_CREATED)
async def signup(
  user_model: Annotated[CreateIUserDict, Form()],
  db: Annotated[AsyncSession, Depends(get_db)]
):
  auth_services = AuthenticationServices(db)
  try:
    user = await auth_services.register(user_model)
    
    datadict = {
      "verify_url": "http://0.0.0.0:8000/api/auth/verify",
      "username": f"{user.first_name} {user.last_name}",
      "company_name": "Monix"
    }
    response = await UserAuthEmail.send_verification_email([user.email], datadict)
    
    return response
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))















