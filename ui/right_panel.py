import os, sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image
from core.i18n import get_lang_text
from utils.path import resource_path
#from ui.scrolling import ScrollRouter

class AttackInfoView(ctk.CTkScrollableFrame):
    def __init__(self, parent, fonts, lang_key, test_path, **kw):
        super().__init__(parent, **kw)
        self.fonts = fonts
        self.lang_key = lang_key
        self.test_path = test_path

        self._boss_overlay = None
        self._load_skillRange_images()

        self._boss_label = None
        self._boss_pil = None
        self._render_after_id = None

        # 폭 변할 때 이미지 재계산
        self.bind("<Configure>", self._on_configure)

    def _content_parent(self):
        """CTkScrollableFrame의 내용 프레임을 반환 (버전별 호환)."""
        # 신버전: public
        if hasattr(self, "scrollable_frame"):
            return self.scrollable_frame
        # 구버전: private
        if hasattr(self, "_scrollable_frame"):
            return self._scrollable_frame
        # 최후: 자기 자신(비권장, 스크롤 안 될 수 있음)
        return self
    
    def _fix_scrollregion(self):
        try:
            canvas = getattr(self, "_parent_canvas", None) or getattr(self, "_canvas", None)
            parent = self._content_parent()
            if canvas and parent:
                parent.update_idletasks()
                canvas.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
        except Exception as e:
            print("fix scrollregion err:", e)
        

    def set_fonts_lang(self, fonts, lang_key):
        self.fonts = fonts
        self.lang_key = lang_key

    def _load_skillRange_images(self):
        def load(rel_path: str | Path, size):
            try:
                p = resource_path(*Path(rel_path).parts)
                return ctk.CTkImage(Image.open(p), size=size)
            except Exception:
                return ctk.CTkImage(Image.open(self.test_path), size=size)

        self.img_comcast = load("./data/skillstat/comcast.png", (160, 45))
        self.img_inscast = load("./data/skillstat/inscast.png", (160, 45))
        self.img_outcombat = load("./data/skillstat/outcombat.png", (160, 45))
        self.img_small = load("./data/skillstat/small.png", (160, 45))
        self.img_medium = load("./data/skillstat/medium.png", (160, 45))
        self.img_large = load("./data/skillstat/large.png", (160, 45))
        self.img_rush = load("./data/skillstat/rush.png", (160, 45))
        self.img_link = load("./data/skillstat/link.png", (160, 45))
        self.img_strattack = load("./data/skillstat/strattack.png", (160, 45))
        self.img_hidden = load("./data/skillstat/hidden.png", (40, 40))

    # 인라인 렌더
    def _render_boss_inline(self, img_path: str):
        self.clear()
        try:
            self._boss_pil = Image.open(img_path)
        except Exception:
            self._boss_pil = Image.open(self.test_path)

        parent = self._content_parent()
        self._boss_label = ctk.CTkLabel(parent, text="")
        self._boss_label.pack(anchor="n", pady=0)

        self.update_idletasks() 
        self._render_boss_inline_render()
        self._fix_scrollregion()
        if hasattr(self, "_scrollrouter_refresh"):
            self._scrollrouter_refresh()
            #print("refresh right")

    def _render_boss_inline_render(self):
        if not (self._boss_pil and self._boss_label and self._boss_label.winfo_exists()):
            return
        # 현재 프레임의 가용 폭
        avail_w = max(1, self.winfo_width())
        if avail_w <= 1:
            self.update_idletasks()
            avail_w = max(1, self.winfo_width())
        ow, oh = self._boss_pil.size
        scale = max(1e-6, avail_w / ow)       # 가로 폭에 맞춰 스케일
        tw, th = int(ow * scale), int(oh * scale)

        img = ctk.CTkImage(self._boss_pil, size=(tw, th))
        self._boss_label.configure(image=img, text="")
        self._boss_label.image = img  # 참조 유지

    # 일반 몬스터 렌더
    def _render_normal_monster(self, monster: dict):
        self.clear()
        parent = self._content_parent()
        title = get_lang_text(monster.get("name"), self.lang_key)
        ctk.CTkLabel(
            parent, 
            text=f"{title}의 스킬 정보.",
            font=self.fonts["title"], 
            text_color="white"
            ).pack(anchor="w", pady=(10, 6))

        skills = monster.get("skills", [])
        amount = monster.get("skills_Amount", len(skills))

        if amount == 0 or len(skills) == 0:
            meh = ctk.CTkImage(
                    Image.open(self.test_path), size=(350, 350)
                )
            meh_label = ctk.CTkLabel(
                parent,
                image=meh,
                text=""
            )
            meh_label.pack(anchor="n", pady=100)
            return

        for i in range(amount):
            card = ctk.CTkFrame(parent, fg_color="#e0efff", corner_radius=10, width=630, height=240)
            card.pack(pady=5, fill="x")

            if i < len(skills):
                s = skills[i]
                s_name = get_lang_text(s.get("name"), self.lang_key)
                s_desc = get_lang_text(s.get("desc"), self.lang_key)
                #s_name_ko = monster["skills"][i]["name"]["ko"]
                area   = s.get("area_img")
                s_size = s.get("size", 0)
            else:
                s = {}
                s_name, s_desc = f"스킬 {i+1}", ""
                s_name_ko = ""
                area = None
                s_size = 0
                
            # 스킬 이름
            ctk.CTkLabel(
                card, 
                text=s_name, 
                font=self.fonts["skill_name"],
                text_color="#0f2c63", 
                fg_color="transparent"
            ).place(relx=0.385, rely=0.1, anchor="w")
            
            if self.lang_key != "ko":
                s_name_ko = s.get("name", {}).get("ko", "")
                if s_name_ko:
                    # 스킬 한글이름
                    ctk.CTkLabel(
                        card, 
                        text=s_name_ko, 
                        font=(("Malgun Gothic", 15, "bold")),
                        text_color="#0f2c63", 
                        fg_color="transparent"
                    ).place(relx=0.385, rely=0.23, anchor="w")
            
            # 스킬 코멘트
            if s_desc=="":
                None
            else:
                cm_frame = ctk.CTkFrame(
                card,
                fg_color="#FFFFFF",
                width=350,
                height=50,
                corner_radius=3
                )
                cm_frame.place(relx=0.38, rely=0.3, anchor="nw")
                cm_label = ctk.CTkLabel(
                    card, 
                    text=s_desc, 
                    font=(("Malgun Gothic", 15)),
                    text_color="#0f2c63", 
                    fg_color="#FFFFFF",
                    wraplength=550, 
                    justify="left",
                    corner_radius=0
                )
                cm_label.place(relx=0.385, rely=0.3, anchor="nw")
            
            
            # 캐스팅?
            cast = s.get("cast")
            if cast==2:
                ctk.CTkLabel(card, text="", image=self.img_outcombat).place(relx=0.38, rely=0.64, anchor="w")
            elif cast==1:
                ctk.CTkLabel(card, text="", image=self.img_inscast).place(relx=0.38, rely=0.64, anchor="w")
            else:
                ctk.CTkLabel(card, text="", image=self.img_comcast).place(relx=0.38, rely=0.64, anchor="w")

            # 공격 사이즈
            skrange = s.get("size")
            if skrange==2:
                ctk.CTkLabel(card, text="", image=self.img_large).place(relx=0.38, rely=0.86, anchor="w")
            elif skrange==1:
                ctk.CTkLabel(card, text="", image=self.img_medium).place(relx=0.38, rely=0.86, anchor="w")
            elif skrange==0:
                ctk.CTkLabel(card, text="", image=self.img_small).place(relx=0.38, rely=0.86, anchor="w")
            elif skrange==3:
                ctk.CTkLabel(card, text="", image=self.img_strattack).place(relx=0.38, rely=0.86, anchor="w")

            # 돌진?
            if s.get("rush"):
                ctk.CTkLabel(card, text="", image=self.img_rush).place(relx=0.68, rely=0.64, anchor="w")

            # 연계 시전?
            if s.get("link"):
                ctk.CTkLabel(card, text="", image=self.img_link).place(relx=0.68, rely=0.86, anchor="w")

            # 범위 이미지
            area = s.get("area_img")
            if area and os.path.exists(area):
                img_path, img_size = area, (215, 215)
            else:
                if s_size==4:
                    #img_path, img_size = "./data/skillran/buff.png", (160, 103)
                    img_path, img_size = resource_path("data", "skillran", "buff.png"), (160, 103)
                elif s_size==3:
                    img_path, img_size = resource_path("data", "skillran", "stratk.png"), (160, 103)
                else:
                    img_path, img_size = self.test_path, (215, 215)
            
            img = ctk.CTkImage(Image.open(img_path), size=img_size)
            lbl = ctk.CTkLabel(card, image=img, text="")
            lbl.image = img
            if os.path.exists(area):
                lbl.place(relx=0.02, rely=0.5, anchor="w")
            else:
                lbl.place(relx=0.07, rely=0.45, anchor="w")

            # AOE
            if s.get("rangeCheck"):
                ctk.CTkLabel(card, text="", image=self.img_hidden).place(relx=0.295, rely=0.85, anchor="w")

        self._fix_scrollregion()
        if hasattr(self, "_scrollrouter_refresh"):
            self._scrollrouter_refresh()
            #print("refresh right")

    def _render_boss_image(self):
        if not (self._boss_overlay and self._boss_overlay.winfo_exists() and self._boss_pil):
            return

        avail_w = max(1, self._boss_overlay.winfo_width() - 2)  # 여백 약간 보정
        ow, oh = self._boss_pil.size
        scale = max(1e-6, avail_w / ow)
        target_w = int(ow * scale)
        target_h = int(oh * scale)

        img = ctk.CTkImage(self._boss_pil, size=(target_w, target_h))
        self._boss_label.configure(image=img, text="")
        self._boss_label.image = img
    

    def _on_overlay_configure(self, _event=None):
        if self._render_after_id:
            self.after_cancel(self._render_after_id)
        self._render_after_id = self.after(50, self._render_boss_image)

    def clear(self):
        parent = self._content_parent()
        for w in parent.winfo_children():
            w.destroy()
        self._boss_label = None
        self._boss_pil = None

    def _on_configure(self, _e=None):
        if self._boss_pil and self._boss_label and self._boss_label.winfo_exists():
            if self._render_after_id:
                self.after_cancel(self._render_after_id)
            self._render_after_id = self.after(50, self._render_boss_inline_render)

    def show_default_hint(self):
        self.clear()
        ctk.CTkLabel(
            self, text="몬스터 정보 확인",
            text_color="white", 
            font=self.fonts["monster_sub"]
            ).pack(expand=True, pady=275)

    def show_monster(self, monster: dict):
        if monster.get("boss"):
            img_path = monster.get("boss_img")
            print(img_path, os.path.exists(img_path))
            if img_path and os.path.exists(img_path):
                self._render_boss_inline(img_path)
                return            
        self._render_normal_monster(monster)

        

