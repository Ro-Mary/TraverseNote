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
        "monster_name": 25,
        "monster_sub": 15,
        "skill_name": 25,
        "skill_desc": 15,
    }
    
    if lang == "ja":
        scale = 0.85 
    else: 
        scale = 1.0
    fam = pick_font_family(lang)

    def mk(key: str, weight: str = "normal"):
        return ctk.CTkFont(
            family=fam,
            size=int(base[key] * scale),
            weight=weight
        )
    return {
        "title":        mk("title",        "bold"),
        "monster_name": mk("monster_name", "bold"),
        "monster_sub":  mk("monster_sub"),
        "skill_name":   mk("skill_name",   "bold"),
        "skill_desc":   mk("skill_desc"),
    }
    
