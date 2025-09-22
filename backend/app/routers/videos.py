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
