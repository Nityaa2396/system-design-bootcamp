from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base
import uuid

class Link(Base):
    __tablename__ = "links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    short_code = Column(String(10), unique=True, nullable=False, index=True)
    owner_id = Column(String, nullable=True, index=True)
    original_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)

class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    link_id = Column(String, nullable=False, index=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())