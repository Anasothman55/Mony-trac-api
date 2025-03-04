
from fastapi import Depends, HTTPException, Response, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select ,desc, asc ,and_
from typing import Annotated, Any, List, Sequence
import uuid

from rich import print

from ..db.index import get_db
from ..db.models import transactionModel
from ..util.categories import CategoryRepository
from ..util.transection import  TransectionsRepository



async def get_all_transection_services(db: AsyncSession,user_uid, order_by) -> Sequence[transactionModel]:
  order_column = getattr(transactionModel, "created_at")
  if order_by.startswith('-'):
    order_column = desc(order_column)
  else:
    order_column = asc(order_column)

  statement = (
    select(transactionModel).where(transactionModel.user_uid == user_uid).order_by(order_column)
  )
  result = await db.execute(statement)
  return result.scalars().all()


async def create_transection_services(
    repo: TransectionsRepository ,category_repo: CategoryRepository,req_data: dict) -> transactionModel:
  category_id = req_data.get("category_id")
  result = await category_repo.get_by_uid(category_id)

  if not result:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

  if result.type != req_data['type']:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category type mismatch")

  new_row = transactionModel(**req_data )
  result = await repo.create_row(new_row)
  return result

async def get_one_transection_services( repo: TransectionsRepository ,transection_uid: uuid.UUID) -> transactionModel:
  result = await repo.get_by_uid(transection_uid)
  if not result:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
  return result

async def get_transection_by_type_services(
    repo: TransectionsRepository, types: str) -> Sequence[transactionModel]:
  result = await repo.get_by_type(types)
  return result

async def update_transaction_services(
    repo: TransectionsRepository, transection_uid: uuid.UUID, req_data: dict) -> transactionModel:
  transaction = await get_one_transection_services(repo ,transection_uid)
  result = await repo.update_row(req_data, transaction)
  return result


async def delete_transaction_services(repo: TransectionsRepository, transection_uid: uuid.UUID) -> None:
  transaction = await repo.get_by_uid(transection_uid)
  if not transaction:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
  await repo.delete_row(transaction)
  return None
