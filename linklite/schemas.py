from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: str
    custom_slug: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    id: str
    short_code: str
    original_url: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True