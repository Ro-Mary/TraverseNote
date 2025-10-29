import sys
from pathlib import Path

def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller
        if hasattr(sys, "_MEIPASS"):      # onefile
            base = Path(sys._MEIPASS)
        else:                             # onedir
            base = Path(sys.executable).resolve().parent
    else:
        # 개발: 이 파일(utils/path.py) 기준으로 프로젝트 루트는 parents[1]
        base = Path(__file__).resolve().parents[1]
    return (base / Path(*parts)).resolve()
