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

@router.post("/v1/links", response_model=LinkResponse, status_code=201)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    slug = payload.custom_slug or generate_slug()
    
    existing = db.query(Link).filter(Link.short_code == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already taken")
    
    link = Link(short_code=slug, original_url=payload.original_url)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

@router.get("/{slug}")
def redirect_link(slug: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(
        Link.short_code == slug,
        Link.is_deleted == False
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return RedirectResponse(url=link.original_url, status_code=302)