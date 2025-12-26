import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB
from config.config import get_config

async def check_users():
    config = get_config()
    db_pool = await get_pg_pool(
        db_name=config.postgres.name,
        host=config.postgres.host,
        port=config.postgres.port,
        user=config.postgres.user,
        password=config.postgres.password,
    )
    
    async with db_pool.connection() as raw_connection:
        connection = PsycopgConnection(raw_connection)
        db = DB(connection)
        
        print("--- Active Users ---")
        async with connection._connection.cursor() as cur:
            await cur.execute("SELECT user_id, username, language, is_alive FROM users WHERE is_alive = True;")
            users = await cur.fetchall()
            print(f"Total active users: {len(users)}")
            for u in users:
                print(f"ID: {u['user_id']}, User: {u['username']}, Lang: {u['language']}")
        
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_users())
