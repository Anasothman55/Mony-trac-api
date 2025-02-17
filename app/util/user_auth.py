from fastapi import HTTPException, status

from ..db.models import UserModel
from ..schema.user import CreateUser, CreateIUserDict
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from pydantic import ValidationError, EmailStr
from sqlmodel import select

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password_utils(password: str) -> str:
  return pwd.hash(password)

def verify_password_utils(plain_password: str, hash_password: str) -> bool:
  return pwd.verify(plain_password, hash_password)


def error_schema(body: str, field: str):
  return {
    "type": "conflict",
    "loc": [ body],
    "msg": f"{body} already exists",
    "input": field
  }



async def auth_unique_validation(db: AsyncSession,email: str, username: str):
  errors = []
  statement = select(UserModel).where(getattr(UserModel, "email") == email)
  result = await db.execute(statement)
  email_uni =  result.scalars().first()
  if email_uni:
    errors.append( error_schema("email", email_uni.email))
  statement = select(UserModel).where(getattr(UserModel, "username") == username)
  result = await db.execute(statement)
  username_uni =  result.scalars().first()
  if username_uni:
    errors.append( error_schema("username", username_uni.email))
  return errors


async def validation_signup(db : AsyncSession, user: CreateIUserDict) -> CreateUser:
  try:
    user_data = CreateUser(**user.model_dump())
    unique_errors = await auth_unique_validation(db, user_data.email, user_data.username)
    if unique_errors:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=unique_errors)

    return user_data
  except ValidationError as pe:
    details = pe.errors()
    unique_errors = await auth_unique_validation(db, user.email, user.username)
    if unique_errors:
      details.append(*unique_errors)
    await db.rollback()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=details)
