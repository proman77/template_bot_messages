import asyncio
import logging
from taskiq import TaskiqMiddleware, TaskiqMessage

logger = logging.getLogger(__name__)

class BroadcastRateLimiterMiddleware(TaskiqMiddleware):
    """
    Middleware for distributed rate limiting of broadcast messages.
    Uses Redis to track the number of messages sent per second across all workers.
    """
    
    def __init__(self, limit_per_sec: int = 25):
        super().__init__()
        self.limit = limit_per_sec
        self.key = "limiter:broadcast"

    async def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        # Only apply rate limiting to the send_one_message task
        logger.debug(f"[LIMITER] Checking task: {message.task_name}")
        if "send_one_message" not in message.task_name:
            return message

        logger.info(f"[LIMITER] Applying rate limit for: {message.task_name}")

        # Access redis from the broker's state
        # Note: broker.state is available in middlewares
        redis = self.broker.state.redis
        
        while True:
            current = await redis.get(self.key)
            
            if current and int(current) >= self.limit:
                # If limit reached, wait a bit and retry
                # We use a small sleep to avoid busy-waiting
                await asyncio.sleep(0.1)
                continue
            
            # Increment the counter and set expiration if it's a new key
            # We use a pipeline for atomicity
            pipe = redis.pipeline()
            await pipe.incr(self.key)
            await pipe.expire(self.key, 1) # Reset every second
            results = await pipe.execute()
            
            # If we just incremented and it's still within limits, we are good
            # (The incr returns the new value)
            if results[0] <= self.limit:
                break
            else:
                # If multiple workers incremented at the same time and we exceeded,
                # we wait and try again
                await asyncio.sleep(0.1)
                
        return message
