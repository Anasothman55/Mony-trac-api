

# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


"""
alembic
1- alembic init -t async migrations
2-  alembic revision --autogenerate -m "fix timestamp 5"
3- alembic upgrade 44b1039302e8    
""" 