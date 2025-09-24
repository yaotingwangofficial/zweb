from pathlib import Path
import os

prefix_dir = '/home/share/wangyt'
data_root = '/data5/wangyt/svtrack/dataset'

class Settings:
    API_BASE = 'http://10.0.0.43:8012'

    VIDEOS_ROOT: Path = Path(f'{data_root}/Videos_v1').resolve()
    FRAMES_ROOT: Path = Path(f'{data_root}/Frames_v1').resolve()
    AUDIOS_ROOT: Path = Path(f"{data_root}/Audios_v1").resolve()
    PSEUDOMASK_ROOT: Path = Path(f'{data_root}/PseudoLabel_v1').resolve()

    SAVE_DIR = Path(f"{prefix_dir}/zweb/dataset/HumanCheck_v1")
    LOG_DIR = Path(f"{prefix_dir}/zweb/dataset/Logs_v1")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")  # 生产建议配具体域名
    PAGE_MAX_SIZE: int = 200

settings = Settings()
