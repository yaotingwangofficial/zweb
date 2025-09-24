import os
import json
import logging
from datetime import datetime
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
    masks_dir = settings.PSEUDOMASK_ROOT / category / base_name / f"frame_{int(frame_number):05d}/PseudoCombine"
    
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
        # print(mask_files)
        # input('==')
        return {"masks": mask_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audios")
def list_audios(
    category: str = Query(..., description="视频类别"),
    base_name: str = Query(..., description="视频基础名称")
):
    """
    获取指定视频的指定帧的所有音频文件
    """
    # Build audio directory path
    audios_dir = settings.AUDIOS_ROOT / category / base_name
    
    # Check if directory exists
    if not audios_dir.exists():
        raise HTTPException(status_code=404, detail=f"Audios directory not found: {audios_dir}")
    
    try:
        # Get all audio files in the directory
        audio_files = [
            f.name for f in audios_dir.iterdir() 
            if f.is_file() and f.name.lower().endswith(('.mp3', '.wav', '.ogg', '.aac', '.flac'))
        ]
        
        if not audio_files:
            raise HTTPException(status_code=404, detail="No audio files found for this frame")
        
        # Sort files by name to ensure consistent order
        audio_files.sort()
        
        return {"audios": audio_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 保存人工检查结果
@router.post("/save-human-check")
async def save_human_check(request: Request):
    try:
        # Get JSON data from request
        data = await request.json()
        print(f"Received data: {data}")
        
        # Extract required fields
        category = data.get("category")
        base_name = data.get("baseName")
        username = data.get("username")
        annotation_data = data.get("data")  # This is the nested data object
        
        # Validate required fields
        if not all([category, base_name, username, annotation_data]):
            missing = [k for k, v in {
                "category": category, 
                "baseName": base_name, 
                "username": username, 
                "data": annotation_data
            }.items() if not v]
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing)}"
            )
        
        try:
            # Save annotation data
            # save_directory = "/home/share/wangyt/zweb/dataset/HumanCheck_v1"
            save_directory = settings.SAVE_DIR
            os.makedirs(save_directory, exist_ok=True)
            
            file_name = f"{category}+{base_name}.json"
            file_path = os.path.join(save_directory, file_name)
            
            # Save the annotation data (the nested object)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(annotation_data, f, indent=2, ensure_ascii=False)
            
            # Create log entry
            # log_directory = "/home/share/wangyt/zweb/dataset/Logs_v1"
            log_directory = settings.LOG_DIR
            user_log_directory = os.path.join(log_directory, username)
            os.makedirs(user_log_directory, exist_ok=True)
            
            # Create safe filename for log (replace problematic characters)
            safe_category = category.replace("/", "+").replace("\\", "+")
            log_file_name = f"{safe_category}+{base_name}.log"
            log_file_path = os.path.join(user_log_directory, log_file_name)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] User '{username}' submitted annotations for {category}/{base_name}\n"
            
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
            
            return {
                "status": "success",
                "message": "Annotations saved successfully",
                "file_path": file_path,
                "log_path": log_file_path
            }
            
        except PermissionError as e:
            logging.error(f"Permission error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Permission error when saving files: {str(e)}"
            )
        except Exception as save_error:
            logging.error(f"Error saving files: {str(save_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error saving files: {str(save_error)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON data: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON data: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


HUMAN_CHECK_DIR = settings.SAVE_DIR

@router.get("/check-annotation-exists")
def check_annotation_exists(file: str = Query(..., description="Annotation file name to check")):
    """
    Check if an annotation file already exists
    """
    try:
        if not file:
            return {"exists": False}
        
        # Make sure the directory exists
        if not os.path.exists(HUMAN_CHECK_DIR):
            logging.warning(f"HumanCheck directory does not exist: {HUMAN_CHECK_DIR}")
            return {"exists": False}
            
        file_path = os.path.join(HUMAN_CHECK_DIR, file)
        
        # Log the exact path we're checking for debugging
        logging.info(f"Checking for annotation file: {file_path}")
        logging.info(f"File parameter received: {file}")
        
        # Check if file exists
        exists = os.path.exists(file_path)
        
        # If it doesn't exist, list files in directory for debugging
        if not exists:
            try:
                files_in_dir = os.listdir(HUMAN_CHECK_DIR)
                logging.info(f"Files in directory: {files_in_dir[:10]}")  # Show first 10 files
            except Exception as e:
                logging.error(f"Error listing directory contents: {e}")
        
        return {"exists": exists, "checked_path": file_path}
    except Exception as e:
        logging.error(f"Error checking annotation file: {e}")
        return {"exists": False, "error": str(e)}