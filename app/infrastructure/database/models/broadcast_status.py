from enum import Enum


class BroadcastStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    SENDING = "sending"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
