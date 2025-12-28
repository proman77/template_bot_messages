import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB
from config.config import get_config

async def debug_campaign(campaign_id: int):
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
        
        async with connection._connection.cursor() as cur:
            await cur.execute("SELECT * FROM broadcast_campaigns WHERE id = %s;", (campaign_id,))
            campaign = await cur.fetchone()
            print(f"--- Campaign {campaign_id} ---")
            print(campaign)
            
            await cur.execute("SELECT * FROM broadcast_messages WHERE campaign_id = %s;", (campaign_id,))
            messages = await cur.fetchall()
            print(f"--- Messages for {campaign_id} ---")
            for m in messages:
                print(m)
        
    await db_pool.close()

if __name__ == "__main__":
    cid = int(sys.argv[1]) if len(sys.argv) > 1 else 23
    asyncio.run(debug_campaign(cid))
