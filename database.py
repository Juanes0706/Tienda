from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida")

DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Async engine and session
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)

AsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

# Synchronous engine and session (for crud.py)
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    # Create tables
    # Since Base.metadata.create_all is sync, run it in a thread to avoid blocking
    import asyncio
    loop = asyncio.get_running_loop()

    def create_tables():
        Base.metadata.create_all(bind=engine)

    await loop.run_in_executor(None, create_tables)
