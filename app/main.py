from fastapi import  FastAPI
from .routes.router import  rout



app = FastAPI()



app.include_router(rout, prefix="/api")









