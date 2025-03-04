from ..util.transection import TransectionsRepository
from ..db.index import get_db


from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

async def get_transaction_repo(db: AsyncSession = Depends(get_db)) -> TransectionsRepository:
  return TransectionsRepository(db)