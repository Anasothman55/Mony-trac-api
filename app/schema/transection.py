
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field
import uuid



class TransactionBase(BaseModel):
  amount: Decimal = Field(..., title="Amount of the transaction", ge=0)
  description: str = Field(None, title="Description of the transaction")


class CreateTransaction(TransactionBase):
  category_id: uuid.UUID

class UseSaveTransaction(BaseModel):
  amount: Decimal = Field(..., title="Amount of the transaction", ge=0)
  category_id: uuid.UUID

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

