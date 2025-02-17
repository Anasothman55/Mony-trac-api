from fastapi import  APIRouter

rout = APIRouter()


from project.app.routes.auth import route as auth_route


rout.include_router(auth_route, prefix="/auth", tags=["auth"])


