import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.infrastructure.database.connection.connect_to_pg import get_pg_pool
from config.config import get_config

async def debug_all_campaigns():
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
            await cur.execute("SELECT * FROM broadcast_campaigns ORDER BY id DESC LIMIT 5")
            campaigns = await cur.fetchall()
            for c in campaigns:
                print(f"Campaign: {c}")
                await cur.execute("SELECT * FROM broadcast_messages WHERE campaign_id = %s", (c['id'],))
                messages = await cur.fetchall()
                for m in messages:
                    print(f"  Message: {m}")
                
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(debug_all_campaigns())
