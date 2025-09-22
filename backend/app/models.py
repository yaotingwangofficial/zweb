from pydantic import BaseModel, Field
from typing import List

class VideoListResp(BaseModel):
    total: int = Field(..., ge=0)
    items: List[str]  # 相对 VIDEOS_ROOT 的路径，例：anime_Conan/1_merged.mp4