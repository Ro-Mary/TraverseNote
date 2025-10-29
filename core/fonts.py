import customtkinter as ctk

def pick_font_family(lang: str) -> str:
    if lang == "ja":
        return "Meiryo"
    elif lang == "en":
        return "Arial"
    else:
        return "Malgun Gothic"

def build_fonts(lang: str):
    base = {
        "title": 30,
        "monster_name": 30,
        "monster_sub": 15,
        "skill_name": 30,
        "skill_desc": 15,
    }
    scale = 0.75 if lang == "ja" else 1.0
    fam = pick_font_family(lang)
    fonts = {}
    for k, sz in base.items():
        weight = "bold" if k in ("title", "monster_name", "skill_name") else "normal"
        fonts[k] = ctk.CTkFont(family=fam, size=int(sz * scale), weight=weight)
    return fonts
