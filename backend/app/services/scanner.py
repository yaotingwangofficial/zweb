from pathlib import Path
from typing import List, Dict, Optional
from cachetools import cached, TTLCache

# 缓存：10分钟失效；你也可改大一些
_index_cache = TTLCache(maxsize=1, ttl=600)

def _scan_all_mp4(root: Path) -> List[Path]:
    if not root.exists():
        print(f"WARNING: VIDEOS_ROOT {root} 不存在")
        return []
    # 递归扫描，按路径排序保证稳定分页
    video_list = sorted(root.rglob("*.mp4"))
    print(video_list)
    return video_list

@cached(_index_cache)
def build_index(root: Path) -> Dict[str, List[str]]:
    """
    返回：
    {
      "__all__": ["anime_Conan/1_merged.mp4", ...],
      "anime_Conan": ["1_merged.mp4", ...]
    }
    """
    files = _scan_all_mp4(root)
    all_rel = [str(p.relative_to(root)).replace("\\", "/") for p in files]
    by_cat: Dict[str, List[str]] = {}
    print('all_rel:', all_rel)
    for rel in all_rel:
        parts = rel.split("/")
        if len(parts) >= 2:
            cat = parts[-2]
            by_cat.setdefault(cat, []).append(parts[-1])
    by_cat["__all__"] = all_rel
    
    print('by_cat init:', by_cat)
    return by_cat

def refresh_index(root: Path) -> Dict[str, List[str]]:
    _index_cache.clear()
    return build_index(root)

def query_videos(root: Path, page: int, page_size: int,
                 category: Optional[str] = None,
                 search: Optional[str] = None) -> (int, List[str]):
    idx = build_index(root)
    if category:
        pool = [f"{category}/{name}" for name in idx.get(category, [])]
    else:
        pool = idx.get("__all__", [])

    if search:
        s = search.lower()
        pool = [p for p in pool if s in p.lower()]
    print('pool:', pool)
    
    total = len(pool)
    start = (page - 1) * page_size
    end = min(total, start + page_size)
    if start >= total:
        return total, []
    return total, pool[start:end]
