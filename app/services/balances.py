from decimal import Decimal

from ..db.models import BalanceModel
from ..util.balance import BalanceRepository

import uuid


def incrise_type(types: str, balance: BalanceModel, amount: Decimal):
  if types == "income":
    balance.income_amount += amount
  elif types == "expenses":
    balance.expenses_amount += amount
  else:
    balance.save_amount += amount
  return balance
def decris_type(types: str, balance: BalanceModel, amount: Decimal):
  if types == "income":
    balance.income_amount -= amount
  elif types == "expenses":
    balance.expenses_amount -= amount
  else:
    balance.save_amount -= amount
  return balance


async def add_transaction_balance(
    repo: BalanceRepository, amount: Decimal, user_uid: uuid.UUID, types: str) :
  balance = await repo.get_by_user_uid(user_uid)
  result = incrise_type(types, balance, amount)
  await repo.update_balance(result)



async def update_transaction_balance(
    repo: BalanceRepository, amount: Decimal,new_amount: Decimal, types: str, user_uid: uuid.UUID) :
  balance = await repo.get_by_user_uid(user_uid)
  if new_amount > amount:
    result = incrise_type(types, balance, new_amount - amount)
  else:
    result = decris_type(types, balance, amount - new_amount)
  await repo.update_balance(result)


async def delete_transaction_balance(
    repo: BalanceRepository, amount: Decimal, user_uid: uuid.UUID, types: str) :
  balance = await repo.get_by_user_uid(user_uid)
  result = decris_type(types, balance, amount)
  await repo.update_balance(result)