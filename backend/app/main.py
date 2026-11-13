from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.conversations.router import router as conversations_router
from app.core import database
from app.documents.router import router as documents_router

app = FastAPI(title="AcademiQ")


@app.on_event("startup")
def on_startup():
    database.create_tables()


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "AcademiQ is running"}


app.include_router(documents_router)
app.include_router(conversations_router)
app.include_router(auth_router)
