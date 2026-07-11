from fastapi import FastAPI

from app import database
from app.routers import documents

app = FastAPI(title="AcademiQ")


@app.on_event("startup")
def on_startup():
    database.create_tables()


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AcademiQ is running"}


app.include_router(documents.router)