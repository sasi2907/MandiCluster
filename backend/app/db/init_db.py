from app.db.base import Base
from app.db import models
from app.db.session import engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    print("Tables:", sorted(Base.metadata.tables.keys()))


if __name__ == "__main__":
    create_tables()
