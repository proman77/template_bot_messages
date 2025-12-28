import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from config.config import get_config

async def list_tables():
    config = get_config()
    db_pool = await get_pg_pool(
        db_name=config.postgres.name,
        host=config.postgres.host,
        port=config.postgres.port,
        user=config.postgres.user,
        password=config.postgres.password,
    )
    
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            rows = await cur.fetchall()
            print("--- Tables ---")
            for r in rows:
                print(r['table_name'])
                
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(list_tables())
