import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///users.db")

if not database_url:
    raise ValueError("DATABASE_URL is not set in environment variables")

connect_args = {}
if database_url.startswith("postgresql"):
    connect_args["sslmode"] = "require"

engine = create_engine(database_url, connect_args=connect_args)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Connected to database successfully ✅")


