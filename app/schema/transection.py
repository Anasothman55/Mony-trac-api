
from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr
import uuid
from typing import List, Optional, Annotated



class TransactionBase(BaseModel):
  amount: Decimal = Field(..., title="Amount of the transaction", ge=0)
  description: str = Field(None, title="Description of the transaction")


class CreateTransaction(TransactionBase):
  type: str
  category_id: uuid.UUID
  user_uid: uuid.UUID

class UpdateTransaction(TransactionBase):
  pass

class GetTransaction(TransactionBase):
  uid: uuid.UUID

class GetAllTransaction(TransactionBase):
  uid: uuid.UUID
  created_at: datetime
  updated_at: datetime
  type: str
  category_id: uuid.UUID
  amount: Decimal
  description: str | None = None

