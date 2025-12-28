import asyncio
import psycopg
from config.config import get_config

async def reset_alembic():
    config = get_config()
    dsn = f"postgresql://{config.postgres.user}:{config.postgres.password}@{config.postgres.host}:{config.postgres.port}/{config.postgres.name}"
    
    print(f"Connecting to {dsn}...")
    try:
        async with await psycopg.AsyncConnection.connect(dsn) as conn:
            print("Connected!")
            async with conn.cursor() as cur:
                print("Dropping alembic_version table...")
                await cur.execute("DROP TABLE IF EXISTS alembic_version;")
                print("alembic_version table dropped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reset_alembic())
