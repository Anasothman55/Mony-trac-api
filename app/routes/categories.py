
from typing import Annotated, List
from fastapi import APIRouter,  Query, status, HTTPException, Form, Depends, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..util.categories import CategoryRepository
from ..db.models import UserModel
from ..dependencies.categories import get_category_repo
from ..dependencies.user_auth import get_current_user
from ..schema.categories import  CreateCategory, GetAllCategory, CATEGORY_TYPE_ENUM, UpadteCategory
from ..db.index import get_db
from ..services.categories import (
  get_all_category_services,
  create_category_services,
  get_one_category_services,
  update_category_services,
  delete_category_services
)





route = APIRouter()


@route.get('/get_all', response_model= List[GetAllCategory], status_code= status.HTTP_200_OK)
async def get_all_categories(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    descending: Annotated[bool, Query()] = False,
    enum: Annotated[CATEGORY_TYPE_ENUM, Query()] = None,
):
  order_by = "created_at"
  if descending:
    order_by = f"-{order_by}"

  user_uid = current_user.uid
  result = await get_all_category_services(db,user_uid=user_uid,order_by= order_by)

  if enum:
    result = [item for item in result if item.type == enum]

  if not result:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No data found"})
  return jsonable_encoder(result)

@route.post("/create", status_code=status.HTTP_201_CREATED)
async def create_category(
    req_data: Annotated[CreateCategory, Form()],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
  user_uid = current_user.uid
  new_data = req_data.model_dump()
  new_data.update({"user_uid": user_uid})

  result = await create_category_services(repo,new_data)
  return jsonable_encoder(result)


@route.get('/get-one/{category_uid}',  status_code= status.HTTP_200_OK)
async def get_one_categories(
    category_uid: Annotated[uuid.UUID, Path(...)],
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
  try:
    result = await get_one_category_services(repo, category_uid)
    return jsonable_encoder(result)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@route.patch("/update/{category_uid}", status_code=status.HTTP_201_CREATED)
async def update_category(
    category_uid: Annotated[uuid.UUID,Path(...)],
    req_data: Annotated[UpadteCategory, Form()],
    repo: Annotated[CategoryRepository, Depends(get_category_repo)],
):
  try:
    new_data = req_data.model_dump()
    result = await update_category_services(repo, category_uid, new_data)
    return jsonable_encoder(result)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@route.delete("/delete/{category_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def update_category(
    category_uid: Annotated[uuid.UUID, Path(...)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
  try:
    await delete_category_services(db, category_uid)

  except HTTPException as ex:
    raise ex
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))












