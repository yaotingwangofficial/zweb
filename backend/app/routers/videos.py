import os
from fastapi import APIRouter, Query, HTTPException
from ..config import settings
from ..models import VideoListResp
from ..services.scanner import query_videos, refresh_index

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.get("", response_model=VideoListResp)
def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=settings.PAGE_MAX_SIZE),
    category: str | None = Query(None, description="例如 anime_Conan"),
    search: str | None = Query(None, description="模糊搜索，例：merged"),
):
    total, items = query_videos(settings.VIDEOS_ROOT, page, page_size, category, search)
    return {"total": total, "items": items}

@router.post("/refresh", response_model=VideoListResp)
def refresh(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=settings.PAGE_MAX_SIZE),
    category: str | None = Query(None),
    search: str | None = Query(None),
):
    # 触发重建索引后，顺便返回第一页数据，方便调试
    from ..services.scanner import refresh_index, query_videos
    refresh_index(settings.VIDEOS_ROOT)
    total, items = query_videos(settings.VIDEOS_ROOT, page, page_size, category, search)
    return {"total": total, "items": items}

# 新增：获取视频帧列表
@router.get("/frames")
def list_frames(
    category: str = Query(..., description="视频类别"),
    base_name: str = Query(..., description="视频基础名称"),
):
    """
    获取指定视频的所有帧
    """
    # 构建帧目录路径
    frames_dir = settings.FRAMES_ROOT / category / base_name
    
    # 检查目录是否存在
    if not frames_dir.exists():
        raise HTTPException(status_code=404, detail=f"Frames directory not found: {frames_dir}")
    
    try:
        # 获取该目录下所有图片文件
        frame_files = [f.name for f in frames_dir.iterdir() if f.is_file() and f.name.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not frame_files:
            raise HTTPException(status_code=404, detail="No frames found for this video")
        
        # 按文件名排序以确保顺序正确
        frame_files.sort()
        
        return {"frames": frame_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))