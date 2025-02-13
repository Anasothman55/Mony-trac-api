from fastapi import  APIRouter


route = APIRouter(tags=["auth"])

@route.get("/")
def simple():
  return {"message": "Hello World"}
