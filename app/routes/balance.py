
from rich import  print


from ..schema.balance import BalanceOut
from ..db.index import get_db
from ..services.balances import get_user_balance

from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Form, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession


from ..db.models import UserModel
from ..dependencies.user_auth import get_current_user
from ..dependencies.transaction import get_transaction_repo
from ..dependencies.categories import get_category_repo
from ..db.index import get_db
from ..schema.categories import  CATEGORY_TYPE_ENUM
from ..schema.transection import GetAllTransaction, CreateTransaction, UseSaveTransaction
from ..services.transection import create_transection_services

from ..util.balance import BalanceRepository, get_balance_repo
from ..util.transection import TransectionsRepository
from ..util.categories import CategoryRepository







route = APIRouter(
  dependencies= [Depends(get_current_user)]
)


@route.get('/get_all', response_model= BalanceOut, status_code= status.HTTP_200_OK)
async def get_all_categories(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
  user_uid = current_user.uid
  result = await get_user_balance(user_uid, db)

  if not result:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found")

  balance_amount = result.income_amount - (result.expenses_amount + result.save_amount)
  res_model = {**result.model_dump(), "balance_amount": balance_amount}
  print(res_model)
  return res_model




