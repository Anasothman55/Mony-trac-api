from fastapi import HTTPException, Depends

from ..db.models import BalanceModel
from ..db.index import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import  Any
import uuid

from decimal import Decimal


class BalanceRepository:
  def __init__(self, db):
    self.db = db
    self.model = BalanceModel

  async def _statement(self, field: str, value: Any):
    statement = select(self.model).where(getattr(self.model, field) == value)
    result = await self.db.execute(statement)
    return result.scalars().first()

  async def _commit_refresh(self, row):
    await self.db.commit()
    await self.db.refresh(row)
    return row


  async def get_by_user_uid(self, uid: uuid.UUID) -> BalanceModel:
    return await self._statement(field="user_id", value=uid)

  async def update_balance(self,row_model: BalanceModel) :
    await self._commit_refresh(row_model)

  async def get_balance_amount(self, user_uid: uuid.UUID):
    result = await self.get_by_user_uid(user_uid)
    amount = result.income_amount - (result.expenses_amount + result.save_amount)
    return amount

  async def get_save_amount(self, user_uid: uuid.UUID):
    result = await self.get_by_user_uid(user_uid)
    return result.save_amount

  async def use_svae_utils(self, user_uid: uuid.UUID, amount: Decimal) :
    result = await self.get_by_user_uid(user_uid)
    result.save_amount -= amount
    await self.db.commit()  
    await self.db.refresh(result)  

async def get_balance_repo(db: AsyncSession = Depends(get_db)) -> BalanceRepository:
  return BalanceRepository(db)