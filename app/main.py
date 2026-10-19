import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.data import RESTAURANT
from app.database import Base, SessionLocal, engine
from app.routers import admin, chat, menu, reservations
from app.seed import seed_menu
logging.basicConfig(level=logging.INFO)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == "production" and settings.admin_password == "change-me":
        raise RuntimeError("Set a real ADMIN_PASSWORD before running in production")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_menu(db)
    yield
app = FastAPI(title="Bella Tavola API", version="1.0.0", lifespan=lifespan)
@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logging.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on our side."})
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/api/info")
def info():
    return RESTAURANT
app.include_router(menu.router)
app.include_router(reservations.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")   # always last