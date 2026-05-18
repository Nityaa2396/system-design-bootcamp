from database import redis, SessionLocal, get_db
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from models import Link, ClickEvent
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
def create_link(
    payload: LinkCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    check_rate_limit(client_ip)
    
    slug = payload.custom_slug or get_unique_slug(db)
    
    existing = db.query(Link).filter(Link.short_code == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already taken")
    
    link = Link(short_code=slug, original_url=payload.original_url)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

@router.get("/{slug}")
def redirect_link(
    slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    cached_url = redis.get(f"link:{slug}")
    if cached_url:
        print(f"CACHE HIT: {slug}")
        background_tasks.add_task(
            record_click,
            link_id=slug,
            user_agent=request.headers.get("user-agent", ""),
            referer=request.headers.get("referer", "")
        )
        return RedirectResponse(url=cached_url, status_code=302)

    print(f"CACHE MISS: {slug}")
    link = db.query(Link).filter(
        Link.short_code == slug,
        Link.is_deleted == False
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    redis.setex(f"link:{slug}", 3600, link.original_url)
    
    background_tasks.add_task(
        record_click,
        link_id=link.id,
        user_agent=request.headers.get("user-agent", ""),
        referer=request.headers.get("referer", "")
    )

    return RedirectResponse(url=link.original_url, status_code=302)

def record_click(link_id: str, user_agent: str, referer: str):
    db = SessionLocal()
    try:
        click = ClickEvent(
            link_id=link_id,
            user_agent=user_agent,
            referer=referer
        )
        db.add(click)
        db.commit()
    finally:
        db.close()

def check_rate_limit(client_ip: str):
    key = f"ratelimit:{client_ip}"
    count = redis.get(key)
    
    if count and int(count) >= 10:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again tomorrow."
        )
    
    if count is None:
        redis.setex(key, 86400, 1)
    else:
        redis.incr(key)


        
        