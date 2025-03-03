from os import access
from typing import Annotated, List
from fastapi import APIRouter,  Query, status, HTTPException, Form, Depends, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..db.models import UserModel
from ..dependencies.user_auth import get_current_user
from ..db.index import get_db



route = APIRouter()




@route.get('/get_all' )
async def get_all_transactions():
  pass


@route.get("/get_by_id/{uid}")
async def get_transaction_by_id():
  pass

@route.post("/create")
async def create_transaction():
  pass


@route.patch("/update/{uid}")
async def update_transaction():
  pass


@route.delete("/delete/{uid}")
async def delete_transaction():
  pass

