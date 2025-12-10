from fastapi import FastAPI
from app.api.routes import router
from app.database import init_db


init_db()

app = FastAPI(title="AI Workflow Engine")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Workflow Engine is Running"}


