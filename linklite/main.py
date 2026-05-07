from fastapi import FastAPI

app = FastAPI(title="LinkLite")

@app.get("/health")
def health():
    return {"status": "ok"}