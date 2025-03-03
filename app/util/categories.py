from ..db.models import CategoryModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import  Any
import uuid

class CategoryRepository:
  def __init__(self, db):
    self.db = db
    self.model = CategoryModel

  async def _statement(self, field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def _commit_refresh(self, row):
    await self.db.commit()
    await self.db.refresh(row)
    return row

  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement(field="uid", value=uid)

  async def create_row(self,new_row) -> CategoryModel:
    self.db.add(new_row)
    return await self._commit_refresh(new_row)

  async def update_row(self, req_data, row_model: CategoryModel) -> CategoryModel:
    for key, value in req_data.items():
      if value:
        setattr(row_model,key,value)
    return await self._commit_refresh(row_model)







