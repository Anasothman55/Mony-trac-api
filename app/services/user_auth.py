from fastapi import HTTPException, status

from pydantic import EmailStr, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Any, List
import uuid

from watchfiles import awatch

from ..db.models import UserModel
from ..util.user_auth import UserAuthUtils
from ..schema.user_auth import CreateIUserDict, CreateUser


class UserRepositoryServer:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.model = UserModel
  async def _statement(self,  field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def get_by_email(self, email: EmailStr):
    return await self._statement("email", email)
  async def get_by_username(self, username: str):
    return await self._statement("username", username)
  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement("uid", uid)
  async def create_user(self,new_user) -> UserModel:
    self.db.add(new_user)
    await self.db.commit()
    await self.db.refresh(new_user)
    return new_user


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
  async def register(self, user_model: CreateIUserDict):
    """* a public method that is used to register a new user """
    user = await self._validate_user_data(user_model)
    hashing = UserAuthUtils.hash_password_utils(user.password)
    user_data = user.model_dump(exclude={"password"})
    
    new_user = UserModel(**user_data, hash_password=hashing)

    return await self.user_repo.create_user(new_user)






























