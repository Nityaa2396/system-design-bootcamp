from pydantic import BaseModel
from typing import Optional

class LinkCreate(BaseModel):
    original_url: str
    custom_slug: Optional[str] = None

class LinkResponse(BaseModel):
    id: str
    short_code: str
    original_url: str

    class Config:
        from_attributes = True