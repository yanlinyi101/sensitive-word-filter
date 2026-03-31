from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db.database import init_db
import os

app = FastAPI(title="逐字稿风险审查工具")

@app.on_event("startup")
def on_startup():
    init_db()
    _seed_if_needed()

def _seed_if_needed():
    from app.db.database import SessionLocal
    from app.db.models import WordlistEntry
    from app.db.seed import seed_from_file
    db = SessionLocal()
    if db.query(WordlistEntry).count() == 0:
        base = os.path.join(os.path.dirname(__file__), "../wordlist/houbb_base.txt")
        if os.path.exists(base):
            seed_from_file(db, base)
    db.close()

from app.api import review, wordlist, rules, history
app.include_router(review.router, prefix="/api")
app.include_router(wordlist.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(history.router, prefix="/api")

static_dir = os.path.join(os.path.dirname(__file__), "../static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(static_dir, "index.html"))
