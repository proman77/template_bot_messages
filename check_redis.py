import asyncio
import sys
import os

# Add win_fix to PYTHONPATH for consistency
sys.path.insert(0, os.path.join(os.getcwd(), "win_fix"))

from app.infrastructure.cache.connect_to_redis import get_redis_pool
from config.config import get_config

async def check_redis(campaign_id: int):
    config = get_config()
    r = await get_redis_pool(
        db=config.redis.database,
        host=config.redis.host,
        port=config.redis.port,
        username=config.redis.username,
        password=config.redis.password,
    )
    
    status = await r.get(f"broadcast:{campaign_id}:status")
    sent = await r.get(f"broadcast:{campaign_id}:sent")
    fail = await r.get(f"broadcast:{campaign_id}:fail")
    total = await r.get(f"broadcast:{campaign_id}:total")
    
    print(f"--- Redis Campaign {campaign_id} ---")
    print(f"Status: {status.decode() if status else 'None'}")
    print(f"Sent: {sent.decode() if sent else 'None'}")
    print(f"Fail: {fail.decode() if fail else 'None'}")
    print(f"Total: {total.decode() if total else 'None'}")
    
    await r.close()

if __name__ == "__main__":
    cid = int(sys.argv[1]) if len(sys.argv) > 1 else 27
    asyncio.run(check_redis(cid))
