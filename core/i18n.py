from typing import Any, Dict

def get_lang_text(multi: Any, lang: str) -> str:
    if isinstance(multi, Dict):
        return multi.get(lang) or multi.get("en") or multi.get("ja") or multi.get("ko") or ""
    return multi or ""
