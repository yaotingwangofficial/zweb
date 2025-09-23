# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.routers.videos import router as videos_router
from app.routers.auth import router as auth_router

app = FastAPI(title="Annotation Backend")

# # 配置 CORS 中间件 - 修复版本
# if settings.CORS_ORIGINS == "*":
#     origins = ["*"]
# else:
#     origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]


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
app.mount("/dataset", StaticFiles(directory="../dataset"), name="dataset")

app.mount("/masks", StaticFiles(directory="/home/share/wangyt/zweb/dataset/PseudoMasks_v1", html=False), name="masks")



# 将根路径指向 index.html
@app.get("/")
async def index():
    return FileResponse("app/frontend/index.html")

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