import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from ..core.config import setting
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy import text
from sqlmodel import SQLModel



engine = create_async_engine(
  url=setting.POSTGRESQL_URI,
  echo=False,  # Set to False in production
  pool_size=5,  # Maximum number of connections in the pool
  max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
  pool_timeout=30,  # Seconds to wait before giving up on getting a connection from the pool
  pool_recycle=1800,  # Recycle connections after 1800 seconds (30 minutes)
  #connect_args={"ssl": True}  # Explicitly enable SSL
)


async_session_maker = sessionmaker(
  bind=engine,
  class_ = AsyncSession,
  expire_on_commit=False
)



async def get_db() -> AsyncGenerator[AsyncSession, None]:
  async with async_session_maker() as session:
    try:
      yield session
    except Exception as e:
      await session.rollback()
      raise
    finally:
      await session.close()

async def close_db_connection():
  await engine.dispose()





async def init_db():
  async with engine.begin() as conn:
    await conn.run_sync(SQLModel.metadata.create_all)
    print("Database tables created successfully")



