
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr
import uuid
from enum import Enum
from typing import List, Optional, Annotated

from .transection import GetTransaction

class CATEGORY_TYPE_ENUM(str, Enum):
  income = "income"
  expenses = "expenses"
  save = "save"
  use_save = "use_save"


class CategoryBase(BaseModel):
  name: str = Field()


class CreateCategory(CategoryBase):
  """ create category """
  type: Annotated[CATEGORY_TYPE_ENUM, Field()]

class UpadteCategory(CategoryBase):
  """ update category """
  name: str = Field(default=None)
  type: Annotated[CATEGORY_TYPE_ENUM, Field()] = None

class GetAllCategory(CategoryBase):
  uid: uuid.UUID
  created_at: datetime
  updated_at: datetime
  type: str

  transactions: List[GetTransaction] = []






