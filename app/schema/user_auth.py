from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr
import uuid
from enum import Enum
from typing import List,Optional

from .balance import BalanceBase


class RoleBase(str, Enum):
  user = "user"
  admin = "admin"



class UserBase(BaseModel):
  username: StrictStr = Field(...,max_length=128)
  email: EmailStr
  first_name: str = Field(min_length=2, max_length=128, pattern=r"^[A-Za-z]+$")
  last_name: str = Field(min_length=2, max_length=128, pattern=r"^[A-Za-z]+$")

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "username": "john_doe",
        "email": "john_doe@example.com",
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  )


class GetFullUser(UserBase):
  uid: uuid.UUID
  role: str
  is_active: bool
  last_login: datetime | None = None
  created_at: datetime
  updated_at: datetime
  is_verified: bool

  balance_model: Optional[BalanceBase] = {}
  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "username": "john_doe",
        "email": "john_doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "uid": str(uuid.uuid4()),
        "role": "users",
        "is_active": True,
        "last_login": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "balance_model": {
          "uid": str(uuid.uuid4()),
          "income_amount": 0.0,
          "expenses_amount": 0.0,
          "save_amount": 0.0,
          "created_at": datetime.now(),
          "updated_at": datetime.now()
        }
      }
    }
  )

class CreateIUserDict(BaseModel):
  username: str | None = None
  email: str | None = None
  first_name: str | None = None
  last_name: str | None = None
  password: str | None = None


  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "first_name": "John",
        "last_name": "Doe",
        "username": "john_doe",
        "email": "john_doe@example.com",
        "password":"example1234"
      }
    }
  )

class CreateUser(UserBase):
  password: str = Field(min_length=8, max_length=128)

  model_config = ConfigDict(
    str_strip_whitespace=True,
    extra='forbid',
    json_schema_extra={
      "example": {
        "first_name": "John",
        "last_name": "Doe",
        "username": "john_doe",
        "email": "john_doe@example.com",
        "password":"example1234"
      }
    }
  )

class UserLogin(BaseModel):
  email: EmailStr
  password: str
















