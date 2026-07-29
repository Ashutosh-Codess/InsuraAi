import os
import sys
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
repo_root = os.path.dirname(current_dir)

load_dotenv(os.path.join(repo_root, ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

for path in (repo_root, current_dir):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.api.router import api_router
from app.core.bootstrap import seed_demo_data
from app.core.config import settings
from app.core.database import initialize_database

app = FastAPI(title=settings.APP_NAME)


@app.get("/", tags=["Root"])
def root():
    return {
        "application": settings.APP_NAME,
        "status": "Running",
        "message": "InsuraAI Backend is Live 🚀",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://insuraai-frontend.onrender.com",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def startup_event():
    initialize_database()
    seed_demo_data()

    # Skip AI startup on Render Free
    if os.getenv("INSURAMIND_SKIP_AI_STARTUP") == "1":
        return

    # Warm up embeddings
    try:
        from rag.embeddings import embed_text
        embed_text("warmup")
    except Exception as exc:
        print(f"[startup] embedding warmup failed (non-fatal): {exc}")

    # Seed knowledge base
    try:
        from app.core.knowledge_seed import seed_knowledge_base
        seed_knowledge_base()
    except Exception as exc:
        print(f"[startup] knowledge base seeding failed (non-fatal): {exc}")
