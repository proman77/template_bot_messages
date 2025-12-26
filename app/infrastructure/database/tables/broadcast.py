import json
import logging
from typing import List

from app.infrastructure.database.models.broadcast_status import BroadcastStatus
from app.infrastructure.database.models.broadcast import (
    BroadcastCampaignModel,
    BroadcastMessageModel,
)
from app.infrastructure.database.tables.base import BaseTable

logger = logging.getLogger(__name__)


class BroadcastTable(BaseTable):
    __tablename__ = "broadcast_campaigns"

    async def create_campaign(self, admin_id: int) -> BroadcastCampaignModel:
        data = await self.connection.fetchone(
            sql="""
                INSERT INTO broadcast_campaigns (admin_id, status)
                VALUES (%s, %s)
                RETURNING *;
            """,
            params=(admin_id, BroadcastStatus.CREATED),
        )
        self._log("CREATE_CAMPAIGN", admin_id=admin_id)
        return data.to_model(model=BroadcastCampaignModel)

    async def add_message(
        self,
        campaign_id: int,
        language_code: str,
        content_type: str,
        text: str | None = None,
        file_id: str | None = None,
        caption: str | None = None,
        reply_markup: dict | None = None,
    ) -> None:
        await self.connection.execute(
            sql="""
                INSERT INTO broadcast_messages (
                    campaign_id, language_code, content_type, text, file_id, caption, reply_markup
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            params=(
                campaign_id,
                language_code,
                content_type,
                text,
                file_id,
                caption,
                json.dumps(reply_markup) if reply_markup else None,
            ),
        )
        self._log("ADD_MESSAGE", campaign_id=campaign_id, language=language_code)

    async def update_status(self, campaign_id: int, status: BroadcastStatus) -> None:
        await self.connection.execute(
            sql="""
                UPDATE broadcast_campaigns 
                SET status = %s, updated_at = NOW() 
                WHERE id = %s;
            """,
            params=(status, campaign_id),
        )
        self._log("UPDATE_STATUS", campaign_id=campaign_id, status=status)

    async def get_campaign_messages(self, campaign_id: int) -> List[BroadcastMessageModel]:
        data = await self.connection.fetchmany(
            sql="SELECT * FROM broadcast_messages WHERE campaign_id = %s;",
            params=(campaign_id,),
        )
        return data.to_models(model=BroadcastMessageModel) or []

    async def get_campaign(self, campaign_id: int) -> BroadcastCampaignModel | None:
        data = await self.connection.fetchone(
            sql="SELECT * FROM broadcast_campaigns WHERE id = %s;",
            params=(campaign_id,),
        )
        return data.to_model(model=BroadcastCampaignModel)
