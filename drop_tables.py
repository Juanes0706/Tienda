from database import async_engine
from models import SQLModel
import asyncio

async def drop_all_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

if __name__ == "__main__":
    asyncio.run(drop_all_tables())
    print("All tables dropped.")
