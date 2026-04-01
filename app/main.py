from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db.database import init_db
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    _seed_if_needed()
    yield

app = FastAPI(title="逐字稿风险审查工具", lifespan=lifespan)

def _seed_if_needed():
    from app.db.database import SessionLocal
    from app.db.models import WordlistEntry
    from app.db.seed import seed_from_file
    db = SessionLocal()
    try:
        if db.query(WordlistEntry).count() == 0:
            base = os.path.join(os.path.dirname(__file__), "../wordlist/houbb_base.txt")
            if os.path.exists(base):
                seed_from_file(db, base)
    finally:
        db.close()

from app.api import review, wordlist, rules, history
app.include_router(review.router, prefix="/api")
app.include_router(wordlist.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(history.router, prefix="/api")

# ------------------------------------------------------------------
# 中间件：对 /api/review 计数，触发突发检测
# ------------------------------------------------------------------
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.rate_guard import rate_guard

class ReviewCountMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/review" and request.method == "POST":
            rate_guard.record_request()
        return await call_next(request)

app.add_middleware(ReviewCountMiddleware)

# ------------------------------------------------------------------
# 管理端点：查看状态 / 手动重置熔断
# ------------------------------------------------------------------
_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

@app.get("/api/admin/status")
def admin_status():
    return rate_guard.status()

@app.post("/api/admin/reset")
def admin_reset(request: Request, password: str = ""):
    if not _ADMIN_PASSWORD or password != _ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="密码错误")
    rate_guard.reset()
    return {"ok": True, "message": "熔断已重置"}

# ------------------------------------------------------------------
# 静态文件 & 前端入口
# ------------------------------------------------------------------
static_dir = os.path.join(os.path.dirname(__file__), "../static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Frontend not built"}, status_code=404)
    return FileResponse(index_path, headers={"Cache-Control": "no-cache"})
