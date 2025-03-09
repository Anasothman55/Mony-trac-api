from os import access
from typing import Annotated, List
from fastapi import APIRouter,  Query, status, HTTPException, Form, Depends, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..db.models import UserModel
from ..dependencies.user_auth import get_current_user
from ..dependencies.transaction import get_transaction_repo
from ..dependencies.categories import get_category_repo
from ..db.index import get_db
from ..schema.categories import  CATEGORY_TYPE_ENUM
from ..schema.transection import GetTransaction,GetAllTransaction, TransactionBase, CreateTransaction,UpdateTransaction
from ..services.transection import (
  get_transection_by_type_services,
  get_all_transection_services,
  create_transection_services,
  get_one_transection_services,
  update_transaction_services,
  delete_transaction_services
)

from ..services.balances import delete_transaction_balance

from ..util.balance import BalanceRepository, get_balance_repo
from ..util.transection import TransectionsRepository
from ..util.categories import CategoryRepository

route = APIRouter(
  dependencies= [Depends(get_current_user)]
)




@route.get('/get_all', response_model= List[GetAllTransaction], status_code= status.HTTP_200_OK)
async def get_all_transaction(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    descending: Annotated[bool, Query()] = False,
    enum: Annotated[CATEGORY_TYPE_ENUM, Query()] = None,
):
  order_by = "created_at"
  if descending:
    order_by = f"-{order_by}"

  user_uid = current_user.uid
  result = await get_all_transection_services(db,user_uid=user_uid,order_by= order_by)

  if enum:
    result = [item for item in result if item.type == enum]

  if not result:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
  return jsonable_encoder(result)

@route.get("/get_by_id/{transaction_uid}", response_model= GetTransaction, status_code= status.HTTP_200_OK)
async def get_one_categories(
    transaction_uid: Annotated[uuid.UUID, Path(...)],
    repo: Annotated[TransectionsRepository, Depends(get_transaction_repo)],
):
  try:
    result = await get_one_transection_services(repo, transaction_uid)
    return jsonable_encoder(result)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@route.get("/get_by_type/{enum_type}", response_model= List[GetAllTransaction], status_code= status.HTTP_200_OK)
async def get_one_categories(
    enum_type: Annotated[CATEGORY_TYPE_ENUM, Path()],
    repo: Annotated[TransectionsRepository, Depends(get_transaction_repo)],
):
  try:
    result = await get_transection_by_type_services(repo, enum_type)
    if not result:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")
    return jsonable_encoder(result)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@route.post("/create/{types}", response_model=GetAllTransaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    types: Annotated[CATEGORY_TYPE_ENUM, Path()],
    req_data: Annotated[CreateTransaction, Form()],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    repo: Annotated[TransectionsRepository, Depends(get_transaction_repo)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repo)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)]
):

  user_uid = current_user.uid
  new_data = req_data.model_dump()
  new_data.update({"user_uid": user_uid,"type":types})

  result = await create_transection_services(repo,category_repo,new_data, balance_repo)
  return jsonable_encoder(result)



@route.patch("/update/{transaction_uid}", status_code=status.HTTP_201_CREATED, response_model=GetAllTransaction)
async def update_transaction(
    transaction_uid: Annotated[uuid.UUID,Path(...)],
    req_data: Annotated[UpdateTransaction, Form()],
    repo: Annotated[TransectionsRepository, Depends(get_transaction_repo)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)]
):
  try:
    new_data = req_data.model_dump()
    result = await update_transaction_services(repo, transaction_uid, new_data, balance_repo)
    return jsonable_encoder(result)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@route.delete("/delete/{transaction_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    *
    transaction_uid: Annotated[uuid.UUID, Path(...)],
    remove_q: Annotated[bool, Query(...)] = True,
    repo: Annotated[TransectionsRepository, Depends(get_transaction_repo)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)]
):
  try:
    user_uid = current_user.uid
    amount,types = await delete_transaction_services(repo, transaction_uid)
    if remove_q:
      await delete_transaction_balance(balance_repo,amount,user_uid, types)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

