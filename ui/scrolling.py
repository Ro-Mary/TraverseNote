import customtkinter as ctk

class ScrollRouter:
    def __init__(self, speed=2.5):
        self.active_canvas = None
        self.default_speed = float(speed)
        self.canvas_speed = {}

    def _bind_widget(self, w, set_active, clear_active):
        if w is None:
            return
        w.bind("<Enter>", set_active, add="+")
        w.bind("<Leave>", clear_active, add="+")
        w.bind("<MouseWheel>", self._on_wheel, add="+")

    def _bind_descendants(self, root, set_active, clear_active):
        try:
            self._bind_widget(root, set_active, clear_active)
            for ch in root.winfo_children():
                self._bind_descendants(ch, set_active, clear_active)
        except Exception:
            pass

    def enable(self, scrollable: ctk.CTkScrollableFrame, speed: float | None = None):
        canvas = scrollable._parent_canvas
        bar = getattr(scrollable, "_scrollbar", None)  # ← 스크롤바 참조
        self.canvas_speed[canvas] = float(speed) if speed is not None else self.default_speed

        # 마우스가 올라간 쪽을 '활성 캔버스'로 지정
        def set_active(_=None, c=canvas): self.active_canvas = c
        def clear_active(_=None): self.active_canvas = None

        # 스크롤 프레임 / 캔버스 / 스크롤바
        for w in (scrollable, canvas, bar):
            self._bind_widget(w, set_active, clear_active)

        # ✅ 현재 존재하는 모든 자식에게도 바인딩 전파
        # (자식은 그때그때 생기므로, 렌더/갱신 이후에 refresh를 한 번 더 호출해 주세요)
        self._bind_descendants(scrollable, set_active, clear_active)

        # refresh용 핸들 저장 (app이 렌더 후 호출)
        scrollable._scrollrouter_refresh = lambda: self._bind_descendants(scrollable, set_active, clear_active)
        return self

    def _set_active(self, canvas):
        self.active_canvas = canvas

    def _on_wheel(self, event):
        #print("wheel!", self.active_canvas)
        c = self.active_canvas
        if not c:
            return  # 활성 없음 → 기본 동작

        speed = self.canvas_speed.get(c, self.default_speed)
        first, _ = c.yview()
        #print("yview:", first, _)

        if getattr(event, "num", None) in (4, 5):
            base = -1.0 if event.num == 4 else 1.0
        else:
            base = -(event.delta / 120.0)

        # 속도 튜닝
        frac = base * 0.03 * speed
        new_first = min(max(first + frac, 0.0), 1.0)
        c.yview_moveto(new_first)
        return "break"   
