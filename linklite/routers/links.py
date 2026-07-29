from auth import get_current_user
from sqlalchemy import func, text
from datetime import datetime, timedelta
import json
from datetime import timezone
from models import Link, ClickEvent, User
from models import User
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
from fastapi.responses import JSONResponse
from database import get_db, redis, SessionLocal
from models import Link, ClickEvent


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
    except Exception as e:
        print(f"CLICK RECORD ERROR: {e}")
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

@router.post("/v1/links", response_model=LinkResponse, status_code=201)
def create_link(
    payload: LinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client_ip = request.client.host
    check_rate_limit(client_ip)

    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        cached = redis.get(f"idempotency:{idempotency_key}")
        if cached:
            import json
            return JSONResponse(status_code=201, content=json.loads(cached))

    slug = payload.custom_slug or get_unique_slug(db)

    existing = db.query(Link).filter(Link.short_code == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already taken")

    link = Link(
        short_code=slug,
        original_url=payload.original_url,
        owner_id=current_user.id,
        expires_at=payload.expires_at
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    if idempotency_key:
        import json
        redis.setex(
            f"idempotency:{idempotency_key}",
            86400,
            json.dumps({
                "id": link.id,
                "short_code": link.short_code,
                "original_url": link.original_url
            })
        )

    return link

@router.get("/v1/links/trending")
def get_trending(db: Session = Depends(get_db)):
    # check cache first
    cached = redis.get("trending:links")
    if cached:
        return {"trending": json.loads(cached), "cached": True}

    # query DB for top 10 links in last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    
    results = db.execute(text("""
        SELECT ce.link_id, COUNT(*) as click_count, 
               l.short_code, l.original_url
        FROM click_events ce
        JOIN links l ON ce.link_id = l.id
        WHERE ce.clicked_at > :since
        AND l.is_deleted = false
        GROUP BY ce.link_id, l.short_code, l.original_url
        ORDER BY click_count DESC
        LIMIT 10
    """), {"since": since}).fetchall()

    trending = [
        {
            "short_code": row.short_code,
            "original_url": row.original_url,
            "clicks_24h": row.click_count,
            "url": f"/{row.short_code}"
        }
        for row in results
    ]

    # cache for 5 minutes
    redis.setex("trending:links", 300, json.dumps(trending))

    return {"trending": trending, "cached": False}

@router.get("/v1/links/{link_id}/stats")
def get_link_stats(
    link_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # verify link exists and belongs to current user
    link = db.query(Link).filter(
        Link.id == link_id,
        Link.owner_id == current_user.id,
        Link.is_deleted == False
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # total clicks
    total_clicks = db.query(ClickEvent).filter(
        ClickEvent.link_id == link_id
    ).count()

    # clicks per day (last 7 days)
    clicks_per_day = db.execute(text("""
        SELECT DATE(clicked_at) as day, COUNT(*) as clicks
        FROM click_events
        WHERE link_id = :link_id
        AND clicked_at > NOW() - INTERVAL '7 days'
        GROUP BY DATE(clicked_at)
        ORDER BY day DESC
    """), {"link_id": link_id}).fetchall()

    # top referrers
    top_referrers = db.execute(text("""
        SELECT 
            COALESCE(NULLIF(referer, ''), 'Direct') as source,
            COUNT(*) as clicks
        FROM click_events
        WHERE link_id = :link_id
        GROUP BY referer
        ORDER BY clicks DESC
        LIMIT 5
    """), {"link_id": link_id}).fetchall()

    return {
        "link": {
            "id": link.id,
            "short_code": link.short_code,
            "original_url": link.original_url,
            "created_at": link.created_at,
            "expires_at": link.expires_at
        },
        "analytics": {
            "total_clicks": total_clicks,
            "clicks_per_day": [
                {"day": str(row.day), "clicks": row.clicks}
                for row in clicks_per_day
            ],
            "top_referrers": [
                {"source": row.source, "clicks": row.clicks}
                for row in top_referrers
            ]
        }
    }

@router.get("/{slug}")
def redirect_link(
    slug: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
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
    except Exception as e:
        print(f"REDIS ERROR: {e} — falling back to DB")

    print(f"CACHE MISS: {slug}")
    link = db.query(Link).filter(
        Link.short_code == slug,
        Link.is_deleted == False
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.expires_at and link.expires_at.replace(tzinfo=None) < datetime.utcnow():
        try:
            redis.delete(f"link:{slug}")
        except Exception:
            pass
        raise HTTPException(status_code=410, detail="Link has expired")

    try:
        redis.setex(f"link:{slug}", 3600, link.original_url)
    except Exception as e:
        print(f"REDIS ERROR: {e} — skipping cache write")

    background_tasks.add_task(
        record_click,
        link_id=link.id,
        user_agent=request.headers.get("user-agent", ""),
        referer=request.headers.get("referer", "")
    )

    return RedirectResponse(url=link.original_url, status_code=302)