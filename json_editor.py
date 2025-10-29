import json
import os
import sys
from typing import List, Dict, Any
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Monsters JSON Editor"
DEFAULT_JSON_PATH = "monsters.json"

AGGRO_OPTIONS = [
    (0, "시야 감지"),
    (1, "소리 감지"),
    (2, "거리 감지"),
]

WARNING_OPTIONS = [(0, "보통"), (1, "주의"), (2, "위험")]

SIZE_OPTIONS = [0, 1, 2, 3, 4]

class MonstersEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x530")
        # 내부 플래그: 폼 로딩 중에는 자동 채우기 억제
        self._is_loading_form = False
        self.resizable(False, False)

        self.monsters: List[Dict[str, Any]] = []
        self.current_index: int | None = None
        self.current_skill_index: int | None = None
        self.json_path: str = DEFAULT_JSON_PATH

        self._build_ui()
        self._new_file_if_absent()
        self._load_json_silent(self.json_path)

    # ---------------- UI ----------------
    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Top toolbar
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))
        for i in range(10):
            toolbar.columnconfigure(i, weight=0)
        
        ttk.Button(toolbar, text="새 파일", command=lambda: self.on_new_file()).grid(row=0, column=0, padx=2)
        ttk.Button(toolbar, text="불러오기", command=lambda: self.on_open()).grid(row=0, column=1, padx=2)
        ttk.Button(toolbar, text="저장", command=lambda: self.on_save()).grid(row=0, column=2, padx=2)
        ttk.Separator(toolbar, orient="vertical").grid(row=0, column=3, sticky="ns", padx=6)
        ttk.Button(toolbar, text="새 몬스터", command=lambda: self.on_new_monster()).grid(row=0, column=4, padx=2)
        ttk.Button(toolbar, text="복제", command=lambda: self.on_clone_monster()).grid(row=0, column=5, padx=2)
        ttk.Button(toolbar, text="삭제", command=lambda: self.on_delete_monster()).grid(row=0, column=6, padx=2)

        # Left: monsters list
        left = ttk.Frame(self)
        left.grid(row=1, column=0, sticky="nsw", padx=(8, 4), pady=(0, 8))
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text="몬스터 목록").grid(row=0, column=0, sticky="w")
        self.list_monsters = tk.Listbox(left, width=36, height=28, exportselection=False)
        self.list_monsters.grid(row=1, column=0, sticky="nsw")
        self.list_monsters.bind("<<ListboxSelect>>", lambda e: self.on_select_monster(e))

        # Right: editor panels (monster + skills)
        right = ttk.Notebook(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))

        # Monster tab
        self.tab_monster = ttk.Frame(right)
        right.add(self.tab_monster, text="몬스터")
        self._build_monster_form(self.tab_monster)

        # Skills tab
        self.tab_skills = ttk.Frame(right)
        right.add(self.tab_skills, text="스킬")
        self._build_skills_form(self.tab_skills)

    def _build_monster_form(self, parent: ttk.Frame):
        parent.columnconfigure(1, weight=1)
        r = 0
        # tag
        ttk.Label(parent, text="tag (코드 번호)").grid(row=r, column=0, sticky="e", padx=6, pady=4)
        self.var_tag = tk.StringVar()
        e_tag = ttk.Entry(parent, textvariable=self.var_tag, width=20)
        e_tag.grid(row=r, column=1, sticky="w", pady=4)
        # tag 변경 시 img 자동 채우기
        self.var_tag.trace_add("write", lambda *args: self._maybe_autofill_img())
        e_tag.bind("<FocusOut>", lambda e: self._maybe_autofill_img())
        r += 1

        # name (ko, en, ja)
        name_frame = ttk.LabelFrame(parent, text="name (다국어)")
        name_frame.grid(row=r, column=0, columnspan=2, sticky="ew", padx=6, pady=4)
        name_frame.columnconfigure(1, weight=1)
        ttk.Label(name_frame, text="ko").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.var_name_ko = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.var_name_ko).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(name_frame, text="en").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.var_name_en = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.var_name_en).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(name_frame, text="ja").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        self.var_name_ja = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.var_name_ja).grid(row=2, column=1, sticky="ew", pady=4)
        r += 1

        # img
        ttk.Label(parent, text="img (이미지 경로)").grid(row=r, column=0, sticky="e", padx=6, pady=4)
        self.var_img = tk.StringVar()
        entry_img = ttk.Entry(parent, textvariable=self.var_img)
        entry_img.grid(row=r, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text="찾기", command=lambda: self._pick_img() ).grid(row=r, column=2, padx=4)
        r += 1

        # floors
        ttk.Label(parent, text="floors (쉼표 구분 정수)").grid(row=r, column=0, sticky="e", padx=6, pady=4)
        self.var_floors = tk.StringVar()
        ttk.Entry(parent, textvariable=self.var_floors).grid(row=r, column=1, sticky="ew", pady=4)
        r += 1

        # stun, roaming
        self.var_stun = tk.BooleanVar(value=False)
        self.var_roaming = tk.BooleanVar(value=False)
        frame_flags = ttk.Frame(parent)
        frame_flags.grid(row=r, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(frame_flags, text="stun(기절 가능)", variable=self.var_stun).grid(row=0, column=0, padx=2)
        ttk.Checkbutton(frame_flags, text="roaming(로밍)", variable=self.var_roaming).grid(row=0, column=1, padx=16)
        r += 1

        # aggro
        ttk.Label(parent, text="aggro (3가지 조건)").grid(row=r, column=0, sticky="e", padx=6, pady=4)
        self.var_aggro = tk.IntVar(value=0)
        self.combo_aggro = ttk.Combobox(parent, state="readonly", values=[f"{i} - {label}" for i, label in AGGRO_OPTIONS])
        self.combo_aggro.current(0)
        self.combo_aggro.grid(row=r, column=1, sticky="w", pady=4)
        r += 1

        # warning (옵션, 콤보박스)
        ttk.Label(parent, text="warning (옵션)").grid(row=r, column=0, sticky="e", padx=6, pady=4)
        self.combo_warning = ttk.Combobox(parent, state="readonly", values=[f"{i} - {label}" for i, label in WARNING_OPTIONS])
        self.combo_warning.current(0)
        self.combo_warning.grid(row=r, column=1, sticky="w", pady=4)
        r += 1

        # boss & boss_img
        frame_boss = ttk.LabelFrame(parent, text="보스 설정")
        frame_boss.grid(row=r, column=0, columnspan=3, sticky="ew", padx=6, pady=6)
        frame_boss.columnconfigure(1, weight=1)
        self.var_boss = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_boss, text="boss (보스 여부)", variable=self.var_boss, command=lambda: self._toggle_boss()).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Label(frame_boss, text="boss_img").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.var_boss_img = tk.StringVar()
        self.entry_boss_img = ttk.Entry(frame_boss, textvariable=self.var_boss_img)
        self.entry_boss_img.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(frame_boss, text="찾기", command=lambda: self._pick_boss_img() ).grid(row=1, column=2, padx=4)
        r += 1

        # Save monster button
        btn = ttk.Button(parent, text="현재 몬스터 변경사항 적용", command=lambda: self.on_apply_monster_changes())
        btn.grid(row=r, column=0, columnspan=3, pady=10)

    def _build_skills_form(self, parent: ttk.Frame):
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(5, weight=1)

        # Skills list
        ttk.Label(parent, text="스킬 목록").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.list_skills = tk.Listbox(parent, height=18, exportselection=False)
        self.list_skills.grid(row=1, column=0, rowspan=6, sticky="nsw", padx=(6, 12))
        self.list_skills.bind("<<ListboxSelect>>", lambda e: self.on_select_skill(e))

        # Skill fields
        r = 0
        fields = ttk.Frame(parent)
        fields.grid(row=1, column=1, sticky="nsew", pady=4)
        fields.columnconfigure(1, weight=1)

        ttk.Label(fields, text="name.ko").grid(row=r, column=0, sticky="e", padx=6, pady=2)
        self.var_s_ko = tk.StringVar()
        ttk.Entry(fields, textvariable=self.var_s_ko).grid(row=r, column=1, sticky="ew", pady=2)
        r += 1
        ttk.Label(fields, text="name.en").grid(row=r, column=0, sticky="e", padx=6, pady=2)
        self.var_s_en = tk.StringVar()
        ttk.Entry(fields, textvariable=self.var_s_en).grid(row=r, column=1, sticky="ew", pady=2)
        r += 1
        ttk.Label(fields, text="name.ja").grid(row=r, column=0, sticky="e", padx=6, pady=2)
        self.var_s_ja = tk.StringVar()
        ttk.Entry(fields, textvariable=self.var_s_ja).grid(row=r, column=1, sticky="ew", pady=2)
        r += 1

        ttk.Label(fields, text="area_img").grid(row=r, column=0, sticky="e", padx=6, pady=2)
        self.var_s_area_img = tk.StringVar()
        ttk.Entry(fields, textvariable=self.var_s_area_img).grid(row=r, column=1, sticky="ew", pady=2)
        ttk.Button(fields, text="찾기", command=lambda: self._pick_skill_img() ).grid(row=r, column=2, padx=4)
        r += 1

        ttk.Label(fields, text="desc").grid(row=r, column=0, sticky="ne", padx=6, pady=2)
        self.txt_s_desc = tk.Text(fields, height=5)
        self.txt_s_desc.grid(row=r, column=1, columnspan=2, sticky="ew", pady=2)
        r += 1

        # cast: 0/1/2 콤보박스
        ttk.Label(fields, text="cast (0/1/2)").grid(row=r, column=0, sticky="e", padx=6, pady=2)
        self.var_s_cast = tk.IntVar(value=0)
        self.combo_s_cast = ttk.Combobox(fields, state="readonly", values=[
            "0 - 일반 캐스팅",
            "1 - 즉시 시전",
            "2 - 비전투 캐스팅",
        ])
        self.combo_s_cast.current(0)
        self.combo_s_cast.grid(row=r, column=1, sticky="w")
        r += 1

        # rush/link 체크박스
        self.var_s_rush = tk.BooleanVar(value=False)
        self.var_s_link = tk.BooleanVar(value=False)
        opts = ttk.Frame(fields)
        opts.grid(row=r, column=1, sticky="w", pady=2)
        ttk.Checkbutton(opts, text="rush", variable=self.var_s_rush).grid(row=0, column=0, padx=4)
        ttk.Checkbutton(opts, text="link", variable=self.var_s_link).grid(row=0, column=1, padx=12)
        r += 1

        ttk.Label(fields, text="size (0/1/2)").grid(row=r, column=0, sticky="e", padx=6, pady=2)
        self.var_s_size = tk.IntVar(value=0)
        self.combo_s_size = ttk.Combobox(fields, state="readonly", values=[
            "0 - 보통",
            "1 - 넓음",
            "2 - 매우 넓음",
            "3 - 강공격",
            "4 - 범위 없음"
        ])
        self.combo_s_size.current(0)
        self.combo_s_size.grid(row=r, column=1, sticky="w")
        r += 1

        # buttons for skills
        btns = ttk.Frame(parent)
        btns.grid(row=7, column=1, sticky="w", pady=8)
        ttk.Button(btns, text="스킬 추가", command=self.on_add_skill).grid(row=0, column=0, padx=2)
        ttk.Button(btns, text="현재 스킬 수정", command=self.on_update_skill).grid(row=0, column=1, padx=2)
        ttk.Button(btns, text="스킬 삭제", command=self.on_delete_skill).grid(row=0, column=2, padx=2)

    # ---------------- Helpers ----------------
    def _new_file_if_absent(self):
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump({"monsters": []}, f, ensure_ascii=False, indent=4)

    def _load_json_silent(self, path: str):
        """monsters.json 로드 (최상위는 {"monsters": [...]} 또는 리스트 하위호환)
        예외는 내부에서 처리하여 메시지로만 표시한다.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("monsters"), list):
                self.monsters = data["monsters"]
            elif isinstance(data, list):
                # 하위호환: 과거 버전의 순수 리스트 형식도 지원
                self.monsters = data
            else:
                raise ValueError("JSON 최상위는 {\"monsters\": [...]} 또는 리스트여야 합니다.")
            self.json_path = path
            self.refresh_monster_list()
            self.current_index = None
            self.clear_monster_form()
            self.clear_skill_form()
            if hasattr(self, 'refresh_skill_list'):
                self.refresh_skill_list()
        except Exception as e:
            messagebox.showerror("불러오기 실패", f"{e}")

    def on_apply_monster_changes(self) -> bool:
        if self.current_index is None:
            messagebox.showwarning("적용 불가", "먼저 몬스터를 선택하거나 새로 만드세요.")
            return False
        try:
            m = self._gather_monster_from_form(self.monsters[self.current_index])
            self.monsters[self.current_index] = m
            self.refresh_monster_list()
            self.list_monsters.select_clear(0, tk.END)
            self.list_monsters.select_set(self.current_index)
            self.list_monsters.see(self.current_index)
            messagebox.showinfo("적용됨", "현재 몬스터 변경사항을 반영했습니다.")
            return True
        except Exception as e:
            messagebox.showerror("검증 실패", str(e))
            return False

    def on_add_skill(self):
        if self.current_index is None:
            messagebox.showwarning("스킬 추가 불가", "먼저 몬스터를 선택하세요.")
            return
        skill = self._gather_skill_from_form()
        self.monsters[self.current_index].setdefault("skills", []).append(skill)
        self._sync_skills_amount(self.monsters[self.current_index])
        # 즉시 목록 갱신 및 방금 추가한 스킬 선택
        self.refresh_skill_list()
        new_idx = len(self.monsters[self.current_index]["skills"]) - 1
        self.list_skills.select_clear(0, tk.END)
        if new_idx >= 0:
            self.list_skills.select_set(new_idx)
            self.list_skills.see(new_idx)
            self.current_skill_index = new_idx
            self.on_select_skill()

    def on_update_skill(self):
        if self.current_index is None:
            messagebox.showwarning("스킬 수정 불가", "먼저 몬스터를 선택하세요.")
            return
        if self.current_skill_index is None:
            messagebox.showwarning("스킬 수정 불가", "수정할 스킬을 선택하세요.")
            return
        skill = self._gather_skill_from_form()
        self.monsters[self.current_index]["skills"][self.current_skill_index] = skill
        self._sync_skills_amount(self.monsters[self.current_index])
        self.refresh_skill_list()
        # 수정한 항목 유지 선택
        idx = self.current_skill_index
        self.list_skills.select_clear(0, tk.END)
        if idx is not None:
            self.list_skills.select_set(idx)
            self.list_skills.see(idx)
        # 저장 완료 알림
        messagebox.showinfo("적용됨", "현재 스킬 변경사항을 반영했습니다.")

    def on_delete_skill(self):
        if self.current_index is None:
            messagebox.showwarning("스킬 삭제 불가", "먼저 몬스터를 선택하세요.")
            return
        if self.current_skill_index is None:
            messagebox.showwarning("스킬 삭제 불가", "삭제할 스킬을 선택하세요.")
            return
        if messagebox.askyesno("스킬 삭제", "선택한 스킬을 삭제할까요?"):
            self.monsters[self.current_index]["skills"].pop(self.current_skill_index)
            self._sync_skills_amount(self.monsters[self.current_index])
            self.refresh_skill_list()
            # 선택 초기화 및 폼 클리어
            self.current_skill_index = None
            self.list_skills.select_clear(0, tk.END)
            self.clear_skill_form()

    def on_select_skill(self, event=None):
        sel = self.list_skills.curselection()
        if not sel:
            self.current_skill_index = None
            return
        self.current_skill_index = sel[0]
        s = self.monsters[self.current_index].get("skills", [])[self.current_skill_index]
        name = s.get("name", {})
        self.var_s_ko.set(name.get("ko", ""))
        self.var_s_en.set(name.get("en", ""))
        self.var_s_ja.set(name.get("ja", ""))
        self.var_s_area_img.set(s.get("area_img", ""))
        self.txt_s_desc.delete("1.0", tk.END)
        self.txt_s_desc.insert("1.0", s.get("desc", ""))
        self.var_s_cast.set(bool(s.get("cast", False)))
        size = int(s.get("size", 0))
        if size not in SIZE_OPTIONS:
            size = 0
        self.combo_s_size.current(SIZE_OPTIONS.index(size))
        cast_val = int(s.get("cast", 0))
        if cast_val not in (0,1,2):
            cast_val = 0
        self.combo_s_cast.current(cast_val)
        self.var_s_rush.set(bool(s.get("rush", False)))
        self.var_s_link.set(bool(s.get("link", False)))

    # ---------------- Missing UI/File helper methods (added) ----------------
    def refresh_monster_list(self):
        self.list_monsters.delete(0, tk.END)
        for m in self.monsters:
            tag = m.get("tag", "?")
            name = m.get("name", {}).get("ko", "(ko 없음)")
            self.list_monsters.insert(tk.END, f"[{tag}] {name}")

    def clear_monster_form(self):
        self._is_loading_form = True
        # 기본 폼 초기화
        self.var_tag.set("")
        self.var_name_ko.set("")
        self.var_name_en.set("")
        self.var_name_ja.set("")
        self.var_img.set("")
        self.var_floors.set("")
        self.var_stun.set(False)
        self.var_roaming.set(False)
        # 콤보 기본값
        if hasattr(self, 'combo_aggro'):
            self.combo_aggro.current(0)
        if hasattr(self, 'combo_warning'):
            self.combo_warning.current(0)
        # 보스 관련
        self.var_boss.set(False)
        self.var_boss_img.set("")
        if hasattr(self, 'entry_boss_img'):
            self._toggle_boss()
        self._is_loading_form = False

    def clear_skill_form(self):
        self.var_s_ko.set("")
        self.var_s_en.set("")
        self.var_s_ja.set("")
        self.var_s_area_img.set("")
        self.txt_s_desc.delete("1.0", tk.END)
        self.combo_s_cast.current(0)
        if hasattr(self, 'combo_s_size'):
            self.combo_s_size.current(0)
        self.var_s_rush.set(False)
        self.var_s_link.set(False)

    def refresh_skill_list(self):
        self.list_skills.delete(0, tk.END)
        if self.current_index is None:
            return
        skills = self.monsters[self.current_index].get("skills", [])
        for i, s in enumerate(skills):
            nm = s.get("name", {}).get("ko", f"스킬 {i+1}")
            self.list_skills.insert(tk.END, f"{i+1}. {nm}")
        # 목록 갱신 후 기존 선택 복원
        if self.current_skill_index is not None:
            if 0 <= self.current_skill_index < len(skills):
                try:
                    self.list_skills.select_set(self.current_skill_index)
                    self.list_skills.see(self.current_skill_index)
                except Exception:
                    pass

    def on_select_monster(self, event=None):
        self._is_loading_form = True
        sel = self.list_monsters.curselection()
        if not sel:
            return
        idx = sel[0]
        self.current_index = idx
        m = self.monsters[idx]
        # fill form
        self.var_tag.set("" if m.get("tag") is None else str(m.get("tag", "")))
        name = m.get("name", {})
        self.var_name_ko.set(name.get("ko", ""))
        self.var_name_en.set(name.get("en", ""))
        self.var_name_ja.set(name.get("ja", ""))
        self.var_img.set(m.get("img", ""))
        self.var_floors.set(", ".join(str(x) for x in m.get("floors", [])))
        self.var_stun.set(bool(m.get("stun", False)))
        self.var_roaming.set(bool(m.get("roaming", False)))
        aggro = int(m.get("aggro", 0))
        aggro_idx = 0 if aggro not in (0,1,2) else aggro
        if hasattr(self, 'combo_aggro'):
            self.combo_aggro.current(aggro_idx)
        warning = int(m.get("warning", 0))
        warning_idx = 0 if warning not in (0,1,2) else warning
        if hasattr(self, 'combo_warning'):
            self.combo_warning.current(warning_idx)
        self.var_boss.set(bool(m.get("boss", False)))
        self.var_boss_img.set("" if m.get("boss_img") in (None, "null") else str(m.get("boss_img", "")))
        self._toggle_boss()
        # skills
        self.refresh_skill_list()
        self.current_skill_index = None
        self.clear_skill_form()
        self._is_loading_form = False

    def _toggle_boss(self):
        try:
            if self.var_boss.get():
                self.entry_boss_img.state(["!disabled"])
            else:
                self.entry_boss_img.state(["disabled"])
        except Exception:
            pass

    def _pick_img(self):
        path = filedialog.askopenfilename(title="이미지 선택", filetypes=[("이미지", "*.png;*.jpg;*.jpeg;*.gif;*.webp"), ("모든 파일", "*.*")])
        if path:
            self.var_img.set(self._relpath(path))

    def _pick_boss_img(self):
        path = filedialog.askopenfilename(title="보스 이미지 선택", filetypes=[("이미지", "*.png;*.jpg;*.jpeg;*.gif;*.webp"), ("모든 파일", "*.*")])
        if path:
            self.var_boss_img.set(self._relpath(path))

    def _pick_skill_img(self):
        path = filedialog.askopenfilename(title="스킬 이미지 선택", filetypes=[("이미지", "*.png;*.jpg;*.jpeg;*.gif;*.webp"), ("모든 파일", "*.*")])
        if path:
            self.var_s_area_img.set(self._relpath(path))

    def _relpath(self, path: str) -> str:
        try:
            return os.path.relpath(path, start=os.getcwd())
        except Exception:
            return path

    def on_new_file(self):
        if not self._confirm_discard_changes():
            return
        self.monsters = []
        self.json_path = DEFAULT_JSON_PATH
        self.refresh_monster_list()
        self.current_index = None
        self.clear_monster_form()
        self.clear_skill_form()
        self.refresh_skill_list()

    def on_open(self):
        path = filedialog.askopenfilename(title="JSON 불러오기", filetypes=[("JSON", "*.json"), ("모든 파일", "*.*")])
        if path:
            self._load_json_silent(path)

    def on_save(self):
        # 현재 선택된 몬스터 변경사항 반영 시도
        if self.current_index is not None:
            if not self.on_apply_monster_changes():
                return
        path = filedialog.asksaveasfilename(initialfile=os.path.basename(self.json_path), defaultextension=".json", filetypes=[("JSON", "*.json")], title="JSON 저장")
        if not path:
            return
        try:
            data = self._export_data()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.json_path = path
            messagebox.showinfo("저장 완료", f"저장됨: {path}")
        except Exception as e:
            messagebox.showerror("저장 실패", str(e))

    def on_new_monster(self):
        new_m = self._empty_monster()
        self.monsters.append(new_m)
        self.refresh_monster_list()
        self.list_monsters.select_clear(0, tk.END)
        idx = len(self.monsters) - 1
        self.list_monsters.select_set(idx)
        self.list_monsters.see(idx)
        self.on_select_monster()

    def on_clone_monster(self):
        if self.current_index is None:
            messagebox.showwarning("복제 불가", "먼저 몬스터를 선택하세요.")
            return
        clone = json.loads(json.dumps(self.monsters[self.current_index], ensure_ascii=False))
        clone["tag"] = None  # 새 태그는 비워 중복 방지
        self.monsters.append(clone)
        self.refresh_monster_list()
        idx = len(self.monsters) - 1
        self.list_monsters.select_clear(0, tk.END)
        self.list_monsters.select_set(idx)
        self.list_monsters.see(idx)
        self.on_select_monster()

    def on_delete_monster(self):
        if self.current_index is None:
            messagebox.showwarning("삭제 불가", "먼저 몬스터를 선택하세요.")
            return
        if messagebox.askyesno("삭제 확인", "선택한 몬스터를 삭제할까요?"):
            self.monsters.pop(self.current_index)
            self.current_index = None
            self.refresh_monster_list()
            self.clear_monster_form()
            self.clear_skill_form()
            self.refresh_skill_list()

# ---------------- Data helpers ----------------
    def _auto_img_from_tag(self, tag: int) -> str:
        """예시 규칙에 따른 img 경로 자동 생성.
        폴더: (ceil(tag/10))가 속한 10단위 블록의 시작~끝 → {start}-{end}
        파일: 3자리 0패딩 PNG → {tag:03d}.png
        전체: ./data/{start}-{end}/{tag:03d}.png
        """
        if tag <= 0:
            return "./data/1-10/000.png"
        n = (tag + 9) // 10  # ceil(tag/10)
        start = ((n - 1) // 10) * 10 + 1
        end = start + 9
        return f"./data/{start}-{end}/{tag:03d}.png"

    def _maybe_autofill_img(self):
        if getattr(self, "_is_loading_form", False):
            return
        tag_str = self.var_tag.get().strip()
        if not tag_str:
            return
        try:
            tag = int(tag_str)
            auto = self._auto_img_from_tag(tag)
            self.var_img.set(auto)
        except ValueError:
            pass
    def _confirm_discard_changes(self) -> bool:
        return messagebox.askyesno("확인", "현재 내용을 모두 비우고 새로 시작할까요?")

    def _empty_monster(self) -> Dict[str, Any]:
        return {
            "tag": None,
            "name": {"ko": "", "en": "", "ja": ""},
            "img": "",
            "floors": [],
            "stun": False,
            "aggro": 0,
            "roaming": False,
            "warning": 0,  # 예시 포함 필드 (선택)
            "skills_Amount": 0,
            "skills": [],
            "boss": False,
            "boss_img": None,
        }

    def _parse_floors(self, text: str) -> List[int]:
        if not text.strip():
            return []
        parts = [p.strip() for p in text.split(',')]
        floors = []
        for p in parts:
            if not p:
                continue
            try:
                floors.append(int(p))
            except ValueError:
                raise ValueError(f"floors 값 '{p}' 는 정수가 아닙니다.")
        return floors

    def _gather_monster_from_form(self, base: Dict[str, Any]) -> Dict[str, Any]:
        tag_str = self.var_tag.get().strip()
        if tag_str == "":
            raise ValueError("tag(코드 번호)는 비워둘 수 없습니다.")
        try:
            tag = int(tag_str)
        except ValueError:
            raise ValueError("tag는 정수여야 합니다.")

        name = {
            "ko": self.var_name_ko.get().strip(),
            "en": self.var_name_en.get().strip(),
            "ja": self.var_name_ja.get().strip(),
        }
        if not name["ko"]:
            raise ValueError("name.ko(한국어 이름)은 필수입니다.")

        img = self.var_img.get().strip()
        if not img:
            # 비어 있으면 자동 경로 채우기
            img = self._auto_img_from_tag(tag)
            self.var_img.set(img)
        floors = self._parse_floors(self.var_floors.get())

        # aggro index from combo text's leading number
        aggro_idx = 0
        sel = self.combo_aggro.get()
        try:
            aggro_idx = int(sel.split("-", 1)[0].strip())
        except Exception:
            pass

        sel_w = self.combo_warning.get()
        try:
            warning = int(sel_w.split("-", 1)[0].strip())
        except Exception:
            warning = 0

        boss = bool(self.var_boss.get())
        boss_img_text = self.var_boss_img.get().strip()
        boss_img = boss_img_text if (boss and boss_img_text) else None

        m = dict(base)
        m.update({
            "tag": tag,
            "name": name,
            "img": img,
            "floors": floors,
            "stun": bool(self.var_stun.get()),
            "aggro": aggro_idx,
            "roaming": bool(self.var_roaming.get()),
            "warning": warning,
            "boss": boss,
            "boss_img": boss_img,
        })
        self._sync_skills_amount(m)
        return m

    def _gather_skill_from_form(self) -> Dict[str, Any]:
        name = {
            "ko": self.var_s_ko.get().strip(),
            "en": self.var_s_en.get().strip(),
            "ja": self.var_s_ja.get().strip(),
        }
        if not name["ko"]:
            raise ValueError("스킬 name.ko 는 필수입니다.")
        area_img = self.var_s_area_img.get().strip()
        desc = self.txt_s_desc.get("1.0", tk.END).rstrip("\n")
        try:
            cast = int(self.combo_s_cast.get().split("-", 1)[0].strip())
        except Exception:
            cast = 0
        try:
            size = int(self.combo_s_size.get().split("-", 1)[0].strip())
        except Exception:
            size = 0
        if size not in SIZE_OPTIONS:
            raise ValueError("size는 0/1/2/3/4 중 하나여야 합니다.")
        rush = bool(self.var_s_rush.get())
        link = bool(self.var_s_link.get())
        return {
            "name": name,
            "area_img": area_img,
            "desc": desc,
            "cast": cast,
            "size": size,
            "rush": rush,
            "link": link,
        }

    def _sync_skills_amount(self, monster: Dict[str, Any]):
        monster["skills_Amount"] = len(monster.get("skills", []))

    def _export_data(self) -> Dict[str, List[Dict[str, Any]]]:
        from typing import List as _List, Dict as _Dict  # for type checker only
        # 저장 전 전체 유효성 간단 점검 및 정렬(선택)
        # tag 중복 방지 안내만. 실제 강제 정렬/유니크는 선택 사항
        tags = [m.get("tag") for m in self.monsters]
        if None in tags:
            raise ValueError("모든 몬스터의 tag를 채워주세요.")
        if len(set(tags)) != len(tags):
            raise ValueError("중복된 tag가 있습니다. 고유한 tag를 사용하세요.")
        # ensure skills_Amount sync
        for m in self.monsters:
            self._sync_skills_amount(m)
        return {"monsters": self.monsters}

# -------------- main --------------
if __name__ == "__main__":
    try:
        app = MonstersEditor()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("오류", str(e))
        sys.exit(1)
