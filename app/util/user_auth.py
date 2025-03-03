import uuid
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from ..core.config import setting
from fastapi import HTTPException, Response, status
from jose import jwt, JWTError  # type: ignore
from datetime import datetime, timezone, timedelta
from pydantic import EmailStr
from ..db.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from typing import Callable, Optional
from ..db.redis import redis_manager


pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

serializer = URLSafeTimedSerializer(
  secret_key=setting.SECRET_KEY,
  salt="email-config"
)


class UserTokenUtils:
  def __init__(self, token_dict: dict):
    self.token_dict = token_dict
  
  def create_access_token(self, data:dict, expires_delta: timedelta | None = None, refresh: bool = False):
    to_encod = data.copy()
    if expires_delta:
      expire = datetime.now(timezone.utc) + expires_delta
    else:
      expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encod.update({"exp": expire})
    to_encod.update({"refresh": refresh})
    encoded_jwt = jwt.encode(to_encod, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt

  def create_refresh_token(self, data:dict, expires_delta: timedelta | None = None, refresh: bool = True):
    to_encod = data.copy()
    if expires_delta:
      expire = datetime.now(timezone.utc) + expires_delta
    else:
      expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encod.update({"exp": expire})
    to_encod.update({"refresh": refresh})
    encoded_jwt = jwt.encode(to_encod, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt

  async def refresh_token_utils(self, rtuid, response: Response):
    atuid = str(uuid.uuid4())
    
    access_token_expire = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = self.create_access_token(
      data={**self.token_dict, "atuid": atuid, "rtuid": rtuid},
      expires_delta=access_token_expire
    )

    response.set_cookie(
      key="access_token",
      value= access_token,
      httponly=True,
      secure=False,  # Added secure flag for HTTPS
      samesite='lax'  # Added samesite protection
    )

    return "Refresh Token successfully"
  async def create_token(self, response: Response):
    """ rhis method to create a new token and store refresh token in redis and access token in cookie"""
    atuid = str(uuid.uuid4())
    rtuid = str(uuid.uuid4())
    
    access_token_expire = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = self.create_access_token(
      data={**self.token_dict, "atuid": atuid, "rtuid": rtuid},
      expires_delta=access_token_expire
    )
    
    user_uid = str(self.token_dict.get("sub"))
    refresh_token_expire = timedelta(days=setting.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = self.create_refresh_token(
      data={"sub": user_uid, "rtuid": rtuid}, expires_delta=refresh_token_expire
    )

    await redis_manager.store_refresh_token(user_id=user_uid, refresh_token=refresh_token,ttl_days=setting.REFRESH_TOKEN_EXPIRE_DAYS)
    
    response.set_cookie(
      key="access_token",
      value= access_token,
      httponly=True,
      secure=False,  # Added secure flag for HTTPS
      samesite='lax'  # Added samesite protection
    )
    
    response.set_cookie(
      key="refresh_token",
      value=refresh_token,
      httponly=True,
      secure=False,
      samesite="lax",
    )
    return "User login successfully"
  
  @staticmethod
  def jwt_decode(token: str, options: dict | None = None):
    try:
      if options:
        payload = jwt.decode(token, setting.SECRET_KEY,algorithms= setting.ALGORITHM, options=options)
      else:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=setting.ALGORITHM)
      return payload
    except JWTError as jex:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'error': str(jex), 'message': "Invalid"})


@dataclass
class CheckAccessTokenData:
  sub: str
  email: EmailStr
  atuid: str
  rtuid: str
  exp: int
  refresh: bool
  user: UserModel | None = None
  get_user_by_uid: Callable[[uuid.UUID], Optional[UserModel]] = None
  db: AsyncSession = None
  
  async def validate(self):
    credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
    )
    
    if not all([self.sub, self.email, self.atuid, self.rtuid, self.exp]):
      raise credentials_exception

    user_data = await self.get_user_by_uid(uuid.UUID(self.sub))

    if not user_data:
      raise credentials_exception

    self.user = user_data

    if not self.user.is_active:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is inactive. Please contact support.",
      )


@dataclass
class CheckRefreshTokenData:
  rrf: dict
  
  def validate(self) -> dict:
    credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
    )
    
    rfdata = ["sub", "rtuid", "exp", "refresh"]
    if not all(rfdata):
      raise credentials_exception
    return dict(self.rrf)


class  UserAuthUtils:

  @staticmethod
  def hash_password_utils(password: str) -> str:
    return pwd.hash(password)
  @staticmethod
  def verify_password_utils(plain_password: str, hash_password: str) -> bool:
    return pwd.verify(plain_password, hash_password)

  @staticmethod
  def error_schema(body: str, field: str):
    return {
      "type": "UniqueViolation",
      "loc": [ body],
      "msg": f"{body} already exists",
      "input": field
    }

  @staticmethod
  def create_url_safe_token(data: dict, expires_in: int = 3600 * 24):
    token = serializer.dumps(data)
    return token
  @staticmethod
  def decode_url_safe_token(token: str, max_age: int = 3600 * 24):
    try:
      return serializer.loads(token, max_age=max_age)
    except SignatureExpired:
      raise HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail={"message": "Token has expired"}
      )
    except BadSignature:
      raise HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail={"message": "Invalid token"}
      )


