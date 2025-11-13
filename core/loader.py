import json, os
from pathlib import Path
from typing import List, Dict, Any
from utils.path import resource_path

def _norm_asset_path(rel: str | None) -> str | None:
    if not rel:
        return None
    p = Path(rel)

    parts = [seg for seg in p.parts if seg not in (".",)]

    if parts and parts[0].lower() == "data":
        parts[0] = "data"

    abs_path = p if p.is_absolute() else resource_path(*parts)
    return str(abs_path)

def load_monsters_from_json(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    monsters = data.get("monsters", [])
    valid: List[Dict[str, Any]] = []
    for i, m in enumerate(monsters):
        if m.get("img"):
            m["img"] = _norm_asset_path(m["img"])
        if m.get("boss_img"):
            m["boss_img"] = _norm_asset_path(m["boss_img"])

        for s in m.get("skills", []) or []:
            if s.get("area_img"):
                s["area_img"] = _norm_asset_path(s["area_img"])
                
        valid.append(m)
        
    return valid
