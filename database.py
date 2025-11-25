from sqlmodel import SQLModel # Necesario para acceder a los metadatos de las tablas
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida")

# Convertir la URL de conexión estándar a una compatible con asyncpg
DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Motor y sesión asíncrona
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)

AsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

async def get_async_db():
    """Dependency para obtener la sesión de base de datos asíncrona (usado en main.py)."""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Inicializa la base de datos creando las tablas si no existen."""
    # Utiliza el motor asíncrono y run_sync para la creación de tablas con SQLModel
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)