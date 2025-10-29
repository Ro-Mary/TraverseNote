import os
import customtkinter as ctk
from pathlib import Path
from PIL import Image
from core.filters import appears_on, first_appearance_floor
from core.i18n import get_lang_text
from utils.path import resource_path

class MonsterListView(ctk.CTkScrollableFrame):
    def __init__(self, parent, fonts, lang_key, test_path, on_select, **kw):
        super().__init__(parent, **kw)
        self.fonts = fonts
        self.lang_key = lang_key
        self.test_path = test_path
        self.on_select = on_select

        self._load_status_images()
        self._load_skill_icons()
        self._load_badges()

    def set_fonts_lang(self, fonts, lang_key):
        self.fonts = fonts
        self.lang_key = lang_key

    def _load_status_images(self):
        def load(rel_path: str | Path, size):
            try:
                p = resource_path(*Path(rel_path).parts)
                return ctk.CTkImage(Image.open(p), size=size)
            except Exception:
                return ctk.CTkImage(Image.open(self.test_path), size=size)

        self.img_stunO = load("./data/status/stunO.png", (142, 40))
        self.img_stunX = load("./data/status/stunX.png", (142, 40))
        self.img_roming = load("./data/status/roming.png", (142, 40))
        self.img_sight = load("./data/status/sight.png", (142, 40))
        self.img_distance = load("./data/status/distance.png", (142, 40))
        self.img_sound = load("./data/status/sound.png", (142, 40))
        self.img_vanish = load("./data/status/vanish.png", (142, 40))

    def _load_skill_icons(self):
        raw_map = [
            ("chariot", "./data/skillran/icon/chariot.png"),
            ("circle", "./data/skillran/icon/circle.png"),
            ("corn_front", "./data/skillran/icon/cone_front.png"),
            ("corn_back", "./data/skillran/icon/cone_back.png"),
            ("dynamo", "./data/skillran/icon/dynamo.png"),
            ("fronthalf", "./data/skillran/icon/half_front.png"),
            ("half_back", "./data/skillran/icon/half_back.png"),
            ("half_left", "./data/skillran/icon/half_left.png"),
            ("half_right", "./data/skillran/icon/half_right.png"),
            ("pack", "./data/skillran/icon/pack.png"),
            ("plus", "./data/skillran/icon/plus.png"),
            ("square", "./data/skillran/icon/square.png"),
            ("saw_left", "./data/skillran/icon/saw_left.png"),
            ("saw_right", "./data/skillran/icon/saw_right.png")
        ]
        self._skill_icon_map = [
        (key, str(resource_path(*Path(icon_rel).parts))) for key, icon_rel in raw_map
        ]
        self._skill_icon_cache = {}
        for _, icon_path in self._skill_icon_map:
            try:
                self._skill_icon_cache[icon_path] = ctk.CTkImage(Image.open(icon_path), size=(50, 50))
            except Exception:
                self._skill_icon_cache[icon_path] = ctk.CTkImage(Image.open(self.test_path), size=(50, 50))

    def _pick_icons_from_monster(self, monster) -> list:
        icons = []
        seen = set()  # 같은 아이콘 중복 방지
        skills = monster.get("skills", [])
        for s in skills:
            area = (s.get("area_img") or "").lower()
            if not area:
                continue
            for key, icon_path in self._skill_icon_map:
                if key in area and icon_path not in seen:
                    icons.append(self._skill_icon_cache[icon_path])
                    seen.add(icon_path)
                    if len(icons) >= 3:
                        return icons
        return icons[:3]
    
    # 첫 등장?
    def _load_badges(self):
        try:
            self.img_newbadge = ctk.CTkImage(Image.open("./data/skillran/icon/firstenc.png"), size=(65, 65))
        except Exception:
            self.img_newbadge = ctk.CTkImage(Image.open(self.test_path), size=(65, 65))

    def render(self, monsters, now_floor):
        # 초기화
        for w in self.winfo_children():
            w.destroy()

        colors = {0: "#e0efff", 1: "#fff3b0", 2: "#ffd7d7"}
        current = [m for m in monsters if appears_on(m.get("floors"), now_floor)]

        newcomers = []
        others = []
        for m in current:
            first_floor = first_appearance_floor(m.get("floors"))
            if first_floor is not None and first_floor == now_floor:
                newcomers.append(m)
            else:
                others.append(m)

        current = newcomers + others  # newcomers 먼저

        if not current:
            ctk.CTkLabel(self, 
                text="버근가",
                font=self.fonts["monster_name"], 
                text_color="#0f2c63").pack(pady=20)
            return

        for i, monster in enumerate(current):
            frame = ctk.CTkFrame(
                self, 
                fg_color=colors.get(monster.get("warning", 0), "#e0efff"), 
                corner_radius=10
                )
            frame.pack(pady=(10 if i == 0 else 0, 10), fill="x")

            # 첫 등장
            first_floor = first_appearance_floor(monster.get("floors"))
            if first_floor is not None and first_floor == now_floor:
                badge = ctk.CTkLabel(frame, image=self.img_newbadge, text="")
                badge.image = self.img_newbadge
                badge.place(relx=0.85, rely=0.35)

            # 대표 이미지
            img_path = monster.get("img")
            if img_path and os.path.exists(img_path):
                img = ctk.CTkImage(Image.open(img_path), size=(180, 180))
            else:
                img = ctk.CTkImage(Image.open(self.test_path), size=(180, 180))
            lbl_img = ctk.CTkLabel(frame, text="", image=img)
            lbl_img.image = img
            lbl_img.place(x=10, rely=0.5, anchor="w")

            # 이름 (현재 언어)
            name_txt = get_lang_text(monster.get("name"), self.lang_key)
            ctk.CTkLabel(
                frame, 
                text=name_txt, 
                fg_color="transparent",
                text_color="#0f2c63", 
                font=self.fonts["monster_name"]
                ).place(relx=0.35, rely=0.11, anchor="w")

            # 한글 이름
            name_ko = monster.get("name", {}).get("ko", "")
            ctk.CTkLabel(
                frame, 
                text=name_ko, 
                fg_color="transparent",
                text_color="#0f2c63", 
                font=("Malgun Gothic", 15, "bold")
                ).place(relx=0.35, rely=0.28, anchor="w")

            # 기절
            if monster.get("stun", False):
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_stunO
                    ).place(relx=0.34, rely=0.45, anchor="w")
            else:
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_stunX
                    ).place(relx=0.34, rely=0.45, anchor="w")

            # 어그로
            aggro = monster.get("aggro")
            if aggro==2:
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_distance
                    ).place(relx=0.34, rely=0.66, anchor="w")
            elif aggro==1:
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_sound
                    ).place(relx=0.34, rely=0.66, anchor="w")
            else:
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_sight
                    ).place(relx=0.34, rely=0.66, anchor="w")

            # 로밍
            if monster.get("roaming", False):
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_roming
                    ).place(relx=0.34, rely=0.87, anchor="w")

            # 카멜레온
            tag = monster.get("tag")
            if tag==604:
                ctk.CTkLabel(
                    frame, 
                    text="", 
                    image=self.img_vanish
                    ).place(relx=0.34, rely=0.87, anchor="w")

            # 범위 간략 표시
            icons = self._pick_icons_from_monster(monster)
            if icons:
                base_x = 400   
                base_y = 145
                gap = 12
                for idx, icon_img in enumerate(icons):
                    x = base_x + idx * (40 + gap)
                    lbl = ctk.CTkLabel(frame, image=icon_img, text="")
                    lbl.image = icon_img  
                    lbl.place(x=x, y=base_y) 

            # 이건 클릭이야
            for w in (frame, lbl_img):
                w.bind("<Button-1>", lambda e, m=monster: self.on_select(m))

        if hasattr(self, "_scrollrouter_refresh"):
            self._scrollrouter_refresh()
