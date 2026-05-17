from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Link
from schemas import LinkCreate, LinkResponse
import random
import string
from fastapi.responses import RedirectResponse

router = APIRouter()
def generate_slug(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def get_unique_slug(db: Session):
    for _ in range(5):
        slug = generate_slug()
        existing = db.query(Link).filter(Link.short_code == slug).first()
        if not existing:
            return slug
    raise HTTPException(status_code=500, detail="Could not generate unique slug")

@router.post("/v1/links", response_model=LinkResponse, status_code=201)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    slug = payload.custom_slug or get_unique_slug(db)
    
    existing = db.query(Link).filter(Link.short_code == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already taken")
    
    link = Link(short_code=slug, original_url=payload.original_url)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link