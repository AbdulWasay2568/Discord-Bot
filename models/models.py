from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Integer, BigInteger, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList, MutableDict
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    discriminator = Column(String, nullable=True)
    global_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    bot = Column(Boolean, default=False)
    system = Column(Boolean, default=False)

    messages = relationship(
        "Message",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class MessageType(Enum):
    DEFAULT = "DEFAULT"
    RECIPIENT_ADD = "RECIPIENT_ADD"
    RECIPIENT_REMOVE = "RECIPIENT_REMOVE"
    CALL = "CALL"
    CHANNEL_NAME_CHANGE = "CHANNEL_NAME_CHANGE"
    CHANNEL_ICON_CHANGE = "CHANNEL_ICON_CHANGE"
    CHANNEL_PINNED_MESSAGE = "CHANNEL_PINNED_MESSAGE"
    USER_JOIN = "USER_JOIN"
    GUILD_BOOST = "GUILD_BOOST"
    GUILD_BOOST_TIER_1 = "GUILD_BOOST_TIER_1"
    GUILD_BOOST_TIER_2 = "GUILD_BOOST_TIER_2"
    GUILD_BOOST_TIER_3 = "GUILD_BOOST_TIER_3"
    CHANNEL_FOLLOW_ADD = "CHANNEL_FOLLOW_ADD"
    GUILD_DISCOVERY_DISQUALIFIED = "GUILD_DISCOVERY_DISQUALIFIED"
    GUILD_DISCOVERY_REQUALIFIED = "GUILD_DISCOVERY_REQUALIFIED"
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = "GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING"
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = "GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING"
    THREAD_CREATED = "THREAD_CREATED"
    REPLY = "REPLY"
    CHAT_INPUT_COMMAND = "CHAT_INPUT_COMMAND"
    THREAD_STARTER_MESSAGE = "THREAD_STARTER_MESSAGE"
    GUILD_INVITE_REMINDER = "GUILD_INVITE_REMINDER"
    CONTEXT_MENU_COMMAND = "CONTEXT_MENU_COMMAND"
    AUTO_MODERATION_ACTION = "AUTO_MODERATION_ACTION"
    ROLE_SUBSCRIPTION_PURCHASE = "ROLE_SUBSCRIPTION_PURCHASE"
    INTERACTION_PREMIUM_UPSELL = "INTERACTION_PREMIUM_UPSELL"
    STAGE_START = "STAGE_START"
    STAGE_END = "STAGE_END"
    STAGE_SPEAKER = "STAGE_SPEAKER"
    STAGE_TOPIC = "STAGE_TOPIC"
    GUILD_APPLICATION_PREMIUM_SUBSCRIPTION = "GUILD_APPLICATION_PREMIUM_SUBSCRIPTION"
    GUILD_INCIDENT_ALERT_MODE_ENABLED = "GUILD_INCIDENT_ALERT_MODE_ENABLED"
    GUILD_INCIDENT_ALERT_MODE_DISABLED = "GUILD_INCIDENT_ALERT_MODE_DISABLED"
    GUILD_INCIDENT_REPORT_RAID = "GUILD_INCIDENT_REPORT_RAID"
    GUILD_INCIDENT_REPORT_FALSE_ALARM = "GUILD_INCIDENT_REPORT_FALSE_ALARM"
    PURCHASE_NOTIFICATION = "PURCHASE_NOTIFICATION"
    POLL_RESULT = "POLL_RESULT"


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)

    author_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )
    author = relationship("User", back_populates="messages")

    content = Column(String, nullable=True)

    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    edited_timestamp = Column(DateTime(timezone=True), nullable=True)

    tts = Column(Boolean, default=False)
    mention_everyone = Column(Boolean, default=False)

    mentions = Column(MutableList.as_mutable(JSON), default=list)
    mention_roles = Column(MutableList.as_mutable(JSON), default=list)
    mention_channels = Column(MutableList.as_mutable(JSON), default=list)
    attachments = Column(MutableList.as_mutable(JSON), default=list)
    embeds = Column(MutableList.as_mutable(JSON), default=list)
    reactions = Column(MutableList.as_mutable(JSON), default=list)

    nonce = Column(String, nullable=True)

    pinned = Column(Boolean, default=False)
    webhook_id = Column(BigInteger, nullable=True)

    type = Column(SQLEnum(MessageType, name="messagetype"), nullable=False)

    activity = Column(MutableDict.as_mutable(JSON), nullable=True)
    application = Column(MutableDict.as_mutable(JSON), nullable=True)
    application_id = Column(BigInteger, nullable=True)

    flags = Column(Integer, nullable=True)

    message_reference = Column(MutableDict.as_mutable(JSON), nullable=True)
    referenced_message = Column(MutableDict.as_mutable(JSON), nullable=True) 
    interaction_metadata = Column(MutableDict.as_mutable(JSON), nullable=True)

    components = Column(JSON, nullable=True)

    sticker_items = Column(JSON, nullable=True)
    stickers = Column(JSON, nullable=True)

    role_subscription_data = Column(JSON, nullable=True)
    resolved = Column(JSON, nullable=True)
    poll = Column(JSON, nullable=True)
    call = Column(JSON, nullable=True)
    thread = Column(JSON, nullable=True)
    message_snapshots = Column(JSON, nullable=True)

    position = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Message id={self.id} channel={self.channel_id}>"
