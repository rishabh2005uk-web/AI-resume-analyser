import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found! Please check your .env file.")

# Create the engine and pass an empty SSL dictionary to tell PyMySQL to use default SSL securely
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {} # This safely enables SSL without crashing PyMySQL!
    }
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()