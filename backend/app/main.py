# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.config import settings, data_root
from app.routers.videos import router as videos_router
from app.routers.auth import router as auth_router

# API_BASE = "http://10.0.0.43:8012"
API_BASE = settings.API_BASE
API_BASE = ''
# API_BASE = os.environ.get("API_BASE", "")

app = FastAPI(title="Annotation Backend")

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS] if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# 设置静态文件目录为 frontend
app.mount("/frontend", StaticFiles(directory="app/frontend"), name="frontend")

# Mount the dataset directory to serve video files
app.mount("/dataset", StaticFiles(directory=data_root), name="dataset")

app.mount("/masks", StaticFiles(directory=settings.PSEUDOMASK_ROOT), name="masks")



# 将根路径指向 index.html
@app.get("/")
async def index():
    return FileResponse("app/frontend/index.html")

@app.get("/api/config")
async def get_frontend_config():
    """
    Provide frontend configuration including API base URL
    """
    return JSONResponse({
        "API_BASE": API_BASE,
        "PAGE_SIZE": 15
    })
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# 注册视频路由
app.include_router(videos_router)
app.include_router(auth_router) 



# ssh 10.0.0.43                                            

# cd backend
# uvicorn app.main:app --host 0.0.0.0 --port 8012 --reload

# http://10.0.0.43:8012/api/videos


# ./cloudflared tunnel --url http://127.0.0.1:8012