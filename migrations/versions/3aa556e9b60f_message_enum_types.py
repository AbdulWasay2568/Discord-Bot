"""message enum types

Revision ID: 3aa556e9b60f
Revises: a1dc24744736
Create Date: 2025-11-19 16:48:58.431322
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3aa556e9b60f'
down_revision: Union[str, Sequence[str], None] = 'a1dc24744736'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the PostgreSQL enum type
message_type_enum = sa.Enum(
    "DEFAULT", "RECIPIENT_ADD", "RECIPIENT_REMOVE", "CALL",
    "CHANNEL_NAME_CHANGE", "CHANNEL_ICON_CHANGE", "CHANNEL_PINNED_MESSAGE",
    "USER_JOIN", "GUILD_BOOST", "GUILD_BOOST_TIER_1", "GUILD_BOOST_TIER_2",
    "GUILD_BOOST_TIER_3", "CHANNEL_FOLLOW_ADD", "GUILD_DISCOVERY_DISQUALIFIED",
    "GUILD_DISCOVERY_REQUALIFIED", "GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING",
    "GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING", "THREAD_CREATED", "REPLY",
    "CHAT_INPUT_COMMAND", "THREAD_STARTER_MESSAGE", "GUILD_INVITE_REMINDER",
    "CONTEXT_MENU_COMMAND", "AUTO_MODERATION_ACTION", "ROLE_SUBSCRIPTION_PURCHASE",
    "INTERACTION_PREMIUM_UPSELL", "STAGE_START", "STAGE_END", "STAGE_SPEAKER",
    "STAGE_TOPIC", "GUILD_APPLICATION_PREMIUM_SUBSCRIPTION",
    "GUILD_INCIDENT_ALERT_MODE_ENABLED", "GUILD_INCIDENT_ALERT_MODE_DISABLED",
    "GUILD_INCIDENT_REPORT_RAID", "GUILD_INCIDENT_REPORT_FALSE_ALARM",
    "PURCHASE_NOTIFICATION", "POLL_RESULT",
    name="messagetype"
)

def upgrade() -> None:
    """Upgrade schema."""
    # create the enum type in PostgreSQL if it doesn't exist
    message_type_enum.create(op.get_bind(), checkfirst=True)

    # alter the 'type' column to use the enum
    # specify USING clause to cast integers to enum
    op.execute("""
        ALTER TABLE messages
        ALTER COLUMN type
        TYPE messagetype
        USING CASE
            WHEN type = 0 THEN 'DEFAULT'::messagetype
            WHEN type = 1 THEN 'RECIPIENT_ADD'::messagetype
            WHEN type = 2 THEN 'RECIPIENT_REMOVE'::messagetype
            WHEN type = 3 THEN 'CALL'::messagetype
            WHEN type = 4 THEN 'CHANNEL_NAME_CHANGE'::messagetype
            WHEN type = 5 THEN 'CHANNEL_ICON_CHANGE'::messagetype
            WHEN type = 6 THEN 'CHANNEL_PINNED_MESSAGE'::messagetype
            WHEN type = 7 THEN 'USER_JOIN'::messagetype
            WHEN type = 8 THEN 'GUILD_BOOST'::messagetype
            WHEN type = 9 THEN 'GUILD_BOOST_TIER_1'::messagetype
            WHEN type = 10 THEN 'GUILD_BOOST_TIER_2'::messagetype
            WHEN type = 11 THEN 'GUILD_BOOST_TIER_3'::messagetype
            WHEN type = 12 THEN 'CHANNEL_FOLLOW_ADD'::messagetype
            WHEN type = 14 THEN 'GUILD_DISCOVERY_DISQUALIFIED'::messagetype
            WHEN type = 15 THEN 'GUILD_DISCOVERY_REQUALIFIED'::messagetype
            WHEN type = 16 THEN 'GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING'::messagetype
            WHEN type = 17 THEN 'GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING'::messagetype
            WHEN type = 18 THEN 'THREAD_CREATED'::messagetype
            WHEN type = 19 THEN 'REPLY'::messagetype
            WHEN type = 20 THEN 'CHAT_INPUT_COMMAND'::messagetype
            WHEN type = 21 THEN 'THREAD_STARTER_MESSAGE'::messagetype
            WHEN type = 22 THEN 'GUILD_INVITE_REMINDER'::messagetype
            WHEN type = 23 THEN 'CONTEXT_MENU_COMMAND'::messagetype
            WHEN type = 24 THEN 'AUTO_MODERATION_ACTION'::messagetype
            WHEN type = 25 THEN 'ROLE_SUBSCRIPTION_PURCHASE'::messagetype
            WHEN type = 26 THEN 'INTERACTION_PREMIUM_UPSELL'::messagetype
            WHEN type = 27 THEN 'STAGE_START'::messagetype
            WHEN type = 28 THEN 'STAGE_END'::messagetype
            WHEN type = 29 THEN 'STAGE_SPEAKER'::messagetype
            WHEN type = 31 THEN 'STAGE_TOPIC'::messagetype
            WHEN type = 32 THEN 'GUILD_APPLICATION_PREMIUM_SUBSCRIPTION'::messagetype
            WHEN type = 36 THEN 'GUILD_INCIDENT_ALERT_MODE_ENABLED'::messagetype
            WHEN type = 37 THEN 'GUILD_INCIDENT_ALERT_MODE_DISABLED'::messagetype
            WHEN type = 38 THEN 'GUILD_INCIDENT_REPORT_RAID'::messagetype
            WHEN type = 39 THEN 'GUILD_INCIDENT_REPORT_FALSE_ALARM'::messagetype
            WHEN type = 44 THEN 'PURCHASE_NOTIFICATION'::messagetype
            ELSE 'POLL_RESULT'::messagetype
        END;
    """)

def downgrade() -> None:
    """Downgrade schema."""
    # revert 'type' column back to integer
    op.alter_column(
        'messages',
        'type',
        existing_type=message_type_enum,
        type_=sa.INTEGER(),
        existing_nullable=False
    )

    # drop the enum type from PostgreSQL
    message_type_enum.drop(op.get_bind(), checkfirst=True)
