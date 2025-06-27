import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import inspect

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    name = Column(String)

def create_tables():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set. Check your environment variables.")

    engine = create_engine(database_url)
    inspector = inspect(engine)

    if not inspector.has_table("users"):
        Base.metadata.create_all(engine)
