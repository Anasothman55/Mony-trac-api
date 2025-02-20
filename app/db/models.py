from sqlmodel import SQLModel,Field,Column, Relationship,DECIMAL, Date
from datetime import datetime, date,timezone, time, timedelta
import sqlalchemy.dialects.postgresql as pg
import uuid
from enum import Enum
from sqlalchemy import Enum as SQLEnum, event, TIMESTAMP, DateTime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.sql import func





class TimestampUUIDMixin:
  uid: uuid.UUID = Field(
    sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4)
  )
  created_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
  )
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  )



class UserModel(TimestampUUIDMixin, SQLModel, table= True):
  __tablename__ = "users"

  username: str = Field(unique=True, index=True)
  email: str = Field(unique=True, index=True)
  first_name: str = Field(index=True)
  last_name: str = Field(index=True)
  role: str = Field(index= True, default="user")
  is_active: bool = Field(default=True)
  hash_password: str = Field(exclude=True, nullable=True)
  is_verified: bool = Field(default = False)
  last_login: datetime = Field(
    sa_column=Column(
      DateTime(timezone=True), nullable=True
    )
  )
  def __repr__(self):
    return f"<Book {self.username}>"



























