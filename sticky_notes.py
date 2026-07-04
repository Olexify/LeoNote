"""
LeoNote — lightweight sticky task app with Obsidian integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, datetime, uuid, ctypes, sys

try:
    import pystray as _pystray
    from PIL import Image as _PILImage
    _TRAY_OK = True
except Exception:
    _TRAY_OK = False

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".leonote_config.json")
TASKS_FILE  = os.path.join(os.path.expanduser("~"), ".leonote_tasks.json")

DEFAULT_CONFIG = {
    "obsidian_note_path": "",
    "always_on_top": True,
    "window_x": 100, "window_y": 100,
    "window_w": 380, "window_h": 600,
    "theme": "peach",
    "show_system_titlebar": False,
    "show_in_tray": False,
    "start_hidden_to_tray": False,
    "show_in_taskbar": False,
    "run_at_startup": False,
    "ui_scale": 1.0,
    "settings_x": None, "settings_y": None,
    "settings_w": 520, "settings_h": 600,
}

THEMES = {
    "yellow": {"bg":"#fff7c2","header_bg":"#f6d860","text":"#3b2f07","muted":"#8a7430","entry_bg":"#fffbe0","entry_fg":"#3b2f07","btn_bg":"#f4cf4d","btn_fg":"#3b2f07","btn_hover":"#eabf20","check_done":"#65a30d","separator":"#efd981","item_bg":"#fffbe6","item_hover":"#fff3bf","tab_bg":"#f8e89b","archive":"#b7791f","close_hover":"#ef4444","low":"#3b82f6","medium":"#f59e0b","high":"#dc2626"},
    "dark": {"bg":"#1c1b19","header_bg":"#27251f","text":"#e7e5e4","muted":"#a8a29e","entry_bg":"#27251f","entry_fg":"#e7e5e4","btn_bg":"#3f3d38","btn_fg":"#e7e5e4","btn_hover":"#4f4c47","check_done":"#4f98a3","separator":"#393836","item_bg":"#201f1d","item_hover":"#2d2c2a","tab_bg":"#2d2c2a","archive":"#d6a547","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "light": {"bg":"#f7f6f2","header_bg":"#f0ede8","text":"#28251d","muted":"#6b7280","entry_bg":"#ffffff","entry_fg":"#28251d","btn_bg":"#e6e4df","btn_fg":"#28251d","btn_hover":"#dcd9d5","check_done":"#437a22","separator":"#dcd9d5","item_bg":"#fafaf8","item_hover":"#f0ede8","tab_bg":"#ece8e1","archive":"#a16207","close_hover":"#ef4444","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "sakura": {"bg":"#ffeef5","header_bg":"#ffc9dd","text":"#4a1f2d","muted":"#8b5d6b","entry_bg":"#fff7fa","entry_fg":"#4a1f2d","btn_bg":"#ffb3cf","btn_fg":"#4a1f2d","btn_hover":"#ff9fc2","check_done":"#22c55e","separator":"#f8b4c9","item_bg":"#fff7fa","item_hover":"#ffe4ef","tab_bg":"#ffe0ec","archive":"#be185d","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "mint": {"bg":"#ecfdf5","header_bg":"#bbf7d0","text":"#16352a","muted":"#4b6b5b","entry_bg":"#f7fffb","entry_fg":"#16352a","btn_bg":"#86efac","btn_fg":"#16352a","btn_hover":"#6ee7b7","check_done":"#16a34a","separator":"#a7f3d0","item_bg":"#f7fffb","item_hover":"#dcfce7","tab_bg":"#d1fae5","archive":"#047857","close_hover":"#ef4444","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "ocean": {"bg":"#eff6ff","header_bg":"#bfdbfe","text":"#132c52","muted":"#5b6f92","entry_bg":"#f8fbff","entry_fg":"#132c52","btn_bg":"#93c5fd","btn_fg":"#132c52","btn_hover":"#60a5fa","check_done":"#2563eb","separator":"#bfdbfe","item_bg":"#f8fbff","item_hover":"#dbeafe","tab_bg":"#dbeafe","archive":"#1d4ed8","close_hover":"#ef4444","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "rose": {"bg":"#fff1f2","header_bg":"#fecdd3","text":"#4a1d24","muted":"#8f5b66","entry_bg":"#fff8f8","entry_fg":"#4a1d24","btn_bg":"#fda4af","btn_fg":"#4a1d24","btn_hover":"#fb7185","check_done":"#16a34a","separator":"#fecdd3","item_bg":"#fff8f8","item_hover":"#ffe4e6","tab_bg":"#ffe4e6","archive":"#be123c","close_hover":"#e11d48","low":"#60a5fa","medium":"#f59e0b","high":"#dc2626"},
    "lavender": {"bg":"#faf5ff","header_bg":"#e9d5ff","text":"#35214f","muted":"#7c6a97","entry_bg":"#fdfaff","entry_fg":"#35214f","btn_bg":"#d8b4fe","btn_fg":"#35214f","btn_hover":"#c084fc","check_done":"#22c55e","separator":"#e9d5ff","item_bg":"#fdfaff","item_hover":"#f3e8ff","tab_bg":"#f3e8ff","archive":"#7e22ce","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "peach": {"bg":"#fff7ed","header_bg":"#fed7aa","text":"#4a2b18","muted":"#916a4e","entry_bg":"#fffaf5","entry_fg":"#4a2b18","btn_bg":"#fdba74","btn_fg":"#4a2b18","btn_hover":"#fb923c","check_done":"#16a34a","separator":"#fed7aa","item_bg":"#fffaf5","item_hover":"#ffedd5","tab_bg":"#ffedd5","archive":"#c2410c","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "sky": {"bg":"#f0f9ff","header_bg":"#bae6fd","text":"#0f2f4a","muted":"#5f7f9a","entry_bg":"#f8fcff","entry_fg":"#0f2f4a","btn_bg":"#7dd3fc","btn_fg":"#0f2f4a","btn_hover":"#38bdf8","check_done":"#0284c7","separator":"#bae6fd","item_bg":"#f8fcff","item_hover":"#e0f2fe","tab_bg":"#e0f2fe","archive":"#0369a1","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "slate": {"bg":"#f8fafc","header_bg":"#cbd5e1","text":"#1e293b","muted":"#64748b","entry_bg":"#ffffff","entry_fg":"#1e293b","btn_bg":"#cbd5e1","btn_fg":"#1e293b","btn_hover":"#94a3b8","check_done":"#22c55e","separator":"#cbd5e1","item_bg":"#ffffff","item_hover":"#f1f5f9","tab_bg":"#e2e8f0","archive":"#334155","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "fire": {"bg":"#fff5f3","header_bg":"#fca5a5","text":"#4a1c14","muted":"#946057","entry_bg":"#fffaf9","entry_fg":"#4a1c14","btn_bg":"#fb7185","btn_fg":"#4a1c14","btn_hover":"#ef4444","check_done":"#16a34a","separator":"#fecaca","item_bg":"#fffaf9","item_hover":"#ffe4e6","tab_bg":"#ffe4e6","archive":"#b91c1c","close_hover":"#dc2626","low":"#2563eb","medium":"#f59e0b","high":"#dc2626"},
    "sand": {"bg":"#fff8ed","header_bg":"#f5d7a1","text":"#4a3720","muted":"#8b7355","entry_bg":"#fffdf8","entry_fg":"#4a3720","btn_bg":"#e9c46a","btn_fg":"#4a3720","btn_hover":"#ddb85a","check_done":"#65a30d","separator":"#efdfbf","item_bg":"#fffdf8","item_hover":"#fbf1dc","tab_bg":"#f7ebd0","archive":"#b7791f","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "island": {"bg":"#eefcf7","header_bg":"#9fe3cf","text":"#133a33","muted":"#5d7f77","entry_bg":"#f8fffc","entry_fg":"#133a33","btn_bg":"#67d4b7","btn_fg":"#133a33","btn_hover":"#34caa0","check_done":"#0f9f6e","separator":"#bfeee0","item_bg":"#f8fffc","item_hover":"#def8ef","tab_bg":"#d8f4eb","archive":"#0f766e","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "crimson": {"bg":"#1a0f12","header_bg":"#3a161d","text":"#f7d7db","muted":"#b48a91","entry_bg":"#221317","entry_fg":"#f7d7db","btn_bg":"#5b1f2b","btn_fg":"#f7d7db","btn_hover":"#7a2434","check_done":"#22c55e","separator":"#3a161d","item_bg":"#211417","item_hover":"#2a181d","tab_bg":"#2a181d","archive":"#f87171","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "forest": {"bg":"#0d1711","header_bg":"#183323","text":"#d8f3df","muted":"#8cb09a","entry_bg":"#132018","entry_fg":"#d8f3df","btn_bg":"#235336","btn_fg":"#d8f3df","btn_hover":"#2f6a45","check_done":"#22c55e","separator":"#183323","item_bg":"#122019","item_hover":"#17281f","tab_bg":"#17281f","archive":"#86efac","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "emerald": {"bg":"#071a17","header_bg":"#0d3b35","text":"#d5fff5","muted":"#7cb6aa","entry_bg":"#0b2521","entry_fg":"#d5fff5","btn_bg":"#0f5b50","btn_fg":"#d5fff5","btn_hover":"#147768","check_done":"#10b981","separator":"#0d3b35","item_bg":"#0b2521","item_hover":"#10302b","tab_bg":"#10302b","archive":"#5eead4","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "midnight": {"bg":"#0b1220","header_bg":"#16233a","text":"#dbeafe","muted":"#7f93b0","entry_bg":"#10192b","entry_fg":"#dbeafe","btn_bg":"#1d4e89","btn_fg":"#dbeafe","btn_hover":"#2563eb","check_done":"#38bdf8","separator":"#16233a","item_bg":"#0f1a2e","item_hover":"#14213a","tab_bg":"#14213a","archive":"#60a5fa","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "space": {"bg":"#09090f","header_bg":"#171726","text":"#ececff","muted":"#8f90ae","entry_bg":"#10101b","entry_fg":"#ececff","btn_bg":"#27273d","btn_fg":"#ececff","btn_hover":"#343452","check_done":"#7dd3fc","separator":"#171726","item_bg":"#10101b","item_hover":"#171726","tab_bg":"#171726","archive":"#c4b5fd","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "violet-night": {"bg":"#120b1f","header_bg":"#24123a","text":"#f1e7ff","muted":"#a38cbf","entry_bg":"#1a102a","entry_fg":"#f1e7ff","btn_bg":"#4c1d95","btn_fg":"#f1e7ff","btn_hover":"#6d28d9","check_done":"#22c55e","separator":"#24123a","item_bg":"#1a102a","item_hover":"#221434","tab_bg":"#221434","archive":"#c084fc","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "eclipse": {"bg":"#0a0a0a","header_bg":"#1a1a1a","text":"#f2f2f2","muted":"#8a8a8a","entry_bg":"#111111","entry_fg":"#f2f2f2","btn_bg":"#2a2a2a","btn_fg":"#f2f2f2","btn_hover":"#3a3a3a","check_done":"#9ca3af","separator":"#1a1a1a","item_bg":"#111111","item_hover":"#181818","tab_bg":"#181818","archive":"#d4d4d8","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"}
}
PRIORITIES = ["none","low","medium","high"]
OPEN_SEP = "<!-- OPEN_TASKS -->"
CLOSED_SEP = "<!-- CLOSED_TASKS -->"
TRASH_HOURS = 24


def enable_high_dpi():
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except Exception: pass

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE,"r",encoding="utf-8") as f: data=json.load(f)
            cfg=DEFAULT_CONFIG.copy(); cfg.update(data); return cfg
        except Exception: pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(cfg,f,indent=2,ensure_ascii=False)

def _norm(t):
    t.setdefault("id", str(uuid.uuid4()))
    t.setdefault("done", False)
    t.setdefault("created", datetime.datetime.now().isoformat(timespec="seconds"))
    t.setdefault("priority","none")
    t.setdefault("subtasks",[])
    t.setdefault("deleted", False)
    return t

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE,"r",encoding="utf-8") as f: return [_norm(t) for t in json.load(f)]
        except Exception: pass
    return []

def save_tasks(tasks):
    with open(TASKS_FILE,"w",encoding="utf-8") as f: json.dump(tasks,f,indent=2,ensure_ascii=False)

def now_dt(): return datetime.datetime.now()
def parse_iso(s): return datetime.datetime.fromisoformat(s)
def fmt_dt(dt): return dt.strftime("%d.%m.%y %H:%M")

def ensure_parent(path):
    d=os.path.dirname(path)
    if d: os.makedirs(d,exist_ok=True)

def subtasks_inline(task):
    sts = task.get("subtasks", [])
    if not sts: return ""
    parts = []
    for st in sts:
        mark = "x" if st.get("done") else " "
        txt = st.get("text", "").replace("\n", " ").strip()
        if txt:
            parts.append(f"[{mark}] {txt}")
    return f" <sub>· {' ; '.join(parts)}</sub>" if parts else ""

def _read_note(path):
    if not path or not os.path.exists(path): return []
    with open(path,"r",encoding="utf-8") as f: return f.read().splitlines()

def _write_note(path, lines):
    ensure_parent(path)
    with open(path,"w",encoding="utf-8") as f: f.write("\n".join(lines).rstrip()+"\n")

def _ensure_note(path):
    if not path: return
    ensure_parent(path)
    if not os.path.exists(path):
        _write_note(path,[OPEN_SEP,"",CLOSED_SEP,""])

def _task_line(task):
    tid=task["id"]; txt=task["text"].replace("\n"," ").strip(); subs = subtasks_inline(task)
    c=fmt_dt(parse_iso(task["created"]))
    if task.get("done"):
        s=fmt_dt(parse_iso(task["completed_at"]))
        return f"=={{green}} **{txt}** <sub>closed · {s}</sub>{subs}== sn:{tid}"
    return f"=={{accent}} **{txt}** <sub>open · created {c}</sub>{subs}== sn:{tid}"

def _remove_task_lines(lines, tid):
    return [l for l in lines if f"sn:{tid}" not in l]

def sync_note(path, task):
    if not path or task.get("deleted"): return
    _ensure_note(path)
    lines = _remove_task_lines(_read_note(path), task["id"])
    new_line = _task_line(task)
    if task.get("done"):
        idx = lines.index(CLOSED_SEP) if CLOSED_SEP in lines else len(lines)
        if CLOSED_SEP not in lines: lines.append(CLOSED_SEP)
        lines.insert(idx+1, new_line)
    else:
        idx = lines.index(OPEN_SEP) if OPEN_SEP in lines else 0
        if OPEN_SEP not in lines: lines.insert(0, OPEN_SEP); idx = 0
        lines.insert(idx+1, new_line)
    _write_note(path, lines)

def remove_from_note(path, tid):
    if not path or not os.path.exists(path): return
    _write_note(path, _remove_task_lines(_read_note(path), tid))


class App:
    def __init__(self):
        enable_high_dpi()
        self.cfg   = load_config()
        self.cfg.setdefault("start_hidden_to_tray", False)
        self.cfg.setdefault("show_in_taskbar", False)
        self.tasks = load_tasks()
        self._purge_old_trash()
        self.current_tab = "active"
        self.search_var = None
        self._drag_x = self._drag_y = 0
        self._restore_geo = None
        self._tray_icon  = None
        self._resize_edge = self._resize_start = None
        self._is_maximized = False
        self._settings_win = None
        self._settings_widgets = {}
        self._pin_btn = None

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("LeoNote")
        self.root.minsize(300,380)
        self._apply_scale()
        self._apply_icon()
        self.root.geometry(f"{self.cfg['window_w']}x{self.cfg['window_h']}+{self.cfg['window_x']}+{self.cfg['window_y']}")
        self.root.attributes("-topmost", self.cfg["always_on_top"])
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.bind("<Configure>", self._on_configure)
        self.root.bind("<Map>", self._on_map)
        self.T = THEMES[self.cfg["theme"]]
        self.search_var = tk.StringVar(master=self.root)
        self._apply_window_mode(first=True)
        self._build_ui()

        if self.cfg.get("show_in_tray"): self._setup_tray()
        if self.cfg.get("start_hidden_to_tray") and self.cfg.get("show_in_tray"):
            self.root.after(50, self.root.withdraw)
        else:
            self.root.deiconify()

    def _purge_old_trash(self):
        now = now_dt()
        kept = []
        changed = False
        for t in self.tasks:
            if t.get("deleted") and t.get("deleted_at"):
                age = now - parse_iso(t["deleted_at"])
                if age > datetime.timedelta(hours=TRASH_HOURS):
                    changed = True
                    continue
            kept.append(t)
        if changed:
            self.tasks = kept
            save_tasks(self.tasks)

    def _apply_icon(self):
        for name in ("icon.png","icon.ico"):
            pth = resource_path(name)
            if not os.path.exists(pth): continue
            try:
                if name.endswith(".png"):
                    img = tk.PhotoImage(file=pth)
                    self._icon_img = img
                    try:
                        w, h = img.width(), img.height()
                        max_side = 28
                        scale = max(1, int(max(w, h) / max_side)) if max(w, h) > max_side else 1
                        self._header_icon_img = img.subsample(scale, scale) if scale > 1 else img
                    except Exception:
                        self._header_icon_img = img
                    self.root.iconphoto(True, img)
                else:
                    self.root.iconbitmap(pth)
                return
            except Exception:
                continue

    def _apply_scale(self):
        s = max(0.5, min(3.0, float(self.cfg.get("ui_scale",1.0))))
        self.root.tk.call("tk","scaling", 1.25*s)

    def _set_scale(self, s):
        self.cfg["ui_scale"] = round(max(0.5,min(3.0,float(s))),2)
        save_config(self.cfg)
        self._apply_scale()
        self._retheme_main_only()

    def _custom_chrome_on(self):
        return not bool(self.cfg.get("show_system_titlebar",False)) and not bool(self.cfg.get("show_in_taskbar",False))

    def _apply_window_mode(self, first=False):
        self.root.overrideredirect(self._custom_chrome_on())
        if not first:
            self.root.update_idletasks()
        self.root.after(20, self._bind_resize)

    def _bind_resize(self):
        self.root.bind("<Motion>", self._resize_cursor)
        self.root.bind("<ButtonPress-1>", self._resize_start_cb, add="+")
        self.root.bind("<B1-Motion>", self._resize_do, add="+")
        self.root.bind("<ButtonRelease-1>", self._resize_stop, add="+")

    def _on_map(self, e=None):
        if self.root.state() != "iconic":
            self.root.after(30, lambda: self.root.overrideredirect(self._custom_chrome_on()))
            self.root.after(50, lambda: self.root.attributes("-topmost", self.cfg.get("always_on_top",True)))

    def _setup_tray(self):
        if not _TRAY_OK or self._tray_icon: return
        pth = resource_path("icon.png")
        if not os.path.exists(pth): return
        try:
            img = _PILImage.open(pth)
            menu = _pystray.Menu(
                _pystray.MenuItem("Show",  self._tray_show, default=True),
                _pystray.MenuItem("Hide",  lambda icon,item: self.root.after(0, self.root.withdraw)),
                _pystray.MenuItem("Exit",  lambda icon,item: self.root.after(0, self._close)),
            )
            self._tray_icon = _pystray.Icon("LeoNote", img, "LeoNote", menu)
            import threading
            threading.Thread(target=self._tray_icon.run, daemon=True).start()
        except Exception:
            self._tray_icon = None

    def _tray_show(self, icon=None, item=None):
        self.root.after(0, self._show_from_tray)

    def _show_from_tray(self):
        try: self.root.overrideredirect(self._custom_chrome_on())
        except Exception: pass
        self.root.deiconify()
        self.root.state("normal")
        self.root.after(30, lambda: (self.root.lift(), self.root.attributes("-topmost", self.cfg.get("always_on_top",True)), self.root.focus_force()))

    def _destroy_tray(self):
        if self._tray_icon:
            try: self._tray_icon.stop()
            except Exception: pass
            self._tray_icon = None

    def _apply_scrollbar_style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        T = self.T
        style.layout("LeSticky.Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
        style.configure("LeSticky.Vertical.TScrollbar", background=T["separator"], troughcolor=T["bg"], bordercolor=T["bg"], darkcolor=T["bg"], lightcolor=T["bg"], arrowcolor=T["bg"], relief="flat", borderwidth=0, arrowsize=1, width=4)
        style.map("LeSticky.Vertical.TScrollbar", background=[("active", T["muted"]), ("!active", T["separator"])])

    def _build_ui(self):
        self._apply_scrollbar_style()
        for w in self.root.winfo_children(): w.destroy()
        self._pin_btn = None
        self.root.configure(bg=self.T["separator"])
        outer = tk.Frame(self.root, bg=self.T["separator"]); outer.pack(fill="both",expand=True)
        self.main = tk.Frame(outer, bg=self.T["bg"]); self.main.pack(fill="both",expand=True,padx=1,pady=1)
        self._build_titlebar()

        tabs_row = tk.Frame(self.main, bg=self.T["tab_bg"]); tabs_row.pack(fill="x")
        self._tab_tasks = self._mktab(tabs_row,"Tasks",lambda:self._set_tab("active"))
        self._tab_archive = self._mktab(tabs_row,"Archive",lambda:self._set_tab("archive"))
        self._tab_bin = self._mktab(tabs_row,"🗑",lambda:self._set_tab("trash"), compact=True)
        self._tab_search = self._mktab(tabs_row,"🔍",lambda:self._set_tab("search"), compact=True)
        self._refresh_tabs()

        self.top_input_host = tk.Frame(self.main, bg=self.T["bg"])
        self.top_input_host.pack(fill="x")

        self.entry_area = tk.Frame(self.top_input_host, bg=self.T["bg"], pady=6, padx=6)
        self.entry_area.pack(fill="x")
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.entry_area,textvariable=self.entry_var,bg=self.T["entry_bg"],fg=self.T["entry_fg"],insertbackground=self.T["entry_fg"],relief="flat",font=("Segoe UI Variable",11),bd=0,highlightthickness=1,highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
        self.entry.pack(side="left",fill="x",expand=True,ipady=6,padx=(0,4))
        self.entry.bind("<Return>", self._add_task)
        self.entry.bind("<Control-MouseWheel>", self._ctrl_scroll)
        self.add_btn = tk.Button(self.entry_area,text="Add",command=self._add_task,bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",font=("Segoe UI Variable",10,"bold"),padx=12,pady=6,cursor="hand2",activebackground=self.T["btn_hover"])
        self.add_btn.pack(side="right")

        self.search_area = tk.Frame(self.top_input_host, bg=self.T["bg"], pady=6, padx=6)
        self.search_entry = tk.Entry(self.search_area,textvariable=self.search_var,bg=self.T["entry_bg"],fg=self.T["entry_fg"],insertbackground=self.T["entry_fg"],relief="flat",font=("Segoe UI Variable",11),bd=0,highlightthickness=1,highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
        self.search_entry.pack(side="left",fill="x",expand=True,ipady=6,padx=(0,4))
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_tasks())
        tk.Button(self.search_area,text="Clear",command=lambda:(self.search_var.set(""), self._render_tasks()),bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",font=("Segoe UI Variable",10),padx=10,pady=6,cursor="hand2",activebackground=self.T["btn_hover"]).pack(side="right")

        lf = tk.Frame(self.main,bg=self.T["bg"]); lf.pack(fill="both",expand=True,padx=6,pady=(0,6))
        self.canvas = tk.Canvas(lf,bg=self.T["bg"],bd=0,highlightthickness=0)
        sb = ttk.Scrollbar(lf,orient="vertical",command=self.canvas.yview, style="LeSticky.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y")
        self.canvas.pack(side="left",fill="both",expand=True)
        self.task_frame = tk.Frame(self.canvas,bg=self.T["bg"])
        self._cw = self.canvas.create_window((0,0),window=self.task_frame,anchor="nw")
        self.task_frame.bind("<Configure>", lambda e: self._update_scroll())
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._cw,width=e.width))
        for w in (self.canvas,self.task_frame):
            w.bind("<MouseWheel>", self._scroll)
            w.bind("<Button-4>", self._scroll)
            w.bind("<Button-5>", self._scroll)
            w.bind("<Control-MouseWheel>", self._ctrl_scroll)
        # Bind scroll on root to always reach canvas
        self.root.bind("<MouseWheel>", self._scroll, add="+")
        self.root.bind("<Button-4>", self._scroll, add="+")
        self.root.bind("<Button-5>", self._scroll, add="+")

        tk.Frame(self.main,bg=self.T["separator"],height=1).pack(fill="x")
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(self.main,textvariable=self.status_var,bg=self.T["header_bg"],fg=self.T["text"],font=("Segoe UI Variable",8),anchor="w",padx=8,pady=4)
        self.status_lbl.pack(fill="x")
        self._render_tasks()
        self.root.after(50, lambda: self._bind_ctrl_wheel_recursive(self.main))

    def _bind_ctrl_wheel_recursive(self, widget):
        for seq in ("<Control-MouseWheel>", "<Control-Button-4>", "<Control-Button-5>"):
            try: widget.bind(seq, self._ctrl_scroll, add="+")
            except Exception: pass
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try: widget.bind(seq, self._scroll, add="+")
            except Exception: pass
        for child in widget.winfo_children():
            self._bind_ctrl_wheel_recursive(child)

    def _retheme_main_only(self):
        self.T = THEMES[self.cfg["theme"]]
        old_tab = self.current_tab
        self._build_ui()
        self.current_tab = old_tab
        self._refresh_tabs()
        self._render_tasks()
        self._restyle_settings_window()

    def _restyle_settings_window(self):
        if not (self._settings_win and self._settings_win.winfo_exists()):
            return
        self._settings_win.configure(bg=self.T["bg"])
        for kind, items in self._settings_widgets.items():
            for w in items:
                try:
                    if kind == "frame_bg": w.configure(bg=self.T["bg"])
                    elif kind == "section": w.configure(bg=self.T["header_bg"], fg=self.T["text"])
                    elif kind == "label": w.configure(bg=self.T["bg"], fg=self.T["text"])
                    elif kind == "muted": w.configure(bg=self.T["bg"], fg=self.T["muted"])
                    elif kind == "entry": w.configure(bg=self.T["entry_bg"], fg=self.T["entry_fg"], insertbackground=self.T["entry_fg"], highlightbackground=self.T["separator"], highlightcolor=self.T["check_done"])
                    elif kind == "button": w.configure(bg=self.T["btn_bg"], fg=self.T["btn_fg"], activebackground=self.T["btn_hover"])
                    elif kind == "check": w.configure(bg=self.T["bg"], fg=self.T["text"], activebackground=self.T["bg"], selectcolor=self.T["entry_bg"])
                    elif kind == "radio": w.configure(bg=self.T["bg"], fg=self.T["text"], activebackground=self.T["bg"], selectcolor=self.T["entry_bg"])
                    elif kind == "scale": w.configure(bg=self.T["bg"], fg=self.T["text"], troughcolor=self.T["separator"], activebackground=self.T["btn_hover"])
                    elif kind == "swatch":
                        pass
                except Exception:
                    pass

    def _soft_pin_color(self):
        darkish = {"dark", "crimson", "forest", "emerald", "midnight", "space", "violet-night", "eclipse"}
        visible_light = {"ocean", "rose", "lavender", "peach", "sky", "slate", "fire", "sand", "island", "yellow"}
        name = self.cfg.get("theme")
        if name in darkish:
            return self.T["btn_hover"]
        if name in visible_light:
            return self.T["btn_bg"]
        return self.T["separator"]

    def _build_titlebar(self):
        T = self.T
        hdr = tk.Frame(self.main,bg=T["header_bg"],cursor="fleur"); hdr.pack(fill="x",side="top")
        for ev,cb in (("<ButtonPress-1>",self._drag_start),("<B1-Motion>",self._drag_do),("<Double-Button-1>",lambda e:self._toggle_maximize())):
            hdr.bind(ev,cb)
        if hasattr(self, "_header_icon_img"):
            il = tk.Label(hdr,image=self._header_icon_img,bg=T["header_bg"])
            il.pack(side="left",padx=(8,4),pady=4)
            for ev,cb in (("<ButtonPress-1>",self._drag_start),("<B1-Motion>",self._drag_do),("<Double-Button-1>",lambda e:self._toggle_maximize())):
                il.bind(ev,cb)
        lbl = tk.Label(hdr,text="LeoNote",bg=T["header_bg"],fg=T["text"],font=("Segoe UI Variable",11,"bold"),padx=6,pady=8)
        lbl.pack(side="left")
        for ev,cb in (("<ButtonPress-1>",self._drag_start),("<B1-Motion>",self._drag_do),("<Double-Button-1>",lambda e:self._toggle_maximize())):
            lbl.bind(ev,cb)
        bf = tk.Frame(hdr,bg=T["header_bg"]); bf.pack(side="right",padx=4)
        def hbtn(text, cmd, red=False):
            b = tk.Button(bf,text=text,command=cmd,bg=T["header_bg"],fg=T["text"],relief="flat",font=("Segoe UI Variable",10),padx=9,pady=5,cursor="hand2",bd=0,activeforeground=T["btn_fg"],activebackground=T["close_hover"] if red else T["btn_hover"])
            b.pack(side="right")
            def leave(_e): b.configure(bg=self._soft_pin_color() if (b is self._pin_btn and self.cfg.get("always_on_top")) else T["header_bg"])
            b.bind("<Enter>", lambda e: b.configure(bg=T["close_hover"] if red else T["btn_hover"]))
            b.bind("<Leave>", leave)
            return b
        hbtn("⚙", self._open_settings)
        hbtn("✕", self._close, red=True)
        hbtn("□", self._toggle_maximize)
        hbtn("─", self._minimize)
        self._pin_btn = hbtn("📌", self._toggle_topmost)
        self._refresh_pin()
        tk.Frame(self.main,bg=T["separator"],height=1).pack(fill="x")

    def _refresh_pin(self):
        if self._pin_btn:
            self._pin_btn.configure(bg=self._soft_pin_color() if self.cfg.get("always_on_top") else self.T["header_bg"])

    def _trash_items(self):
        return [t for t in self.tasks if t.get("deleted")]

    def _mktab(self, parent, text, cmd, compact=False):
        T = self.T
        b = tk.Button(parent,text=text,command=cmd,bg=T["tab_bg"],fg=T["text"],relief="flat",bd=0,padx=8 if compact else 12,pady=5,cursor="hand2",font=("Segoe UI Variable",9,"bold"),activebackground=T["btn_hover"])
        b.pack(side="left",padx=(6,0),pady=4)
        return b

    def _refresh_tabs(self):
        T = self.T
        for tab, name in ((self._tab_tasks,"active"),(self._tab_archive,"archive"),(self._tab_search,"search")):
            tab.configure(bg=T["btn_bg"] if self.current_tab==name else T["tab_bg"], fg=T["text"])
        if self._trash_items():
            self._tab_bin.pack(side="left",padx=(6,0),pady=4)
            self._tab_bin.configure(bg=T["btn_bg"] if self.current_tab=="trash" else T["tab_bg"], fg=T["text"])
        else:
            self._tab_bin.pack_forget()
            if self.current_tab == "trash":
                self.current_tab = "active"
        if hasattr(self, "entry_area") and self.entry_area.winfo_exists():
            self.entry_area.pack_forget()
        if hasattr(self, "search_area") and self.search_area.winfo_exists():
            self.search_area.pack_forget()
        if self.current_tab == "search":
            if hasattr(self, "search_area") and self.search_area.winfo_exists():
                self.search_area.pack(fill="x")
            if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
                self.root.after(10, self.search_entry.focus_set)
        else:
            if hasattr(self, "entry_area") and self.entry_area.winfo_exists():
                self.entry_area.pack(fill="x")

    def _set_tab(self, name):
        self.current_tab = name
        self._refresh_tabs()
        self.entry.configure(state="normal" if name=="active" else "disabled")
        self._render_tasks()

    def _update_scroll(self): self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def _scroll(self, e):
        if getattr(e,'num',None)==4: d=-1
        elif getattr(e,'num',None)==5: d=1
        else:
            delta = getattr(e,'delta',0)
            d = -1 if delta>0 else (1 if delta<0 else 0)
        if d == 0: return "break"
        top,_ = self.canvas.yview()
        if d < 0 and top <= 0:
            self.canvas.yview_moveto(0.0)
            return "break"
        self.canvas.yview_scroll(d,"units")
        top,_ = self.canvas.yview()
        if top < 0:
            self.canvas.yview_moveto(0.0)
        return "break"
    def _ctrl_scroll(self, e): self._set_scale(self.cfg.get("ui_scale",1.0) + (0.05 if ((getattr(e,"num",None)==4) or getattr(e,"delta",0)>0) else -0.05))

    def _active_tasks(self):
        now = now_dt()
        return [t for t in self.tasks if not t.get("deleted") and not (t.get("done") and t.get("completed_at") and now - parse_iso(t["completed_at"]) > datetime.timedelta(days=1))]
    def _archived_tasks(self):
        now = now_dt()
        return [t for t in self.tasks if not t.get("deleted") and t.get("done") and t.get("completed_at") and now - parse_iso(t["completed_at"]) > datetime.timedelta(days=1)]

    def _search_pool(self):
        q = self.search_var.get().strip().lower()
        if not q: return [t for t in self.tasks if not t.get("deleted")]
        out = []
        for t in self.tasks:
            if t.get("deleted"): continue
            blob = [t.get("text",""), t.get("priority","")]
            blob += [s.get("text","") for s in t.get("subtasks",[])]
            hay = " ".join(blob).lower()
            if q in hay: out.append(t)
        return out

    def _render_tasks(self):
        for w in self.task_frame.winfo_children(): w.destroy()
        self._purge_old_trash()
        T = self.T
        if self.current_tab=="active":
            pool = self._active_tasks()
        elif self.current_tab=="archive":
            pool = sorted(self._archived_tasks(),key=lambda t:t.get("completed_at",""),reverse=True)
        elif self.current_tab=="trash":
            pool = sorted(self._trash_items(),key=lambda t:t.get("deleted_at",""),reverse=True)
        else:
            pool = self._search_pool()
        if not pool:
            msg = "No tasks yet.\nAdd one above ↑" if self.current_tab=="active" else ("Archive is empty." if self.current_tab=="archive" else ("Bin is empty." if self.current_tab=="trash" else "No search results."))
            tk.Label(self.task_frame,text=msg,bg=T["bg"],fg=T["muted"],font=("Segoe UI Variable",10),justify="center",pady=28).pack(fill="x")
        else:
            for task in pool:
                self._task_row(task, archived=(self.current_tab=="archive"), trashed=(self.current_tab=="trash"), searching=(self.current_tab=="search"))
        # Bottom overscroll spacer
        tk.Frame(self.task_frame, bg=self.T["bg"], height=60).pack(fill="x")
        self._update_scroll()
        self._refresh_tabs()
        open_count = len([t for t in self.tasks if not t.get("deleted") and not t.get("done")])
        archive_count = len(self._archived_tasks())
        parts = [f"Tasks: {open_count}", f"Archive: {archive_count}"]
        trash_count = len(self._trash_items())
        if trash_count:
            parts.append(f"Trash: {trash_count}")
        self.status_var.set(" · ".join(parts))

    def _task_row(self, task, archived=False, trashed=False, searching=False):
        T = self.T
        row = tk.Frame(self.task_frame,bg=T["item_bg"],pady=3,padx=4); row.pack(fill="x",pady=2)
        row._task_ref = task
        action_buttons = []
        def paint(bg):
            for w in (row, tw, lbl, meta):
                try: w.configure(bg=bg)
                except Exception: pass
            for b in action_buttons:
                try: b.configure(bg=bg)
                except Exception: pass
            if drag_lbl: drag_lbl.configure(bg=bg)
        row.bind("<Enter>", lambda e: paint(T["item_hover"]))
        row.bind("<Leave>", lambda e: paint(T["item_bg"]))

        pri = task.get("priority","none")
        pri_color = T.get(pri, T["separator"]) if pri != "none" else T["separator"]
        tk.Frame(row,bg=pri_color,width=5).pack(side="left",fill="y",padx=(0,4))

        drag_lbl = None
        if not archived and not trashed and not searching:
            drag_lbl = tk.Label(row,text="⋮⋮",bg=T["item_bg"],fg=T["muted"],font=("Segoe UI Variable",9),cursor="fleur",width=2)
            drag_lbl.pack(side="left",padx=(0,2))
            drag_lbl.bind("<ButtonPress-1>", lambda e,t=task: self._dt_start(t))
            drag_lbl.bind("<ButtonRelease-1>", lambda e,t=task: self._dt_drop(e,t))

        is_done = task.get("done",False)
        var = tk.BooleanVar(value=is_done)
        chk = tk.Checkbutton(row,variable=var,bg=T["item_bg"],activebackground=T["item_bg"],selectcolor=T["check_done"] if is_done else T["item_bg"],relief="flat",bd=0,highlightthickness=0,state="disabled" if (archived or trashed or searching) else "normal",command=lambda v=var,t=task: self._toggle(t,v))
        chk.pack(side="left",padx=(2,4))

        style = ("Segoe UI Variable",10,"overstrike") if is_done else ("Segoe UI Variable",10)
        fg = T["muted"] if is_done else T["text"]
        tw = tk.Frame(row,bg=T["item_bg"]); tw.pack(side="left",fill="x",expand=True)
        lbl = tk.Label(tw,text=task["text"],bg=T["item_bg"],fg=fg,font=style,anchor="w",wraplength=210,justify="left")
        lbl.pack(anchor="w")
        if not archived and not trashed and not searching:
            lbl.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._inline_edit_task(p,l,t))
            tw.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._body_dblclick(e,p,l,t))
            row.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._body_dblclick(e,p,l,t))

        for st in task.get("subtasks",[]):
            sf = tk.Frame(tw,bg=T["item_bg"]); sf.pack(anchor="w",fill="x")
            sv = tk.BooleanVar(value=st.get("done",False))
            sc = tk.Checkbutton(sf,variable=sv,bg=T["item_bg"],activebackground=T["item_bg"],selectcolor=T["check_done"] if st.get("done") else T["item_bg"],relief="flat",bd=0,highlightthickness=0,state="disabled" if (archived or trashed or searching) else "normal",command=lambda sv=sv,sub=st,ta=task: self._toggle_subtask(ta,sub,sv))
            sc.pack(side="left")
            sl = tk.Label(sf,text=st.get("text",""),bg=T["item_bg"],fg=T["muted"],font=("Segoe UI Variable",8,"overstrike" if st.get("done") else "normal"),anchor="w",justify="left")
            sl.pack(side="left",anchor="w")
            if not archived and not trashed and not searching:
                sl.bind("<Double-Button-1>", lambda e,parent=sf,lab=sl,ta=task,sub=st: self._inline_edit_subtask(parent,lab,ta,sub))
            if st.get("_editing") and not archived and not trashed and not searching:
                self.root.after(10, lambda parent=sf,lab=sl,ta=task,sub=st: self._inline_edit_subtask(parent,lab,ta,sub))

        dt = parse_iso(task["completed_at"]) if is_done and task.get("completed_at") else parse_iso(task["created"])
        meta_txt = (f"Resolved {fmt_dt(dt)}" if is_done and task.get("completed_at") else f"Created {fmt_dt(dt)}")
        if pri != "none": meta_txt += f" · {pri.capitalize()}"
        if trashed and task.get("deleted_at"):
            remain = max(0, int((datetime.timedelta(hours=TRASH_HOURS) - (now_dt() - parse_iso(task["deleted_at"]))).total_seconds() // 3600))
            meta_txt += f" · in bin ~{remain}h left"
        meta = tk.Label(tw,text=meta_txt,bg=T["item_bg"],fg=T["archive"] if archived else T["muted"],font=("Segoe UI Variable",8),anchor="w")
        meta.pack(anchor="w")

        def mk_btn(txt, cmd_fn):
            b = tk.Button(row,text=txt,command=cmd_fn,bg=T["item_bg"],fg=T["text"],relief="flat",bd=0,padx=4,pady=0,font=("Segoe UI Variable",9),cursor="hand2",activebackground=T["item_hover"])
            b.pack(side="right"); action_buttons.append(b); return b
        if trashed:
            mk_btn("↺", lambda t=task: self._recover_task(t))
            mk_btn("🗑", lambda t=task: self._delete_forever(t))
        elif not archived and not searching:
            mk_btn("🗑", lambda t=task: self._trash_task(t))
            mk_btn("⊞", lambda t=task: self._add_subtask(t))
            mk_btn("!", lambda t=task: self._cycle_priority(t))
            mk_btn("✎", lambda t=task,p=tw,l=lbl: self._inline_edit_task(p,l,t))

    def _dt_start(self, t): self._dragging_task = t
    def _dt_drop(self, e, src):
        w = e.widget.winfo_containing(e.x_root, e.y_root); tgt = None
        while w:
            if getattr(w,"_task_ref",None): tgt = w._task_ref; break
            w = getattr(w,"master",None)
        if tgt and tgt is not src:
            fi,ti = self.tasks.index(src), self.tasks.index(tgt)
            self.tasks.pop(fi); self.tasks.insert(max(0,ti if fi>ti else ti-1), src)
            save_tasks(self.tasks)
        self._render_tasks()

    def _body_dblclick(self, e, parent, label, task):
        if e.widget.winfo_class() in ("Checkbutton","Button","Entry"): return
        self._inline_edit_task(parent,label,task)

    def _inline_edit_task(self, parent, label, task):
        entry = tk.Entry(parent,bg=self.T["entry_bg"],fg=self.T["entry_fg"],insertbackground=self.T["entry_fg"],relief="flat",font=("Segoe UI Variable",10))
        entry.insert(0, task.get("text",""))
        label.pack_forget(); entry.pack(anchor="w",fill="x")
        entry.focus_set(); entry.select_range(0,"end")
        def finish(save=True):
            new = entry.get().strip()
            try: entry.destroy()
            except Exception: pass
            if save and new:
                task["text"] = new; save_tasks(self.tasks)
                np = self.cfg.get("obsidian_note_path","").strip()
                if np: sync_note(np, task)
            self._render_tasks()
        entry.bind("<Return>", lambda e: finish(True))
        entry.bind("<Escape>", lambda e: finish(False))
        entry.bind("<FocusOut>", lambda e: finish(True))

    def _inline_edit_subtask(self, parent, label, task, subtask):
        entry = tk.Entry(parent,bg=self.T["entry_bg"],fg=self.T["entry_fg"],insertbackground=self.T["entry_fg"],relief="flat",font=("Segoe UI Variable",8))
        entry.insert(0, subtask.get("text",""))
        label.pack_forget(); entry.pack(side="left",fill="x",expand=True)
        entry.focus_set(); entry.select_range(0,"end")
        def finish(save=True):
            new = entry.get().strip()
            try: entry.destroy()
            except Exception: pass
            if save and new:
                subtask["text"] = new; subtask.pop("_editing",None)
                save_tasks(self.tasks)
                np = self.cfg.get("obsidian_note_path","").strip()
                if np: sync_note(np, task)
            elif not new:
                try: task.get("subtasks",[]).remove(subtask)
                except ValueError: pass
                save_tasks(self.tasks)
                np = self.cfg.get("obsidian_note_path","").strip()
                if np: sync_note(np, task)
            self._render_tasks()
        entry.bind("<Return>", lambda e: finish(True))
        entry.bind("<Escape>", lambda e: finish(False))
        entry.bind("<FocusOut>", lambda e: finish(True))

    def _add_task(self, e=None):
        text = self.entry_var.get().strip()
        if not text: return
        task = _norm({"id":str(uuid.uuid4()),"text":text,"done":False,"created":now_dt().isoformat(timespec="seconds"),"priority":"none","subtasks":[]})
        self.tasks.insert(0, task)
        self.entry_var.set("")
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np, task)
        self.current_tab = "active"; self._render_tasks()

    def _add_subtask(self, task):
        task.setdefault("subtasks",[]).append({"id":str(uuid.uuid4()),"text":"","done":False,"_editing":True})
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np, task)
        self._render_tasks()

    def _toggle_subtask(self, task, sub, var):
        sub["done"] = var.get(); save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np, task)
        self._render_tasks()

    def _cycle_priority(self, task):
        cur = task.get("priority","none")
        task["priority"] = PRIORITIES[(PRIORITIES.index(cur)+1) % len(PRIORITIES)]
        save_tasks(self.tasks)
        self._render_tasks()

    def _toggle(self, task, var):
        task["done"] = var.get()
        if task["done"]: task["completed_at"] = now_dt().isoformat(timespec="seconds")
        else: task.pop("completed_at", None)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np, task)
        self._render_tasks()

    def _trash_task(self, task):
        task["deleted"] = True
        task["deleted_at"] = now_dt().isoformat(timespec="seconds")
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: remove_from_note(np, task["id"])
        self.current_tab = "active"
        self._render_tasks()

    def _recover_task(self, task):
        task["deleted"] = False
        task.pop("deleted_at", None)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np, task)
        self._render_tasks()

    def _delete_forever(self, task):
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: remove_from_note(np, task["id"])
        self.tasks = [t for t in self.tasks if t["id"] != task["id"]]
        save_tasks(self.tasks)
        self._render_tasks()

    def _open_settings(self):
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.lift(); return
        self._settings_widgets = {k: [] for k in ["frame_bg","section","label","muted","entry","button","check","radio","scale","swatch"]}
        win = tk.Toplevel(self.root)
        self._settings_win = win
        win.title("LeoNote — Settings")
        win.minsize(420,420)
        x = self.cfg["settings_x"] if self.cfg["settings_x"] is not None else self.root.winfo_x()+20
        y = self.cfg["settings_y"] if self.cfg["settings_y"] is not None else self.root.winfo_y()+40
        win.geometry(f"{self.cfg.get('settings_w',520)}x{self.cfg.get('settings_h',600)}+{x}+{y}")
        win.attributes("-topmost", True)
        win.bind("<Return>", lambda e: win.destroy())
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        def remember(e=None):
            if e and e.widget == win:
                self.cfg.update(settings_x=win.winfo_x(), settings_y=win.winfo_y(), settings_w=win.winfo_width(), settings_h=win.winfo_height())
                save_config(self.cfg)
        win.bind("<Configure>", remember)

        body = tk.Frame(win,bg=self.T["bg"]); body.pack(fill="both",expand=True)
        self._settings_widgets["frame_bg"].append(body)
        canvas = tk.Canvas(body,bg=self.T["bg"],bd=0,highlightthickness=0)
        sb = ttk.Scrollbar(body,orient="vertical",command=canvas.yview, style="LeSticky.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        sf = tk.Frame(canvas,bg=self.T["bg"])
        self._settings_widgets["frame_bg"].append(sf); self._settings_widgets["frame_bg"].append(canvas)
        sfw = canvas.create_window((0,0),window=sf,anchor="nw")
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(sfw,width=e.width))

        def wheel(e):
            d = int(-1*(e.delta/120)) if getattr(e,"delta",0) else (-1 if getattr(e,"num",None)==4 else 1)
            canvas.yview_scroll(d,"units")
            return "break"
        def bind_all(w):
            for seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
                try: w.bind(seq,wheel,add="+")
                except Exception: pass
            for ch in w.winfo_children(): bind_all(ch)
        win.after(120, lambda: bind_all(sf))

        def section(txt):
            f = tk.Frame(sf,bg=self.T["header_bg"]); f.pack(fill="x",pady=(10,2))
            l = tk.Label(f,text=txt,bg=self.T["header_bg"],fg=self.T["text"],font=("Segoe UI Variable",9,"bold"),anchor="w",padx=8,pady=5)
            l.pack(fill="x")
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["section"].append(l)
        def rowf(label,maker):
            f = tk.Frame(sf,bg=self.T["bg"]); f.pack(fill="x",padx=12,pady=4)
            l = tk.Label(f,text=label,bg=self.T["bg"],fg=self.T["text"],font=("Segoe UI Variable",9),width=26,anchor="w")
            l.pack(side="left")
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["label"].append(l)
            maker(f)
            return f

        section("Obsidian (Optional)")
        note_var = tk.StringVar(value=self.cfg.get("obsidian_note_path",""))
        note_var.trace_add("write", lambda *a: (self.cfg.__setitem__("obsidian_note_path", note_var.get().strip()), save_config(self.cfg)))
        def note_row(p):
            e=tk.Entry(p,textvariable=note_var,bg=self.T["entry_bg"],fg=self.T["entry_fg"],insertbackground=self.T["entry_fg"],relief="flat",font=("Segoe UI Variable",9),highlightthickness=1,highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
            e.pack(side="left",fill="x",expand=True,ipady=4)
            b=tk.Button(p,text="📄",bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",font=("Segoe UI Variable",9),padx=6,cursor="hand2",command=lambda: note_var.set(filedialog.asksaveasfilename(title="Select note",defaultextension=".md",filetypes=[("Markdown","*.md"),("All","*.*")]) or note_var.get()))
            b.pack(side="left",padx=(4,0))
            self._settings_widgets["entry"].append(e); self._settings_widgets["button"].append(b)
        rowf("Task note path:", note_row)

        section("Theme")
        theme_var = tk.StringVar(value=self.cfg.get("theme","peach"))
        def apply_theme():
            self.cfg["theme"] = theme_var.get(); save_config(self.cfg)
            self._retheme_main_only()
            self.root.after(10, self._keep_settings_alive)
            if self._settings_win and self._settings_win.winfo_exists():
                self._settings_win.after(1, self._keep_settings_alive)
        tf = tk.Frame(sf,bg=self.T["bg"]); tf.pack(fill="x",padx=12,pady=4); self._settings_widgets["frame_bg"].append(tf)
        for i,(name,samp) in enumerate(THEMES.items()):
            f=tk.Frame(tf,bg=self.T["bg"]); f.grid(row=i//3,column=i%3,sticky="w",padx=6,pady=3)
            r=tk.Radiobutton(f,text=name.capitalize(),variable=theme_var,value=name,bg=self.T["bg"],fg=self.T["text"],activebackground=self.T["bg"],selectcolor=self.T["entry_bg"],font=("Segoe UI Variable",9),command=apply_theme)
            r.pack(side="left")
            preview_bg = samp["header_bg"]
            if name in {"dark", "crimson", "forest", "emerald", "midnight", "space", "violet-night", "eclipse"}:
                preview_bg = samp["btn_bg"]
            sw=tk.Label(f,text="   ",bg=preview_bg,width=3); sw.pack(side="left",padx=(4,0))
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["radio"].append(r); self._settings_widgets["swatch"].append(sw)

        section("Display & Behavior")
        def live_toggle(label, key, callback=None):
            var=tk.BooleanVar(value=self.cfg.get(key,False))
            def apply_toggle():
                self.cfg[key] = var.get(); save_config(self.cfg)
                if callback: callback(var.get())
                if self._settings_win and self._settings_win.winfo_exists():
                    self._settings_win.after(1, self._keep_settings_alive)
            rowf(label, lambda p, vv=var: self._mk_check(p, vv, apply_toggle))
        live_toggle("Always on top:", "always_on_top", lambda v: (self.root.attributes("-topmost", v), self._refresh_pin()))
        live_toggle("Show in tray:", "show_in_tray", lambda v: self._setup_tray() if v else self._destroy_tray())
        live_toggle("Start hidden to tray:", "start_hidden_to_tray")
        live_toggle("Show Windows title bar:", "show_system_titlebar", lambda v: self._apply_window_mode())
        live_toggle("Display in taskbar:", "show_in_taskbar", lambda v: self._apply_window_mode())
        live_toggle("Run at Windows startup:", "run_at_startup", lambda v: self._apply_startup(v))

        section("UI Scale")
        scale_var = tk.DoubleVar(value=float(self.cfg.get("ui_scale",1.0)))
        def scale_row(p):
            sc=tk.Scale(p,variable=scale_var,from_=0.5,to=3.0,resolution=0.05,orient="horizontal",bg=self.T["bg"],fg=self.T["text"],troughcolor=self.T["separator"],activebackground=self.T["btn_hover"],highlightthickness=0,bd=0,length=220,command=lambda v:(self._set_scale(float(v)), self.root.after(10, self._keep_settings_alive)))
            sc.pack(side="left")
            lb=tk.Label(p,textvariable=scale_var,bg=self.T["bg"],fg=self.T["text"],font=("Segoe UI Variable",9),width=5)
            lb.pack(side="left",padx=4)
            self._settings_widgets["scale"].append(sc); self._settings_widgets["label"].append(lb)
        rowf("Scale (0.5–3.0):", scale_row)
        m=tk.Label(sf,text="Close with Enter or window close button.",bg=self.T["bg"],fg=self.T["muted"],font=("Segoe UI Variable",8),anchor="w",padx=12)
        m.pack(fill="x")
        self._settings_widgets["muted"].append(m)

        section("Data")
        def export_fn():
            path=filedialog.asksaveasfilename(title="Export",defaultextension=".json",filetypes=[("JSON","*.json")])
            if path:
                with open(path,"w",encoding="utf-8") as f: json.dump(self.tasks,f,indent=2,ensure_ascii=False)
        def import_fn():
            path=filedialog.askopenfilename(title="Import",filetypes=[("JSON","*.json")])
            if not path: return
            try:
                with open(path,"r",encoding="utf-8") as f: imp=[_norm(t) for t in json.load(f)]
                have={t["id"] for t in self.tasks}; added=0
                for t in imp:
                    if t["id"] not in have: self.tasks.insert(0,t); added+=1
                save_tasks(self.tasks); self._render_tasks()
                messagebox.showinfo("Import",f"Imported {added} task(s).",parent=win)
            except Exception as ex:
                messagebox.showerror("Error",str(ex),parent=win)
        br=tk.Frame(sf,bg=self.T["bg"]); br.pack(fill="x",padx=12,pady=4); self._settings_widgets["frame_bg"].append(br)
        b1=tk.Button(br,text="⬆ Export",command=export_fn,bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",font=("Segoe UI Variable",9),padx=10,pady=5,cursor="hand2",activebackground=self.T["btn_hover"])
        b1.pack(side="left",padx=(0,8))
        b2=tk.Button(br,text="⬇ Import",command=import_fn,bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",font=("Segoe UI Variable",9),padx=10,pady=5,cursor="hand2",activebackground=self.T["btn_hover"])
        b2.pack(side="left")
        self._settings_widgets["button"].extend([b1,b2])

    def _mk_check(self, parent, var, command):
        c=tk.Checkbutton(parent,variable=var,bg=self.T["bg"],fg=self.T["text"],activebackground=self.T["bg"],selectcolor=self.T["entry_bg"],font=("Segoe UI Variable",9),command=command)
        c.pack(side="left")
        self._settings_widgets["check"].append(c)
        return c

    def _startup_shortcut_path(self):
        appdata = os.environ.get("APPDATA", "")
        return os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "LeoNote.bat") if appdata else ""

    def _apply_startup(self, enabled):
        path = self._startup_shortcut_path()
        if not path:
            return
        try:
            if enabled:
                exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f'@echo off\nstart "" "{exe}"\n')
            else:
                if os.path.exists(path):
                    os.remove(path)
        except Exception:
            pass

    def _reset_scale(self, var=None):
        self.cfg["ui_scale"] = 1.0
        save_config(self.cfg)
        if var is not None:
            var.set(1.0)
        self._apply_scale()
        self._retheme_main_only()
        self.root.after(10, self._keep_settings_alive)

    def _toggle_topmost(self):
        v = not self.root.attributes("-topmost")
        self.root.attributes("-topmost", v)
        self.cfg["always_on_top"] = v
        save_config(self.cfg)
        self._refresh_pin()

    def _toggle_maximize(self):
        self.root.update_idletasks()
        if not self._is_maximized:
            self._restore_geo = self.root.geometry()
            sw,sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")
            self._is_maximized = True
        else:
            if self._restore_geo: self.root.geometry(self._restore_geo)
            self._is_maximized = False

    def _minimize(self):
        if self.cfg.get("show_in_tray",False) and not self.cfg.get("show_in_taskbar",False):
            self.root.withdraw(); return
        was = bool(self.cfg.get("always_on_top",False))
        self.root.attributes("-topmost",False)
        self.root.overrideredirect(False)
        self.root.iconify()
        def restore():
            if self.root.state() != "iconic":
                self.root.overrideredirect(self._custom_chrome_on())
                self.root.attributes("-topmost",was)
        self.root.after(600, restore)

    def _close(self):
        save_config(self.cfg); save_tasks(self.tasks); self._destroy_tray(); self.root.destroy()

    def _drag_start(self, e):
        if self._is_maximized or not self._custom_chrome_on(): return
        self._drag_x = e.x_root - self.root.winfo_x(); self._drag_y = e.y_root - self.root.winfo_y()
    def _drag_do(self, e):
        if self._is_maximized or not self._custom_chrome_on() or self._resize_edge: return
        self.root.geometry(f"+{e.x_root-self._drag_x}+{e.y_root-self._drag_y}")

    _CURSORS = {"n":"sb_v_double_arrow","s":"sb_v_double_arrow","e":"sb_h_double_arrow","w":"sb_h_double_arrow","ne":"top_right_corner","sw":"bottom_left_corner","nw":"top_left_corner","se":"bottom_right_corner"}
    def _edge_zone(self, xr, yr, m=12):
        rx,ry = self.root.winfo_rootx(), self.root.winfo_rooty(); rw,rh = self.root.winfo_width(), self.root.winfo_height()
        L=xr-rx<=m; R=(rx+rw)-xr<=m; To=yr-ry<=m; B=(ry+rh)-yr<=m
        if To and L: return "nw"
        if To and R: return "ne"
        if B and L: return "sw"
        if B and R: return "se"
        if L: return "w"
        if R: return "e"
        if To: return "n"
        if B: return "s"
        return None
    def _resize_cursor(self, e):
        if not self._custom_chrome_on() or self._is_maximized:
            self.root.config(cursor=""); return
        z = self._edge_zone(e.x_root,e.y_root)
        self.root.config(cursor=self._CURSORS.get(z,""))
    def _resize_start_cb(self, e):
        if not self._custom_chrome_on() or self._is_maximized: return
        z = self._edge_zone(e.x_root,e.y_root)
        if z: self._resize_edge=z; self._resize_start=(self.root.winfo_x(),self.root.winfo_y(),self.root.winfo_width(),self.root.winfo_height(),e.x_root,e.y_root)
    def _resize_do(self, e):
        if not self._resize_edge or not self._resize_start: return
        x0,y0,w0,h0,sx,sy = self._resize_start
        dx,dy = e.x_root-sx, e.y_root-sy
        nx,ny,nw,nh = x0,y0,w0,h0; mw,mh=300,380
        if "e" in self._resize_edge: nw=max(mw,w0+dx)
        if "s" in self._resize_edge: nh=max(mh,h0+dy)
        if "w" in self._resize_edge: nw=max(mw,w0-dx); nx=x0+(w0-nw)
        if "n" in self._resize_edge: nh=max(mh,h0-dy); ny=y0+(h0-nh)
        self.root.geometry(f"{nw}x{nh}+{nx}+{ny}")
    def _resize_stop(self, e): self._resize_edge=None; self._resize_start=None
    def _on_configure(self, e=None):
        if e and e.widget == self.root and not self._is_maximized:
            self.cfg.update(window_x=self.root.winfo_x(), window_y=self.root.winfo_y(), window_w=self.root.winfo_width(), window_h=self.root.winfo_height())
            save_config(self.cfg)
    def run(self):
        self.entry.focus_set(); self.root.mainloop()

if __name__ == "__main__":
    App().run()

    def _keep_settings_alive(self):
        if self._settings_win and self._settings_win.winfo_exists():
            try:
                self._settings_win.deiconify()
                self._settings_win.lift()
                self._settings_win.attributes("-topmost", True)
                self._settings_win.focus_force()
            except Exception:
                pass
