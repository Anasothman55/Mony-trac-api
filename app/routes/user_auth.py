from typing import Annotated
from fastapi import  APIRouter, status, HTTPException, Form,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import  ValidationError
from ..schema.user import GetFullUser, CreateIUserDict,CreateUser
from ..db.index import get_db
from  ..util.user import verify_password_utils,hash_password_utils, validation_signup
from  ..db.models import UserModel


route = APIRouter(tags=["auth"])




@route.post("/signup", status_code= status.HTTP_201_CREATED, response_model= GetFullUser)
async def signup(
  user_model: Annotated[CreateIUserDict, Form()],
  db: Annotated[AsyncSession, Depends(get_db)]
):
  user = await validation_signup(db, user_model)
  hashing = hash_password_utils(user.password)
  user_data = user.model_dump(exclude={"password"})

  new_user = UserModel(**user_data, hash_password=hashing)
  db.add(new_user)
  await db.commit()
  await db.refresh(new_user)

  return new_user