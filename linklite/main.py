from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from database import engine, Base
from routers import links
import models
import logging
import time
import uuid
from routers import auth


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkLite")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    logger.info(
        f"request_id={request_id} "
        f"method={request.method} "
        f"path={request.url.path} "
        f"status={response.status_code} "
        f"duration_ms={duration_ms}"
    )
    
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(links.router)

@app.get("/")
def frontend():
    return FileResponse("frontend.html")