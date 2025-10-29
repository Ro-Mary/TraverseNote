from typing import Any, Optional

def first_appearance_floor(info: Any) -> Optional[int]:
    if info is None:
        return None

    def seg_min(seg):
        if isinstance(seg, int):
            return seg
        if isinstance(seg, list) and len(seg) == 2 and all(isinstance(x, int) for x in seg):
            s, e = seg
            return min(s, e)
        return None

    if isinstance(info, list):
        mins = [seg_min(seg) for seg in info]
        mins = [m for m in mins if m is not None]
        return min(mins) if mins else None
    return seg_min(info)

def appears_on(info: Any, floor: int) -> bool:
    if info is None:
        return True

    def match(seg):
        if isinstance(seg, int):
            return seg == floor
        if isinstance(seg, list) and len(seg) == 2 and all(isinstance(x, int) for x in seg):
            s, e = seg
            return s <= floor <= e
        return False

    if isinstance(info, list):
        return any(match(seg) for seg in info)
    return match(info)
