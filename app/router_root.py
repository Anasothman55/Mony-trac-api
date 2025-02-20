from fastapi import  APIRouter, Depends, status, HTTPException
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




from .routes.user_auth import route as auth_route

@root.get("/")
async def root_route():
  return {"message": "Welcome to FastAPI Project"}

root.include_router(auth_route, prefix="/api/auth", tags=["auth"])


