import json
from pathlib import Path
from typing import List, Dict, Any

def load_monsters_from_json(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    monsters = data.get("monsters", [])
    valid = []
    for i, m in enumerate(monsters):
        # 필수 체크
        if not isinstance(m.get("name", {}), dict) or "ko" not in m["name"]:
            print(f"[warn] monsters[{i}] name.ko 누락 → 제외"); continue
        if "floors" not in m:
            print(f"[warn] monsters[{i}] floors 누락 → 제외"); continue

        floors = m["floors"]
        def _ok_floor(f):
            return (isinstance(f, int)) or (isinstance(f, list) and len(f) == 2 and all(isinstance(x, int) for x in f))
        if isinstance(floors, list):
            if not (_ok_floor(floors) or all(_ok_floor(x) for x in floors)):
                print(f"[warn] monsters[{i}] floors 형식 이상 → 제외: {floors}"); continue
        elif not isinstance(floors, int):
            print(f"[warn] monsters[{i}] floors 형식 이상 → 제외: {floors}"); continue

        if m.get("boss") and not m.get("boss_img"):
            print(f"[warn] monsters[{i}] boss=true지만 boss_img 없음 → 제외"); continue

        valid.append(m)
    return valid
