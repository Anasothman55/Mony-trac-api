
from fastapi import Depends, HTTPException, Response, status

from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt, ExpiredSignatureError
from pydantic import EmailStr, ValidationError
import redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from typing import Annotated, Any, List
import uuid

from rich import print
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from ..db.index import get_db
from ..db.redis import redis_manager
from ..db.models import UserModel, BalanceModel
from ..util.user_auth import CheckRefreshTokenData, UserAuthUtils, UserTokenUtils
from ..schema.user_auth import CreateIUserDict, CreateUser
from ..email.user_auth import UserAuthEmail


class UserRepositoryServer:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.model = UserModel
  async def _statement(self,  field: str, value: Any):
    statement = (
      select(self.model)
      .options(selectinload(self.model.balance_model))  # Eager load balance
      .where(getattr(self.model, field) == value)
    )

    result = await self.db.execute(statement)
    return result.scalars().first()
  async def get_by_email(self, email: EmailStr) -> UserModel:
    return await self._statement("email", email)
  async def get_by_username(self, username: str) -> UserModel:
    return await self._statement("username", username)
  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement("uid", uid)
  async def create_row(self,new_row):
    self.db.add(new_row)
    await self.db.commit()
    await self.db.refresh(new_row)
    return new_row

class AuthenticationServices:

  def __init__(self, db: AsyncSession):
    self.db = db
    self.user_repo = UserRepositoryServer(db)
    
  async def _unique_validation(self, email: EmailStr, username: str) -> List[dict]:
    """* a private methods that are used to validate the uniqueness of the email and username """
    errors = []
    if existing_username :=  await self.user_repo.get_by_username(username):
      errors.append(UserAuthUtils.error_schema("username", existing_username.username))
    if existing_email := await self.user_repo.get_by_email(email):
      errors.append(UserAuthUtils.error_schema("email", existing_email.email))
    return errors

  async def _validate_user_data(self, user: CreateIUserDict) -> CreateUser:
    """* a private methods that are used to validate the user data and check for uniqueness """
    errors = []
    result = None
    try:
      user_data = CreateUser(**user.model_dump())
    except ValidationError as pe:
      errors.extend(pe.errors())
    else:
      result = user_data

    unique_errors = await self._unique_validation( user.email, user.username)
    if unique_errors:
      errors.extend(unique_errors)

    if errors:
      raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=errors
      )

    return result
  
  async def _send_verify_email(self, email: EmailStr, full_name: str):
    serializer = {"email": email}
    verify_token = UserAuthUtils.create_url_safe_token(serializer)
    
    datadict = {
      "verify_url": f"http://0.0.0.0:8000/api/auth/verify?token={verify_token}",
      "username": full_name,
      "company_name": "Monix"
    }
    
    response = await UserAuthEmail.send_verification_email([email], datadict)
    return response
  async def _send_reset_password_email(self, email: str, full_name: str):
    serializer = {"email": email}
    reset_token = UserAuthUtils.create_url_safe_token(serializer)

    datadict = {
      "reset_url": f"http://0.0.0.0:8000/api/auth/reset-password?token={reset_token}",
      "username": full_name,
      "company_name": "Monix"
    }
    msg = "Password reset email sent successfully. Please check your email address."
    response = await UserAuthEmail.send_reset_password_email([email], datadict, msg)
    return response
  async def _authenticate_user(self, email: EmailStr, password: str) -> UserModel:
    user = await self.user_repo.get_by_email(email)
  
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "User not found", "hint": "Please check the email address","loc":"email"}
      )
    
    if password != user.hash_password:

      if not UserAuthUtils.verify_password_utils(password, user.hash_password):
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail={"error": "Invalid password", "hint": "Ensure the password is correct", "loc": "password"}
        )

    return user
  async def _set_auth_token(self, user: UserModel) -> None:
    user_token_dict = {"sub": str(user.uid), "email": user.email}
    token = await self._token_service.create_token(user_token_dict)
    self._token_service.set_cookie_token(self.response, token)
  async def register(self, user_model: CreateIUserDict) -> dict:
    """* a public method that is used to register a new user """
    user = await self._validate_user_data(user_model)
    hashing = UserAuthUtils.hash_password_utils(user.password)
    user_data = user.model_dump(exclude={"password"})
    
    new_user = UserModel(**user_data, hash_password=hashing)
    
    user = await self.user_repo.create_row(new_user)

    new_balance = BalanceModel(user_id= user.uid)
    await self.user_repo.create_row(new_balance)

    response = await self._send_verify_email(user.email, f"{user.first_name} {user.last_name}")
    return response
  async def verify_email(self, user_email: EmailStr, response: Response):
    
    user = await self.user_repo.get_by_email(user_email)
    
    if user.is_verified:
      return RedirectResponse(url="/")
    
    user.is_verified = True
    await self.db.commit()
    await self.db.refresh(user)
    
    return user
  @staticmethod
  async def refresh_token_service(access_token, refresh_token, response: Response):
    try:
      payload = UserTokenUtils.jwt_decode(access_token, options={"verify_exp": False})
      user_uid = payload.get("sub")
      at_rtuid = payload.get("rtuid")

      redis_refresh_token = await redis_manager.get_refresh_token(user_uid)
      
      redis_refresh_payload = CheckRefreshTokenData(UserTokenUtils.jwt_decode(redis_refresh_token)).validate()
      rrp_rtuid = redis_refresh_payload.get('rtuid')
      await redis_manager.is_token_blacklisted(rrp_rtuid)
      
      refresh_token_payload = CheckRefreshTokenData(UserTokenUtils.jwt_decode(refresh_token)).validate()
      rt_user_uid = refresh_token_payload.get('sub')
      rt_rtuid = refresh_token_payload.get('rtuid')
      await redis_manager.is_token_blacklisted(rt_rtuid)
      if redis_refresh_token != refresh_token:
        raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail={
            "error": "Invalid refresh token you refresh token and server refresh token don't match"
          })
      if user_uid != rt_user_uid or at_rtuid != rt_rtuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Token mismatch: Access token and refresh token details do not match."}
        )
      token_dict = {
        "sub": user_uid,
        "email": payload.get("email"),
      }
      user_token = UserTokenUtils(token_dict)
      result = await user_token.refresh_token_utils(rt_rtuid, response)
      return result
    except ExpiredSignatureError:
        # Handle expired JWT token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
    except JWTError as e:
        # Log the exception and return a more specific error message
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")
  async def login_services(self, form_data: dict, response: Response):
    user = await self._authenticate_user(**form_data)
    
    if not user.is_verified:
      msg = "Your account is not verified. A new verification email has been sent."
      response_data = await self._send_verify_email(user.email, f"{user.first_name} {user.last_name}", msg)
      return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": response_data}
      )
    
    token_dict = {
      "sub": str(user.uid),
      "email": user.email
    }

    user.last_login = datetime.now(timezone.utc)
    await self.db.commit()
    await self.db.refresh(user)
    
    user_token = UserTokenUtils(token_dict)
    result = await user_token.create_token(response)

    return {"message": result, "user": user}

  @staticmethod
  async def logout_service(access_token, refresh_token, response: Response):
    try:

      access_token_decode = UserTokenUtils.jwt_decode(access_token)
      user_uid = str(access_token_decode.get("sub"))
      redis_refresh_token = await redis_manager.get_refresh_token(user_uid)
      
      if redis_refresh_token != refresh_token:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail={"error": "Invalid refresh token"}
        )
      
      redis_payload = UserTokenUtils.jwt_decode(redis_refresh_token)
      await redis_manager.delete_refresh_token(user_uid)
      await redis_manager.blacklist_refresh_token(redis_payload.get('rtuid'))
      
      response.delete_cookie("access_token")
      response.delete_cookie("refresh_token")
    except ExpiredSignatureError:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired"
      )
    except JWTError as e:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token: {str(e)}"
      )

  async def forgot_password_services(self, email: EmailStr):
    user = await self.user_repo.get_by_email(email)
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "User not found", "hint": "Please check the email address", "loc": "email"}
      )
    email = user.email
    full_name = f"{user.first_name} {user.last_name}"
    response = await self._send_reset_password_email(email, full_name)
    return response

  async def reset_password_(self, token: str, new_password: str):

    await redis_manager.is_password_reset_token_blacklisted(token)

    user_email = dict(UserAuthUtils.decode_url_safe_token(token)).get('email', None)
    user = await self.user_repo.get_by_email(user_email)

    if not user.is_verified:
      return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Your account is not verified. Please verify your account."
      )

    password_match = UserAuthUtils.verify_password_utils(new_password, user.hash_password)

    if password_match:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="You cannot use the same password as the current password."
      )

    hashing = UserAuthUtils.hash_password_utils(new_password)

    user.hash_password = hashing
    await self.db.commit()
    await self.db.refresh(user)

    await redis_manager.blacklist_password_reset_token(token)

    return user













