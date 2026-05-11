from fastapi import FastAPI
from database import engine, Base
from routers import links
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkLite")
app.include_router(links.router)

@app.get("/health")
def health():
    return {"status": "ok"}
