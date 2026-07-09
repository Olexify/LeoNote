"""
LeoNote - lightweight sticky task app with Obsidian integration
v3 features: docs square grid + trash + singleton window + inline rename,
             habits rename (dbl-click) + delete confirmation,
             XP reverts on unsolve, subtask name flush on new subtask,
             full export (tasks/docs/habits/progression),
             CPU/RAM optimisations (debounced config save, rate-limited purge,
             deferred bar draw, grid relayout debounce, lighter scroll binding)
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

CONFIG_FILE  = os.path.join(os.path.expanduser("~"), ".leonote_config.json")
TASKS_FILE   = os.path.join(os.path.expanduser("~"), ".leonote_tasks.json")
DOCS_FILE    = os.path.join(os.path.expanduser("~"), ".leonote_docs.json")
HABITS_FILE  = os.path.join(os.path.expanduser("~"), ".leonote_habits.json")

DEFAULT_CONFIG = {
    "obsidian_note_path": "",
    "docs_backup_path": "",
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
    "ui_font": "Segoe UI Variable",
    "settings_x": None, "settings_y": None,
    "settings_w": 520, "settings_h": 600,
}

THEMES = {
    "yellow":       {"bg":"#fff7c2","header_bg":"#f6d860","text":"#3b2f07","muted":"#8a7430","entry_bg":"#fffbe0","entry_fg":"#3b2f07","btn_bg":"#f4cf4d","btn_fg":"#3b2f07","btn_hover":"#eabf20","check_done":"#65a30d","separator":"#efd981","item_bg":"#fffbe6","item_hover":"#fff3bf","tab_bg":"#f8e89b","archive":"#b7791f","close_hover":"#ef4444","low":"#3b82f6","medium":"#f59e0b","high":"#dc2626"},
    "dark":         {"bg":"#1c1b19","header_bg":"#27251f","text":"#e7e5e4","muted":"#a8a29e","entry_bg":"#27251f","entry_fg":"#e7e5e4","btn_bg":"#3f3d38","btn_fg":"#e7e5e4","btn_hover":"#4f4c47","check_done":"#4f98a3","separator":"#393836","item_bg":"#201f1d","item_hover":"#2d2c2a","tab_bg":"#2d2c2a","archive":"#d6a547","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "light":        {"bg":"#f7f6f2","header_bg":"#f0ede8","text":"#28251d","muted":"#6b7280","entry_bg":"#ffffff","entry_fg":"#28251d","btn_bg":"#e6e4df","btn_fg":"#28251d","btn_hover":"#dcd9d5","check_done":"#437a22","separator":"#dcd9d5","item_bg":"#fafaf8","item_hover":"#f0ede8","tab_bg":"#ece8e1","archive":"#a16207","close_hover":"#ef4444","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "sakura":       {"bg":"#ffeef5","header_bg":"#ffc9dd","text":"#4a1f2d","muted":"#8b5d6b","entry_bg":"#fff7fa","entry_fg":"#4a1f2d","btn_bg":"#ffb3cf","btn_fg":"#4a1f2d","btn_hover":"#ff9fc2","check_done":"#22c55e","separator":"#f8b4c9","item_bg":"#fff7fa","item_hover":"#ffe4ef","tab_bg":"#ffe0ec","archive":"#be185d","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "mint":         {"bg":"#ecfdf5","header_bg":"#bbf7d0","text":"#16352a","muted":"#4b6b5b","entry_bg":"#f7fffb","entry_fg":"#16352a","btn_bg":"#86efac","btn_fg":"#16352a","btn_hover":"#6ee7b7","check_done":"#16a34a","separator":"#a7f3d0","item_bg":"#f7fffb","item_hover":"#dcfce7","tab_bg":"#d1fae5","archive":"#047857","close_hover":"#ef4444","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "ocean":        {"bg":"#eff6ff","header_bg":"#bfdbfe","text":"#132c52","muted":"#5b6f92","entry_bg":"#f8fbff","entry_fg":"#132c52","btn_bg":"#93c5fd","btn_fg":"#132c52","btn_hover":"#60a5fa","check_done":"#2563eb","separator":"#bfdbfe","item_bg":"#f8fbff","item_hover":"#dbeafe","tab_bg":"#dbeafe","archive":"#1d4ed8","close_hover":"#ef4444","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "rose":         {"bg":"#fff1f2","header_bg":"#fecdd3","text":"#4a1d24","muted":"#8f5b66","entry_bg":"#fff8f8","entry_fg":"#4a1d24","btn_bg":"#fda4af","btn_fg":"#4a1d24","btn_hover":"#fb7185","check_done":"#16a34a","separator":"#fecdd3","item_bg":"#fff8f8","item_hover":"#ffe4e6","tab_bg":"#ffe4e6","archive":"#be123c","close_hover":"#e11d48","low":"#60a5fa","medium":"#f59e0b","high":"#dc2626"},
    "lavender":     {"bg":"#faf5ff","header_bg":"#e9d5ff","text":"#35214f","muted":"#7c6a97","entry_bg":"#fdfaff","entry_fg":"#35214f","btn_bg":"#d8b4fe","btn_fg":"#35214f","btn_hover":"#c084fc","check_done":"#22c55e","separator":"#e9d5ff","item_bg":"#fdfaff","item_hover":"#f3e8ff","tab_bg":"#f3e8ff","archive":"#7e22ce","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "peach":        {"bg":"#fff7ed","header_bg":"#fed7aa","text":"#4a2b18","muted":"#916a4e","entry_bg":"#fffaf5","entry_fg":"#4a2b18","btn_bg":"#fdba74","btn_fg":"#4a2b18","btn_hover":"#fb923c","check_done":"#16a34a","separator":"#fed7aa","item_bg":"#fffaf5","item_hover":"#ffedd5","tab_bg":"#ffedd5","archive":"#c2410c","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "sky":          {"bg":"#f0f9ff","header_bg":"#bae6fd","text":"#0f2f4a","muted":"#5f7f9a","entry_bg":"#f8fcff","entry_fg":"#0f2f4a","btn_bg":"#7dd3fc","btn_fg":"#0f2f4a","btn_hover":"#38bdf8","check_done":"#0284c7","separator":"#bae6fd","item_bg":"#f8fcff","item_hover":"#e0f2fe","tab_bg":"#e0f2fe","archive":"#0369a1","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "slate":        {"bg":"#f8fafc","header_bg":"#cbd5e1","text":"#1e293b","muted":"#64748b","entry_bg":"#ffffff","entry_fg":"#1e293b","btn_bg":"#cbd5e1","btn_fg":"#1e293b","btn_hover":"#94a3b8","check_done":"#22c55e","separator":"#cbd5e1","item_bg":"#ffffff","item_hover":"#f1f5f9","tab_bg":"#e2e8f0","archive":"#334155","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "coral":        {"bg":"#fff5f3","header_bg":"#fca5a5","text":"#4a1c14","muted":"#946057","entry_bg":"#fffaf9","entry_fg":"#4a1c14","btn_bg":"#fb7185","btn_fg":"#4a1c14","btn_hover":"#ef4444","check_done":"#16a34a","separator":"#fecaca","item_bg":"#fffaf9","item_hover":"#ffe4e6","tab_bg":"#ffe4e6","archive":"#b91c1c","close_hover":"#dc2626","low":"#2563eb","medium":"#f59e0b","high":"#dc2626"},
    "sand":         {"bg":"#fff8ed","header_bg":"#f5d7a1","text":"#4a3720","muted":"#8b7355","entry_bg":"#fffdf8","entry_fg":"#4a3720","btn_bg":"#e9c46a","btn_fg":"#4a3720","btn_hover":"#ddb85a","check_done":"#65a30d","separator":"#efdfbf","item_bg":"#fffdf8","item_hover":"#fbf1dc","tab_bg":"#f7ebd0","archive":"#b7791f","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "island":       {"bg":"#eefcf7","header_bg":"#9fe3cf","text":"#133a33","muted":"#5d7f77","entry_bg":"#f8fffc","entry_fg":"#133a33","btn_bg":"#67d4b7","btn_fg":"#133a33","btn_hover":"#34caa0","check_done":"#0f9f6e","separator":"#bfeee0","item_bg":"#f8fffc","item_hover":"#def8ef","tab_bg":"#d8f4eb","archive":"#0f766e","close_hover":"#dc2626","low":"#2563eb","medium":"#d97706","high":"#dc2626"},
    "crimson":      {"bg":"#1a0f12","header_bg":"#3a161d","text":"#f7d7db","muted":"#b48a91","entry_bg":"#221317","entry_fg":"#f7d7db","btn_bg":"#5b1f2b","btn_fg":"#f7d7db","btn_hover":"#7a2434","check_done":"#22c55e","separator":"#3a161d","item_bg":"#211417","item_hover":"#2a181d","tab_bg":"#2a181d","archive":"#f87171","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "forest":       {"bg":"#0d1711","header_bg":"#183323","text":"#d8f3df","muted":"#8cb09a","entry_bg":"#132018","entry_fg":"#d8f3df","btn_bg":"#235336","btn_fg":"#d8f3df","btn_hover":"#2f6a45","check_done":"#22c55e","separator":"#183323","item_bg":"#122019","item_hover":"#17281f","tab_bg":"#17281f","archive":"#86efac","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "emerald":      {"bg":"#071a17","header_bg":"#0d3b35","text":"#d5fff5","muted":"#7cb6aa","entry_bg":"#0b2521","entry_fg":"#d5fff5","btn_bg":"#0f5b50","btn_fg":"#d5fff5","btn_hover":"#147768","check_done":"#10b981","separator":"#0d3b35","item_bg":"#0b2521","item_hover":"#10302b","tab_bg":"#10302b","archive":"#5eead4","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "midnight":     {"bg":"#0b1220","header_bg":"#16233a","text":"#dbeafe","muted":"#7f93b0","entry_bg":"#10192b","entry_fg":"#dbeafe","btn_bg":"#1d4e89","btn_fg":"#dbeafe","btn_hover":"#2563eb","check_done":"#38bdf8","separator":"#16233a","item_bg":"#0f1a2e","item_hover":"#14213a","tab_bg":"#14213a","archive":"#60a5fa","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "space":        {"bg":"#09090f","header_bg":"#171726","text":"#ececff","muted":"#8f90ae","entry_bg":"#10101b","entry_fg":"#ececff","btn_bg":"#27273d","btn_fg":"#ececff","btn_hover":"#343452","check_done":"#7dd3fc","separator":"#171726","item_bg":"#10101b","item_hover":"#171726","tab_bg":"#171726","archive":"#c4b5fd","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "violet-night": {"bg":"#120b1f","header_bg":"#24123a","text":"#f1e7ff","muted":"#a38cbf","entry_bg":"#1a102a","entry_fg":"#f1e7ff","btn_bg":"#4c1d95","btn_fg":"#f1e7ff","btn_hover":"#6d28d9","check_done":"#22c55e","separator":"#24123a","item_bg":"#1a102a","item_hover":"#221434","tab_bg":"#221434","archive":"#c084fc","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "eclipse":      {"bg":"#0a0a0a","header_bg":"#1a1a1a","text":"#f2f2f2","muted":"#8a8a8a","entry_bg":"#111111","entry_fg":"#f2f2f2","btn_bg":"#2a2a2a","btn_fg":"#f2f2f2","btn_hover":"#3a3a3a","check_done":"#9ca3af","separator":"#1a1a1a","item_bg":"#111111","item_hover":"#181818","tab_bg":"#181818","archive":"#d4d4d8","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
}
PRIORITIES  = ["none","low","medium","high"]
UI_FONTS    = [
    "Segoe UI Variable", "Segoe UI", "Calibri", "Helvetica", "Arial",
    "Trebuchet MS", "Verdana", "Tahoma", "Georgia", "Palatino Linotype",
    "Courier New", "Consolas", "Lucida Console", "Comic Sans MS",
]
OPEN_SEP   = "<!-- OPEN_TASKS -->"
CLOSED_SEP = "<!-- CLOSED_TASKS -->"
TRASH_HOURS = 24

# ── XP / level thresholds ────────────────────────────────────────────────────
LEVEL_XP = [0,50,120,220,350,520,740,1020,1370,1800,2400]

def _xp_for_level(lvl):
    if lvl <= 0: return 0
    if lvl < len(LEVEL_XP): return LEVEL_XP[lvl]
    return LEVEL_XP[-1] + (lvl - len(LEVEL_XP) + 1) * 800

def _compute_level(xp):
    lvl = 0
    while _xp_for_level(lvl+1) <= xp:
        lvl += 1
    return lvl

# ── helpers ───────────────────────────────────────────────────────────────────
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
    t.setdefault("id",     str(uuid.uuid4()))
    t.setdefault("done",   False)
    t.setdefault("created",datetime.datetime.now().isoformat(timespec="seconds"))
    t.setdefault("priority","none")
    t.setdefault("subtasks",[])
    t.setdefault("deleted", False)
    return t

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE,"r",encoding="utf-8") as f:
                return [_norm(t) for t in json.load(f)]
        except Exception: pass
    return []

def save_tasks(tasks):
    with open(TASKS_FILE,"w",encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# ── docs ──────────────────────────────────────────────────────────────────────
def load_docs():
    if os.path.exists(DOCS_FILE):
        try:
            with open(DOCS_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return []

def save_docs(docs):
    with open(DOCS_FILE,"w",encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

# ── habits ────────────────────────────────────────────────────────────────────
def load_habits():
    if os.path.exists(HABITS_FILE):
        try:
            with open(HABITS_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return {"habits":[], "log":{}}

def save_habits(data):
    with open(HABITS_FILE,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _habit_streak(habit_id, log):
    """Return streak; forgiving = 1 missed day allowed."""
    today = datetime.date.today()
    streak = 0
    miss   = 0
    day    = today
    for _ in range(365):
        key = day.isoformat()
        if habit_id in log.get(key, []):
            streak += 1
            miss = 0
        else:
            miss += 1
            if miss > 1: break
        day -= datetime.timedelta(days=1)
    return streak

def _habit_best_streak(habit_id, log):
    """Best (longest) streak ever for a habit."""
    all_dates = sorted(log.keys())
    if not all_dates: return 0
    d0 = datetime.date.fromisoformat(all_dates[0])
    d1 = datetime.date.today()
    best = cur = miss = 0
    dd = d0
    while dd <= d1:
        if habit_id in log.get(dd.isoformat(),[]):
            cur += 1; miss = 0
            if cur > best: best = cur
        else:
            miss += 1
            if miss > 1: cur = 0; miss = 0
        dd += datetime.timedelta(days=1)
    return best

def _habit_total_days(habit_id, log):
    return sum(1 for v in log.values() if habit_id in v)

def _habit_last_n(habit_id, log, n):
    count = 0
    today = datetime.date.today()
    for i in range(n):
        d = (today - datetime.timedelta(days=i)).isoformat()
        if habit_id in log.get(d,[]): count += 1
    return count

def _habit_done_on(habit_id, log, days_ago):
    d = (datetime.date.today()-datetime.timedelta(days=days_ago)).isoformat()
    return habit_id in log.get(d,[])

# ── misc utils ────────────────────────────────────────────────────────────────
def now_dt():      return datetime.datetime.now()
def parse_iso(s):  return datetime.datetime.fromisoformat(s)
def fmt_dt(dt):    return dt.strftime("%d.%m.%y %H:%M")

def ensure_parent(path):
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)

def subtasks_inline(task):
    sts = task.get("subtasks",[])
    if not sts: return ""
    parts = []
    for st in sts:
        mark = "x" if st.get("done") else " "
        txt  = st.get("text","").replace("\n"," ").strip()
        if txt: parts.append(f"[{mark}] {txt}")
    return (" <sub>· " + " ; ".join(parts) + "</sub>") if parts else ""

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
    tid  = task["id"]; txt = task["text"].replace("\n"," ").strip()
    subs = subtasks_inline(task)
    c    = fmt_dt(parse_iso(task["created"]))
    if task.get("done"):
        s = fmt_dt(parse_iso(task["completed_at"]))
        return f"=={{green}} **{txt}** <sub>closed · {s}</sub>{subs}== sn:{tid}"
    return f"=={{accent}} **{txt}** <sub>open · created {c}</sub>{subs}== sn:{tid}"

def _remove_task_lines(lines, tid):
    return [l for l in lines if f"sn:{tid}" not in l]

def sync_note(path, task):
    if not path or task.get("deleted"): return
    _ensure_note(path)
    lines    = _remove_task_lines(_read_note(path), task["id"])
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


# ═══════════════════════════════════════════════════════════════════════════════
class App:
    def __init__(self):
        enable_high_dpi()
        self.cfg   = load_config()
        self.cfg.setdefault("start_hidden_to_tray", False)
        self.cfg.setdefault("show_in_taskbar", False)
        self.tasks = load_tasks()
        self._purge_old_trash()
        self.current_tab   = "active"
        self.search_var    = None
        self._drag_x = self._drag_y = 0
        self._restore_geo  = None
        self._tray_icon    = None
        self._resize_edge  = self._resize_start = None
        self._is_maximized = False
        self._settings_win = None
        self._settings_widgets = {}
        self._pin_btn      = None
        self._dragging_task = None
        # gamification state (persisted in config)
        self.cfg.setdefault("xp", 0)
        self.cfg.setdefault("tasks_created", 0)
        self.cfg.setdefault("tasks_done", 0)

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
        self.root.bind("<Map>",       self._on_map)
        self.T = THEMES[self.cfg["theme"]]
        self.search_var = tk.StringVar(master=self.root)
        self._apply_window_mode(first=True)
        self._build_ui()

        if self.cfg.get("show_in_tray"): self._setup_tray()
        if self.cfg.get("start_hidden_to_tray") and self.cfg.get("show_in_tray"):
            self.root.after(50, self.root.withdraw)
        else:
            self.root.deiconify()

    # ── purge ─────────────────────────────────────────────────────────────────
    def _purge_old_trash(self):
        now  = now_dt(); kept = []; changed = False
        for t in self.tasks:
            if t.get("deleted") and t.get("deleted_at"):
                if now - parse_iso(t["deleted_at"]) > datetime.timedelta(hours=TRASH_HOURS):
                    changed = True; continue
            kept.append(t)
        if changed: self.tasks = kept; save_tasks(self.tasks)

    # ── icon ──────────────────────────────────────────────────────────────────
    def _apply_icon(self):
        for name in ("icon.png","icon.ico"):
            pth = resource_path(name)
            if not os.path.exists(pth): continue
            try:
                if name.endswith(".png"):
                    img = tk.PhotoImage(file=pth)
                    self._icon_img = img
                    try:
                        w,h = img.width(), img.height()
                        max_side = 28
                        scale = max(1, int(max(w,h)/max_side)) if max(w,h)>max_side else 1
                        self._header_icon_img = img.subsample(scale,scale) if scale>1 else img
                    except Exception:
                        self._header_icon_img = img
                    self.root.iconphoto(True, img)
                else:
                    self.root.iconbitmap(pth)
                return
            except Exception: continue

    # ── scale ─────────────────────────────────────────────────────────────────
    def _apply_scale(self):
        s = max(0.5, min(3.0, float(self.cfg.get("ui_scale",1.0))))
        self.root.tk.call("tk","scaling", 1.25*s)

    def _set_scale(self, s):
        self.cfg["ui_scale"] = round(max(0.5,min(3.0,float(s))),2)
        save_config(self.cfg)
        self._apply_scale()
        self._retheme_main_only()

    # ── chrome ────────────────────────────────────────────────────────────────
    def _custom_chrome_on(self):
        return not bool(self.cfg.get("show_system_titlebar",False)) and not bool(self.cfg.get("show_in_taskbar",False))

    def _apply_window_mode(self, first=False):
        self.root.overrideredirect(self._custom_chrome_on())
        if not first: self.root.update_idletasks()
        self.root.after(20, self._bind_resize)

    def _bind_resize(self):
        self.root.bind("<Motion>",        self._resize_cursor)
        self.root.bind("<ButtonPress-1>", self._resize_start_cb, add="+")
        self.root.bind("<B1-Motion>",     self._resize_do,       add="+")
        self.root.bind("<ButtonRelease-1>",self._resize_stop,    add="+")

    def _on_map(self, e=None):
        if self.root.state() != "iconic":
            self.root.after(30, lambda: self.root.overrideredirect(self._custom_chrome_on()))
            self.root.after(50, lambda: self.root.attributes("-topmost", self.cfg.get("always_on_top",True)))

    # ── tray ──────────────────────────────────────────────────────────────────
    def _setup_tray(self):
        if not _TRAY_OK or self._tray_icon: return
        pth = resource_path("icon.png")
        if not os.path.exists(pth): return
        try:
            img  = _PILImage.open(pth)
            menu = _pystray.Menu(
                _pystray.MenuItem("Show", self._tray_show, default=True),
                _pystray.MenuItem("Hide", lambda icon,item: self.root.after(0, self.root.withdraw)),
                _pystray.MenuItem("Exit", lambda icon,item: self.root.after(0, self._close)),
            )
            self._tray_icon = _pystray.Icon("LeoNote", img, "LeoNote", menu)
            import threading
            threading.Thread(target=self._tray_icon.run, daemon=True).start()
        except Exception: self._tray_icon = None

    def _tray_show(self, icon=None, item=None): self.root.after(0, self._show_from_tray)
    def _show_from_tray(self):
        try: self.root.overrideredirect(self._custom_chrome_on())
        except Exception: pass
        self.root.deiconify(); self.root.state("normal")
        self.root.after(30, lambda: (self.root.lift(), self.root.attributes("-topmost", self.cfg.get("always_on_top",True)), self.root.focus_force()))

    def _destroy_tray(self):
        if self._tray_icon:
            try: self._tray_icon.stop()
            except Exception: pass
            self._tray_icon = None

    # ── scrollbar style ───────────────────────────────────────────────────────
    def _apply_scrollbar_style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        T = self.T
        style.layout("LeSticky.Vertical.TScrollbar",
            [("Vertical.Scrollbar.trough",{"sticky":"ns","children":[("Vertical.Scrollbar.thumb",{"expand":"1","sticky":"nswe"})]})])
        style.configure("LeSticky.Vertical.TScrollbar",
            background=T["separator"], troughcolor=T["bg"], bordercolor=T["bg"],
            darkcolor=T["bg"], lightcolor=T["bg"], arrowcolor=T["bg"],
            relief="flat", borderwidth=0, arrowsize=1, width=4)
        style.map("LeSticky.Vertical.TScrollbar",
            background=[("active", T["muted"]),("!active", T["separator"])])

    # ── main UI build ─────────────────────────────────────────────────────────
    def _build_ui(self):
        self._apply_scrollbar_style()
        for w in self.root.winfo_children():
            if isinstance(w, tk.Toplevel): continue
            w.destroy()
        self._pin_btn = None
        self.root.configure(bg=self.T["separator"])
        outer = tk.Frame(self.root, bg=self.T["separator"]); outer.pack(fill="both",expand=True)
        self.main = tk.Frame(outer, bg=self.T["bg"]); self.main.pack(fill="both",expand=True,padx=1,pady=1)
        self._build_titlebar()

        tabs_row = tk.Frame(self.main, bg=self.T["tab_bg"]); tabs_row.pack(fill="x")
        self._tab_tasks   = self._mktab(tabs_row,"Tasks",   lambda:self._set_tab("active"))
        self._tab_archive = self._mktab(tabs_row,"Archive", lambda:self._set_tab("archive"))
        self._tab_habits  = self._mktab(tabs_row,"🌱",      lambda:self._set_tab("habits"),  compact=True)
        self._tab_docs    = self._mktab(tabs_row,"📄", lambda:self._set_tab("docs"))
        self._tab_stats   = self._mktab(tabs_row,"🎮",      lambda:self._set_tab("stats"),   compact=True)
        self._tab_bin     = self._mktab(tabs_row,"🗑",      lambda:self._set_tab("trash"),   compact=True)
        self._tab_search  = self._mktab(tabs_row,"🔍",      lambda:self._set_tab("search"),  compact=True)
        self._refresh_tabs()

        self.top_input_host = tk.Frame(self.main, bg=self.T["bg"])
        self.top_input_host.pack(fill="x")

        # task entry
        self.entry_area = tk.Frame(self.top_input_host, bg=self.T["bg"], pady=6, padx=6)
        self.entry_area.pack(fill="x")
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.entry_area,textvariable=self.entry_var,
            bg=self.T["entry_bg"],fg=self.T["entry_fg"],
            insertbackground=self.T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),11),
            bd=0,highlightthickness=1,
            highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
        self.entry.pack(side="left",fill="x",expand=True,ipady=6,padx=(0,4))
        self.entry.bind("<Return>", self._add_task)
        self.entry.bind("<Control-MouseWheel>", self._ctrl_scroll)
        self.add_btn = tk.Button(self.entry_area,text="Add",command=self._add_task,
            bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",
            font=("Segoe UI Variable",10,"bold"),padx=12,pady=6,cursor="hand2",
            activebackground=self.T["btn_hover"])
        self.add_btn.pack(side="right")

        # search entry
        self.search_area = tk.Frame(self.top_input_host, bg=self.T["bg"], pady=6, padx=6)
        self.search_entry = tk.Entry(self.search_area,textvariable=self.search_var,
            bg=self.T["entry_bg"],fg=self.T["entry_fg"],
            insertbackground=self.T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),11),
            bd=0,highlightthickness=1,
            highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
        self.search_entry.pack(side="left",fill="x",expand=True,ipady=6,padx=(0,4))
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_tasks())
        tk.Button(self.search_area,text="Clear",
            command=lambda:(self.search_var.set(""), self._render_tasks()),
            bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
            padx=10,pady=6,cursor="hand2",
            activebackground=self.T["btn_hover"]).pack(side="right")

        lf = tk.Frame(self.main,bg=self.T["bg"]); lf.pack(fill="both",expand=True,padx=6,pady=(0,6))
        self.canvas = tk.Canvas(lf,bg=self.T["bg"],bd=0,highlightthickness=0)
        sb = ttk.Scrollbar(lf,orient="vertical",command=self.canvas.yview,
            style="LeSticky.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y")
        self.canvas.pack(side="left",fill="both",expand=True)
        self.task_frame = tk.Frame(self.canvas,bg=self.T["bg"])
        self._cw = self.canvas.create_window((0,0),window=self.task_frame,anchor="nw")
        self.task_frame.bind("<Configure>", lambda e: self._update_scroll())
        self.canvas.bind("<Configure>",     lambda e: self.canvas.itemconfig(self._cw,width=e.width))
        for w in (self.canvas, self.task_frame):
            w.bind("<MouseWheel>",         self._scroll)
            w.bind("<Button-4>",           self._scroll)
            w.bind("<Button-5>",           self._scroll)
            w.bind("<Control-MouseWheel>", self._ctrl_scroll)
        # root-level scroll handled by _bind_ctrl_wheel_recursive after build

        tk.Frame(self.main,bg=self.T["separator"],height=1).pack(fill="x")
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(self.main,textvariable=self.status_var,
            bg=self.T["header_bg"],fg=self.T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8),anchor="w",padx=8,pady=4)
        self.status_lbl.pack(fill="x")
        self._render_tasks()
        self.root.after(50, lambda: self._bind_ctrl_wheel_recursive(self.main))

    def _bind_ctrl_wheel_recursive(self, widget):
        # Only bind on Frame/Label/Checkbutton – skip Entry/Text to avoid swallowing keys
        cls = widget.winfo_class()
        if cls not in ("TEntry","Entry","Text","Scrollbar","TScrollbar"):
            for seq in ("<Control-MouseWheel>","<Control-Button-4>","<Control-Button-5>"):
                try: widget.bind(seq, self._ctrl_scroll, add="+")
                except Exception: pass
            for seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
                try: widget.bind(seq, self._scroll, add="+")
                except Exception: pass
        for child in widget.winfo_children():
            self._bind_ctrl_wheel_recursive(child)

    # ── retheme ───────────────────────────────────────────────────────────────
    def _retheme_main_only(self):
        self.T = THEMES[self.cfg["theme"]]
        old_tab = self.current_tab
        self._build_ui()
        self.current_tab = old_tab
        self._refresh_tabs()
        self._render_tasks()
        self._restyle_settings_window()
        self.root.after(30, self._keep_settings_alive)

    def _restyle_settings_window(self):
        if not (self._settings_win and self._settings_win.winfo_exists()): return
        self._settings_win.configure(bg=self.T["bg"])
        for kind, items in self._settings_widgets.items():
            for w in items:
                try:
                    if   kind=="frame_bg": w.configure(bg=self.T["bg"])
                    elif kind=="section":  w.configure(bg=self.T["header_bg"],fg=self.T["text"])
                    elif kind=="label":    w.configure(bg=self.T["bg"],fg=self.T["text"])
                    elif kind=="muted":    w.configure(bg=self.T["bg"],fg=self.T["muted"])
                    elif kind=="entry":    w.configure(bg=self.T["entry_bg"],fg=self.T["entry_fg"],insertbackground=self.T["entry_fg"],highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
                    elif kind=="button":   w.configure(bg=self.T["btn_bg"],fg=self.T["btn_fg"],activebackground=self.T["btn_hover"])
                    elif kind=="check":    w.configure(bg=self.T["bg"],fg=self.T["text"],activebackground=self.T["bg"],selectcolor=self.T["entry_bg"])
                    elif kind=="radio":    w.configure(bg=self.T["bg"],fg=self.T["text"],activebackground=self.T["bg"],selectcolor=self.T["entry_bg"])
                    elif kind=="scale":    w.configure(bg=self.T["bg"],fg=self.T["text"],troughcolor=self.T["separator"],activebackground=self.T["btn_hover"])
                except Exception: pass

    # ── titlebar ──────────────────────────────────────────────────────────────
    def _soft_pin_color(self):
        darkish = {"dark","crimson","forest","emerald","midnight","space","violet-night","eclipse"}
        visible_light = {"ocean","rose","lavender","peach","sky","slate","coral","sand","island","yellow"}
        name = self.cfg.get("theme")
        if name in darkish:    return self.T["btn_hover"]
        if name in visible_light: return self.T["btn_bg"]
        return self.T["separator"]

    def _build_titlebar(self):
        T = self.T
        hdr = tk.Frame(self.main,bg=T["header_bg"],cursor="fleur"); hdr.pack(fill="x",side="top")
        for ev,cb in (("<ButtonPress-1>",self._drag_start),("<B1-Motion>",self._drag_do),
                      ("<Double-Button-1>",lambda e:self._toggle_maximize())):
            hdr.bind(ev,cb)
        if hasattr(self,"_header_icon_img"):
            il = tk.Label(hdr,image=self._header_icon_img,bg=T["header_bg"])
            il.pack(side="left",padx=(8,4),pady=4)
            for ev,cb in (("<ButtonPress-1>",self._drag_start),("<B1-Motion>",self._drag_do),
                          ("<Double-Button-1>",lambda e:self._toggle_maximize())):
                il.bind(ev,cb)
        lbl = tk.Label(hdr,text="LeoNote",bg=T["header_bg"],fg=T["text"],
            font=("Segoe UI Variable",11,"bold"),padx=6,pady=8)
        lbl.pack(side="left")
        for ev,cb in (("<ButtonPress-1>",self._drag_start),("<B1-Motion>",self._drag_do),
                      ("<Double-Button-1>",lambda e:self._toggle_maximize())):
            lbl.bind(ev,cb)
        bf = tk.Frame(hdr,bg=T["header_bg"]); bf.pack(side="right",padx=4)
        def hbtn(text, cmd, red=False):
            b = tk.Button(bf,text=text,command=cmd,bg=T["header_bg"],fg=T["text"],
                relief="flat",font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                padx=9,pady=5,cursor="hand2",bd=0,
                activeforeground=T["btn_fg"],
                activebackground=T["close_hover"] if red else T["btn_hover"])
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

    # ── tabs ──────────────────────────────────────────────────────────────────
    def _trash_items(self):
        return [t for t in self.tasks if t.get("deleted")]

    def _trash_docs(self):
        return [d for d in load_docs() if d.get("deleted")]

    def _purge_old_doc_trash(self):
        now = now_dt()
        all_docs = load_docs()
        kept = [d for d in all_docs
            if not d.get("deleted") or
               (d.get("deleted_at") and now - parse_iso(d["deleted_at"]) <= datetime.timedelta(hours=TRASH_HOURS))]
        if len(kept) != len(all_docs):
            save_docs(kept)


    def _mktab(self, parent, text, cmd, compact=False):
        T = self.T
        b = tk.Button(parent,text=text,command=cmd,
            bg=T["tab_bg"],fg=T["text"],relief="flat",bd=0,
            padx=8 if compact else 12,pady=5,cursor="hand2",
            font=("Segoe UI Variable",9,"bold"),activebackground=T["btn_hover"])
        b.pack(side="left",padx=(6,0),pady=4)
        return b

    def _refresh_tabs(self):
        T = self.T
        tab_map = [
            (self._tab_tasks,  "active"),
            (self._tab_archive,"archive"),
            (self._tab_habits, "habits"),
            (self._tab_docs,   "docs"),
            (self._tab_stats,  "stats"),
            (self._tab_search, "search"),
        ]
        for tab, name in tab_map:
            tab.configure(bg=T["btn_bg"] if self.current_tab==name else T["tab_bg"], fg=T["text"])
        if self._trash_items() or self._trash_docs():
            self._tab_bin.pack(side="left",padx=(6,0),pady=4)
            self._tab_bin.configure(bg=T["btn_bg"] if self.current_tab=="trash" else T["tab_bg"], fg=T["text"])
        else:
            self._tab_bin.pack_forget()
            if self.current_tab == "trash":
                self.current_tab = "active"
        if hasattr(self,"entry_area") and self.entry_area.winfo_exists():
            self.entry_area.pack_forget()
        if hasattr(self,"search_area") and self.search_area.winfo_exists():
            self.search_area.pack_forget()
        if self.current_tab == "search":
            if hasattr(self,"search_area") and self.search_area.winfo_exists():
                self.search_area.pack(fill="x")
            if hasattr(self,"search_entry") and self.search_entry.winfo_exists():
                self.root.after(10, self.search_entry.focus_set)
        elif self.current_tab == "active":
            if hasattr(self,"entry_area") and self.entry_area.winfo_exists():
                self.entry_area.pack(fill="x")

    def _set_tab(self, name):
        self.current_tab = name
        self._refresh_tabs()
        self.entry.configure(state="normal" if name=="active" else "disabled")
        self._render_tasks()
        self.canvas.yview_moveto(0.0)

    # ── scroll ────────────────────────────────────────────────────────────────
    def _update_scroll(self): self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def _scroll(self, e):
        if   getattr(e,"num",None)==4: d=-1
        elif getattr(e,"num",None)==5: d=1
        else:
            delta = getattr(e,"delta",0)
            d = -1 if delta>0 else (1 if delta<0 else 0)
        if d==0: return "break"
        top,_ = self.canvas.yview()
        if d<0 and top<=0: self.canvas.yview_moveto(0.0); return "break"
        self.canvas.yview_scroll(d,"units")
        top,_ = self.canvas.yview()
        if top<0: self.canvas.yview_moveto(0.0)
        return "break"
    def _ctrl_scroll(self, e):
        self._set_scale(self.cfg.get("ui_scale",1.0) + (0.05 if (getattr(e,"num",None)==4 or getattr(e,"delta",0)>0) else -0.05))

    # ── task pools ────────────────────────────────────────────────────────────
    def _active_tasks(self):
        now = now_dt()
        return [t for t in self.tasks
            if not t.get("deleted") and not (
                t.get("done") and t.get("completed_at") and
                now - parse_iso(t["completed_at"]) > datetime.timedelta(days=1)
            )]

    def _archived_tasks(self):
        now = now_dt()
        return [t for t in self.tasks
            if not t.get("deleted") and t.get("done") and t.get("completed_at") and
               now - parse_iso(t["completed_at"]) > datetime.timedelta(days=1)]

    def _search_pool(self):
        q = self.search_var.get().strip().lower()
        if not q: return [t for t in self.tasks if not t.get("deleted")]
        out = []
        for t in self.tasks:
            if t.get("deleted"): continue
            blob = [t.get("text",""), t.get("priority","")]
            blob += [s.get("text","") for s in t.get("subtasks",[])]
            if q in " ".join(blob).lower(): out.append(t)
        return out

    # ── render ────────────────────────────────────────────────────────────────
    def _render_tasks(self):
        self._subtask_label_registry = {}
        self._subtask_check_registry = {}
        for w in self.task_frame.winfo_children(): w.destroy()
        now_ts = datetime.datetime.now().timestamp()
        if now_ts - getattr(self,"_last_purge_ts",0) > 60:
            self._purge_old_trash(); self._purge_old_doc_trash()
            self._last_purge_ts = now_ts
        T = self.T
        if   self.current_tab=="active":  self._render_active(T)
        elif self.current_tab=="archive": self._render_archive(T)
        elif self.current_tab=="trash":   self._render_trash(T)
        elif self.current_tab=="search":  self._render_pool(self._search_pool(), T, searching=True)
        elif self.current_tab=="stats":   self._render_stats(T)
        elif self.current_tab=="docs":    self._render_docs(T)
        elif self.current_tab=="habits":  self._render_habits(T)
        else:                             self._render_active(T)

        tk.Frame(self.task_frame, bg=T["bg"], height=60).pack(fill="x")
        self._update_scroll()
        self._refresh_tabs()
        self.root.after(50, lambda: self._bind_ctrl_wheel_recursive(self.task_frame))
        open_count    = len([t for t in self.tasks if not t.get("deleted") and not t.get("done")])
        archive_count = len(self._archived_tasks())
        parts = [f"Tasks: {open_count}", f"Archive: {archive_count}"]
        trash_count = len(self._trash_items())
        if trash_count: parts.append(f"Trash: {trash_count}")
        self.status_var.set(" · ".join(parts))

    # ── feature 1: two-section active list ───────────────────────────────────
    def _render_active(self, T):
        pool    = self._active_tasks()
        unsolved = [t for t in pool if not t.get("done")]
        solved   = [t for t in pool if t.get("done")]
        if not unsolved and not solved:
            tk.Label(self.task_frame,text="No tasks yet.\nAdd one above ↑",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=28).pack(fill="x")
            return
        for task in unsolved:
            self._task_row(task)
        if solved:
            sep = tk.Frame(self.task_frame,bg=T["separator"],height=1); sep.pack(fill="x",pady=(4,2))
            tk.Label(self.task_frame,text="✓ Completed",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8,"bold"),
                anchor="w",padx=6).pack(fill="x")
            for task in solved:
                self._task_row(task)

    # ── archive render (feat 3 – unsolve + delete) ────────────────────────────
    def _render_archive(self, T):
        pool = sorted(self._archived_tasks(), key=lambda t:t.get("completed_at",""), reverse=True)
        if not pool:
            tk.Label(self.task_frame,text="Archive is empty.",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=28).pack(fill="x")
            return
        for task in pool:
            self._task_row(task, archived=True)



    def _sync_doc_backup(self, doc, folder):
        """Write doc as a markdown file in the backup folder."""
        import re, os
        safe = re.sub(r'[\\/:*?"<>|]',"_", doc.get("title","Untitled"))[:60] or "Untitled"
        path = os.path.join(folder, safe+".md")
        try:
            os.makedirs(folder, exist_ok=True)
            with open(path,"w",encoding="utf-8") as f:
                f.write(f"# {doc.get('title','Untitled')}\n\n{doc.get('body','')}")
        except Exception:
            pass

    def _render_trash(self, T):
        tasks = sorted(self._trash_items(), key=lambda t:t.get("deleted_at",""), reverse=True)
        docs  = sorted(self._trash_docs(),  key=lambda d:d.get("deleted_at",""), reverse=True)
        if not tasks and not docs:
            tk.Label(self.task_frame,text="Bin is empty.",bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=28).pack(fill="x")
            return
        if tasks:
            for task in tasks:
                self._task_row(task, trashed=True)
        if docs:
            tk.Label(self.task_frame,text="- Deleted Docs -",bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),pady=4).pack(fill="x")
            for doc in docs:
                self._trash_doc_row(doc, T)

    def _trash_doc_row(self, doc, T):
        row = tk.Frame(self.task_frame,bg=T["item_bg"],pady=4,padx=6); row.pack(fill="x",pady=2)
        tw  = tk.Frame(row,bg=T["item_bg"]); tw.pack(side="left",fill="x",expand=True)
        tk.Label(tw,text=doc.get("title","Untitled"),bg=T["item_bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10,"bold"),anchor="w").pack(anchor="w")
        deleted_at = doc.get("deleted_at","")
        if deleted_at:
            remain = max(0,int((datetime.timedelta(hours=TRASH_HOURS)-(now_dt()-parse_iso(deleted_at))).total_seconds()//3600))
            tk.Label(tw,text=f"~{remain}h left",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),anchor="w").pack(anchor="w")
        bf = tk.Frame(row,bg=T["item_bg"]); bf.pack(side="right")
        def restore_doc(d=doc):
            all_docs=load_docs()
            for dd in all_docs:
                if dd.get("id")==d.get("id"):
                    dd.pop("deleted",None); dd.pop("deleted_at",None); break
            save_docs(all_docs); self._render_tasks()
        _del_doc_ref = [None]
        def del_doc_confirm(btn_r=_del_doc_ref, d=doc):
            b = btn_r[0]
            if b is None: return
            if getattr(b,"_confirm",False):
                all_docs=[x for x in load_docs() if x.get("id")!=d.get("id")]
                save_docs(all_docs); self._render_tasks()
            else:
                b._confirm = True; b.configure(text="Sure?",fg=T["close_hover"])
                b.after(2000, lambda: (setattr(b,"_confirm",False),
                    b.configure(text="🗑",fg=T["text"])) if b.winfo_exists() else None)
        tk.Button(bf,text="↺",command=restore_doc,
            bg=T["item_bg"],fg=T["text"],relief="flat",bd=0,padx=4,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),cursor="hand2",
            activebackground=T["item_hover"]).pack(side="right")
        del_doc_btn = tk.Button(bf,text="🗑",command=del_doc_confirm,
            bg=T["item_bg"],fg=T["text"],relief="flat",bd=0,padx=4,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),cursor="hand2",
            activebackground=T["item_hover"])
        del_doc_btn._confirm=False; _del_doc_ref[0]=del_doc_btn
        del_doc_btn.pack(side="right")


    # ── doc drag-reorder ──────────────────────────────────────────────────────
    def _doc_drag_start(self, e, idx):
        self._drag_doc_idx  = idx
        self._drag_start_y  = e.y_root
        self._drag_moved    = False

    def _doc_drag_motion(self, e):
        if not hasattr(self,"_drag_doc_idx"): return
        if abs(e.y_root - self._drag_start_y) > 4:
            self._drag_moved = True

    def _doc_drag_end(self, e):
        if not hasattr(self,"_drag_doc_idx") or not getattr(self,"_drag_moved",False):
            self._drag_doc_idx = None; return
        src = self._drag_doc_idx
        self._drag_doc_idx = None; self._drag_moved = False
        # find which cell the pointer is over
        gh = getattr(self,"_doc_grid_host",None)
        if not gh or not gh.winfo_exists(): return
        cells = gh.grid_slaves()
        target = None
        for cell in cells:
            cx = cell.winfo_rootx(); cy = cell.winfo_rooty()
            if cx <= e.x_root <= cx+cell.winfo_width() and cy <= e.y_root <= cy+cell.winfo_height():
                # find index of this cell
                info = cell.grid_info()
                row,col = info.get("row",0), info.get("column",0)
                cols = max(2, gh.winfo_width()//140)
                target = row*cols + col
                break
        if target is None or target == src: return
        docs = [d for d in load_docs() if not d.get("deleted")]
        if src < len(docs) and target < len(docs):
            docs.insert(target, docs.pop(src))
            # now rebuild full list preserving deleted items
            all_docs = load_docs()
            deleted  = [d for d in all_docs if d.get("deleted")]
            save_docs(docs + deleted)
            if self.current_tab == "docs": self._render_tasks()

    def _render_pool(self, pool, T, trashed=False, searching=False):
        if not pool:
            if trashed:    msg = "Bin is empty."
            elif searching: msg = "No search results."
            else:           msg = "Empty."
            tk.Label(self.task_frame,text=msg,bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=28).pack(fill="x")
            return
        for task in pool:
            self._task_row(task, trashed=trashed, searching=searching)

    # ── feature 2: gamification stats ────────────────────────────────────────
    def _render_stats(self, T):
        created  = self.cfg.get("tasks_created",0)
        done     = self.cfg.get("tasks_done",0)
        xp       = self.cfg.get("xp",0)
        lvl      = _compute_level(xp)
        xp_cur   = xp - _xp_for_level(lvl)
        xp_next  = _xp_for_level(lvl+1) - _xp_for_level(lvl)
        pct      = min(1.0, xp_cur/xp_next) if xp_next>0 else 1.0

        f = tk.Frame(self.task_frame, bg=T["bg"]); f.pack(fill="x",padx=12,pady=10)
        # header
        tk.Label(f,text="🎮  Productivity",bg=T["bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),12,"bold")).pack(anchor="w",pady=(0,8))
        # level badge
        badge_f = tk.Frame(f,bg=T["header_bg"]); badge_f.pack(fill="x",pady=(0,6))
        tk.Label(badge_f,text=f"⭐ Level {lvl}",bg=T["header_bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),13,"bold"),pady=6,padx=10).pack(side="left")
        tk.Label(badge_f,text=f"{xp} XP total",bg=T["header_bg"],fg=T["muted"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),padx=10).pack(side="right",anchor="center")
        # progress bar
        bar_host = tk.Frame(f,bg=T["separator"],height=8); bar_host.pack(fill="x",pady=(0,4))
        _bar_drawn = [False]
        def _draw_bar(bh=bar_host,p=pct,col=T["check_done"],flag=_bar_drawn):
            bw = bh.winfo_width()
            if bw < 2:
                bh.after(50, lambda: _draw_bar(bh,p,col,flag))
                return
            for w in bh.winfo_children(): w.destroy()
            tk.Frame(bh,bg=col,height=8,width=max(0,int(bw*p))).place(x=0,y=0)
            flag[0] = True
        bar_host.bind("<Configure>", lambda e,fn=_draw_bar: fn())
        bar_host.after(30, _draw_bar)
        tk.Label(f,text=f"  {xp_cur} / {xp_next} XP to level {lvl+1}",
            bg=T["bg"],fg=T["muted"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(anchor="w",pady=(0,8))
        # stats grid
        stats = [
            ("📝 Created",   created),
            ("✅ Completed",  done),
            ("🔓 Open",       len([t for t in self.tasks if not t.get("deleted") and not t.get("done")])),
            ("📦 Archived",   len(self._archived_tasks())),
        ]
        gf = tk.Frame(f,bg=T["bg"]); gf.pack(fill="x")
        for i,(label,val) in enumerate(stats):
            cf = tk.Frame(gf,bg=T["item_bg"]); cf.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
            gf.grid_columnconfigure(0,weight=1); gf.grid_columnconfigure(1,weight=1)
            tk.Label(cf,text=str(val),bg=T["item_bg"],fg=T["check_done"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),16,"bold"),pady=4).pack()
            tk.Label(cf,text=label,bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(pady=(0,4))
        # motivational message
        msgs = ["Keep it up! 🚀","You are on a roll! 🔥","Great progress! ✨","Unstoppable! 💪"]
        tk.Label(f,text=msgs[lvl % len(msgs)],bg=T["bg"],fg=T["archive"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"italic"),pady=8).pack(anchor="w")

    # ── feature 8: Docs hub (square grid, trash, singleton window, inline rename) ─
    def _render_docs(self, T):
        all_docs = [d for d in load_docs() if not d.get("deleted")]
        tb = tk.Frame(self.task_frame,bg=T["bg"]); tb.pack(fill="x",padx=6,pady=(8,4))
        tk.Label(tb,text="📄  Docs",bg=T["bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),11,"bold")).pack(side="left")
        tk.Button(tb,text="+ New",command=self._new_doc,
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=8,pady=3,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right")
        # search bar
        sb = tk.Frame(self.task_frame,bg=T["bg"]); sb.pack(fill="x",padx=6,pady=(0,4))
        doc_search_var = tk.StringVar()
        se = tk.Entry(sb,textvariable=doc_search_var,bg=T["entry_bg"],fg=T["entry_fg"],
            insertbackground=T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            highlightthickness=1,highlightbackground=T["separator"],highlightcolor=T["check_done"])
        se.pack(side="left",fill="x",expand=True,ipady=4)
        ph_shown = [True]
        def _show_ph():
            if not doc_search_var.get(): se.insert(0,"🔍 Search docs…"); ph_shown[0]=True
        def _hide_ph(e):
            if ph_shown[0]: se.delete(0,"end"); ph_shown[0]=False
        def _on_search(*_):
            q = doc_search_var.get().strip().lower()
            if ph_shown[0]: q=""
            filtered = [d for d in all_docs if
                q in d.get("title","").lower() or q in d.get("body","").lower()] if q else all_docs
            self._doc_grid_docs = filtered
            if hasattr(self,"_grid_job"): self.root.after_cancel(self._grid_job)
            self._grid_job = self.root.after(80, lambda: self._relayout_doc_grid(
                self._doc_grid_host.winfo_width() or 320))
        se.bind("<FocusIn>", _hide_ph)
        se.bind("<FocusOut>", lambda e: (_show_ph() if not doc_search_var.get() else None))
        doc_search_var.trace_add("write", _on_search)
        self.root.after(10, _show_ph)
        if not all_docs:
            tk.Label(self.task_frame,text="No docs yet.\nClick + New to create one.",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=24).pack(fill="x")
            return
        docs = all_docs
        grid_host = tk.Frame(self.task_frame,bg=T["bg"]); grid_host.pack(fill="x",padx=6,pady=2)
        self._doc_grid_host = grid_host
        self._doc_grid_docs = docs
        self._doc_grid_T    = T
        def _debounce_grid(e, gh=grid_host):
            if hasattr(self,"_grid_job"): self.root.after_cancel(self._grid_job)
            self._grid_job = self.root.after(80, lambda: self._relayout_doc_grid(gh.winfo_width() or 320))
        grid_host.bind("<Configure>", _debounce_grid)
        self.root.after(120, lambda: self._relayout_doc_grid(grid_host.winfo_width() or 320))

    def _relayout_doc_grid(self, total_w):
        if not hasattr(self,"_doc_grid_host") or not self._doc_grid_host.winfo_exists(): return
        T    = self._doc_grid_T
        docs = self._doc_grid_docs
        for w in self._doc_grid_host.winfo_children(): w.destroy()
        cols    = max(2, total_w // 140)
        cell_w  = max(60, (total_w - (cols+1)*4) // cols)
        for i,doc in enumerate(docs):
            r,c = divmod(i,cols)
            CARD_H  = 280
            cell = tk.Frame(self._doc_grid_host,bg=T["item_bg"],
                width=cell_w,height=CARD_H); cell.grid(row=r,column=c,padx=2,pady=2,sticky="nsew")
            cell.grid_propagate(False)
            self._doc_grid_host.grid_columnconfigure(c,weight=1)
            self._doc_grid_host.grid_rowconfigure(r,weight=1)
            # inner layout: title fixed top, body expands to fill
            cell.rowconfigure(0,weight=0)
            cell.rowconfigure(1,weight=1)
            cell.columnconfigure(0,weight=1)
            title_txt = doc.get("title","Untitled")
            body_txt  = doc.get("body","")
            chars_per_line = max(8,(cell_w-16)//7)
            max_body_chars = chars_per_line * 20
            preview_raw = body_txt[:max_body_chars]+("…" if len(body_txt)>max_body_chars else "")
            tl = tk.Label(cell,text=title_txt,bg=T["item_bg"],fg=T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold"),
                anchor="nw",wraplength=cell_w-8,justify="left",padx=4,pady=3)
            tl.grid(row=0,column=0,sticky="ew",padx=0,pady=0)
            pl = tk.Label(cell,text=preview_raw,bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                anchor="nw",wraplength=cell_w-8,justify="left",padx=4,pady=1)
            pl.grid(row=1,column=0,sticky="nsew",padx=0,pady=(0,16))
            def trash_doc(d=doc):
                all_docs=load_docs()
                for dd in all_docs:
                    if dd.get("id")==d.get("id"):
                        dd["deleted"]=True; dd["deleted_at"]=now_dt().isoformat(timespec="seconds"); break
                save_docs(all_docs); self._render_tasks()
            del_btn = tk.Label(cell,text="✕",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),7),cursor="hand2",padx=2)
            del_btn.place(x=cell_w-16,y=3)
            del_btn.bind("<Button-1>", lambda e,fn=trash_doc: fn())
            tl.bind("<Button-1>",        lambda e,d=doc,l=tl: self._inline_rename_doc(d,l))
            tl.bind("<Double-Button-1>", lambda e,d=doc: self._open_doc(d))
            for w in (cell,pl):
                w.bind("<Double-Button-1>", lambda e,d=doc: self._open_doc(d))
            def _enter(e,ww=(cell,tl,pl,del_btn)):
                for w in ww[:3]: w.configure(bg=T["item_hover"])
                ww[3].configure(bg=T["item_hover"],fg=T["text"])
            def _leave(e,ww=(cell,tl,pl,del_btn)):
                for w in ww[:3]: w.configure(bg=T["item_bg"])
                ww[3].configure(bg=T["item_bg"],fg=T["muted"])
            for w in (cell,tl,pl):
                w.bind("<Enter>",_enter); w.bind("<Leave>",_leave)
            # drag to reorder
            for w in (cell,tl,pl):
                w.bind("<ButtonPress-1>",   lambda e,i=i: self._doc_drag_start(e,i))
                w.bind("<B1-Motion>",       self._doc_drag_motion)
                w.bind("<ButtonRelease-1>", self._doc_drag_end)

    def _inline_rename_doc(self, doc, label):
        label.place_forget()
        cell  = label.master
        cell_w = cell.winfo_width() or 120
        T = self.T
        var = tk.StringVar(value=doc.get("title",""))
        e = tk.Entry(cell,textvariable=var,bg=T["entry_bg"],fg=T["entry_fg"],
            insertbackground=T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold"),
            highlightthickness=1,highlightbackground=T["check_done"])
        e.place(x=0,y=0,width=cell_w,height=28)
        e.focus_set(); e.select_range(0,"end")
        _done=[False]
        def finish(*_):
            if _done[0]: return
            _done[0]=True
            new = var.get().strip() or "Untitled"
            try: e.destroy()
            except Exception: pass
            doc["title"]=new
            all_docs=load_docs()
            for i,d in enumerate(all_docs):
                if d.get("id")==doc.get("id"): all_docs[i]=doc; break
            save_docs(all_docs)
            if self.current_tab=="docs": self._render_tasks()
        e.bind("<Return>",finish)
        e.bind("<Escape>",lambda ev:(e.destroy(),))
        e.bind("<FocusOut>",lambda ev: self.root.after(80,finish))

    def _new_doc(self):
        d = {"id":str(uuid.uuid4()),"title":"New Doc","body":"",
             "created":now_dt().isoformat(timespec="seconds"),"deleted":False}
        docs = load_docs(); docs.insert(0,d); save_docs(docs)
        self._open_doc(d)

    def _open_doc(self, doc):
        wid = doc.get("id","")
        for w in self.root.winfo_children():
            if isinstance(w,tk.Toplevel) and getattr(w,"_doc_id",None)==wid:
                w.lift(); w.focus_force(); return
        win = tk.Toplevel(self.root)
        win._doc_id = wid
        win.title(f"Doc - {doc.get('title','Untitled')}")
        win.geometry("500x520")
        win.configure(bg=self.T["bg"])
        win.attributes("-topmost", True)
        T = self.T
        title_var = tk.StringVar(value=doc.get("title",""))
        tf = tk.Frame(win,bg=T["bg"]); tf.pack(fill="x",padx=10,pady=(10,4))
        tk.Label(tf,text="Title:",bg=T["bg"],fg=T["muted"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9)).pack(side="left")
        title_entry = tk.Entry(tf,textvariable=title_var,
            bg=T["entry_bg"],fg=T["entry_fg"],
            insertbackground=T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),11,"bold"),
            highlightthickness=1,highlightbackground=T["separator"])
        title_entry.pack(side="left",fill="x",expand=True,ipady=4,padx=(6,4))
        # inline done button beside title field
        _done_btn_ref = [None]
        _done_btn_ref[0] = tk.Button(tf,text="✓",width=2,
            bg=T["check_done"],fg="#ffffff",relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10,"bold"),
            cursor="hand2",activebackground=T["check_done"])
        _done_btn_ref[0].pack(side="left",ipady=1)
        body_frame = tk.Frame(win,bg=T["bg"]); body_frame.pack(fill="both",expand=True,padx=10,pady=4)
        body_sb = ttk.Scrollbar(body_frame,orient="vertical",style="LeSticky.Vertical.TScrollbar")
        body_text = tk.Text(body_frame,
            bg=T["entry_bg"],fg=T["entry_fg"],
            insertbackground=T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
            wrap="word",highlightthickness=1,yscrollcommand=body_sb.set,
            highlightbackground=T["separator"],padx=6,pady=6,
            undo=True,maxundo=100)
        body_sb.configure(command=body_text.yview)
        body_sb.pack(side="right",fill="y")
        body_text.pack(fill="both",expand=True)
        body_text.insert("1.0", doc.get("body",""))
        def save_doc():
            doc["title"] = title_var.get().strip() or "Untitled"
            doc["body"]  = body_text.get("1.0","end-1c")
            doc["updated"] = now_dt().isoformat(timespec="seconds")
            all_docs = load_docs()
            # remove old entry, prepend updated doc so it appears at top
            all_docs = [d for d in all_docs if d.get("id")!=doc.get("id")]
            all_docs.insert(0, doc)
            save_docs(all_docs)
            win.title(f"Doc - {doc['title']}")
            # sync backup md file if path configured
            bp = self.cfg.get("docs_backup_path","").strip()
            if bp:
                self._sync_doc_backup(doc, bp)
            if self.current_tab=="docs": self._render_tasks()
        def close_save():
            save_doc(); win.destroy()
        if _done_btn_ref[0]:
            _done_btn_ref[0].configure(command=close_save)
        # Enter on title → done
        title_entry.bind("<Return>", lambda e: close_save())
        title_entry.bind("<Escape>", lambda e: close_save())
        # Ctrl+Z / Ctrl+Y handled natively by tk.Text when undo=True

        bf = tk.Frame(win,bg=T["bg"]); bf.pack(fill="x",padx=10,pady=(0,10))
        tk.Button(bf,text="✓ Done",command=close_save,
            bg=T["check_done"],fg="#ffffff",relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold"),
            padx=12,pady=5,cursor="hand2",activebackground=T["check_done"]).pack(side="right")
        tk.Button(bf,text="💾 Save",command=save_doc,
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=10,pady=5,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right",padx=(0,6))
        win.protocol("WM_DELETE_WINDOW", close_save)

    # ── feature 9: Habits ────────────────────────────────────────────────────
    def _render_habits(self, T):
        data    = load_habits()
        habits  = data.get("habits",[])
        log     = data.get("log",{})
        today   = datetime.date.today().isoformat()

        tb = tk.Frame(self.task_frame,bg=T["bg"]); tb.pack(fill="x",padx=6,pady=(8,4))
        tk.Label(tb,text="🌱  Habits",bg=T["bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),11,"bold")).pack(side="left")
        tk.Button(tb,text="+ Habit",command=lambda: self._add_habit(data),
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=8,pady=3,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right")

        if not habits:
            tk.Label(self.task_frame,text="No habits yet.\nClick + Habit to add one.",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=24).pack(fill="x")
            return

        # ── overall summary bar ───────────────────────────────────────────
        all_days = sorted(log.keys(), reverse=True)
        total_checks = sum(len(v) for v in log.values())
        done_today_count = len(log.get(today,[]))
        total_h = len(habits)
        pct_today = done_today_count/total_h if total_h else 0
        summary = tk.Frame(self.task_frame,bg=T["item_bg"],pady=6,padx=10)
        summary.pack(fill="x",pady=(0,6))
        tk.Label(summary,text=f"Today: {done_today_count}/{total_h} done",
            bg=T["item_bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold")).pack(anchor="w")
        bar_bg = tk.Frame(summary,bg=T["separator"],height=5); bar_bg.pack(fill="x",pady=(3,0))
        def _draw_today_bar(bh=bar_bg,p=pct_today,col=T["check_done"]):
            bw=bh.winfo_width() or 200
            tk.Frame(bh,bg=col,height=5,width=max(0,int(bw*p))).place(x=0,y=0)
        bar_bg.after(20,_draw_today_bar)

        for h in habits:
            hid        = h["id"]
            done_today_h = hid in log.get(today,[])
            streak       = _habit_streak(hid,log)
            best         = _habit_best_streak(hid,log)
            total_h_days = _habit_total_days(hid,log)
            last_7       = _habit_last_n(hid,log,7)
            last_30      = _habit_last_n(hid,log,30)
            # mini 7-day dots
            dots_7 = "".join("●" if _habit_done_on(hid,log,i) else "○" for i in range(6,-1,-1))

            card = tk.Frame(self.task_frame,bg=T["item_bg"],pady=5,padx=8)
            card.pack(fill="x",pady=2)

            # top row: flame+streak, name, done-btn, delete-btn
            top = tk.Frame(card,bg=T["item_bg"]); top.pack(fill="x")
            flame = "🔥" if streak>0 else "○"
            tk.Label(top,text=f"{flame} {streak}d",bg=T["item_bg"],
                fg=T["check_done"] if streak>0 else T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10,"bold"),width=6).pack(side="left")

            tw = tk.Frame(top,bg=T["item_bg"]); tw.pack(side="left",fill="x",expand=True)
            name_lbl = tk.Label(tw,text=h.get("name","Habit"),bg=T["item_bg"],fg=T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),anchor="w")
            name_lbl.pack(anchor="w",fill="x",expand=True)
            name_lbl.bind("<Double-Button-1>",
                lambda e,lbl=name_lbl,hab=h,d=data: self._inline_rename_habit(lbl,hab,d))

            def del_habit(btn_ref=[None], hid=hid, data=data):
                if btn_ref[0] is None: return
                b = btn_ref[0]
                if getattr(b,"_confirm",False):
                    data["habits"] = [x for x in data["habits"] if x["id"]!=hid]
                    save_habits(data); self._render_tasks()
                else:
                    b._confirm = True
                    b.configure(text="Sure?",fg=T["close_hover"])
                    b.after(2000, lambda: (setattr(b,"_confirm",False),
                        b.configure(text="✕",fg=T["muted"])) if b.winfo_exists() else None)
            del_b = tk.Button(top,text="✕",bg=T["item_bg"],fg=T["muted"],relief="flat",bd=0,padx=4,
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),cursor="hand2",
                activebackground=T["item_hover"])
            del_b._confirm = False
            del_b.configure(command=lambda br=[del_b],hid=hid,data=data: del_habit(br,hid,data))
            del_b.pack(side="right")

            def toggle_habit(hid=hid, data=data, today=today):
                log2 = data.setdefault("log",{})
                day_log = log2.setdefault(today,[])
                if hid in day_log: day_log.remove(hid)
                else:              day_log.append(hid)
                save_habits(data); self._render_tasks()
            btn_text = "✓ Done" if done_today_h else "Mark done"
            btn_bg2  = T["check_done"] if done_today_h else T["btn_bg"]
            btn_fg2  = "#ffffff" if done_today_h else T["btn_fg"]
            tk.Button(top,text=btn_text,command=toggle_habit,
                bg=btn_bg2,fg=btn_fg2,relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
                padx=8,pady=3,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right",padx=(0,6))

            # 7-day mini heatmap row
            dot_row = tk.Frame(card,bg=T["item_bg"]); dot_row.pack(fill="x",pady=(2,0))
            tk.Label(dot_row,text="7d: ",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(side="left")
            for di,done_dot in enumerate(
                    [_habit_done_on(hid,log,6-j) for j in range(7)]):
                col_dot = T["check_done"] if done_dot else T["separator"]
                tk.Frame(dot_row,bg=col_dot,width=10,height=10).pack(side="left",padx=1,pady=1)

            # stats disclosure row
            stats_frame = tk.Frame(card,bg=T["item_bg"]); # packed when expanded

            def _toggle_stats(sf=stats_frame, hid=hid, best=best,
                               total=total_h_days, l7=last_7, l30=last_30,
                               created=h.get("created",""), T=T, data=data):
                if sf.winfo_ismapped():
                    sf.pack_forget(); return
                for w in sf.winfo_children(): w.destroy()
                # compute per-weekday breakdown
                wd_counts = [0]*7
                wd_totals = [0]*7
                all_log_dates = sorted(log.keys())
                if all_log_dates:
                    d0 = datetime.date.fromisoformat(all_log_dates[0])
                    d1 = datetime.date.today()
                    dd = d0
                    while dd <= d1:
                        wd = dd.weekday()
                        wd_totals[wd] += 1
                        if hid in log.get(dd.isoformat(),[]):
                            wd_counts[wd] += 1
                        dd += datetime.timedelta(days=1)
                wd_names = ["Mo","Tu","We","Th","Fr","Sa","Su"]
                # last-14-day bar
                bar14 = [_habit_done_on(hid,log,13-j) for j in range(14)]
                days_since = ""
                if created:
                    try:
                        age = (datetime.date.today()-datetime.date.fromisoformat(created[:10])).days
                        days_since = f"{age}d old"
                    except Exception: pass
                consistency = f"{int(total/max(1,(datetime.date.today()-datetime.date.fromisoformat(all_log_dates[0])).days+1)*100)}%" if all_log_dates else "-"

                sf.pack(fill="x",pady=(4,0))
                inner = tk.Frame(sf,bg=T["bg"],padx=8,pady=6); inner.pack(fill="x")
                # stats grid
                stats_data = [
                    ("🔥 Current streak", f"{_habit_streak(hid,log)}d"),
                    ("🏆 Best streak",     f"{best}d"),
                    ("✅ Total done",       f"{total}d"),
                    ("📅 Last 7 days",     f"{l7}/7"),
                    ("📆 Last 30 days",    f"{l30}/30"),
                    ("📈 Consistency",     consistency),
                    ("🗓 Habit age",       days_since or "-"),
                ]
                for row_i,(lbl,val) in enumerate(stats_data):
                    r,c = divmod(row_i,2)
                    cell = tk.Frame(inner,bg=T["bg"]); cell.grid(row=r,column=c,sticky="w",padx=(0,16),pady=1)
                    tk.Label(cell,text=lbl,bg=T["bg"],fg=T["muted"],
                        font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(side="left")
                    tk.Label(cell,text=" "+val,bg=T["bg"],fg=T["text"],
                        font=(self.cfg.get("ui_font","Segoe UI Variable"),8,"bold")).pack(side="left")
                # weekday breakdown row
                wd_row = tk.Frame(inner,bg=T["bg"]); wd_row.grid(row=4,column=0,columnspan=2,sticky="w",pady=(6,2))
                tk.Label(wd_row,text="Weekday: ",bg=T["bg"],fg=T["muted"],
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(side="left")
                for wdi in range(7):
                    pct2 = wd_counts[wdi]/wd_totals[wdi] if wd_totals[wdi] else 0
                    shade = int(30+180*pct2)
                    hex_col = T["check_done"] if pct2>0.6 else (T["btn_bg"] if pct2>0.3 else T["separator"])
                    wf = tk.Frame(wd_row,bg=T["bg"]); wf.pack(side="left",padx=2)
                    tk.Frame(wf,bg=hex_col,width=14,height=14).pack()
                    tk.Label(wf,text=wd_names[wdi],bg=T["bg"],fg=T["muted"],
                        font=(self.cfg.get("ui_font","Segoe UI Variable"),7)).pack()
                # 14-day mini bar chart
                bar_host2 = tk.Frame(inner,bg=T["bg"]); bar_host2.grid(row=5,column=0,columnspan=2,sticky="w",pady=(4,0))
                tk.Label(bar_host2,text="14d: ",bg=T["bg"],fg=T["muted"],
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(side="left")
                for b14 in bar14:
                    tk.Frame(bar_host2,bg=T["check_done"] if b14 else T["separator"],
                        width=12,height=12).pack(side="left",padx=1)

            # small "▸ Stats" toggle label
            stl = tk.Label(card,text="▸ Stats",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),cursor="hand2")
            stl.pack(anchor="w",pady=(2,0))
            def _toggle_wrap(sf=stats_frame,l=stl,fn=_toggle_stats):
                fn()
                l.configure(text="▾ Stats" if sf.winfo_ismapped() else "▸ Stats")
            stl.bind("<Button-1>",lambda e,fn=_toggle_wrap: fn())

        # new habit entry at bottom
        add_f = tk.Frame(self.task_frame,bg=T["bg"],pady=4); add_f.pack(fill="x",padx=6)
        tk.Button(add_f,text="+ New Habit",command=lambda: self._add_habit(data),
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=10,pady=4,cursor="hand2",activebackground=T["btn_hover"]).pack(pady=8)

    def _add_habit(self, data):
        new_h = {"id": str(uuid.uuid4()), "name": "New Habit",
                 "created": datetime.date.today().isoformat()}
        data.setdefault("habits",[]).append(new_h)
        save_habits(data)
        self._render_tasks()

    def _inline_rename_habit(self, label, habit, data):
        label.pack_forget()
        parent = label.master
        T = self.T
        var = tk.StringVar(value=habit.get("name",""))
        e = tk.Entry(parent, textvariable=var, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
            highlightthickness=1, highlightbackground=T["check_done"])
        e.pack(anchor="w", fill="x", expand=True)
        e.focus_set(); e.select_range(0, "end")
        _done = [False]
        def finish(*_):
            if _done[0]: return
            _done[0] = True
            new = var.get().strip()
            try: e.destroy()
            except Exception: pass
            if new:
                habit["name"] = new
                save_habits(data)
            self._render_tasks()
        e.bind("<Return>", finish)
        e.bind("<Escape>", lambda ev: (e.destroy(),))
        e.bind("<FocusOut>", lambda ev: self.root.after(80, finish))

    # ── task row ──────────────────────────────────────────────────────────────
    def _task_row(self, task, archived=False, trashed=False, searching=False):
        T = self.T
        row = tk.Frame(self.task_frame,bg=T["item_bg"],pady=3,padx=4); row.pack(fill="x",pady=2)
        row._task_ref = task
        action_buttons = []

        def paint(bg):
            for w in _paint_widgets:
                try: w.configure(bg=bg)
                except Exception: pass
            for b in action_buttons:
                try: b.configure(bg=bg)
                except Exception: pass
            if drag_lbl: drag_lbl.configure(bg=bg)

        row.bind("<Enter>", lambda e: paint(T["item_hover"]))
        row.bind("<Leave>", lambda e: paint(T["item_bg"]))

        pri = task.get("priority","none")
        pri_color = T.get(pri, T["separator"]) if pri!="none" else T["separator"]
        tk.Frame(row,bg=pri_color,width=5).pack(side="left",fill="y",padx=(0,4))

        drag_lbl = None
        if not archived and not trashed and not searching:
            drag_lbl = tk.Label(row,text="⋮⋮",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),cursor="fleur",width=2)
            drag_lbl.pack(side="left",padx=(0,2))
            drag_lbl.bind("<ButtonPress-1>",  lambda e,t=task: self._dt_start(t))
            drag_lbl.bind("<ButtonRelease-1>",lambda e,t=task: self._dt_drop(e,t))

        is_done = task.get("done",False)
        var = tk.BooleanVar(value=is_done)
        chk = tk.Checkbutton(row,variable=var,bg=T["item_bg"],activebackground=T["item_bg"],
            selectcolor=T["check_done"] if is_done else T["item_bg"],
            relief="flat",bd=0,highlightthickness=0,
            state="disabled" if (archived or trashed or searching) else "normal",
            command=lambda v=var,t=task: self._toggle(t,v))
        chk.pack(side="left",padx=(2,4))

        style = ("Segoe UI Variable",10,"overstrike") if is_done else (self.cfg.get("ui_font","Segoe UI Variable"),10)
        fg    = T["muted"] if is_done else T["text"]
        tw    = tk.Frame(row,bg=T["item_bg"]); tw.pack(side="left",fill="x",expand=True)

        # Feature 4: wraplength uses full available width dynamically
        def _make_lbl(tw=tw,task=task,style=style,fg=fg):
            lbl = tk.Label(tw,text=task["text"],bg=T["item_bg"],fg=fg,
                font=style,anchor="w",justify="left",wraplength=1)
            lbl.pack(anchor="w",fill="x",expand=True)
            def _update_wrap(e,l=lbl): l.configure(wraplength=max(60,e.width-4))
            tw.bind("<Configure>", _update_wrap, add="+")
            lbl.bind("<Configure>", lambda e,l=lbl,t=tw: l.configure(wraplength=max(60,t.winfo_width()-4)))
            return lbl
        lbl = _make_lbl()

        if not archived and not trashed and not searching:
            lbl.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._inline_edit_task(p,l,t))
            tw.bind("<Double-Button-1>",  lambda e,p=tw,l=lbl,t=task: self._body_dblclick(e,p,l,t))
            row.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._body_dblclick(e,p,l,t))

        for st in task.get("subtasks",[]):
            sf = tk.Frame(tw,bg=T["item_bg"]); sf.pack(anchor="w",fill="x")
            sv = tk.BooleanVar(value=st.get("done",False))
            sc = tk.Checkbutton(sf,variable=sv,bg=T["item_bg"],activebackground=T["item_bg"],
                selectcolor=T["check_done"] if st.get("done") else T["item_bg"],
                relief="flat",bd=0,highlightthickness=0,
                state="disabled" if (archived or trashed or searching) else "normal",
                command=lambda sv=sv,sub=st,ta=task: self._toggle_subtask(ta,sub,sv))
            sc.pack(side="left")
            self._subtask_check_registry[id(st)] = sc
            sl = tk.Label(sf,text=st.get("text",""),bg=T["item_bg"],
                fg=T["muted"] if st.get("done") else T["text"],
                font=("Segoe UI Variable",8,"overstrike" if st.get("done") else "normal"),
                anchor="w",justify="left")
            sl.pack(side="left",anchor="w",fill="x",expand=True)
            self._subtask_label_registry[id(st)] = sl  # track for in-place update
            if not archived and not trashed and not searching:
                sl.bind("<Double-Button-1>", lambda e,parent=sf,lab=sl,ta=task,sub=st: self._inline_edit_subtask(parent,lab,ta,sub))
            if st.get("_editing") and not archived and not trashed and not searching:
                self.root.after(10, lambda parent=sf,lab=sl,ta=task,sub=st: self._inline_edit_subtask(parent,lab,ta,sub))

        dt      = parse_iso(task["completed_at"]) if is_done and task.get("completed_at") else parse_iso(task["created"])
        meta_txt = (f"Resolved {fmt_dt(dt)}" if is_done and task.get("completed_at") else f"Created {fmt_dt(dt)}")
        if pri!="none": meta_txt += f" · {pri.capitalize()}"
        if trashed and task.get("deleted_at"):
            remain = max(0, int((datetime.timedelta(hours=TRASH_HOURS)-(now_dt()-parse_iso(task["deleted_at"]))).total_seconds()//3600))
            meta_txt += f" · ~{remain}h left"
        meta = tk.Label(tw,text=meta_txt,bg=T["item_bg"],
            fg=T["archive"] if archived else T["muted"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8),anchor="w")
        meta.pack(anchor="w")

        _paint_widgets = [row,tw,lbl,meta]

        def mk_btn(txt, cmd_fn):
            b = tk.Button(row,text=txt,command=cmd_fn,bg=T["item_bg"],fg=T["text"],
                relief="flat",bd=0,padx=4,pady=0,
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
                cursor="hand2",activebackground=T["item_hover"])
            b.pack(side="right"); action_buttons.append(b); return b

        if trashed:
            mk_btn("↺", lambda t=task: self._recover_task(t))
            # double-confirm delete
            _del_btn_ref = [None]
            def _confirm_del_task(btn_r=_del_btn_ref, t=task):
                b = btn_r[0]
                if b is None: return
                if getattr(b,"_confirm",False):
                    self._delete_forever(t)
                else:
                    b._confirm = True; b.configure(text="Sure?",fg=self.T["close_hover"])
                    b.after(2000, lambda: (setattr(b,"_confirm",False),
                        b.configure(text="🗑",fg=self.T["text"])) if b.winfo_exists() else None)
            _del_b = mk_btn("🗑", _confirm_del_task)
            if _del_b: _del_b._confirm=False; _del_btn_ref[0]=_del_b
        elif archived:
            # Feature 3: unsolve + delete in archive
            mk_btn("↩ Unsolve", lambda t=task: self._unsolve_task(t))
            mk_btn("🗑",        lambda t=task: self._trash_task(t))
        elif not searching:
            mk_btn("🗑", lambda t=task: self._trash_task(t))
            mk_btn("⊞", lambda t=task: self._add_subtask(t))
            mk_btn("!", lambda t=task: self._cycle_priority(t))
            mk_btn("✎", lambda t=task,p=tw,l=lbl: self._inline_edit_task(p,l,t))

    # ── drag-drop ─────────────────────────────────────────────────────────────
    def _dt_start(self, t): self._dragging_task = t
    def _dt_drop(self, e, src):
        w = e.widget.winfo_containing(e.x_root, e.y_root); tgt = None
        while w:
            if getattr(w,"_task_ref",None): tgt=w._task_ref; break
            w = getattr(w,"master",None)
        if tgt and tgt is not src:
            fi,ti = self.tasks.index(src), self.tasks.index(tgt)
            self.tasks.pop(fi); self.tasks.insert(max(0,ti if fi>ti else ti-1), src)
            save_tasks(self.tasks)
        self._render_tasks()

    def _body_dblclick(self, e, parent, label, task):
        if e.widget.winfo_class() in ("Checkbutton","Button","Entry"): return
        self._inline_edit_task(parent, label, task)

    # ── Feature 5+7: inline edit task (multiline + click-outside submit) ─────
    def _inline_edit_task(self, parent, label, task):
        text_val = task.get("text","")
        use_multi = len(text_val) > 60 or "\n" in text_val
        label.pack_forget()
        if use_multi:
            # Feature 5: multi-line text widget for long texts
            ef = tk.Frame(parent,bg=self.T["entry_bg"]); ef.pack(anchor="w",fill="x")
            entry = tk.Text(ef,
                bg=self.T["entry_bg"],fg=self.T["entry_fg"],
                insertbackground=self.T["entry_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                wrap="word",height=4,
                highlightthickness=1,
                highlightbackground=self.T["check_done"],padx=2,pady=2)
            entry.pack(fill="x")
            entry.insert("1.0", text_val)
            entry.focus_set()
            _finished = [False]
            def finish(save=True, _e=None):
                if _finished[0]: return
                _finished[0] = True
                new = entry.get("1.0","end-1c").strip()
                try: ef.destroy()
                except Exception: pass
                if save and new: task["text"]=new; save_tasks(self.tasks)
                self._render_tasks()
            entry.bind("<Escape>",      lambda e: finish(False))
            entry.bind("<Control-Return>", lambda e: finish(True))
            # Feature 7: click outside submits
            entry.bind("<FocusOut>",    lambda e: self.root.after(80,lambda: finish(True)))
        else:
            entry = tk.Entry(parent,
                bg=self.T["entry_bg"],fg=self.T["entry_fg"],
                insertbackground=self.T["entry_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10))
            entry.insert(0, text_val)
            entry.pack(anchor="w",fill="x")
            entry.focus_set(); entry.select_range(0,"end")
            _finished = [False]
            def finish(save=True, _e=None):
                if _finished[0]: return
                _finished[0] = True
                new = entry.get().strip()
                try: entry.destroy()
                except Exception: pass
                if save and new: task["text"]=new; save_tasks(self.tasks)
                np = self.cfg.get("obsidian_note_path","").strip()
                if np and save and new: sync_note(np,task)
                self._render_tasks()
            entry.bind("<Return>",   lambda e: finish(True))
            entry.bind("<Escape>",   lambda e: finish(False))
            # Feature 7: click outside submits
            entry.bind("<FocusOut>", lambda e: self.root.after(80,lambda: finish(True)))

    # ── Feature 6+7: inline edit subtask ─────────────────────────────────────
    def _inline_edit_subtask(self, parent, label, task, subtask):
        entry = tk.Entry(parent,
            bg=self.T["entry_bg"],fg=self.T["entry_fg"],
            insertbackground=self.T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8))
        entry._subtask_ref = subtask  # tag for flush lookup
        entry.insert(0, subtask.get("text",""))
        label.pack_forget(); entry.pack(side="left",fill="x",expand=True)
        entry.focus_set(); entry.select_range(0,"end")
        _finished = [False]
        def finish(save=True, _e=None):
            if _finished[0]: return
            _finished[0] = True
            new = entry.get().strip()
            try: entry.destroy()
            except Exception: pass
            if save and new:
                subtask["text"]=new; subtask.pop("_editing",None)
                save_tasks(self.tasks)
                np = self.cfg.get("obsidian_note_path","").strip()
                if np: sync_note(np,task)
            elif not new:
                try: task.get("subtasks",[]).remove(subtask)
                except ValueError: pass
                save_tasks(self.tasks)
            self._render_tasks()
        entry.bind("<Return>",   lambda e: finish(True))
        entry.bind("<Escape>",   lambda e: finish(False))
        # Feature 7: click outside submits
        entry.bind("<FocusOut>", lambda e: self.root.after(80,lambda: finish(True)))

    # ── add task ──────────────────────────────────────────────────────────────
    def _add_task(self, e=None):
        text = self.entry_var.get().strip()
        if not text: return
        task = _norm({"id":str(uuid.uuid4()),"text":text,"done":False,
            "created":now_dt().isoformat(timespec="seconds"),"priority":"none","subtasks":[]})
        self.tasks.insert(0, task)
        self.entry_var.set("")
        # Feature 6: preserve currently-editing subtask names (handled by FocusOut)
        self.cfg["tasks_created"] = self.cfg.get("tasks_created",0)+1
        self.cfg["xp"]            = self.cfg.get("xp",0)+5
        save_config(self.cfg)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np,task)
        self.current_tab = "active"; self._render_tasks()

    # ── subtask ───────────────────────────────────────────────────────────────
    def _add_subtask(self, task):
        # flush any open subtask entry for THIS task before adding a new one
        self._flush_editing_subtasks(task)
        task.setdefault("subtasks",[]).append({"id":str(uuid.uuid4()),"text":"","done":False,"_editing":True})
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np,task)
        self._render_tasks()

    def _flush_editing_subtasks(self, task):
        """Commit text from any currently open subtask Entry widget belonging to task."""
        # Walk all Entry widgets in the task_frame and find those editing a subtask of task
        def _flush_widget(w):
            if isinstance(w, tk.Entry):
                # check if it has a subtask ref stored
                sub_ref = getattr(w, "_subtask_ref", None)
                if sub_ref is not None and sub_ref in task.get("subtasks",[]):
                    val = w.get().strip()
                    if val:
                        sub_ref["text"] = val
                        sub_ref.pop("_editing", None)
                    else:
                        try: task["subtasks"].remove(sub_ref)
                        except ValueError: pass
                    return
            for child in w.winfo_children():
                try: _flush_widget(child)
                except Exception: pass
        try: _flush_widget(self.task_frame)
        except Exception: pass

    def _toggle_subtask(self, task, sub, var):
        sub["done"] = var.get()
        if sub["done"]:
            self.cfg["xp"] = self.cfg.get("xp",0) + 3
        else:
            self.cfg["xp"] = max(0, self.cfg.get("xp",0) - 3)
        save_config(self.cfg)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np,task)
        # update subtask label style in place without full re-render
        lbl = getattr(self, "_subtask_label_registry", {}).get(id(sub))
        chk = getattr(self, "_subtask_check_registry", {}).get(id(sub))
        if lbl and lbl.winfo_exists():
            done = sub["done"]
            T = self.T
            lbl.configure(
                fg=T["muted"] if done else T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"), 8,
                      "overstrike" if done else "normal"))
            if chk and chk.winfo_exists():
                chk.configure(selectcolor=T["check_done"] if done else T["item_bg"])
        else:
            self._render_tasks()

    def _cycle_priority(self, task):
        cur = task.get("priority","none")
        task["priority"] = PRIORITIES[(PRIORITIES.index(cur)+1) % len(PRIORITIES)]
        save_tasks(self.tasks); self._render_tasks()

    # ── Feature 1: toggle moves solved task to correct section ───────────────
    def _toggle(self, task, var):
        task["done"] = var.get()
        if task["done"]:
            task["completed_at"] = now_dt().isoformat(timespec="seconds")
            # XP + stats
            self.cfg["tasks_done"] = self.cfg.get("tasks_done",0)+1
            self.cfg["xp"]         = self.cfg.get("xp",0)+15
            save_config(self.cfg)
            # Move: find first solved task in active pool and insert just before it
            # (so newest-solved is at top of solved section)
            self.tasks.remove(task)
            active_pool = [t for t in self.tasks
                if not t.get("deleted") and not (
                    t.get("done") and t.get("completed_at") and
                    now_dt() - parse_iso(t["completed_at"]) > datetime.timedelta(days=1)
                )]
            first_solved_idx = None
            for i,t in enumerate(active_pool):
                if t.get("done"):
                    first_solved_idx = self.tasks.index(t); break
            if first_solved_idx is not None:
                self.tasks.insert(first_solved_idx, task)
            else:
                # no solved tasks yet - append after last active
                last_active_idx = None
                for i,t in enumerate(self.tasks):
                    if not t.get("deleted") and not t.get("done"): last_active_idx=i
                self.tasks.insert((last_active_idx+1) if last_active_idx is not None else len(self.tasks), task)
        else:
            # Unsolve: move back to top of unsolved section, revert XP+stats
            task.pop("completed_at", None)
            self.tasks.remove(task)
            self.tasks.insert(0, task)
            self.cfg["tasks_done"] = max(0, self.cfg.get("tasks_done",0)-1)
            self.cfg["xp"]         = max(0, self.cfg.get("xp",0)-15)
            save_config(self.cfg)

        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np,task)
        self._render_tasks()

    # ── Feature 3: unsolve from archive ──────────────────────────────────────
    def _unsolve_task(self, task):
        task["done"] = False
        task.pop("completed_at", None)
        self.tasks.remove(task)
        self.tasks.insert(0, task)
        self.cfg["tasks_done"] = max(0, self.cfg.get("tasks_done",0)-1)
        self.cfg["xp"]         = max(0, self.cfg.get("xp",0)-15)
        save_config(self.cfg)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np,task)
        self.current_tab = "active"
        self._render_tasks()

    def _trash_task(self, task):
        task["deleted"]    = True
        task["deleted_at"] = now_dt().isoformat(timespec="seconds")
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: remove_from_note(np,task["id"])
        self.current_tab = "active"; self._render_tasks()

    def _recover_task(self, task):
        task["deleted"] = False; task.pop("deleted_at",None)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np,task)
        self._render_tasks()

    def _delete_forever(self, task):
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: remove_from_note(np,task["id"])
        self.tasks = [t for t in self.tasks if t["id"]!=task["id"]]
        save_tasks(self.tasks); self._render_tasks()

    # ── settings ──────────────────────────────────────────────────────────────
    def _open_settings(self):
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.lift(); return
        self._settings_widgets = {k:[] for k in ["frame_bg","section","label","muted","entry","button","check","radio","scale","swatch"]}
        win = tk.Toplevel(self.root)
        self._settings_win = win
        win.title("LeoNote - Settings")
        win.minsize(420,420)
        x = self.cfg["settings_x"] if self.cfg["settings_x"] is not None else self.root.winfo_x()+20
        y = self.cfg["settings_y"] if self.cfg["settings_y"] is not None else self.root.winfo_y()+40
        win.geometry(f"{self.cfg.get('settings_w',520)}x{self.cfg.get('settings_h',600)}+{x}+{y}")
        win.attributes("-topmost",True)
        win.bind("<Return>", lambda e: win.destroy())
        win.protocol("WM_DELETE_WINDOW", win.destroy)

        def remember(e=None):
            if e and e.widget==win:
                self.cfg.update(settings_x=win.winfo_x(),settings_y=win.winfo_y(),settings_w=win.winfo_width(),settings_h=win.winfo_height())
                save_config(self.cfg)
        win.bind("<Configure>", remember)

        body   = tk.Frame(win,bg=self.T["bg"]); body.pack(fill="both",expand=True)
        self._settings_widgets["frame_bg"].append(body)
        canvas = tk.Canvas(body,bg=self.T["bg"],bd=0,highlightthickness=0)
        sb     = ttk.Scrollbar(body,orient="vertical",command=canvas.yview,style="LeSticky.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        sf  = tk.Frame(canvas,bg=self.T["bg"])
        self._settings_widgets["frame_bg"].extend([sf,canvas])
        sfw = canvas.create_window((0,0),window=sf,anchor="nw")
        sf.bind("<Configure>",     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(sfw,width=e.width))

        def wheel(e):
            d = int(-1*(e.delta/120)) if getattr(e,"delta",0) else (-1 if getattr(e,"num",None)==4 else 1)
            canvas.yview_scroll(d,"units"); return "break"
        def bind_all(w):
            for seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
                try: w.bind(seq,wheel,add="+")
                except Exception: pass
            for ch in w.winfo_children(): bind_all(ch)
        win.after(120, lambda: bind_all(sf))

        def section(txt):
            f = tk.Frame(sf,bg=self.T["header_bg"]); f.pack(fill="x",pady=(10,2))
            l = tk.Label(f,text=txt,bg=self.T["header_bg"],fg=self.T["text"],
                font=("Segoe UI Variable",9,"bold"),anchor="w",padx=8,pady=5)
            l.pack(fill="x")
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["section"].append(l)

        def rowf(label,maker):
            f = tk.Frame(sf,bg=self.T["bg"]); f.pack(fill="x",padx=12,pady=4)
            l = tk.Label(f,text=label,bg=self.T["bg"],fg=self.T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),width=26,anchor="w")
            l.pack(side="left")
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["label"].append(l)
            maker(f); return f

        section("Obsidian (Optional)")
        note_var = tk.StringVar(value=self.cfg.get("obsidian_note_path",""))
        note_var.trace_add("write", lambda *a:(self.cfg.__setitem__("obsidian_note_path",note_var.get().strip()),save_config(self.cfg)))
        def note_row(p):
            e=tk.Entry(p,textvariable=note_var,bg=self.T["entry_bg"],fg=self.T["entry_fg"],
                insertbackground=self.T["entry_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
                highlightthickness=1,highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
            e.pack(side="left",fill="x",expand=True,ipady=4)
            b=tk.Button(p,text="📄",bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),padx=6,cursor="hand2",
                command=lambda:note_var.set(filedialog.asksaveasfilename(title="Select note",defaultextension=".md",filetypes=[("Markdown","*.md"),("All","*.*")]) or note_var.get()))
            b.pack(side="left",padx=(4,0))
            self._settings_widgets["entry"].append(e); self._settings_widgets["button"].append(b)
        rowf("Task note path:", note_row)

        section("Docs (Optional)")
        docs_path_var = tk.StringVar(value=self.cfg.get("docs_backup_path",""))
        docs_path_var.trace_add("write", lambda *a:(self.cfg.__setitem__("docs_backup_path",docs_path_var.get().strip()),save_config(self.cfg)))
        def docs_path_row(p):
            e=tk.Entry(p,textvariable=docs_path_var,bg=self.T["entry_bg"],fg=self.T["entry_fg"],
                insertbackground=self.T["entry_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
                highlightthickness=1,highlightbackground=self.T["separator"],highlightcolor=self.T["check_done"])
            e.pack(side="left",fill="x",expand=True,ipady=4)
            def _pick():
                import tkinter.filedialog as fd
                d=fd.askdirectory(title="Docs backup folder")
                if d: docs_path_var.set(d)
            b=tk.Button(p,text="📁",bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),padx=6,cursor="hand2",
                command=_pick,activebackground=self.T["btn_hover"])
            b.pack(side="left",padx=(4,0))
            self._settings_widgets["entry"].append(e); self._settings_widgets["button"].append(b)
        rowf("Docs backup folder:", docs_path_row)

        section("Theme")
        theme_var = tk.StringVar(value=self.cfg.get("theme","peach"))
        def apply_theme():
            self.cfg["theme"]=theme_var.get(); save_config(self.cfg)
            self._retheme_main_only()
            self.root.after(30,self._keep_settings_alive)
            if self._settings_win and self._settings_win.winfo_exists():
                self._settings_win.after(1,self._keep_settings_alive)
        tf = tk.Frame(sf,bg=self.T["bg"]); tf.pack(fill="x",padx=12,pady=4)
        self._settings_widgets["frame_bg"].append(tf)
        for i,(name,samp) in enumerate(THEMES.items()):
            f=tk.Frame(tf,bg=self.T["bg"]); f.grid(row=i//3,column=i%3,sticky="w",padx=6,pady=3)
            r=tk.Radiobutton(f,text=name.capitalize(),variable=theme_var,value=name,
                bg=self.T["bg"],fg=self.T["text"],activebackground=self.T["bg"],
                selectcolor=self.T["entry_bg"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),command=apply_theme)
            r.pack(side="left")
            preview_bg = samp["header_bg"]
            if name in {"dark","crimson","forest","emerald","midnight","space","violet-night","eclipse"}:
                preview_bg = samp["btn_bg"]
            sw=tk.Label(f,text="   ",bg=preview_bg,width=3); sw.pack(side="left",padx=(4,0))
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["radio"].append(r); self._settings_widgets["swatch"].append(sw)

        section("Display & Behavior")
        def live_toggle(label,key,callback=None):
            var=tk.BooleanVar(value=self.cfg.get(key,False))
            def apply_toggle():
                self.cfg[key]=var.get(); save_config(self.cfg)
                if callback: callback(var.get())
                if self._settings_win and self._settings_win.winfo_exists():
                    self._settings_win.after(1,self._keep_settings_alive)
            rowf(label, lambda p,vv=var: self._mk_check(p,vv,apply_toggle))
        live_toggle("Always on top:","always_on_top",lambda v:(self.root.attributes("-topmost",v),self._refresh_pin()))
        live_toggle("Show in tray:","show_in_tray",lambda v:self._setup_tray() if v else self._destroy_tray())
        live_toggle("Start hidden to tray:","start_hidden_to_tray")
        live_toggle("Show Windows title bar:","show_system_titlebar",lambda v:self._apply_window_mode())
        live_toggle("Display in taskbar:","show_in_taskbar",lambda v:self._apply_window_mode())
        live_toggle("Run at Windows startup:","run_at_startup",lambda v:self._apply_startup(v))

        section("UI Scale")
        scale_var = tk.DoubleVar(value=float(self.cfg.get("ui_scale",1.0)))
        def scale_row(p):
            sc=tk.Scale(p,variable=scale_var,from_=0.5,to=3.0,resolution=0.05,orient="horizontal",
                bg=self.T["bg"],fg=self.T["text"],troughcolor=self.T["separator"],
                activebackground=self.T["btn_hover"],highlightthickness=0,bd=0,length=220,
                command=lambda v:(self._set_scale(float(v)),self.root.after(10,self._keep_settings_alive)))
            sc.pack(side="left")
            lb=tk.Label(p,textvariable=scale_var,bg=self.T["bg"],fg=self.T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),width=5)
            lb.pack(side="left",padx=4)
            self._settings_widgets["scale"].append(sc); self._settings_widgets["label"].append(lb)
        rowf("Scale (0.5–3.0):", scale_row)
        m=tk.Label(sf,text="Close with Enter or window close button.",bg=self.T["bg"],fg=self.T["muted"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8),anchor="w",padx=12)
        m.pack(fill="x"); self._settings_widgets["muted"].append(m)

        section("Font")
        font_var = tk.StringVar(value=self.cfg.get("ui_font","Segoe UI Variable"))
        def apply_font():
            self.cfg["ui_font"]=font_var.get(); save_config(self.cfg)
            self._retheme_main_only(); self.root.after(30,self._keep_settings_alive)
        ff = tk.Frame(sf,bg=self.T["bg"]); ff.pack(fill="x",padx=12,pady=4)
        self._settings_widgets["frame_bg"].append(ff)
        for i,fname in enumerate(UI_FONTS):
            rf=tk.Frame(ff,bg=self.T["bg"]); rf.grid(row=i//2,column=i%2,sticky="w",padx=6,pady=2)
            r=tk.Radiobutton(rf,text=fname,variable=font_var,value=fname,
                bg=self.T["bg"],fg=self.T["text"],activebackground=self.T["bg"],
                selectcolor=self.T["entry_bg"],font=(fname,9),command=apply_font)
            r.pack(side="left")
            self._settings_widgets["frame_bg"].append(rf); self._settings_widgets["radio"].append(r)

        section("Data")
        def export_fn():
            path=filedialog.asksaveasfilename(title="Export All Data",defaultextension=".json",filetypes=[("JSON","*.json")])
            if path:
                bundle = {
                    "tasks":    self.tasks,
                    "docs":     load_docs(),
                    "habits":   load_habits(),
                    "gamification": {
                        "xp":            self.cfg.get("xp",0),
                        "tasks_created": self.cfg.get("tasks_created",0),
                        "tasks_done":    self.cfg.get("tasks_done",0),
                    }
                }
                with open(path,"w",encoding="utf-8") as f: json.dump(bundle,f,indent=2,ensure_ascii=False)
                messagebox.showinfo("Export","All data exported (tasks, docs, habits, progression).",parent=win)
        def import_fn():
            path=filedialog.askopenfilename(title="Import",filetypes=[("JSON","*.json")])
            if not path: return
            try:
                with open(path,"r",encoding="utf-8") as f: raw=json.load(f)
                # support both old (list) and new (bundle) format
                if isinstance(raw, list):
                    imp=[_norm(t) for t in raw]; have={t["id"] for t in self.tasks}; added=0
                    for t in imp:
                        if t["id"] not in have: self.tasks.insert(0,t); added+=1
                    save_tasks(self.tasks); self._render_tasks()
                    messagebox.showinfo("Import",f"Imported {added} task(s).",parent=win)
                else:
                    # full bundle
                    added_tasks=0
                    if "tasks" in raw:
                        imp=[_norm(t) for t in raw["tasks"]]; have={t["id"] for t in self.tasks}
                        for t in imp:
                            if t["id"] not in have: self.tasks.insert(0,t); added_tasks+=1
                        save_tasks(self.tasks)
                    if "docs" in raw:
                        existing={d["id"] for d in load_docs()}
                        new_docs=load_docs()
                        for d in raw["docs"]:
                            if d.get("id") not in existing: new_docs.append(d)
                        save_docs(new_docs)
                    if "habits" in raw:
                        save_habits(raw["habits"])
                    if "gamification" in raw:
                        g=raw["gamification"]
                        self.cfg["xp"]=max(self.cfg.get("xp",0), g.get("xp",0))
                        self.cfg["tasks_created"]=max(self.cfg.get("tasks_created",0),g.get("tasks_created",0))
                        self.cfg["tasks_done"]=max(self.cfg.get("tasks_done",0),g.get("tasks_done",0))
                        save_config(self.cfg)
                    self._render_tasks()
                    messagebox.showinfo("Import",f"Imported {added_tasks} task(s) + docs/habits/progression.",parent=win)
            except Exception as ex:
                messagebox.showerror("Error",str(ex),parent=win)
        br=tk.Frame(sf,bg=self.T["bg"]); br.pack(fill="x",padx=12,pady=4)
        self._settings_widgets["frame_bg"].append(br)
        b1=tk.Button(br,text="⬆ Export",command=export_fn,bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),padx=10,pady=5,cursor="hand2",activebackground=self.T["btn_hover"])
        b1.pack(side="left",padx=(0,8))
        b2=tk.Button(br,text="⬇ Import",command=import_fn,bg=self.T["btn_bg"],fg=self.T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),padx=10,pady=5,cursor="hand2",activebackground=self.T["btn_hover"])
        b2.pack(side="left")
        self._settings_widgets["button"].extend([b1,b2])

    def _mk_check(self, parent, var, command):
        c=tk.Checkbutton(parent,variable=var,bg=self.T["bg"],fg=self.T["text"],
            activebackground=self.T["bg"],selectcolor=self.T["entry_bg"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),command=command)
        c.pack(side="left"); self._settings_widgets["check"].append(c); return c

    def _startup_shortcut_path(self):
        appdata = os.environ.get("APPDATA","")
        return os.path.join(appdata,"Microsoft","Windows","Start Menu","Programs","Startup","LeoNote.bat") if appdata else ""

    def _apply_startup(self, enabled):
        path = self._startup_shortcut_path()
        if not path: return
        try:
            if enabled:
                exe = sys.executable if getattr(sys,"frozen",False) else os.path.abspath(sys.argv[0])
                with open(path,"w",encoding="utf-8") as f: f.write(f'@echo off\nstart "" "{exe}"\n')
            else:
                if os.path.exists(path): os.remove(path)
        except Exception: pass

    def _reset_scale(self, var=None):
        self.cfg["ui_scale"]=1.0; save_config(self.cfg)
        if var is not None: var.set(1.0)
        self._apply_scale(); self._retheme_main_only()
        self.root.after(10, self._keep_settings_alive)

    def _toggle_topmost(self):
        v = not self.root.attributes("-topmost")
        self.root.attributes("-topmost",v); self.cfg["always_on_top"]=v
        save_config(self.cfg); self._refresh_pin()

    def _toggle_maximize(self):
        self.root.update_idletasks()
        if not self._is_maximized:
            self._restore_geo = self.root.geometry()
            sw,sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0"); self._is_maximized=True
        else:
            if self._restore_geo: self.root.geometry(self._restore_geo)
            self._is_maximized=False

    def _minimize(self):
        if self.cfg.get("show_in_tray",False) and not self.cfg.get("show_in_taskbar",False):
            self.root.withdraw(); return
        was = bool(self.cfg.get("always_on_top",False))
        self.root.attributes("-topmost",False)
        self.root.overrideredirect(False)
        self.root.iconify()
        def restore():
            if self.root.state()!="iconic":
                self.root.overrideredirect(self._custom_chrome_on())
                self.root.attributes("-topmost",was)
        self.root.after(600, restore)

    def _close(self):
        save_config(self.cfg); save_tasks(self.tasks); self._destroy_tray(); self.root.destroy()

    def _drag_start(self, e):
        if self._is_maximized or not self._custom_chrome_on(): return
        self._drag_x=e.x_root-self.root.winfo_x(); self._drag_y=e.y_root-self.root.winfo_y()

    def _drag_do(self, e):
        if self._is_maximized or not self._custom_chrome_on() or self._resize_edge: return
        self.root.geometry(f"+{e.x_root-self._drag_x}+{e.y_root-self._drag_y}")

    _CURSORS = {"n":"sb_v_double_arrow","s":"sb_v_double_arrow","e":"sb_h_double_arrow","w":"sb_h_double_arrow","ne":"top_right_corner","sw":"bottom_left_corner","nw":"top_left_corner","se":"bottom_right_corner"}

    def _edge_zone(self, xr, yr, m=12):
        rx,ry=self.root.winfo_rootx(),self.root.winfo_rooty(); rw,rh=self.root.winfo_width(),self.root.winfo_height()
        L=xr-rx<=m; R=(rx+rw)-xr<=m; To=yr-ry<=m; B=(ry+rh)-yr<=m
        if To and L: return "nw"
        if To and R: return "ne"
        if B and L:  return "sw"
        if B and R:  return "se"
        if L: return "w"
        if R: return "e"
        if To: return "n"
        if B:  return "s"
        return None

    def _resize_cursor(self, e):
        if not self._custom_chrome_on() or self._is_maximized: self.root.config(cursor=""); return
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
        if e and e.widget==self.root and not self._is_maximized:
            self.cfg.update(window_x=self.root.winfo_x(),window_y=self.root.winfo_y(),
                window_w=self.root.winfo_width(),window_h=self.root.winfo_height())
            if hasattr(self,"_save_cfg_job"): self.root.after_cancel(self._save_cfg_job)
            self._save_cfg_job = self.root.after(500, lambda: save_config(self.cfg))

    def _keep_settings_alive(self):
        if self._settings_win and self._settings_win.winfo_exists():
            try: self._settings_win.lift(); self._settings_win.attributes("-topmost",True)
            except Exception: pass

    def run(self):
        self.entry.focus_set(); self.root.mainloop()


if __name__ == "__main__":
    App().run()
