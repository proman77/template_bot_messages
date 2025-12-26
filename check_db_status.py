import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB
from config.config import get_config

async def check_campaigns():
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
        
        print("--- Campaigns ---")
        async with connection._connection.cursor() as cur:
            await cur.execute("SELECT id, admin_id, status, created_at FROM broadcast_campaigns ORDER BY id DESC LIMIT 10;")
            campaigns = await cur.fetchall()
            for c in campaigns:
                cid = c['id']
                await cur.execute("SELECT count(*) as cnt FROM broadcast_messages WHERE campaign_id = %s;", (cid,))
                count_row = await cur.fetchone()
                print(f"ID: {cid}, Status: {c['status']}, Messages: {count_row['cnt']}, Created: {c['created_at']}")
        
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_campaigns())
