from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, EmailStr, StrictStr
import uuid
from decimal import Decimal
from enum import Enum




class BalanceBase(BaseModel):
  uid: uuid.UUID
  income_amount : Decimal  = Field(default=0.0)
  expenses_amount : Decimal  = Field(default=0.0)
  save_amount: Decimal  = Field(default=0.0)
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(
    str_strip_whitespace=True,
    json_schema_extra={
      "example": {
        "uid": str(uuid.uuid4()),
        "income_amount": 0.0,
        "expenses_amount": 0.0,
        "save_amount": 0.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
      }
    }
  )


class BalanceOut(BaseModel):
  uid: uuid.UUID
  income_amount : Decimal  = Field(default=0.0)
  expenses_amount : Decimal  = Field(default=0.0)
  save_amount: Decimal  = Field(default=0.0)
  balance_amount: Decimal  = Field(default=0.0)








