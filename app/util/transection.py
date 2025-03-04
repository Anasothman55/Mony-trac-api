from fastapi import HTTPException

from ..db.models import transactionModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import  Any
import uuid

class TransectionsRepository:
  def __init__(self, db):
    self.db = db
    self.model = transactionModel

  async def _statement(self, field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def _commit_refresh(self, row):
    await self.db.commit()
    await self.db.refresh(row)
    return row

  async def delete_row(self, row):
    try:
        await self.db.delete(row)
        await self.db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

  async def get_by_uid(self, uid: uuid.UUID):
    return await self._statement(field="uid", value=uid)
  async def get_by_type(self, type: str):
    statement = select(self.model).where(getattr(self.model, "type") == type)
    result = await self.db.execute(statement)
    return result.scalars().all()

  async def create_row(self,new_row) -> transactionModel:
    self.db.add(new_row)
    return await self._commit_refresh(new_row)

  async def update_row(self, req_data, row_model: transactionModel) -> transactionModel:
    for key, value in req_data.items():
      if value:
        setattr(row_model,key,value)
    return await self._commit_refresh(row_model)
