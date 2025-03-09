from sqlmodel import SQLModel,Field,Column, Relationship,DECIMAL, Date
from sqlalchemy import Enum as SQLEnum, event, TIMESTAMP, DateTime
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.sql import func

from datetime import datetime, date,timezone, time, timedelta
import uuid
from enum import Enum
from decimal import Decimal
from typing import List, Optional




class UserModel(SQLModel, table= True):
  __tablename__ = "users"

  uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4))
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

  created_at: datetime = Field( sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)) )
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  )

  balance_model: Optional["BalanceModel"] = Relationship(back_populates="user_model", sa_relationship_kwargs={"lazy": "selectin"})
  category_model: List["CategoryModel"] = Relationship(back_populates="user_model", sa_relationship_kwargs={"lazy": "selectin"})

  def __repr__(self):
    return f"<Book {self.username}>"


class BalanceModel(SQLModel, table = True):
  __tablename__ = "balances"

  uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4))
  income_amount : Decimal = Field(sa_column=Column(DECIMAL, default=0.0))
  expenses_amount : Decimal = Field(sa_column=Column(DECIMAL, default=0.0))
  save_amount: Decimal = Field(sa_column=Column(DECIMAL, default=0.0))

  user_id: uuid.UUID  = Field(foreign_key="users.uid", unique=True)

  created_at: datetime = Field( sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)) )
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  )

  user_model: Optional[UserModel] = Relationship(back_populates="balance_model",sa_relationship_kwargs={"lazy": "selectin"})

  def __repr__(self):
    return f"<Book {self.income_amount - (self.expenses_amount + self.save_amount)}>"



class CategoryModel( SQLModel, table = True):
  __tablename__ = "categories"

  uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4))
  name: str = Field(index=True, unique= True)
  type: str = Field(index=True)
  user_uid: uuid.UUID = Field( foreign_key="users.uid")

  user_model: Optional[UserModel] = Relationship(back_populates="category_model", sa_relationship_kwargs={"lazy": "selectin"})
  transactions: List["transactionModel"] = Relationship(
    back_populates="category",sa_relationship_kwargs={"lazy": "selectin"}
  )

  created_at: datetime = Field( sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)) )
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  )
  def __repr__(self):
    return f"<Book {self.name}>"


class transactionModel(SQLModel, table = True):
  __tablename__ = "transactions"

  uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), index=True, primary_key=True, default=uuid.uuid4))
  amount: Decimal = Field(sa_column=Column(DECIMAL, default=0.0))
  description: str = Field(nullable=True)

  type: str = Field(index=True)
  category_id: uuid.UUID = Field(foreign_key="categories.uid")
  user_uid: uuid.UUID = Field (foreign_key="users.uid")

  category: Optional[CategoryModel] = Relationship(back_populates="transactions", sa_relationship_kwargs={"lazy": "selectin"})


  created_at: datetime = Field( sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)) )
  updated_at: datetime = Field(
    sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  )
  def __repr__(self):
    return f"<Book {self.description}>"




















