import os
import json
from fastapi import APIRouter, Query, HTTPException, Request
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


# 获取视频帧对应的 mask 列表
@router.get("/masks")
def list_masks(
    category: str = Query(..., description="视频类别"),
    base_name: str = Query(..., description="视频基础名称"),
    frame_number: str = Query(..., description="帧编号"),
):
    """
    获取指定视频的指定帧的所有 mask
    """
    # 构建 mask 目录路径
    masks_dir = settings.PSEUDOMASK_ROOT / category / base_name / f"frame_{frame_number}"
    
    # 检查目录是否存在
    if not masks_dir.exists():
        raise HTTPException(status_code=404, detail=f"Masks directory not found: {masks_dir}")
    
    try:
        # 获取该目录下所有图片文件
        mask_files = [f.name for f in masks_dir.iterdir() if f.is_file() and f.name.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not mask_files:
            raise HTTPException(status_code=404, detail="No masks found for this frame")
        
        # 按文件名排序以确保顺序正确
        mask_files.sort()
        
        return {"masks": mask_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 保存人工检查结果
@router.post("/save-human-check")
async def save_human_check(request: Request):
    """
    保存人工检查的标注结果到指定目录
    """
    try:
        # 获取请求体中的JSON数据
        data = await request.json()
        
        # 提取数据
        category = data.get("category")
        base_name = data.get("baseName")
        annotation_data = data.get("data")
        
        # 检查必要参数
        if not category or not base_name or not annotation_data:
            raise HTTPException(status_code=400, detail="Missing required parameters: category, baseName, or data")
        
        # 定义保存目录
        save_directory = "/home/share/wangyt/zweb/dataset/HumanCheck_v1"
        
        # 创建目录（如果不存在）
        os.makedirs(save_directory, exist_ok=True)
        
        # 创建文件路径
        file_name = f"{category}_{base_name}_annotations.json"
        file_path = os.path.join(save_directory, file_name)
        
        # 保存JSON数据到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, indent=2, ensure_ascii=False)
        
        return {"status": "success", "message": "Annotations saved successfully", "file_path": file_path}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving annotations: {str(e)}")