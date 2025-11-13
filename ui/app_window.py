import os, sys
from pathlib import Path
import customtkinter as ctk
from core.loader import load_monsters_from_json
from core.fonts import build_fonts
#from core.i18n import get_lang_text
#from core.filters import appears_on
from ui.left_panel import MonsterListView
from ui.right_panel import AttackInfoView
from ui.scrolling import ScrollRouter
from utils.path import resource_path

class MonsterDexApp(ctk.CTk):
    def __init__(self):
        if sys.platform.startswith("win"):
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MyCompany.TraverseNote")
            except Exception:
                pass
                
        super().__init__()

        # 앱 설정
        self.iconbitmap(default=str(resource_path("data", "icon.ico")))
        
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.title("Traverse Note")
        self.geometry("1250x700")
        self.resizable(False, False)

        # 상태
        self.nowFloor = 1
        self.test_Path = str(resource_path("data", "skillran", "meh.png"))
        self.selected_monster = None

        # 데이터 로드
        self.monsters = load_monsters_from_json(resource_path("data", "monsters.json"))

        # 언어
        self.lang_options = ["영어", "일본어", "한국어"]
        self.lang_map     = {"영어": "en", "일본어": "ja", "한국어": "ko"}
        self.nowLangKey   = "en"
        self.fonts = build_fonts(self.nowLangKey)

        # 메인 프레임
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#bcdaff", 
            width=1250, 
            height=700)
        self.main_frame.place(x=0, y=0)

        # 현재 층 프레임
        self.nowFloor_Frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#0f2c63", 
            width=250, 
            height=70, 
            corner_radius=0
            )
        self.nowFloor_Frame.place(x=0, y=0)

        self.nowFloor_Label = ctk.CTkLabel(
            self.nowFloor_Frame, 
            text=f"T{self.nowFloor}",
            font=('Malgun Gothic', 50, 'bold'), 
            text_color='#FFFFFF'
            )
        self.nowFloor_Label.place(relx=0.5, rely=0.45, anchor="center")

        # 층 선택 프레임
        self.selectFloor_Frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#0f2c63",
            width=1000, 
            height=70, 
            corner_radius=0
            )
        self.selectFloor_Frame.place(x=250, y=0)

        # 언어 드롭박스
        self.selectLang = ctk.CTkComboBox(
            self.selectFloor_Frame, 
            values=self.lang_options, 
            state="readonly",
            font=('Malgun Gothic', 15), 
            button_color="#a0c9fc",
            border_color="#a0c9fc", 
            command=self._on_language_change)
        self.selectLang.place(relx=0.95, rely=0.5, anchor="e")
        self.selectLang.set("영어")

        # 좌측(몬스터 리스트)
        self.monsterInfo_Frame = MonsterListView(
            self.main_frame, 
            fonts=self.fonts, 
            lang_key=self.nowLangKey,
            test_path=self.test_Path, 
            on_select=self._on_select_monster,
            fg_color="#bcdaff", 
            width=580, height=600
            )
        self.monsterInfo_Frame.place(x=5, y=80)
        self.monsterInfo_Frame._scrollbar.grid_forget()

        # 우측(공격 정보)
        self.attackInfo_Frame = AttackInfoView(
            self.main_frame, 
            fonts=self.fonts, 
            lang_key=self.nowLangKey,
            test_path=self.test_Path, 
            fg_color="#a0c9fc", 
            width=617, 
            height=590
            )
        self.attackInfo_Frame.place(relx=0.48, rely=0.55, anchor="w")
        self.attackInfo_Frame.show_default_hint()

        self.router = ScrollRouter(speed=2.5)
        self.router.enable(self.monsterInfo_Frame, 1.6)
        self.router.enable(self.attackInfo_Frame, 1.4)

        self.upDownFloorButton()
        self.selectFloorFrame()
        self._render_monster_list()

    # 언어 변경 
    def _on_language_change(self, selected: str):
        self.nowLangKey = self.lang_map.get(selected, "en")
        self.fonts = build_fonts(self.nowLangKey)
        self.monsterInfo_Frame.set_fonts_lang(self.fonts, self.nowLangKey)
        self.attackInfo_Frame.set_fonts_lang(self.fonts, self.nowLangKey)
        self._render_monster_list()
        if self.selected_monster:
            self.attackInfo_Frame.show_monster(self.selected_monster)
        else:
            self.attackInfo_Frame.show_default_hint()

    # 층 이동 버튼 (위아래)
    def upDownFloorButton(self):
        self.nextFloor_Button = ctk.CTkButton(
            self.nowFloor_Frame, 
            text="next", 
            width=40, 
            height=20,
            font=('Meiryo', 15), 
            text_color='#FFFFFF',
            command=lambda: self.changeFloor(1)
            )
        self.nextFloor_Button.place(relx=0.95, rely=0.5, anchor="e")

        self.prevFloor_Button = ctk.CTkButton(
            self.nowFloor_Frame, 
            text="prev", 
            width=40, 
            height=20,
            font=('Meiryo', 15), 
            text_color='#FFFFFF',
            command=lambda: self.changeFloor(-1)
            )
        self.prevFloor_Button.place(relx=0.05, rely=0.5, anchor="w")

    def changeFloor(self, diff):
        newFloor = self.nowFloor + diff
        if newFloor < 1: newFloor = 1
        if newFloor > 99: newFloor = 99
        self.nowFloor = newFloor
        self.nowFloor_Label.configure(text=f"T{self.nowFloor}")
        self.updateFloorButtons()
        self.updateNowFloor(str(self.nowFloor))

    def updateFloorButtons(self):
        if self.nowFloor <= 1:
            self.prevFloor_Button.configure(
                state="disabled", 
                fg_color="gray50", 
                hover_color="gray50"
                )
        else:
            self.prevFloor_Button.configure(
                state="normal", 
                fg_color="#3b8ed0", 
                hover_color="#1f6aa5"
                )
        if self.nowFloor >= 99:
            self.nextFloor_Button.configure(
                state="disabled", 
                fg_color="gray50", 
                hover_color="gray50"
                )
        else:
            self.nextFloor_Button.configure(
                state="normal", 
                fg_color="#3b8ed0", 
                hover_color="#1f6aa5"
                )

    # 층 구간 버튼 
    def selectFloorFrame(self):
        button_width, button_height, gap = 65, 50, 8
        start_Floor = 1
        self.floor_buttons = []
        for i in range(10):
            btn_Text = f"{start_Floor}"
            x_pos = 10 + i * (button_width + gap)
            btn = ctk.CTkButton(
                self.selectFloor_Frame, 
                text=f"T{btn_Text}", 
                text_color='#000000',
                width=button_width, 
                height=button_height, 
                corner_radius=5,
                fg_color="#bcdaff", hover_color="#3568a7",
                font=("Malgun Gothic", 20, 'bold'),
                command=lambda text=btn_Text: self.updateNowFloor(text)
                )
            btn.place(x=x_pos+5, y=25)
            self.floor_buttons.append(btn)
            start_Floor += 10

    def updateNowFloor(self, floor_range):
        self.nowFloor_Label.configure(text=f"T{floor_range}")
        self.nowFloor = int(floor_range)

        for btn in self.floor_buttons:
            btn.configure(fg_color="#bcdaff")

        for i in range(10):
            start = i * 10 + 1
            end = start + 9
            if start <= self.nowFloor <= end:
                self.floor_buttons[i].configure(fg_color="#3568a7")
                break
        self._render_monster_list()
        self.updateFloorButtons()

    # 왼쪽 목록 렌더 
    def _render_monster_list(self):
        self.monsterInfo_Frame.render(self.monsters, self.nowFloor)
        self.monsterInfo_Frame.update_idletasks()
        self.monsterInfo_Frame._parent_canvas.yview_moveto(0.0)

    # 몹 클릭
    def _on_select_monster(self, monster: dict):
        self.selected_monster = monster
        #self.attackInfo_Frame._render_normal_monster(monster)
        self.attackInfo_Frame.show_monster(monster)

