from fastapi import  APIRouter, Depends, Response, status, HTTPException
from typing import Annotated
from sqlalchemy import  text
from sqlalchemy.ext.asyncio import AsyncSession
from .db.index import get_db


root = APIRouter()


@root.get("/helth", status_code=status.HTTP_200_OK)
async def helth(db: Annotated[AsyncSession, Depends(get_db)]):
  try:
    result = await db.execute(text("SELECT 1"))
    await db.commit()

    return {
      "status": "healthy",
      "database": "connected",
      "message": "Application is running normally",
      "execute": result
    }
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail=f"Database connection failed: {str(e)}"
    )

@root.get("/")
async def root_route(res: Response):
  return {"message": "Welcome to FastAPI Project"}



from .routes.user_auth import route as auth_route
from .routes.categories import route as category_route
from .routes.transection import route as transaction_route
from .routes.balance import route as balance_route

root.include_router(auth_route, prefix="/api/auth", tags=["auth"])
root.include_router(category_route, prefix="/api/categories", tags=["categories"])
root.include_router(transaction_route, prefix="/api/transactions", tags=["transactions"])
root.include_router(balance_route, prefix="/api/balance", tags=["balance"])


