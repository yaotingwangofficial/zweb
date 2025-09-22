from pathlib import Path
import os

class Settings:
    VIDEOS_ROOT: Path = Path('../dataset/Videos_v1').resolve()
    FRAMES_ROOT: Path = Path('../dataset/Frames_v1').resolve()
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")  # 生产建议配具体域名
    PAGE_MAX_SIZE: int = 200

settings = Settings()
