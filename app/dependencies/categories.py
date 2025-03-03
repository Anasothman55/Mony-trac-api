from ..util.categories import CategoryRepository
from ..db.index import get_db


from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

async def get_category_repo(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
  return CategoryRepository(db)