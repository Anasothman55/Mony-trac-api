
from os import access
from typing import Annotated, List
from fastapi import  APIRouter, Body, Query, Response, status, HTTPException, Form,Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import  EmailStr, ValidationError

from ..db.redis import redis_manager
from ..db.models import UserModel
from ..dependencies.user_auth import get_all_token, get_current_user
from ..schema.user_auth import GetFullUser, CreateIUserDict,CreateUser
from ..db.index import get_db
from ..services.user_auth import AuthenticationServices
from ..util.user_auth import UserAuthUtils
from rich import print

route = APIRouter(tags=["auth"])




@route.post("/signup", status_code= status.HTTP_201_CREATED)
async def signup_route(
  user_model: Annotated[CreateIUserDict, Form()],
  db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
  auth_services = AuthenticationServices(db)
  try:
    user = await auth_services.register(user_model)
    return user
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@route.get("/verify", status_code= status.HTTP_202_ACCEPTED)
async def verify_user_route(
  token : Annotated[str , Query(...)],
  db: Annotated[AsyncSession, Depends(get_db)],
  response: Response
):
  user_email = dict(UserAuthUtils.decode_url_safe_token(token))
  auth_services = AuthenticationServices(db)

  try:
    user = await auth_services.verify_email(user_email.get('email', None), response)
    
    if isinstance(user, RedirectResponse):
      return user
    
    if user:
      return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
          "message": "Email verified successfully. You will be redirected shortly.",
          "redirect_url": "/"  
        }
      )

  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@route.post("/login", status_code= status.HTTP_202_ACCEPTED)
async def login_route(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  db: Annotated[AsyncSession, Depends(get_db)],
  response: Response
):
  auth_services = AuthenticationServices(db)
  try:
    form_dict = {
      "email": form_data.username,
      "password": form_data.password
    }
    response = await auth_services.login_services(form_dict,response = response)
    return response
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@route.post("/logout", status_code= status.HTTP_204_NO_CONTENT)
async def logout_route(current_user: Annotated[UserModel, Depends(get_current_user)] ,token: Annotated[dict, Depends(get_all_token)], response: Response):
  access_token, refresh_token = token.values()
  auth_services = await AuthenticationServices.logout_service(access_token, refresh_token, response)
  return auth_services
@route.get('/me', response_model=GetFullUser, status_code=status.HTTP_200_OK)
async def get_user_me_router( current_user: Annotated[UserModel, Depends(get_current_user)]):
  try:
    json_data = jsonable_encoder( current_user)
    return json_data
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))






