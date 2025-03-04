from fastapi import Depends, HTTPException, Response, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select,desc, asc,and_
from typing import Annotated, Any, List, Sequence
import uuid

from rich import print

from ..db.index import get_db
from ..db.models import CategoryModel
from ..util.categories import CategoryRepository



async def get_all_category_services(db: AsyncSession,user_uid, order_by) -> Sequence[CategoryModel]:
  order_column = getattr(CategoryModel, "created_at")
  if order_by.startswith('-'):
    order_column = desc(order_column)
  else:
    order_column = asc(order_column)

  statement = (
    select(CategoryModel).where(CategoryModel.user_uid == user_uid).order_by(order_column)
  )
  result = await db.execute(statement)
  return result.scalars().all()


async def create_category_services(repo: CategoryRepository,req_data: dict) -> CategoryModel:
  new_row = CategoryModel(**req_data )
  result = await repo.create_row(new_row)
  return result
  
async def get_one_category_services(repo: CategoryRepository, category_uid: uuid.UUID) -> CategoryModel:
  result = await repo.get_by_uid(category_uid)
  if not result:
    raise HTTPException(status_code=404, detail="Category not found")
  return result


async def update_category_services(repo: CategoryRepository, category_uid: uuid.UUID, req_data: dict) -> CategoryModel:
  category = await get_one_category_services(repo,category_uid)
  result = await repo.update_row(req_data, category)
  return result


async def delete_category_services(repo: CategoryRepository, category_uid: uuid.UUID) -> None:
  category = await repo.get_by_uid(category_uid)
  await repo.delete_row(category)
  return None
