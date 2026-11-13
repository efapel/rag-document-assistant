import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def create_tables():
    # Import every domain's models so their tables are registered on SQLModel.metadata
    import app.auth.models  # noqa: F401
    import app.conversations.models  # noqa: F401
    import app.documents.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
