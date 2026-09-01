"""
LeoNote - lightweight sticky task app with Obsidian integration
v4 features: docs multi-category filter dropdown + per-category backup folders +
             refresh button (scan dirs) + delete/restore syncs backup dir,
             new-doc popup focuses & clears title; archive delete stays on archive tab;
             habits Mark-done grants XP; all v3 features retained
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, datetime, uuid, ctypes, sys
_dtm = datetime          # module-level alias (was re-imported per task row)

try:
    import pystray as _pystray
    from PIL import Image as _PILImage
    _TRAY_OK = True
except Exception:
    _TRAY_OK = False

CONFIG_FILE  = os.path.join(os.path.expanduser("~"), ".leonote_config.json")
TASKS_FILE   = os.path.join(os.path.expanduser("~"), ".leonote_tasks.json")
DOCS_FILE    = os.path.join(os.path.expanduser("~"), ".leonote_docs.json")
HABITS_FILE      = os.path.join(os.path.expanduser("~"), ".leonote_habits.json")
PRIORITIES_FILE  = os.path.join(os.path.expanduser("~"), ".leonote_priorities.json")

DEFAULT_CONFIG = {
    "obsidian_note_path": "",
    "docs_backup_path": "",
    "always_on_top": True,
    "focus_view": "list",
    "use_priorities_tab": True,
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
    "docs_categories": ["Default"],
    "docs_active_categories": [],
}

THEMES = {
    "yellow":       {"bg":"#fef9d0","header_bg":"#f9e000","text":"#2c1a00","muted":"#7d5c0f","entry_bg":"#fffce0","entry_fg":"#2c1a00","btn_bg":"#f5cc00","btn_fg":"#2c1a00","btn_hover":"#e0b800","check_done":"#2e7d00","separator":"#f7e040","item_bg":"#fefad8","item_hover":"#fdf180","tab_bg":"#f9e840","archive":"#a05010","close_hover":"#ef4444","low":"#1a5fc4","medium":"#d96500","high":"#c00000"},
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
    "dusk":         {"bg":"#1e1a2e","header_bg":"#2d2847","text":"#e0d9f7","muted":"#9d93c4","entry_bg":"#26223a","entry_fg":"#e0d9f7","btn_bg":"#433e6a","btn_fg":"#e0d9f7","btn_hover":"#5c5692","check_done":"#a78bfa","separator":"#312c4e","item_bg":"#25213a","item_hover":"#302b4a","tab_bg":"#302b4a","archive":"#f9a8d4","close_hover":"#f87171","low":"#93c5fd","medium":"#fbbf24","high":"#f87171"},
    "slate-teal":   {"bg":"#15252b","header_bg":"#1e3540","text":"#d9eef5","muted":"#7eaab8","entry_bg":"#1b2f38","entry_fg":"#d9eef5","btn_bg":"#2a4f5e","btn_fg":"#d9eef5","btn_hover":"#346171","check_done":"#2dd4bf","separator":"#22404e","item_bg":"#192d36","item_hover":"#1f3844","tab_bg":"#1f3844","archive":"#7dd3fc","close_hover":"#f87171","low":"#60a5fa","medium":"#fb923c","high":"#f87171"},
    "mochi":        {"bg":"#1e1614","header_bg":"#2e2220","text":"#f3ede9","muted":"#b89c96","entry_bg":"#261c1a","entry_fg":"#f3ede9","btn_bg":"#4a3230","btn_fg":"#f3ede9","btn_hover":"#5f4240","check_done":"#fb923c","separator":"#342523","item_bg":"#241b19","item_hover":"#2e2220","tab_bg":"#2e2220","archive":"#fcd34d","close_hover":"#f87171","low":"#93c5fd","medium":"#fb923c","high":"#f87171"},
    "pine":         {"bg":"#141f18","header_bg":"#1e3025","text":"#d6eedc","muted":"#7aab87","entry_bg":"#192820","entry_fg":"#d6eedc","btn_bg":"#2a5238","btn_fg":"#d6eedc","btn_hover":"#356644","check_done":"#4ade80","separator":"#1e3025","item_bg":"#182720","item_hover":"#1f312a","tab_bg":"#1f312a","archive":"#86efac","close_hover":"#f87171","low":"#60a5fa","medium":"#fbbf24","high":"#f87171"},
    "storm":        {"bg":"#181c24","header_bg":"#232b38","text":"#dce8f5","muted":"#7b92ad","entry_bg":"#1e2532","entry_fg":"#dce8f5","btn_bg":"#2e3f55","btn_fg":"#dce8f5","btn_hover":"#3a4f68","check_done":"#38bdf8","separator":"#273345","item_bg":"#1c2230","item_hover":"#232c3e","tab_bg":"#232c3e","archive":"#93c5fd","close_hover":"#f87171","low":"#60a5fa","medium":"#fb923c","high":"#f87171"},
    "amber-dark":   {"bg":"#1a1200","header_bg":"#2c1e00","text":"#ffdf80","muted":"#c49030","entry_bg":"#221800","entry_fg":"#ffdf80","btn_bg":"#6b4a00","btn_fg":"#ffdf80","btn_hover":"#805a00","check_done":"#fbbf24","separator":"#3a2800","item_bg":"#1e1500","item_hover":"#2c1e00","tab_bg":"#2c1e00","archive":"#fde68a","close_hover":"#f87171","low":"#60a5fa","medium":"#fb923c","high":"#f87171"},
    "crimson":      {"bg":"#1a0f12","header_bg":"#3a161d","text":"#f7d7db","muted":"#b48a91","entry_bg":"#221317","entry_fg":"#f7d7db","btn_bg":"#5b1f2b","btn_fg":"#f7d7db","btn_hover":"#7a2434","check_done":"#22c55e","separator":"#3a161d","item_bg":"#211417","item_hover":"#2a181d","tab_bg":"#2a181d","archive":"#f87171","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "forest":       {"bg":"#0d1711","header_bg":"#183323","text":"#d8f3df","muted":"#8cb09a","entry_bg":"#132018","entry_fg":"#d8f3df","btn_bg":"#235336","btn_fg":"#d8f3df","btn_hover":"#2f6a45","check_done":"#22c55e","separator":"#183323","item_bg":"#122019","item_hover":"#17281f","tab_bg":"#17281f","archive":"#86efac","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "emerald":      {"bg":"#071a17","header_bg":"#0d3b35","text":"#d5fff5","muted":"#7cb6aa","entry_bg":"#0b2521","entry_fg":"#d5fff5","btn_bg":"#0f5b50","btn_fg":"#d5fff5","btn_hover":"#147768","check_done":"#10b981","separator":"#0d3b35","item_bg":"#0b2521","item_hover":"#10302b","tab_bg":"#10302b","archive":"#5eead4","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "midnight":     {"bg":"#0b1220","header_bg":"#16233a","text":"#dbeafe","muted":"#7f93b0","entry_bg":"#10192b","entry_fg":"#dbeafe","btn_bg":"#1d4e89","btn_fg":"#dbeafe","btn_hover":"#2563eb","check_done":"#38bdf8","separator":"#16233a","item_bg":"#0f1a2e","item_hover":"#14213a","tab_bg":"#14213a","archive":"#60a5fa","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "space":        {"bg":"#0d0b1e","header_bg":"#1a1535","text":"#e8e4ff","muted":"#8b82c4","entry_bg":"#13102a","entry_fg":"#e8e4ff","btn_bg":"#2d2560","btn_fg":"#e8e4ff","btn_hover":"#3d347a","check_done":"#a78bfa","separator":"#22194a","item_bg":"#11101f","item_hover":"#1e1a3a","tab_bg":"#1e1a3a","archive":"#f0abfc","close_hover":"#f87171","low":"#60a5fa","medium":"#fb923c","high":"#f87171"},
    "violet-night": {"bg":"#120b1f","header_bg":"#24123a","text":"#f1e7ff","muted":"#a38cbf","entry_bg":"#1a102a","entry_fg":"#f1e7ff","btn_bg":"#4c1d95","btn_fg":"#f1e7ff","btn_hover":"#6d28d9","check_done":"#22c55e","separator":"#24123a","item_bg":"#1a102a","item_hover":"#221434","tab_bg":"#221434","archive":"#c084fc","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
    "eclipse":      {"bg":"#0a0a0a","header_bg":"#1a1a1a","text":"#f2f2f2","muted":"#8a8a8a","entry_bg":"#111111","entry_fg":"#f2f2f2","btn_bg":"#2a2a2a","btn_fg":"#f2f2f2","btn_hover":"#3a3a3a","check_done":"#9ca3af","separator":"#1a1a1a","item_bg":"#111111","item_hover":"#181818","tab_bg":"#181818","archive":"#d4d4d8","close_hover":"#ef4444","low":"#60a5fa","medium":"#f59e0b","high":"#ef4444"},
}

# ═══════════════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM v1  —  colour math · derived tokens · type & space scale
#  Paste the module-level half immediately AFTER the THEMES dict (~line 76).
#  Paste the _AppMixin half INSIDE class App (de-indent one level, or simply
#  make App inherit the mixin).  Nothing here mutates THEMES: every original
#  key survives verbatim, so all 550+ existing T["..."] reads keep working.
# ═══════════════════════════════════════════════════════════════════════════════

# ── colour math (pure stdlib) ────────────────────────────────────────────────
def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _hx(r, g, b):
    f = lambda v: max(0, min(255, int(round(v))))
    return "#%02x%02x%02x" % (f(r), f(g), f(b))

def mix(a, b, t):
    """t=0 -> a, t=1 -> b."""
    ar, ag, ab = _rgb(a); br, bg, bb = _rgb(b)
    return _hx(ar + (br - ar) * t, ag + (bg - ag) * t, ab + (bb - ab) * t)

def lighten(c, t): return mix(c, "#ffffff", t)
def darken(c, t):  return mix(c, "#000000", t)

def _lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

def luminance(c):
    r, g, b = _rgb(c)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)

def is_dark(c): return luminance(c) < 0.30

def chroma(c):
    r, g, b = _rgb(c)
    return (max(r, g, b) - min(r, g, b)) / 255.0

def on(c, light="#ffffff", dark="#12100e"):
    """Readable foreground for a background colour."""
    return light if contrast(c, light) >= contrast(c, dark) else dark

def step(base, ratio, toward=None, max_t=0.40):
    """Nudge `base` until contrast(base, result) >= ratio. Used for elevation."""
    tgt = toward or ("#ffffff" if is_dark(base) else "#000000")
    t, out = 0.0, base
    while t < max_t:
        t += 0.02
        out = mix(base, tgt, t)
        if contrast(base, out) >= ratio: return out
    return out

def ensure(c, against, ratio, max_t=0.90):
    """Nudge `c` away from `against` until it is legible on it."""
    if contrast(c, against) >= ratio: return c
    tgt = "#ffffff" if is_dark(against) else "#000000"
    t, out = 0.0, c
    while t < max_t:
        t += 0.03
        out = mix(c, tgt, t)
        if contrast(out, against) >= ratio: return out
    return out


# ── derived token layer ──────────────────────────────────────────────────────
_TOKEN_CACHE = {}

def tokens(theme_name):
    """THEMES[name] + ~30 derived tokens. Computed once per theme, then cached."""
    t = _TOKEN_CACHE.get(theme_name)
    if t is None:
        t = _TOKEN_CACHE[theme_name] = _derive(THEMES[theme_name])
    return t

def _derive(P):
    T   = dict(P)                       # every legacy key survives verbatim
    bg  = P["bg"]
    dk  = is_dark(bg)
    T["is_dark"] = dk                   # <- the ONE dark test; kills all 3 lists

    # accent = the palette's own identity hue. `archive` is already the deep,
    # legible version of each theme's colour (sakura #be185d, lavender #7e22ce,
    # peach #c2410c ...), so it is the honest accent. Do NOT derive it from
    # check_done: that is the SUCCESS colour and is green on 9 themes whose
    # identity is pink/purple — the accent would fight the palette.
    cands = (P["archive"], P["btn_hover"], P["btn_bg"], P["header_bg"])
    acc   = P["archive"] if contrast(P["archive"], bg) >= 2.0 else \
            max(cands, key=lambda c: (chroma(c) + .08) * min(contrast(c, bg), 3.0))
    T["accent"]      = ensure(acc, bg, 2.2)
    T["accent_hi"]   = lighten(T["accent"], .14) if dk else darken(T["accent"], .12)
    T["on_accent"]   = on(T["accent"])
    T["accent_ring"] = mix(bg, T["accent"], .45)
    # the tab underline sits on tab_bg, not bg — guarantee it there too
    T["accent_ind"]  = ensure(T["accent"], P["tab_bg"], 2.6)

    # surfaces — elevation is REAL on dark themes (a card can be lighter than
    # the page). On light themes bg is already ~white, so there is no room to
    # go up: the card stays paper-white and its edge is carried by `hairline`
    # plus a 1-px `shadow_line`. That is the honest answer, not a compromise.
    if dk:
        T["surface"]      = step(bg, 1.16, "#ffffff", .35)
        T["surface_2"]    = step(bg, 1.34, "#ffffff", .45)
        T["surface_sunk"] = darken(bg, .30)
        T["shadow_line"]  = darken(bg, .55)
    else:
        T["surface"]      = lighten(bg, .55)
        T["surface_2"]    = darken(bg, .05)
        T["surface_sunk"] = darken(bg, .05)
        T["shadow_line"]  = darken(bg, .09)
    s = T["surface"]
    # washes are mixed into the SURFACE they sit on, not into bg — mixing into
    # bg makes them invisible on every dark theme (measured 1.00-1.08).
    T["accent_wash"]   = mix(s, T["accent"], .14)
    T["accent_soft"]   = mix(s, T["accent"], .26)
    T["surface_hover"] = ensure(mix(s, T["accent"], .16 if not dk else .12), s, 1.10, .60)
    T["surface_press"] = ensure(mix(s, T["accent"], .28 if not dk else .22), s, 1.18, .70)

    # hairlines — measured against the surface they actually sit on
    T["hairline"]        = step(s, 1.30, None, .45)
    T["hairline_strong"] = step(s, 1.85, None, .60)
    T["divider"]         = step(bg, 1.22, None, .40)

    # semantic aliases (so call sites stop overloading check_done / archive)
    T["success"], T["warning"] = P["check_done"], P["medium"]
    T["danger"],  T["info"]    = P["close_hover"], P["low"]
    # *_text = the tone made legible ON ITS OWN CHIP (the tightest case, which
    # also covers plain use on `surface`).
    for k in ("success", "warning", "danger", "info", "accent"):
        T[k + "_text"] = ensure(T[k], mix(s, T[k], .16), 4.5)
    T["focus"]     = ensure(T["accent"], s, 3.0)
    T["disabled"]  = mix(P["muted"], bg, .45)
    T["tab_hover"] = step(P["tab_bg"], 1.14, None, .30)
    T["scrim"]     = darken(bg, .55)
    return T


# ── type & space scale ───────────────────────────────────────────────────────
# Sizes stay POSITIVE (points) so Tk's own `tk scaling` keeps honouring ui_scale.
TYPE_SCALE = {
    "micro":       (7,  ""),
    "caption":     (8,  ""),
    "caption_str": (8,  "bold"),
    "body":        (10, ""),
    "body_str":    (10, "bold"),
    "title":       (12, "bold"),
    "display":     (16, "bold"),
    "hero":        (30, "bold"),
}
# 4-px rhythm: SPACE[k] == 4*k
SPACE  = {0: 0, 1: 4, 2: 8, 3: 12, 4: 16, 5: 20, 6: 24, 8: 32}
RADIUS = 10


def round_rect_pts(x1, y1, x2, y2, r):
    """Point list for a rounded rectangle. Use with create_polygon(smooth=True)."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


class RoundedCard(tk.Canvas):
    """A rounded, bordered card drawn on a Canvas, hosting a normal Frame.

    Use `card.body` as the parent for content. Height auto-tracks the body.

    Caveats — real, not theoretical:
      * Canvas does not antialias. Corners are stair-stepped. Keep radius <= 10
        and keep `stroke` within ~1.4 contrast of `fill`; at that size it reads
        clean (verified at 4x zoom). Above r=14 the steps show and it looks cheap.
      * The canvas is opaque: `behind` MUST be the true parent background.
      * The hosted Frame has square corners, so it is inset by 0.30*r — the
        exact distance at which a square corner sits inside the arc
        (p >= r*(1 - 1/sqrt(2)) ~= 0.293r). Do not shrink that inset.
      * Costs 2 widgets + 1 canvas item + a <Configure> handler per card. Fine
        for the <= 40 cards of a Focus/Stats screen. NOT for a 300-row task
        list — use the flat `_card(rounded=False)` hairline card there.
      * Mouse-wheel events do not bubble out of a nested Canvas: run the app's
        _bind_ctrl_wheel_recursive over the card after building it.
    """

    def __init__(self, parent, fill, stroke, behind, radius=RADIUS, pad=8, **kw):
        super().__init__(parent, bg=behind, bd=0, highlightthickness=0,
                         takefocus=0, height=1, **kw)
        self._fill, self._stroke, self._r = fill, stroke, radius
        self._inset = max(pad, int(radius * 0.30) + 1)
        self._h = 0
        self._shape = self.create_polygon(0, 0, 0, 0, fill=fill, outline=stroke,
                                          width=1, smooth=True, splinesteps=12)
        self.body = tk.Frame(self, bg=fill, bd=0, highlightthickness=0)
        self._win = self.create_window(self._inset, self._inset,
                                       window=self.body, anchor="nw")
        self.body.bind("<Configure>", self._sync, add="+")
        self.bind("<Configure>", self._redraw, add="+")
        self.after_idle(self._redraw)   # kick: the canvas starts 1px tall

    def _sync(self, _e=None):
        """Canvas does not grow to fit its window item — we must set height."""
        h = self.body.winfo_reqheight() + self._inset * 2
        if abs(h - self._h) > 1:
            self._h = h
            self.configure(height=h)

    def _redraw(self, _e=None):
        w = self.winfo_width()
        if w > 4:                                   # push our width into the body
            self.itemconfigure(self._win, width=w - self._inset * 2)
        self._sync()                                # ...then pull the body's height
        h = self.winfo_height()
        if w < 4 or h < 4: return
        self.coords(self._shape, *round_rect_pts(1, 1, w - 1, h - 1, self._r))

    def repaint(self, fill=None, stroke=None):
        """Hover/selected states: recolour the shape AND every child of body."""
        if fill:
            self._fill = fill
            self.itemconfigure(self._shape, fill=fill)
        if stroke:
            self._stroke = stroke
            self.itemconfigure(self._shape, outline=stroke)
        self._tint(self.body, self._fill)

    def _tint(self, w, bg):
        try:
            if w.winfo_class() in ("Frame", "Label", "Checkbutton", "Button", "Canvas"):
                w.configure(bg=bg)
        except Exception:
            pass
        for c in w.winfo_children():
            self._tint(c, bg)


# ═══════════════════════════════════════════════════════════════════════════════
#  App methods — paste INSIDE class App (next to _save_cfg_debounced, ~4483).
#  Delete the `class _AppMixin:` line and de-indent, or make App inherit it.

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
    t.setdefault("start_date", None)
    t.setdefault("due_date", None)
    t.setdefault("due_time", "")
    t.setdefault("scheduled_jumped", False)
    t.setdefault("due_jumped", False)
    return t

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE,"r",encoding="utf-8") as f:
                return [_norm(t) for t in json.load(f)]
        except Exception: pass
    return []

_app_instance = None  # set in App.__init__

# ── in-memory data cache with write-through ───────────────────────────────────
# DOCS_FILE / HABITS_FILE / PRIORITIES_FILE are opened nowhere else in this
# file, so these six functions are the single choke point for both caching and
# dirty-flagging. Names and signatures are unchanged: no call site changes.
#
# CONTRACT:
#   load_X()  -> returns the LIVE cached object, NOT a copy. Callers that
#                mutate it in place must still call save_X() to persist.
#                (Every existing call site already does exactly that.)
#   save_X(v) -> writes to disk, installs v as the new cache, and marks the
#                tabs that display it dirty.
_cache = {"docs": None, "habits": None, "priorities": None}

def _cache_read(key, path, make_default):
    if _cache[key] is None:
        data = None
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = None
        _cache[key] = make_default() if data is None else data
    return _cache[key]

def _cache_write(key, path, value, dirty_tabs):
    _cache[key] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
    if _app_instance:
        _app_instance._mark_tabs_dirty(dirty_tabs)

def invalidate_data_cache(*keys):
    """Force the next load_* to re-read from disk. Safety valve for any
    out-of-band write to the JSON files."""
    for k in (keys or tuple(_cache.keys())):
        _cache[k] = None

def save_tasks(tasks):
    with open(TASKS_FILE,"w",encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    # Invalidate app-level task pool cache
    if _app_instance:
        _app_instance._tasks_cache = None
        _app_instance._mark_tabs_dirty(
            ("active", "archive", "search", "trash", "stats"))

# ── docs ──────────────────────────────────────────────────────────────────────
def load_docs():
    return _cache_read("docs", DOCS_FILE, list)

def save_docs(docs):
    _cache_write("docs", DOCS_FILE, docs, ("docs", "trash"))

# ── habits ────────────────────────────────────────────────────────────────────
def load_habits():
    return _cache_read("habits", HABITS_FILE, lambda: {"habits": [], "log": {}})

def save_habits(data):
    _cache_write("habits", HABITS_FILE, data, ("habits", "trash"))

# ── priorities ────────────────────────────────────────────────────────────────
def load_priorities():
    return _cache_read("priorities", PRIORITIES_FILE, list)

def save_priorities(items):
    _cache_write("priorities", PRIORITIES_FILE, items, ("priorities",))

# ── recurring rules engine ──────────────────────────────────
import calendar as _rc_cal   # json/os/datetime/uuid already imported at line 11

RECUR_FILE = os.path.join(os.path.expanduser("~"), ".leonote_recurring.json")

REC_KINDS       = ("daily", "weekly", "monthly", "once")
REC_CATCHUP     = ("collapse", "all", "skip")
REC_MAX_SPAWN   = 10      # hard cap on tasks spawned per rule per catch-up
REC_SCAN_DAYS   = 366     # never look further back than this when catching up
REC_WD_SHORT    = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")   # 0=Mon, date.weekday()
REC_TICK_MS     = 60000   # reminder heartbeat


# ── schema ────────────────────────────────────────────────────────────────────
def _rec_norm(r):
    """Normalize one rule in place. Mirrors _norm() for tasks. Never raises."""
    r.setdefault("id",       str(uuid.uuid4()))
    r.setdefault("title",    "Recurring task")
    r.setdefault("created",  datetime.date.today().isoformat())
    r.setdefault("anchor",   r.get("created") or datetime.date.today().isoformat())
    r.setdefault("until",    None)          # None | "YYYY-MM-DD" inclusive end
    r.setdefault("time",     "")            # "" | "HH:MM"  (display only, never converted)
    r.setdefault("priority", "none")        # priority given to the spawned task
    r.setdefault("mode",     "task")        # "task" -> spawn into tasks | "reminder" -> row only
    r.setdefault("catchup",  "collapse")    # collapse | all | skip
    r.setdefault("notify",   True)          # badge/toast/sound on fire
    r.setdefault("active",   True)
    r.setdefault("last_fired",   None)      # "YYYY-MM-DD" — highest materialized occurrence
    r.setdefault("snooze_until", None)      # "YYYY-MM-DD" — suppressed up to & including
    r.setdefault("skip",     [])            # ["YYYY-MM-DD"] occurrences the user waved off
    r.setdefault("deleted",  False)
    r.setdefault("deleted_at", None)
    rule = r.get("rule")
    if not isinstance(rule, dict): rule = {}
    kind = rule.get("kind")
    if kind not in REC_KINDS: kind = "weekly"
    out = {"kind": kind}
    if kind == "daily":
        out["interval"] = max(1, int(rule.get("interval", 1) or 1))
    elif kind == "weekly":
        days = [int(d) for d in rule.get("days", []) if isinstance(d, (int, float)) and 0 <= int(d) <= 6]
        out["days"]     = sorted(set(days)) or [datetime.date.today().weekday()]
        out["interval"] = max(1, int(rule.get("interval", 1) or 1))
    elif kind == "monthly":
        out["day"]      = min(31, max(1, int(rule.get("day", 1) or 1)))
        out["interval"] = max(1, int(rule.get("interval", 1) or 1))
    r["rule"] = out
    if r["catchup"] not in REC_CATCHUP: r["catchup"] = "collapse"
    if r["priority"] not in ("none", "low", "medium", "high"): r["priority"] = "none"
    if r["mode"] not in ("task", "reminder"): r["mode"] = "task"
    if not isinstance(r["skip"], list): r["skip"] = []
    return r


def _rec_date(s):
    """Tolerant ISO date parse. Accepts 'YYYY-MM-DD' and 'YYYY-MM-DDTHH:MM'. None on junk."""
    if not s or not isinstance(s, str): return None
    try:
        return datetime.date.fromisoformat(s[:10])
    except Exception:
        return None


# ── persistence (cached; zero disk reads on the render path) ──────────────────
_rec_cache = None     # module-level, invalidated by save_recurring()


def load_recurring(force=False):
    """Return {"version":1,"rules":[...],"log":{rid:[iso,...]}}. Cached in memory."""
    global _rec_cache
    if _rec_cache is not None and not force:
        return _rec_cache
    data = {"version": 1, "rules": [], "log": {}}
    if os.path.exists(RECUR_FILE):
        try:
            with open(RECUR_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                data["rules"] = [_rec_norm(r) for r in raw.get("rules", []) if isinstance(r, dict)]
                lg = raw.get("log", {})
                if isinstance(lg, dict):
                    data["log"] = {k: list(v) for k, v in lg.items() if isinstance(v, list)}
        except Exception:
            pass
    _rec_cache = data
    return data


def save_recurring(data):
    """Atomic write (temp + fsync + os.replace). The tasks/habits files are not; this is."""
    global _rec_cache
    _rec_cache = data
    tmp = RECUR_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, RECUR_FILE)
    except Exception:
        try:
            with open(RECUR_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        try:
            if os.path.exists(tmp): os.remove(tmp)
        except Exception:
            pass
    # C3: the habits tab hosts the recurring list and is frame-cached, so a
    # rule change must invalidate it or the new rule will not appear.
    if _app_instance:
        _app_instance._mark_tabs_dirty(("habits",))
        # _rec_catch_up parks itself until 00:01 tomorrow whenever nothing is
        # due. Without this, a rule created (or edited, un-snoozed, re-enabled)
        # during that quiet window would not fire until the next calendar day.
        _app_instance._rec_quiet_until = None


# ── calendar helpers ──────────────────────────────────────────────────────────
def _rec_monday(d):
    return d - datetime.timedelta(days=d.weekday())


def _rec_add_months(y, m, n):
    t = (y * 12 + (m - 1)) + n
    return t // 12, (t % 12) + 1


def _rec_clamp_dom(y, m, day):
    """Day-of-month with month-end clamping: 31 -> 28/29/30/31. Day 31 IS 'last day'."""
    return datetime.date(y, m, min(day, _rc_cal.monthrange(y, m)[1]))


# ── the engine ────────────────────────────────────────────────────────────────
def rec_is_occurrence(rule, d, anchor):
    """True if calendar date d is an occurrence of rule (ignores until/skip/active)."""
    if d < anchor: return False
    k = rule.get("kind")
    if k == "once":
        return d == anchor
    if k == "daily":
        n = max(1, int(rule.get("interval", 1)))
        return (d - anchor).days % n == 0
    if k == "weekly":
        n = max(1, int(rule.get("interval", 1)))
        if d.weekday() not in rule.get("days", []): return False
        return ((_rec_monday(d) - _rec_monday(anchor)).days // 7) % n == 0
    if k == "monthly":
        n = max(1, int(rule.get("interval", 1)))
        if ((d.year * 12 + d.month) - (anchor.year * 12 + anchor.month)) % n != 0: return False
        return d == _rec_clamp_dom(d.year, d.month, int(rule.get("day", 1)))
    return False


def next_occurrence(rule, from_date, anchor=None, until=None):
    """First occurrence on or after from_date. Returns date or None.

    Pure calendar arithmetic — date + timedelta only, no datetime, no tzinfo.
    A 23h or 25h DST day cannot move a calendar date, so 'every Tuesday' is
    exact through every transition; date.today() already reads local civil time.
    """
    if anchor is None:
        anchor = from_date
    start = from_date if from_date > anchor else anchor
    k     = rule.get("kind")
    res   = None

    if k == "once":
        res = anchor if anchor >= from_date else None

    elif k == "daily":
        n    = max(1, int(rule.get("interval", 1)))
        gap  = (start - anchor).days
        step = ((gap + n - 1) // n) * n          # ceil to the next multiple
        res  = anchor + datetime.timedelta(days=step)

    elif k == "weekly":
        n    = max(1, int(rule.get("interval", 1)))
        days = sorted(rule.get("days", []))
        if days:
            wk  = _rec_monday(start)
            aw  = _rec_monday(anchor)
            rem = (((wk - aw).days // 7) % n)
            if rem: wk += datetime.timedelta(weeks=(n - rem))
            for _ in range(2):                    # this valid week, then the next one
                for wd in days:
                    cand = wk + datetime.timedelta(days=wd)
                    if cand >= start and cand >= anchor:
                        res = cand
                        break
                if res: break
                wk += datetime.timedelta(weeks=n)

    elif k == "monthly":
        n   = max(1, int(rule.get("interval", 1)))
        dom = int(rule.get("day", 1))
        am  = anchor.year * 12 + (anchor.month - 1)
        sm  = start.year * 12 + (start.month - 1)
        off = sm - am
        if off < 0: off = 0
        if off % n: off += n - (off % n)          # align to the anchor's interval grid
        for _ in range(400):                      # bounded; 2 iterations in practice
            y, m = _rec_add_months(anchor.year, anchor.month, off)
            cand = _rec_clamp_dom(y, m, dom)
            if cand >= start and cand >= anchor:
                res = cand
                break
            off += n

    if res is not None and until is not None and res > until:
        return None
    return res


def next_occurrences(r, from_date, count=3):
    """Convenience for the dialog preview: the next `count` dates for a normalized rule."""
    anchor = _rec_date(r.get("anchor")) or datetime.date.today()
    until  = _rec_date(r.get("until"))
    skip   = set(r.get("skip", []))
    out, cur = [], from_date
    for _ in range(count * 8 + 24):
        if len(out) >= count: break
        d = next_occurrence(r.get("rule", {}), cur, anchor, until)
        if d is None: break
        if d.isoformat() not in skip:
            out.append(d)
        cur = d + datetime.timedelta(days=1)
    return out


def rec_next_due(r, today):
    """Next *actionable* date for a rule: the pending occurrence, or the next future one.

    Returns (date|None, overdue_bool). Snooze pushes the shown date forward without
    losing the occurrence.
    """
    if not r.get("active", True) or r.get("deleted"):
        return None, False
    anchor = _rec_date(r.get("anchor")) or today
    until  = _rec_date(r.get("until"))
    skip   = set(r.get("skip", []))
    lf     = _rec_date(r.get("last_fired"))
    floor  = max(anchor, (lf + datetime.timedelta(days=1)) if lf else anchor,
                 today - datetime.timedelta(days=REC_SCAN_DAYS))
    cur = floor
    for _ in range(64):
        d = next_occurrence(r.get("rule", {}), cur, anchor, until)
        if d is None: return None, False
        if d.isoformat() in skip:
            cur = d + datetime.timedelta(days=1)
            continue
        sn = _rec_date(r.get("snooze_until"))
        if sn and sn >= today and d <= today:
            return sn + datetime.timedelta(days=1), False   # suppressed through sn
        return d, d < today
    return None, False


def due_occurrences(r, last_fired, today, limit=REC_MAX_SPAWN):
    """Occurrence dates that should have been materialized by `today` and were not.

    Window is (last_fired, today], floored at max(anchor, created, today-REC_SCAN_DAYS)
    so a rule anchored in 2020 cannot back-fill six years of history on creation.
    Returns (dates, truncated_bool) — ascending, at most `limit` (the most RECENT ones).
    """
    today   = today if isinstance(today, datetime.date) else _rec_date(today)
    anchor  = _rec_date(r.get("anchor")) or today
    created = _rec_date(r.get("created")) or anchor
    until   = _rec_date(r.get("until"))
    skip    = set(r.get("skip", []))
    lf      = last_fired if isinstance(last_fired, datetime.date) else _rec_date(last_fired)

    floor = max(anchor, created, today - datetime.timedelta(days=REC_SCAN_DAYS))
    if lf is not None:
        floor = max(floor, lf + datetime.timedelta(days=1))

    out, cur, truncated = [], floor, False
    while cur <= today:
        d = next_occurrence(r.get("rule", {}), cur, anchor, until)
        if d is None or d > today: break
        if d.isoformat() not in skip:
            out.append(d)
            if len(out) > limit * 4:              # bound memory on pathological daily rules
                truncated = True
                out = out[-limit:]
        cur = d + datetime.timedelta(days=1)
    if len(out) > limit:
        truncated = True
        out = out[-limit:]
    return out, truncated


def rec_occ_key(rid, d):
    """Idempotency key. One materialization per (rule, occurrence date), ever."""
    return "%s@%s" % (rid, d.isoformat() if hasattr(d, "isoformat") else d)


def rec_catch_up_plan(rules, today, existing_keys, log=None):
    """PURE. Decide what to materialize. No I/O, no Tk, no mutation of `rules`.

    rules         : list of normalized rule dicts
    today         : datetime.date
    existing_keys : set of rec_occ_key() already present in tasks (2nd idempotency guard)
    log           : {rid: [iso,...]} completion log; an already-completed occurrence
                    is never re-spawned

    Returns (spawns, updates, fired_ids)
      spawns  : [{"rule_id","title","date","missed","priority","time","mode","notify","key"}]
      updates : {rid: {"last_fired": iso}}   — apply with rules[i].update(...)
      fired   : [rid, ...] rules that produced something new (notification surface)
    """
    log     = log or {}
    spawns  = []
    updates = {}
    fired   = []

    for r in rules:
        if r.get("deleted") or not r.get("active", True):
            continue
        rid = r.get("id")
        sn  = _rec_date(r.get("snooze_until"))
        if sn and sn >= today:
            continue                                  # snoozed: do not advance last_fired

        occ, _trunc = due_occurrences(r, r.get("last_fired"), today)
        if not occ:
            continue

        done = set(log.get(rid, []))
        mode = r.get("catchup", "collapse")
        if mode == "skip":
            wanted = [occ[-1]] if occ[-1] == today else []
        elif mode == "all":
            wanted = occ
        else:                                          # collapse (default)
            wanted = [occ[-1]]

        made = False
        for d in wanted:
            key = rec_occ_key(rid, d)
            if key in existing_keys or d.isoformat() in done:
                continue
            spawns.append({
                "rule_id":  rid,
                "title":    r.get("title", "Recurring task"),
                "date":     d,
                "missed":   (len(occ) - 1) if mode == "collapse" else 0,
                "priority": r.get("priority", "none"),
                "time":     r.get("time", ""),
                "mode":     r.get("mode", "task"),
                "notify":   bool(r.get("notify", True)),
                "key":      key,
            })
            made = True

        # last_fired always advances to the newest accounted-for occurrence, even when
        # every candidate was skipped or deduped. That is what makes an app closed for
        # a week produce ONE task instead of seven, and every rerun a no-op.
        updates[rid] = {"last_fired": occ[-1].isoformat()}
        if made and r.get("notify", True):
            fired.append(rid)

    return spawns, updates, fired


# ── cadence-aware stats (does NOT touch _habit_streak & friends) ──────────────
def rec_streak(r, log, today):
    """Consecutive completed occurrences ending at the most recent past occurrence.

    Counts EXPECTED occurrences, not calendar days. 'Every Tuesday' done every
    Tuesday is a streak of N here; _habit_streak (line 189) would report 1 forever
    because Wed+Thu trip its two-consecutive-misses break at line 199.
    """
    rid    = r.get("id")
    done   = set((log or {}).get(rid, []))
    anchor = _rec_date(r.get("anchor")) or today
    until  = _rec_date(r.get("until"))
    skip   = set(r.get("skip", []))
    occ, cur = [], max(anchor, today - datetime.timedelta(days=REC_SCAN_DAYS))
    while cur <= today and len(occ) < 400:
        d = next_occurrence(r.get("rule", {}), cur, anchor, until)
        if d is None or d > today: break
        if d.isoformat() not in skip: occ.append(d)
        cur = d + datetime.timedelta(days=1)
    streak = 0
    for d in reversed(occ):
        if d.isoformat() in done:
            streak += 1
        elif d == today:
            continue                    # today is still open, not a miss
        else:
            break
    return streak


def rec_rate(r, log, today, window=8):
    """(hits, total) over the last `window` expected occurrences. Honest denominator."""
    rid    = r.get("id")
    done   = set((log or {}).get(rid, []))
    anchor = _rec_date(r.get("anchor")) or today
    until  = _rec_date(r.get("until"))
    occ, cur = [], max(anchor, today - datetime.timedelta(days=REC_SCAN_DAYS))
    while cur <= today and len(occ) < 400:
        d = next_occurrence(r.get("rule", {}), cur, anchor, until)
        if d is None or d > today: break
        occ.append(d)
        cur = d + datetime.timedelta(days=1)
    occ = occ[-window:]
    return sum(1 for d in occ if d.isoformat() in done), len(occ)


# ── display helpers ───────────────────────────────────────────────────────────
def rec_fmt_date(d, today):
    """'today' / 'tomorrow' / 'Tue 3 Sep' / 'Tue 3 Sep 2027'."""
    if d is None: return "—"
    if d == today: return "today"
    if d == today + datetime.timedelta(days=1): return "tomorrow"
    if d == today - datetime.timedelta(days=1): return "yesterday"
    s = d.strftime("%a %#d %b") if os.name == "nt" else d.strftime("%a %-d %b")
    if d.year != today.year: s += d.strftime(" %Y")
    return s


def rec_describe(r):
    """Human cadence label: 'Weekly · Tu', 'Every 3 days', 'Monthly · day 31 (last)'."""
    rule = r.get("rule", {})
    k, n = rule.get("kind"), int(rule.get("interval", 1) or 1)
    if k == "once":
        return "Once"
    if k == "daily":
        return "Daily" if n == 1 else "Every %d days" % n
    if k == "weekly":
        names = ", ".join(REC_WD_SHORT[d] for d in sorted(rule.get("days", [])))
        base  = "Weekly" if n == 1 else "Every %d weeks" % n
        return "%s · %s" % (base, names or "—")
    if k == "monthly":
        dom  = int(rule.get("day", 1))
        base = "Monthly" if n == 1 else "Every %d months" % n
        return "%s · day %d%s" % (base, dom, " (last)" if dom == 31 else "")
    return "—"

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
    # Every tab that owns a cached frame.
    _ALL_TABS = ("active", "archive", "trash", "search",
                 "stats", "docs", "habits", "priorities")
    # Never served from cache: "stats" reads live cfg (xp / pomodoro counters),
    # "search" reads the live query string. Both are cheap single-column views.
    _ALWAYS_FRESH = ("stats", "search")

    def __init__(self):
        enable_high_dpi()
        self.cfg   = load_config()
        self.cfg.setdefault("start_hidden_to_tray", False)
        self.cfg.setdefault("show_in_taskbar", False)
        self.tasks = load_tasks()
        self._purge_old_trash()
        global _app_instance; _app_instance = self
        self._tasks_cache = None
        self._init_tab_cache()
        _last_tab = self.cfg.get("last_tab")
        if _last_tab in ("active","archive","priorities","docs","habits","stats"):
            self.current_tab = _last_tab
        else:
            self.current_tab = "priorities" if self.cfg.get("use_priorities_tab", True) else "active"
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
        # pomodoro
        self.cfg.setdefault("pomo_work_mins", 20)
        self.cfg.setdefault("pomo_break_mins", 3)
        self.cfg.setdefault("pomo_tick_volume", 0.15)
        self.cfg.setdefault("pomo_tick_enabled", True)
        self.cfg.setdefault("pomo_no_tick_break", True)
        self.cfg.setdefault("pomo_alert_enabled", True)
        self.cfg.setdefault("pomo_alert_volume", 0.8)
        self.cfg.setdefault("pomo_work_color", "#e05c5c")
        self.cfg.setdefault("pomo_break_color", "#4caf88")
        self.cfg.setdefault("pomo_total_work_secs", 0)
        self.cfg.setdefault("pomo_total_break_secs", 0)
        # pomodoro runtime state (not persisted between sessions)
        # filter state - persists across re-renders
        self._archive_filters = {"q": "", "priority": "all", "date": "all"}
        self._search_filters  = {"priority": "all", "status": "all", "date": "all"}
        self._pomo_running = False
        self._pomo_phase   = "work"   # "work" or "break"
        self._pomo_secs    = self.cfg["pomo_work_mins"] * 60
        self._pomo_job     = None
        self._pomo_tick_job= None
        self._pomo_phase_start = None  # datetime when current phase began
        self._pomo_lbl     = None      # timer label widget in status bar
        self._pomo_play_btn= None

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
        self.T = tokens(self.cfg["theme"])
        self.search_var = tk.StringVar(master=self.root)
        self._apply_window_mode(first=True)
        self._build_ui()
        self._bind_wheel_once()
        # Trash purge + date jumps used to piggyback on _render_tasks. With tabs
        # cached, _render_tasks stops running on most navigation, so this work
        # needs its own clock.
        self._maint_job = None
        self.root.after(2000, lambda: self._maintenance_tick(first=True))
        self._rec_init()

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

    def _set_scale_debounced(self, s):
        """Update scale value immediately for display, but defer the expensive
        _apply_scale + _retheme until the user stops scrolling/sliding (150ms idle)."""
        self.cfg["ui_scale"] = round(max(0.5, min(3.0, float(s))), 2)
        if hasattr(self, "_scale_job") and self._scale_job:
            try: self.root.after_cancel(self._scale_job)
            except Exception: pass
        self._scale_job = self.root.after(150, self._flush_scale)

    def _flush_scale(self):
        self._scale_job = None
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
        self._tab_archive   = self._mktab(tabs_row,"Archive",    lambda:self._set_tab("archive"))
        self._tab_priorities= self._mktab(tabs_row,"Focus",      lambda:self._set_tab("priorities"))
        # These two are mutually exclusive — _refresh_tabs manages which is visible
        self._tab_archive.pack_forget()
        self._tab_priorities.pack_forget()
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
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_tasks_debounced(160))
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
        # _build_ui rebuilds the canvas, so every cached frame is now a child of
        # a dead widget: drop them all and mark every tab dirty so the new theme
        # is applied on each tab's next visit.
        self._tab_frames = {}
        self._tab_reg    = {}
        self._tab_dirty  = set(self._ALL_TABS)
        self._current_frame_tab = None
        self._mounted_tab = None
        self.task_frame = self._tab_frame(self.current_tab)
        self._cw = self.canvas.create_window((0,0),window=self.task_frame,anchor="nw")
        self._mounted_tab = self.current_tab
        self._show_tab_frame(self.current_tab)
        self.canvas.bind("<Configure>",     lambda e: self.canvas.itemconfig(self._cw,width=e.width))
        for w in (self.canvas,):
            w.bind("<MouseWheel>",         self._scroll)
            w.bind("<Button-4>",           self._scroll)
            w.bind("<Button-5>",           self._scroll)
            w.bind("<Control-MouseWheel>", self._ctrl_scroll)
        # root-level scroll handled by _bind_wheel_once() from __init__

        tk.Frame(self.main,bg=self.T["separator"],height=1).pack(fill="x")
        # ── bottom bar: status + pomodoro controls ───────────────────────────
        bot = tk.Frame(self.main,bg=self.T["header_bg"]); bot.pack(fill="x")
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(bot,textvariable=self.status_var,
            bg=self.T["header_bg"],fg=self.T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8),anchor="w",padx=8,pady=4)
        self.status_lbl.pack(side="left",fill="x",expand=True)
        # pomodoro timer label (hidden until running)
        self._pomo_lbl = tk.Label(bot,text="",bg=self.T["header_bg"],fg=self.T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8,"bold"),padx=4,pady=4,
            cursor="hand2")
        self._pomo_lbl.pack(side="right")
        self._pomo_lbl.bind("<Button-1>",   self._pomo_toggle)
        self._pomo_lbl.bind("<Button-3>",   self._pomo_skip)
        self._pomo_lbl.bind("<Double-Button-1>", lambda e: self._open_pomo_settings())
        # play/pause button
        self._pomo_play_btn = tk.Button(bot,text="▶",command=self._pomo_toggle,
            bg=self.T["header_bg"],fg=self.T["text"],relief="flat",bd=0,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=4,pady=2,cursor="hand2",activebackground=self.T["btn_hover"])
        self._pomo_play_btn.pack(side="right")
        self._pomo_play_btn.bind("<Button-3>", self._pomo_skip)
        # clock icon → open settings
        tk.Button(bot,text="⏱",command=self._open_pomo_settings,
            bg=self.T["header_bg"],fg=self.T["text"],relief="flat",bd=0,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=4,pady=2,cursor="hand2",activebackground=self.T["btn_hover"]).pack(side="right")
        self._render_tasks()
        # NOTE: wheel bindings are registered ONCE from __init__ (_bind_wheel_once).
        # They used to live here, but bind_all(add="+") inside _build_ui stacked a
        # fresh duplicate handler set on every theme/font/scale change and nothing
        # ever unbound them, so scrolling got progressively jumpier over a session.
        # bind_all lives on Tk's "all" bindtag, not on the widgets _build_ui
        # destroys, so registering once is correct.

    def _bind_wheel_once(self):
        """Register wheel/ctrl-wheel handlers exactly once per session.

        Replaces the old _bind_ctrl_wheel_recursive whole-tree walk, which added
        6 bindings to ~1,500 widgets after every _build_ui. That walk was already
        provably redundant: it ran once at startup, so every widget created by any
        later tab switch only ever had these bind_all bindings - and scrolling
        works on those tabs today."""
        if getattr(self, "_wheel_bound", False): return
        for _seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
            self.root.bind_all(_seq, self._scroll, add="+")
        for _seq in ("<Control-MouseWheel>","<Control-Button-4>","<Control-Button-5>"):
            self.root.bind_all(_seq, self._ctrl_scroll, add="+")
        self._wheel_bound = True

    # ── retheme ───────────────────────────────────────────────────────────────
    def _retheme_main_only(self):
        self.T = tokens(self.cfg["theme"])
        old_tab = self.current_tab
        self._build_ui()
        self.current_tab = old_tab
        self._refresh_tabs()
        # _build_ui marked every tab dirty and rebuilt the frames, so this
        # renders; the guard keeps it honest if that ever changes.
        if self.current_tab in self._tab_dirty or self.current_tab in self._ALWAYS_FRESH:
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
        # was two hardcoded theme-name sets covering only 18 of 27 themes; the
        # other 9 silently fell through to `separator`. accent_soft is derived
        # per theme and is guaranteed to read against the titlebar everywhere.
        return self.T["accent_soft"] if self.cfg.get("always_on_top") else self.T["header_bg"]

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
            self._pin_btn.configure(bg=self._soft_pin_color())

    # ── tabs ──────────────────────────────────────────────────────────────────
    def _trash_items(self):
        return [t for t in self.tasks if t.get("deleted")]

    def _trash_habits(self):
        data = load_habits()
        return [h for h in data.get("habits",[]) if h.get("deleted")]

    def _purge_old_habit_trash(self):
        now = now_dt()
        data = load_habits()
        habits = data.get("habits",[])
        kept = [h for h in habits
            if not h.get("deleted") or
               (h.get("deleted_at") and now - parse_iso(h["deleted_at"]) <= datetime.timedelta(hours=TRASH_HOURS))]
        if len(kept) != len(habits):
            data["habits"] = kept
            save_habits(data)

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


    def _refresh_tabs(self):
        T = self.T
        use_pri = self.cfg.get("use_priorities_tab", True)
        # Swap archive <-> priorities tab (they share the same slot)
        self._tab_archive.pack_forget()
        self._tab_priorities.pack_forget()
        if use_pri:
            self._tab_priorities.pack(side="left", padx=(6,0), pady=4, after=self._tab_tasks)
            if self.current_tab == "archive":
                self.current_tab = "priorities"
        else:
            self._tab_archive.pack(side="left", padx=(6,0), pady=4, after=self._tab_tasks)
            if self.current_tab == "priorities":
                self.current_tab = "archive"
        tab_map = [
            (self._tab_tasks,      "active"),
            (self._tab_archive,    "archive"),
            (self._tab_priorities, "priorities"),
            (self._tab_habits,     "habits"),
            (self._tab_docs,       "docs"),
            (self._tab_stats,      "stats"),
            (self._tab_search,     "search"),
        ]
        for tab, name in tab_map:
            self._paint_tab(tab, self.current_tab == name)
        if self._trash_items() or self._trash_docs() or self._trash_habits():
            self._tab_bin.pack(side="left",padx=(6,0),pady=4)
            self._paint_tab(self._tab_bin, self.current_tab == "trash")
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
        # Fast path: already showing this tab and nothing invalidated it.
        if (self._current_frame_tab == name
                and name not in self._tab_dirty
                and name not in self._ALWAYS_FRESH):
            return
        self._stash_tab_state(self._current_frame_tab)
        self.current_tab = name
        self.cfg["last_tab"] = name
        self._save_cfg_debounced()          # was a synchronous save_config()
        self._refresh_tabs()                # may flip archive <-> priorities
        name = self.current_tab             # honour that flip
        self.entry.configure(state="normal" if name == "active" else "disabled")

        if name in self._tab_dirty or name in self._ALWAYS_FRESH:
            # Build OFF-SCREEN, then swap. The previous tab stays on screen
            # untouched for the whole build, so there is no empty frame and no
            # progressive fill-in - the new tab appears complete, in one step.
            self._bind_tab_context(name)
            self._render_tasks()            # clears the dirty flag
            self._flush_pending_draws()     # bars/overlays that defer via after()
            self._mount_tab_frame(name)
        else:
            self._show_tab_frame(name)
            self._refresh_status_bar()
        self._update_scroll()
        self._restore_scroll(name)

    def _flush_pending_draws(self):
        """Run the after()-deferred painters (progress bars, button overlays,
        grid relayout) BEFORE the frame is mounted, so they do not pop in one
        frame late. Bounded: only already-queued idle work is drained."""
        try:
            self.root.update_idletasks()
        except Exception:
            pass

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
        self._set_scale_debounced(self.cfg.get("ui_scale",1.0) + (0.05 if (getattr(e,"num",None)==4 or getattr(e,"delta",0)>0) else -0.05))

    # ── task pools ────────────────────────────────────────────────────────────
    def _build_task_cache(self):
        """Single-pass split of self.tasks into pools. Cached until next save."""
        now = now_dt()
        today = datetime.date.today()
        cutoff = now - datetime.timedelta(days=1)
        active = []; scheduled = []; archived = []
        for t in self.tasks:
            if t.get("deleted"): continue
            done = t.get("done", False)
            if done:
                ca = t.get("completed_at")
                if ca:
                    try:
                        if parse_iso(ca) < cutoff:
                            archived.append(t)
                            continue
                    except Exception:
                        pass
            sd = t.get("start_date")
            if sd and not done:
                try:
                    if datetime.date.fromisoformat(sd) > today:
                        scheduled.append(t)
                        continue
                except Exception:
                    pass
            active.append(t)
        self._tasks_cache = {"active": active, "scheduled": scheduled, "archived": archived}

    def _active_tasks(self):
        if self._tasks_cache is None: self._build_task_cache()
        return self._tasks_cache["active"]

    def _scheduled_tasks(self):
        if self._tasks_cache is None: self._build_task_cache()
        return self._tasks_cache["scheduled"]

    def _archived_tasks(self):
        if self._tasks_cache is None: self._build_task_cache()
        return self._tasks_cache["archived"]

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
        # Self-correcting resync. _add_task, _unsolve_task and _trash_task
        # assign self.current_tab directly and then call _render_tasks,
        # bypassing _set_tab; without this they would render one tab's content
        # into another tab's frame.
        if self._current_frame_tab != self.current_tab:
            self._stash_tab_state(self._current_frame_tab)
            self._show_tab_frame(self.current_tab)
        # Preserve scroll across in-tab re-renders (checkbox toggle, priority
        # cycle, trash/recover). Every one of these used to jump to the top.
        try: keep_off = self.canvas.yview()[0]
        except Exception: keep_off = 0.0
        # _refresh_tabs (called below, AFTER the dispatch) can itself reassign
        # self.current_tab - archive<->priorities, or trash->active when the bin
        # empties. Book-keep against what we actually rendered, not against the
        # post-flip value, or we file this tab's registries under another tab's
        # name and mark that other tab clean while its frame is still empty.
        rendered = self.current_tab
        self._subtask_label_registry = {}
        self._subtask_check_registry = {}
        self._task_widget_registry   = {}   # id(task) -> {lbl, pri_bar, tw, ...}
        # Keep this pack_propagate pair: it stops task_frame collapsing to zero
        # height mid-rebuild.
        self.task_frame.pack_propagate(False)
        for w in self.task_frame.winfo_children(): w.destroy()
        T = self.T
        if   rendered == "active":     self._render_active(T)
        elif rendered == "archive":    self._render_archive(T)
        elif rendered == "trash":      self._render_trash(T)
        elif rendered == "search":     self._render_search(T)
        elif rendered == "stats":      self._render_stats(T)
        elif rendered == "docs":       self._render_docs(T)
        elif rendered == "habits":     self._render_habits(T)
        elif rendered == "priorities": self._render_priorities(T)
        else:                          self._render_active(T)
        tk.Frame(self.task_frame, bg=T["bg"], height=60).pack(fill="x")
        self.task_frame.pack_propagate(True)   # re-enable: single repaint
        self._update_scroll()
        self._refresh_tabs()
        self._tab_dirty.discard(rendered)
        # Store the freshly built registries against the tab we rendered. These
        # are the same mutable dicts the row builders keep filling afterwards,
        # so storing the reference (not a copy) is correct.
        self._tab_reg[rendered] = (self._task_widget_registry,
                                   self._subtask_label_registry,
                                   self._subtask_check_registry)
        if self.current_tab != rendered:       # _refresh_tabs flipped us
            self._tab_dirty.add(self.current_tab)
            self._render_tasks_debounced(0)
        self._refresh_status_bar()
        try: self.canvas.yview_moveto(keep_off)
        except Exception: pass

    def _render_active(self, T):
        pool     = self._active_tasks()
        scheduled = self._scheduled_tasks()
        unsolved = [t for t in pool if not t.get("done")]
        solved   = [t for t in pool if t.get("done")]
        if not unsolved and not solved and not scheduled:
            tk.Label(self.task_frame,text="No tasks yet.\nAdd one above ↑",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=28).pack(fill="x")
            return
        for task in unsolved:
            self._task_row(task)
        if scheduled:
            sep2 = tk.Frame(self.task_frame,bg=T["separator"],height=1)
            sep2.pack(fill="x",pady=4,padx=2)
            tk.Label(self.task_frame,text="🗓 Scheduled",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8,"bold"),
                anchor="w",padx=6).pack(fill="x")
            for task in scheduled:
                self._task_row(task, scheduled=True)
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
        import datetime as _dt
        all_pool = sorted(self._archived_tasks(),
                          key=lambda t: t.get("completed_at",""), reverse=True)

        # ── Filter bar ─────────────────────────────────────────────────────
        fbar = tk.Frame(self.task_frame, bg=T["header_bg"], padx=6, pady=4)
        fbar.pack(fill="x", pady=(0,4))
        fn = (self.cfg.get("ui_font","Segoe UI Variable"), 8)

        # search input
        af = self._archive_filters
        q_var = tk.StringVar(value=af["q"])
        q_ent = tk.Entry(fbar, textvariable=q_var, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat",
            font=fn, width=14, bd=0, highlightthickness=1,
            highlightbackground=T["separator"], highlightcolor=T["check_done"])
        q_ent.pack(side="left", padx=(0,6), ipady=3)
        tk.Label(fbar, text="🔍", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(0,2))

        # priority filter
        prio_var = tk.StringVar(value=af["priority"])
        tk.Label(fbar, text="Priority:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(6,2))
        prio_menu = tk.OptionMenu(fbar, prio_var, "all", "high", "medium", "low", "none")
        prio_menu.configure(bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            activebackground=T["btn_hover"], highlightthickness=0, font=fn, padx=4, pady=2)
        prio_menu["menu"].configure(bg=T["entry_bg"], fg=T["entry_fg"], font=fn)
        prio_menu.pack(side="left", padx=(0,6))

        # date filter
        date_var = tk.StringVar(value=af["date"])
        tk.Label(fbar, text="Date:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(6,2))
        date_menu = tk.OptionMenu(fbar, date_var, "all", "today", "week", "month")
        date_menu.configure(bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            activebackground=T["btn_hover"], highlightthickness=0, font=fn, padx=4, pady=2)
        date_menu["menu"].configure(bg=T["entry_bg"], fg=T["entry_fg"], font=fn)
        date_menu.pack(side="left", padx=(0,6))

        # result count label
        count_lbl = tk.Label(fbar, text="", bg=T["header_bg"], fg=T["muted"], font=fn)
        count_lbl.pack(side="right")

        def _apply_filters(*_):
            q  = q_var.get().strip().lower()
            pr = prio_var.get()
            dt = date_var.get()
            af["q"] = q; af["priority"] = pr; af["date"] = dt
            now = _dt.datetime.now()
            cutoff = None
            if dt == "today":  cutoff = now - _dt.timedelta(days=1)
            elif dt == "week": cutoff = now - _dt.timedelta(days=7)
            elif dt == "month":cutoff = now - _dt.timedelta(days=30)
            filtered = []
            for t in all_pool:
                if q and q not in t.get("text","").lower(): continue
                if pr != "all" and t.get("priority","none") != pr: continue
                if cutoff:
                    ca = t.get("completed_at","")
                    if ca:
                        try:
                            td = _dt.datetime.fromisoformat(ca)
                            if td < cutoff: continue
                        except Exception: pass
                    else: continue
                filtered.append(t)
            # remove old task rows (keep filter bar)
            for w in self.task_frame.winfo_children():
                if w is not fbar: w.destroy()
            count_lbl.configure(text=f"{len(filtered)} tasks")
            if not filtered:
                tk.Label(self.task_frame, text="No matching tasks.",
                    bg=T["bg"], fg=T["muted"],
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                    justify="center", pady=20).pack(fill="x")
            else:
                for task in filtered:
                    self._task_row(task, archived=True)
            self._update_scroll()
            # rebind scroll on new widgets

        q_var.trace_add("write", _apply_filters)
        prio_var.trace_add("write", _apply_filters)
        date_var.trace_add("write", _apply_filters)

        # middle-mouse click to scroll to top/bottom
        def _mid_scroll(e):
            self.canvas.yview_moveto(0.0 if self.canvas.yview()[0] > 0.3 else 1.0)
        self.canvas.bind("<Button-2>", _mid_scroll)
        self.task_frame.bind("<Button-2>", _mid_scroll)

        if not all_pool:
            count_lbl.configure(text="0 tasks")
            tk.Label(self.task_frame, text="Archive is empty.",
                bg=T["bg"], fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center", pady=28).pack(fill="x")
            return

        _apply_filters()



    def _sync_doc_backup(self, doc, folder):
        """Write doc as a markdown file in the backup folder."""
        import re as _re
        safe = _re.sub(r'[\\/:*?"<>|]',"_", doc.get("title","Untitled"))[:60] or "Untitled"
        path = os.path.join(folder, safe+".md")
        try:
            os.makedirs(folder, exist_ok=True)
            with open(path,"w",encoding="utf-8") as f:
                f.write(f"# {doc.get('title','Untitled')}\n\n{doc.get('body','')}")
        except Exception:
            pass

    def _delete_doc_backup(self, doc):
        """Remove backup markdown file when doc is deleted."""
        import re as _re
        bp = self.cfg.get("docs_backup_path","").strip()
        if not bp: return
        cat = doc.get("category","Default") or "Default"
        cat_folder = os.path.join(bp, cat)
        safe = _re.sub(r'[\\/:*?"<>|]',"_", doc.get("title","Untitled"))[:60] or "Untitled"
        path = os.path.join(cat_folder, safe+".md")
        try:
            if os.path.exists(path): os.remove(path)
        except Exception:
            pass

    def _restore_doc_backup(self, doc):
        """Re-write backup markdown file when doc is restored from trash."""
        bp = self.cfg.get("docs_backup_path","").strip()
        if not bp: return
        cat = doc.get("category","Default") or "Default"
        cat_folder = os.path.join(bp, cat)
        self._sync_doc_backup(doc, cat_folder)

    def _render_trash(self, T):
        tasks   = sorted(self._trash_items(),   key=lambda t:t.get("deleted_at",""), reverse=True)
        docs    = sorted(self._trash_docs(),    key=lambda d:d.get("deleted_at",""), reverse=True)
        habits  = sorted(self._trash_habits(),  key=lambda h:h.get("deleted_at",""), reverse=True)
        if not tasks and not docs and not habits:
            tk.Label(self.task_frame,text="Bin is empty.",bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                justify="center",pady=28).pack(fill="x")
            return
        if tasks:
            for task in tasks:
                self._task_row(task, trashed=True)
        if habits:
            tk.Label(self.task_frame,text="- Deleted Habits -",bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),pady=4).pack(fill="x")
            for habit in habits:
                self._trash_habit_row(habit, T)
        if docs:
            tk.Label(self.task_frame,text="- Deleted Docs -",bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),pady=4).pack(fill="x")
            for doc in docs:
                self._trash_doc_row(doc, T)

    def _trash_habit_row(self, habit, T):
        row = tk.Frame(self.task_frame,bg=T["item_bg"],pady=4,padx=6); row.pack(fill="x",pady=2)
        tw = tk.Frame(row,bg=T["item_bg"]); tw.pack(side="left",fill="x",expand=True)
        tk.Label(tw,text=f"🌱 {habit.get('name','Habit')}",bg=T["item_bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10,"bold"),anchor="w").pack(anchor="w")
        deleted_at = habit.get("deleted_at","")
        if deleted_at:
            remain = max(0,int((datetime.timedelta(hours=TRASH_HOURS)-(now_dt()-parse_iso(deleted_at))).total_seconds()//3600))
            tk.Label(tw,text=f"~{remain}h left",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),anchor="w").pack(anchor="w")
        bf = tk.Frame(row,bg=T["item_bg"]); bf.pack(side="right")
        def restore_habit(h=habit):
            data = load_habits()
            for hx in data.get("habits",[]):
                if hx.get("id")==h.get("id"):
                    hx.pop("deleted",None); hx.pop("deleted_at",None); break
            save_habits(data); self._render_tasks()
        _del_hab_ref = [None]
        def del_habit_confirm(btn_r=_del_hab_ref, h=habit):
            b = btn_r[0]
            if b is None: return
            if getattr(b,"_confirm",False):
                data = load_habits()
                data["habits"] = [hx for hx in data.get("habits",[]) if hx.get("id")!=h.get("id")]
                save_habits(data); self._render_tasks()
            else:
                b._confirm = True; b.configure(text="Sure?",fg=T["close_hover"])
                b.after(2000, lambda: (setattr(b,"_confirm",False),
                    b.configure(text="🗑",fg=T["text"])) if b.winfo_exists() else None)
        tk.Button(bf,text="↺",command=restore_habit,
            bg=T["item_bg"],fg=T["text"],relief="flat",bd=0,padx=4,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),cursor="hand2",
            activebackground=T["item_hover"]).pack(side="right")
        del_hab_btn = tk.Button(bf,text="🗑",command=del_habit_confirm,
            bg=T["item_bg"],fg=T["text"],relief="flat",bd=0,padx=4,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),cursor="hand2",
            activebackground=T["item_hover"])
        del_hab_btn._confirm=False; _del_hab_ref[0]=del_hab_btn
        del_hab_btn.pack(side="right")


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
            restored = None
            for dd in all_docs:
                if dd.get("id")==d.get("id"):
                    dd.pop("deleted",None); dd.pop("deleted_at",None)
                    restored = dd; break
            save_docs(all_docs)
            if restored: self._restore_doc_backup(restored)
            self._render_tasks()
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


    # ── habit drag-reorder ───────────────────────────────────────────────────
    def _habit_drag_start(self, e, idx, habits_list, data):
        self._drag_habit_idx   = idx
        self._drag_habit_start = e.y_root
        self._drag_habit_moved = False
        self._drag_habit_list  = habits_list
        self._drag_habit_data  = data
        # Grab motion/release globally so drag works outside the handle widget
        self.root.bind("<B1-Motion>",       self._habit_drag_motion,   add="+")
        self.root.bind("<ButtonRelease-1>", self._habit_drag_end_root, add="+")

    def _habit_drag_motion(self, e):
        if not hasattr(self, "_drag_habit_idx") or self._drag_habit_idx is None: return
        if abs(e.y_root - self._drag_habit_start) > 6:
            self._drag_habit_moved = True

    def _habit_drag_end_root(self, e):
        self.root.unbind("<B1-Motion>")
        self.root.unbind("<ButtonRelease-1>")
        if not hasattr(self, "_drag_habit_idx") or self._drag_habit_idx is None: return
        if not getattr(self, "_drag_habit_moved", False):
            self._drag_habit_idx = None; return
        src          = self._drag_habit_idx
        habits_list  = self._drag_habit_list
        data         = self._drag_habit_data
        self._drag_habit_idx = None; self._drag_habit_moved = False
        # find which habit card the pointer is over
        target = None
        for child in self.task_frame.winfo_children():
            if not hasattr(child, "_habit_idx"): continue
            cy = child.winfo_rooty()
            if cy <= e.y_root <= cy + child.winfo_height():
                target = child._habit_idx; break
        if target is None or target == src: return
        if src < len(habits_list) and target < len(habits_list):
            moved_id  = habits_list[src]["id"]
            target_id = habits_list[target]["id"]
            all_habits = data.get("habits", [])
            src_full = next((i for i,h in enumerate(all_habits) if h["id"]==moved_id), None)
            tgt_full = next((i for i,h in enumerate(all_habits) if h["id"]==target_id), None)
            if src_full is not None and tgt_full is not None:
                all_habits.insert(tgt_full, all_habits.pop(src_full))
                save_habits(data)
                self._render_tasks()

    def _habit_drag_end(self, e, habits_list, data):
        pass  # kept for compat; real logic in _habit_drag_end_root

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

    def _show_calendar_picker(self, parent_widget, initial_date, on_select,
                              show_time=False, initial_time=None):
        """Calendar popup. on_select(date) or on_select((date, "HH:MM")) if show_time."""
        import datetime as _dt, calendar as _cal
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=self.T["header_bg"])
        T = self.T
        fn  = (self.cfg.get("ui_font","Segoe UI Variable"), 9)
        fnb = (self.cfg.get("ui_font","Segoe UI Variable"), 9, "bold")

        today = _dt.date.today()
        # selected = the date the user has actually picked (or initial)
        selected = [initial_date]          # may be None
        # view = month being displayed (always a valid date, default today)
        view = [initial_date or today]

        # time vars
        hour_var  = tk.StringVar(value=(initial_time or "")[0:2] or "")
        min_var   = tk.StringVar(value=(initial_time or "")[-2:] or "")

        frame = tk.Frame(win, bg=T["header_bg"], padx=4, pady=4)
        frame.pack()

        def _build():
            for w in frame.winfo_children():
                w.destroy()
            y, m = view[0].year, view[0].month
            # header
            hdr = tk.Frame(frame, bg=T["header_bg"]); hdr.pack(fill="x", pady=(0,4))
            tk.Button(hdr, text="◀", command=lambda: _shift(-1),
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=fn,
                padx=6, pady=2, cursor="hand2").pack(side="left")
            tk.Label(hdr, text=f"{_cal.month_name[m]} {y}",
                bg=T["header_bg"], fg=T["text"], font=fnb).pack(side="left", expand=True)
            tk.Button(hdr, text="▶", command=lambda: _shift(1),
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=fn,
                padx=6, pady=2, cursor="hand2").pack(side="right")
            # day headers
            gf = tk.Frame(frame, bg=T["header_bg"]); gf.pack()
            for i, d in enumerate(["Mo","Tu","We","Th","Fr","Sa","Su"]):
                tk.Label(gf, text=d, bg=T["header_bg"], fg=T["muted"],
                    font=fn, width=3).grid(row=0, column=i, padx=1)
            # day grid
            for r, week in enumerate(_cal.monthcalendar(y, m)):
                for c, day in enumerate(week):
                    if day == 0:
                        tk.Label(gf, text="", bg=T["header_bg"], width=3).grid(row=r+1, column=c)
                        continue
                    d = _dt.date(y, m, day)
                    # is_sel: only if selected date matches this exact cell's date
                    is_sel   = (selected[0] is not None and d == selected[0])
                    is_today = (d == today)
                    if is_sel:
                        bg, fg = T["archive"], "#ffffff"
                    elif is_today:
                        bg, fg = "#22a34a", "#ffffff"
                    else:
                        bg, fg = T["item_bg"], T["text"]
                    def _click(date=d):
                        selected[0] = date
                        _do_select(date)
                    tk.Button(gf, text=str(day), command=_click,
                        bg=bg, fg=fg, relief="flat", font=fn,
                        width=3, pady=2, cursor="hand2",
                        activebackground=T["btn_hover"]).grid(row=r+1, column=c, padx=1, pady=1)
            # time row (only for due)
            if show_time:
                tf = tk.Frame(frame, bg=T["header_bg"]); tf.pack(fill="x", pady=(4,0))
                tk.Label(tf, text="⏰ Time:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(0,4))
                hv = tk.Spinbox(tf, from_=0, to=23, width=3, format="%02.0f",
                    textvariable=hour_var, bg=T["entry_bg"], fg=T["entry_fg"],
                    relief="flat", font=fn, wrap=True)
                hv.pack(side="left")
                tk.Label(tf, text=":", bg=T["header_bg"], fg=T["text"], font=fnb).pack(side="left", padx=2)
                mv = tk.Spinbox(tf, from_=0, to=59, width=3, format="%02.0f",
                    textvariable=min_var, bg=T["entry_bg"], fg=T["entry_fg"],
                    relief="flat", font=fn, wrap=True)
                mv.pack(side="left")
            # bottom bar
            bf = tk.Frame(frame, bg=T["header_bg"]); bf.pack(fill="x", pady=(4,0))
            tk.Button(bf, text="✕ Clear", command=lambda: (on_select(None), win.destroy()),
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=fn,
                padx=8, pady=2, cursor="hand2").pack(side="left")
            tk.Button(bf, text="Today", command=lambda: (selected.__setitem__(0, today), _do_select(today)),
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=fn,
                padx=8, pady=2, cursor="hand2").pack(side="right")

        def _do_select(date):
            if show_time:
                try:
                    h = int(hour_var.get() or 0); m2 = int(min_var.get() or 0)
                    on_select((date, f"{h:02d}:{m2:02d}"))
                except Exception:
                    on_select((date, "00:00"))
            else:
                on_select(date)
            win.destroy()

        def _shift(delta):
            y, m = view[0].year, view[0].month
            m += delta
            if m > 12: m, y = 1, y+1
            elif m < 1: m, y = 12, y-1
            last = _cal.monthrange(y, m)[1]
            # update view only; selected stays unchanged
            view[0] = view[0].replace(year=y, month=m, day=min(view[0].day, last))
            _build()

        _build()
        win.update_idletasks()
        try:
            wx = parent_widget.winfo_rootx()
            wy = parent_widget.winfo_rooty() + parent_widget.winfo_height() + 2
        except Exception:
            wx, wy = 100, 100
        win.geometry(f"+{wx}+{wy}")
        win.focus_set()
        win.bind("<Escape>", lambda e: win.destroy())

        # Close when user clicks anywhere outside this popup
        def _global_click(e, w=win):
            if not w.winfo_exists(): return
            # check if click landed inside the popup window
            wx0, wy0 = w.winfo_rootx(), w.winfo_rooty()
            wx1, wy1 = wx0 + w.winfo_width(), wy0 + w.winfo_height()
            if wx0 <= e.x_root <= wx1 and wy0 <= e.y_root <= wy1:
                return  # click inside popup — ignore
            try: w.destroy()
            except Exception: pass
            try: self.root.unbind("<Button-1>", _click_id[0])
            except Exception: pass

        # Destroy any previously open calendar
        prev = getattr(self, "_open_calendar", None)
        if prev:
            try: prev.destroy()
            except Exception: pass
        self._open_calendar = win

        _click_id = [None]
        _click_id[0] = self.root.bind("<Button-1>", _global_click, add="+")
        win.bind("<Destroy>", lambda e: self._clear_calendar_bind(_click_id[0]))


    def _clear_calendar_bind(self, bid):
        try: self.root.unbind("<Button-1>", bid)
        except Exception: pass
        if getattr(self, "_open_calendar", None):
            try:
                if not self._open_calendar.winfo_exists():
                    self._open_calendar = None
            except Exception:
                self._open_calendar = None

    def _render_search(self, T):
        import datetime as _dt
        sf = self._search_filters

        # ── Filter bar ──────────────────────────────────────────────────────
        fbar = tk.Frame(self.task_frame, bg=T["header_bg"], padx=6, pady=4)
        fbar.pack(fill="x", pady=(0,4))
        fn = (self.cfg.get("ui_font","Segoe UI Variable"), 8)

        # priority filter
        prio_var = tk.StringVar(value=sf["priority"])
        tk.Label(fbar, text="Priority:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(0,2))
        prio_menu = tk.OptionMenu(fbar, prio_var, "all", "high", "medium", "low", "none")
        prio_menu.configure(bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            activebackground=T["btn_hover"], highlightthickness=0, font=fn, padx=4, pady=2)
        prio_menu["menu"].configure(bg=T["entry_bg"], fg=T["entry_fg"], font=fn)
        prio_menu.pack(side="left", padx=(0,8))

        # status filter
        status_var = tk.StringVar(value=sf["status"])
        tk.Label(fbar, text="Status:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(0,2))
        status_menu = tk.OptionMenu(fbar, status_var, "all", "active", "resolved")
        status_menu.configure(bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            activebackground=T["btn_hover"], highlightthickness=0, font=fn, padx=4, pady=2)
        status_menu["menu"].configure(bg=T["entry_bg"], fg=T["entry_fg"], font=fn)
        status_menu.pack(side="left", padx=(0,8))

        # From / To date pickers (filters by completed_at for resolved tasks)
        sd = [sf.get("date_from"), sf.get("date_to")]
        tk.Label(fbar, text="From:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(0,2))
        s_from_btn = tk.Button(fbar, text=str(sd[0]) if sd[0] else "any",
            bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=fn, padx=6, pady=2, cursor="hand2",
            activebackground=T["btn_hover"])
        s_from_btn.pack(side="left", padx=(0,4))
        tk.Label(fbar, text="To:", bg=T["header_bg"], fg=T["muted"], font=fn).pack(side="left", padx=(2,2))
        s_to_btn = tk.Button(fbar, text=str(sd[1]) if sd[1] else "any",
            bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=fn, padx=6, pady=2, cursor="hand2",
            activebackground=T["btn_hover"])
        s_to_btn.pack(side="left", padx=(0,8))

        count_lbl = tk.Label(fbar, text="", bg=T["header_bg"], fg=T["muted"], font=fn)
        count_lbl.pack(side="right")

        base_pool = self._search_pool()

        def _apply(*_):
            pr = prio_var.get()
            st = status_var.get()
            sf["priority"] = pr; sf["status"] = st
            sf["date_from"] = sd[0]; sf["date_to"] = sd[1]
            filtered = []
            for t in base_pool:
                if pr != "all" and t.get("priority","none") != pr: continue
                if st == "active" and t.get("done"): continue
                if st == "resolved" and not t.get("done"): continue
                if (sd[0] or sd[1]) and t.get("done"):
                    ca = t.get("completed_at","")
                    if ca:
                        try:
                            td = _dt.datetime.fromisoformat(ca).date()
                            if sd[0] and td < sd[0]: continue
                            if sd[1] and td > sd[1]: continue
                        except Exception: pass
                    else: continue
                filtered.append(t)
            for w in self.task_frame.winfo_children():
                if w is not fbar: w.destroy()
            count_lbl.configure(text=f"{len(filtered)} results")
            if not filtered:
                tk.Label(self.task_frame, text="No results match filters.",
                    bg=T["bg"], fg=T["muted"],
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
                    justify="center", pady=20).pack(fill="x")
            else:
                for task in filtered:
                    self._task_row(task, searching=True)
            self._update_scroll()

        def _pick_s_from():
            self._show_calendar_picker(s_from_btn, sd[0],
                lambda d: (sd.__setitem__(0, d),
                           s_from_btn.configure(text=str(d) if d else "any"),
                           _apply()))
        def _pick_s_to():
            self._show_calendar_picker(s_to_btn, sd[1],
                lambda d: (sd.__setitem__(1, d),
                           s_to_btn.configure(text=str(d) if d else "any"),
                           _apply()))
        s_from_btn.configure(command=_pick_s_from)
        s_to_btn.configure(command=_pick_s_to)

        prio_var.trace_add("write", _apply)
        status_var.trace_add("write", _apply)
        _apply()


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

        # ── Pomodoro statistics ────────────────────────────────────────────
        tk.Frame(f,bg=T["separator"],height=1).pack(fill="x",pady=(4,8))
        tk.Label(f,text="⏱  Focus Time",bg=T["bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10,"bold")).pack(anchor="w",pady=(0,4))

        import datetime as _dt2
        _today_key = _dt2.date.today().isoformat()
        _today_data = self.cfg.get("pomo_daily", {}).get(_today_key, {})
        work_secs  = _today_data.get("work", 0)
        break_secs = _today_data.get("break", 0)
        # add current running session if timer is active today
        if getattr(self, "_pomo_running", False):
            elapsed = self.cfg.get("pomo_work_mins",25)*60 - getattr(self,"_pomo_secs",0)
            if getattr(self,"_pomo_phase","work") == "work":
                work_secs = max(work_secs, work_secs)  # already accumulated in daily
        total_secs = work_secs + break_secs

        def _fmt_dur(s):
            h = s // 3600; m = (s % 3600) // 60
            return f"{h}h {m:02d}m" if h > 0 else f"{m}m {s%60:02d}s"

        pf = tk.Frame(f, bg=T["bg"]); pf.pack(fill="x")
        pf.columnconfigure(1, weight=1)
        rows_p = [
            ("💼 Work time:",   _fmt_dur(work_secs),  self.cfg.get("pomo_work_color","#e05c5c")),
            ("☕ Break time:",  _fmt_dur(break_secs), self.cfg.get("pomo_break_color","#4caf88")),
            ("🕐 Total tracked:", _fmt_dur(total_secs), T["text"]),
        ]
        for i,(lbl_t,val_t,col) in enumerate(rows_p):
            tk.Label(pf,text=lbl_t,bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                anchor="w").grid(row=i,column=0,sticky="w",pady=1)
            tk.Label(pf,text=val_t,bg=T["bg"],fg=col,
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8,"bold"),
                anchor="e").grid(row=i,column=1,sticky="e",pady=1)
        if total_secs > 0:
            work_pct = int(100 * work_secs / total_secs)
            tk.Label(f,text=f"Work ratio: {work_pct}%  |  Break: {100-work_pct}%",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),pady=2).pack(anchor="w")
            bar_c = tk.Canvas(f, bg=T["bg"], height=10, bd=0, highlightthickness=0)
            bar_c.pack(fill="x", pady=(2,6))
            def _draw_pbar(e=None, wc=work_secs, tc=total_secs):
                bw = bar_c.winfo_width() or 200
                bar_c.delete("all")
                ww = int(bw * wc / tc)
                if ww > 0:
                    bar_c.create_rectangle(0,0,ww,10,
                        fill=self.cfg.get("pomo_work_color","#e05c5c"),outline="")
                if ww < bw:
                    bar_c.create_rectangle(ww,0,bw,10,
                        fill=self.cfg.get("pomo_break_color","#4caf88"),outline="")
            bar_c.bind("<Configure>", _draw_pbar)
            self.root.after(120, _draw_pbar)
        else:
            tk.Label(f,text="Start the timer to track focus time ⏱",
                bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),pady=4).pack(anchor="w")

        # ── All-time totals (computed from daily data) ──────────────────────
        tk.Frame(f,bg=T["separator"],height=1).pack(fill="x",pady=(6,4))
        tk.Label(f,text="📊  All-Time Totals",bg=T["bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold")).pack(anchor="w",pady=(0,4))

        _all_daily = self.cfg.get("pomo_daily", {})
        total_work  = sum(v.get("work", 0)  for v in _all_daily.values())
        total_break = sum(v.get("break", 0) for v in _all_daily.values())
        total_all   = total_work + total_break

        def _fmt_full(s):
            h = s // 3600; m = (s % 3600) // 60
            return f"{h}h {m:02d}m" if h else f"{m}m {s%60:02d}s"

        tot_f = tk.Frame(f, bg=T["bg"]); tot_f.pack(fill="x")
        tot_f.columnconfigure(1, weight=1)
        for i,(lbl_t,val_t,col) in enumerate([
            ("💼 Total work:",   _fmt_full(total_work),  self.cfg.get("pomo_work_color","#e05c5c")),
            ("☕ Total break:",  _fmt_full(total_break), self.cfg.get("pomo_break_color","#4caf88")),
            ("🕐 Grand total:", _fmt_full(total_all),   T["text"]),
        ]):
            tk.Label(tot_f,text=lbl_t,bg=T["bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                anchor="w").grid(row=i,column=0,sticky="w",pady=1)
            tk.Label(tot_f,text=val_t,bg=T["bg"],fg=col,
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8,"bold"),
                anchor="e").grid(row=i,column=1,sticky="e",pady=1)

        # ── Daily activity heatmap ─────────────────────────────────────────
        tk.Frame(f,bg=T["separator"],height=1).pack(fill="x",pady=(6,6))

        daily = self.cfg.get("pomo_daily", {})
        today = datetime.date.today()

        # color bands
        _HMAP_BANDS = [
            (0,         T["item_bg"]),
            (1,         "#e05c5c"),
            (1800,      "#f4a623"),
            (3600,      "#ffe100"),
            (7200,      "#4caf88"),
            (14400,     "#29b6d8"),
            (21600,     "#a855f7"),
        ]
        def _day_color(secs):
            for threshold, color in reversed(_HMAP_BANDS):
                if secs >= threshold:
                    return color
            return T["item_bg"]

        # title row with expand button
        _hmap_days = [60]
        hmap_title_row = tk.Frame(f, bg=T["bg"]); hmap_title_row.pack(fill="x", pady=(0,2))
        _hmap_title_lbl = tk.Label(hmap_title_row,
            text="📅  Daily Work Heatmap (last 60 days)",
            bg=T["bg"], fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold"))
        _hmap_title_lbl.pack(side="left")

        # legend
        leg_f = tk.Frame(f, bg=T["bg"]); leg_f.pack(anchor="w", pady=(0,4))
        for txt, col in [("None",T["item_bg"]),("<30m","#e05c5c"),("<1h","#f4a623"),
                         ("<2h","#ffe100"),("<4h","#4caf88"),("<6h","#29b6d8"),("6h+","#a855f7")]:
            li = tk.Frame(leg_f, bg=T["bg"]); li.pack(side="left", padx=(0,6))
            tk.Frame(li, bg=col, width=10, height=10).pack(side="left", padx=(0,2))
            tk.Label(li, text=txt, bg=T["bg"], fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),7)).pack(side="left")

        heat_container = [None]

        def _build_heatmap(n_days):
            if heat_container[0] and heat_container[0].winfo_exists():
                heat_container[0].destroy()
            days = [(today - datetime.timedelta(days=i)) for i in range(n_days-1, -1, -1)]
            COLS = 10 if n_days <= 60 else 26
            SQ   = 18 if n_days <= 60 else 14
            heat_f = tk.Frame(f, bg=T["bg"]); heat_f.pack(anchor="w", pady=(0,4))
            heat_container[0] = heat_f
            for i, day in enumerate(days):
                r, c   = divmod(i, COLS)
                dk     = day.isoformat()
                dd     = daily.get(dk, {})
                w_s    = dd.get("work", 0)
                b_s    = dd.get("break", 0)
                color  = _day_color(w_s)
                tip    = (f"{dk}\n\U0001f4bc {w_s//60}m work\n\u2615 {b_s//60}m break"
                          if (w_s or b_s) else dk)
                sq = tk.Canvas(heat_f, width=SQ, height=SQ, bd=0,
                    highlightthickness=1,
                    highlightbackground=T["separator"],
                    highlightcolor=T["separator"])
                sq.create_rectangle(0, 0, SQ, SQ, fill=color, outline="")
                sq.grid(row=r, column=c, padx=1, pady=1)
                tip_lbl = [None]
                def _enter(e, t=tip):
                    tl = tk.Toplevel(self.root); tl.overrideredirect(True)
                    tl.attributes("-topmost", True); tl.configure(bg=T["header_bg"])
                    tk.Label(tl, text=t, bg=T["header_bg"], fg=T["text"],
                        font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                        padx=6, pady=3, justify="left").pack()
                    tl.geometry(f"+{e.x_root+12}+{e.y_root+12}")
                    tip_lbl[0] = tl
                def _leave(e):
                    if tip_lbl[0]:
                        try: tip_lbl[0].destroy()
                        except Exception: pass
                        tip_lbl[0] = None
                sq.bind("<Enter>", _enter)
                sq.bind("<Leave>", _leave)

        _build_heatmap(60)

        # expand button row (below grid)
        exp_row = tk.Frame(f, bg=T["bg"]); exp_row.pack(anchor="e", pady=(0,2))
        def _toggle_expand():
            if _hmap_days[0] == 60:
                _hmap_days[0] = 365
                _hmap_title_lbl.configure(text="📅  Daily Work Heatmap (last 365 days)")
                exp_btn.configure(text="⊡ 60d")
            else:
                _hmap_days[0] = 60
                _hmap_title_lbl.configure(text="📅  Daily Work Heatmap (last 60 days)")
                exp_btn.configure(text="⊞ 365d")
            _build_heatmap(_hmap_days[0])
        _all_days_win = [None]
        def _open_all_days():
            if _all_days_win[0] and _all_days_win[0].winfo_exists():
                _all_days_win[0].lift(); _all_days_win[0].focus_set(); return
            aw = tk.Toplevel(self.root)
            _all_days_win[0] = aw
            aw.title("All Tracked Days")
            aw.configure(bg=T["bg"])
            aw.attributes("-topmost", True)
            # restore saved geometry
            _ad_geo = self.cfg.get("all_days_geo", "540x460")
            try: aw.geometry(_ad_geo)
            except Exception: aw.geometry("540x460")
            aw.minsize(360, 260)
            def _save_geo(e=None):
                if aw.winfo_exists():
                    self.cfg["all_days_geo"] = aw.geometry()
            aw.bind("<Configure>", _save_geo)

            # title + toggle row
            top_row = tk.Frame(aw, bg=T["bg"]); top_row.pack(fill="x", padx=8, pady=(8,0))
            tk.Label(top_row, text="📅  All Tracked Days",
                bg=T["bg"], fg=T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),11,"bold")).pack(side="left")
            _view_mode = [self.cfg.get("all_days_view","list")]
            toggle_btn = tk.Button(top_row, text="⊞ Squares" if _view_mode[0]=="list" else "☰ List",
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                padx=8, pady=2, cursor="hand2", activebackground=T["btn_hover"])
            toggle_btn.pack(side="right")
            tk.Frame(aw, bg=T["separator"], height=1).pack(fill="x", pady=(4,0))

            # scrollable area
            cf = tk.Frame(aw, bg=T["bg"]); cf.pack(fill="both", expand=True)
            ac = tk.Canvas(cf, bg=T["bg"], bd=0, highlightthickness=0)
            asb = ttk.Scrollbar(cf, orient="vertical", command=ac.yview,
                style="LeSticky.Vertical.TScrollbar")
            ac.configure(yscrollcommand=asb.set)
            asb.pack(side="right", fill="y"); ac.pack(side="left", fill="both", expand=True)
            inner = [tk.Frame(ac, bg=T["bg"])]
            aw_cw = [ac.create_window(0, 0, window=inner[0], anchor="nw")]
            inner[0].bind("<Configure>", lambda e: ac.configure(scrollregion=ac.bbox("all")))
            ac.bind("<Configure>", lambda e: ac.itemconfig(aw_cw[0], width=e.width))
            for w2 in (ac, inner[0]):
                w2.bind("<MouseWheel>", lambda e: ac.yview_scroll(-1 if e.delta>0 else 1, "units"))

            all_days_data = self.cfg.get("pomo_daily", {})
            all_days_sorted = sorted(all_days_data.keys(), reverse=True)
            fn_d = (self.cfg.get("ui_font","Segoe UI Variable"), 9)
            wc = self.cfg.get("pomo_work_color","#e05c5c")
            bc = self.cfg.get("pomo_break_color","#4caf88")

            def _rebuild_inner():
                if inner[0].winfo_exists(): inner[0].destroy()
                new_inner = tk.Frame(ac, bg=T["bg"])
                inner[0] = new_inner
                ac.delete(aw_cw[0])
                aw_cw[0] = ac.create_window(0, 0, window=new_inner, anchor="nw")
                new_inner.bind("<Configure>", lambda e: ac.configure(scrollregion=ac.bbox("all")))
                ac.bind("<Configure>", lambda e: ac.itemconfig(aw_cw[0], width=e.width))
                for w2 in (ac, new_inner):
                    w2.bind("<MouseWheel>", lambda e: ac.yview_scroll(-1 if e.delta>0 else 1, "units"))
                if not all_days_sorted:
                    tk.Label(new_inner, text="No data tracked yet.", bg=T["bg"], fg=T["muted"],
                        font=fn_d, pady=20).pack()
                    return
                if _view_mode[0] == "list":
                    for dk in all_days_sorted:
                        dd2 = all_days_data[dk]
                        ws = dd2.get("work",0); bs = dd2.get("break",0)
                        if ws==0 and bs==0: continue
                        row = tk.Frame(new_inner, bg=T["item_bg"], pady=3, padx=8)
                        row.pack(fill="x", pady=1)
                        tk.Label(row, text=dk, bg=T["item_bg"], fg=T["text"],
                            font=fn_d, width=12, anchor="w").pack(side="left")
                        tk.Label(row, text=f"💼 {ws//3600}h {(ws%3600)//60:02d}m",
                            bg=T["item_bg"], fg=wc, font=fn_d).pack(side="left", padx=(8,4))
                        tk.Label(row, text=f"☕ {bs//3600}h {(bs%3600)//60:02d}m",
                            bg=T["item_bg"], fg=bc, font=fn_d).pack(side="left", padx=4)
                else:
                    # squares view - sorted oldest first for visual grid
                    sq_days = sorted(all_days_data.keys())
                    import datetime as _dt3
                    _td = _dt3.date.today()
                    COLS = 26
                    SQ = 18
                    gf = tk.Frame(new_inner, bg=T["bg"]); gf.pack(anchor="w", padx=8, pady=8)
                    for i, dk in enumerate(sq_days):
                        dd2 = all_days_data[dk]
                        ws = dd2.get("work",0)
                        bs = dd2.get("break",0)
                        col = _day_color(ws)
                        tip = f"{dk}\n💼 {ws//60}m work\n☕ {bs//60}m break" if (ws or bs) else dk
                        r, c = divmod(i, COLS)
                        sq = tk.Canvas(gf, width=SQ, height=SQ, bd=0,
                            highlightthickness=1,
                            highlightbackground=T["separator"],
                            highlightcolor=T["separator"])
                        sq.create_rectangle(0,0,SQ,SQ,fill=col,outline="")
                        sq.grid(row=r, column=c, padx=1, pady=1)
                        tl2 = [None]
                        def _en(e, t=tip):
                            _tl = tk.Toplevel(self.root); _tl.overrideredirect(True)
                            _tl.attributes("-topmost",True); _tl.configure(bg=T["header_bg"])
                            tk.Label(_tl,text=t,bg=T["header_bg"],fg=T["text"],
                                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                                padx=6,pady=3,justify="left").pack()
                            _tl.geometry(f"+{e.x_root+12}+{e.y_root+12}")
                            tl2[0]=_tl
                        def _lv(e):
                            if tl2[0]:
                                try: tl2[0].destroy()
                                except: pass
                                tl2[0]=None
                        sq.bind("<Enter>",_en); sq.bind("<Leave>",_lv)

            _rebuild_inner()

            def _toggle_view():
                _view_mode[0] = "squares" if _view_mode[0]=="list" else "list"
                self.cfg["all_days_view"] = _view_mode[0]
                toggle_btn.configure(text="⊞ Squares" if _view_mode[0]=="list" else "☰ List")
                _rebuild_inner()
            toggle_btn.configure(command=_toggle_view)
            aw.focus_set()

        tk.Button(exp_row, text="📋 All days", command=_open_all_days,
            bg=T["bg"], fg=T["muted"], relief="flat", bd=0,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),7),
            padx=4, pady=1, cursor="hand2",
            activebackground=T["item_hover"]).pack(side="right", padx=(0,6))

        exp_btn = tk.Button(exp_row, text="⊞ 365d", command=_toggle_expand,
            bg=T["bg"], fg=T["muted"], relief="flat", bd=0,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),7),
            padx=4, pady=1, cursor="hand2",
            activebackground=T["item_hover"])
        exp_btn.pack(side="right")




    # ── feature 8: Docs hub (square grid, trash, singleton window, inline rename) ─
    # ── helper: scan backup dir and import any .md files not yet in docs ──────
    def _scan_docs_backup(self):
        bp = self.cfg.get("docs_backup_path","").strip()
        if not bp or not os.path.isdir(bp): return
        all_docs = load_docs()
        existing_paths = {}  # title -> id map for quick lookup
        for d in all_docs:
            if not d.get("deleted"):
                existing_paths[d.get("title","").lower()] = d["id"]
        changed = False
        cats = self.cfg.get("docs_categories",["Default"])
        for entry in os.scandir(bp):
            # check category sub-folders
            if entry.is_dir() and entry.name in cats:
                scan_dir = entry.path
                cat_name = entry.name
            elif entry.is_file() and entry.name.endswith(".md"):
                scan_dir = bp; cat_name = "Default"
                # handled below as single file
                scan_dir = None
            else:
                continue
            if scan_dir:
                try:
                    for fe in os.scandir(scan_dir):
                        if fe.is_file() and fe.name.endswith(".md"):
                            title = fe.name[:-3]
                            if title.lower() not in existing_paths:
                                try:
                                    with open(fe.path,"r",encoding="utf-8") as f:
                                        body = f.read()
                                    # strip leading "# title" line if present
                                    lines = body.splitlines()
                                    if lines and lines[0].startswith("# "):
                                        body = "\n".join(lines[1:]).lstrip("\n")
                                    new_doc = {"id":str(uuid.uuid4()),"title":title,"body":body,
                                               "category":cat_name,
                                               "created":now_dt().isoformat(timespec="seconds"),
                                               "deleted":False}
                                    all_docs.insert(0, new_doc)
                                    existing_paths[title.lower()] = new_doc["id"]
                                    changed = True
                                except Exception:
                                    pass
                except Exception:
                    pass
        # also scan root of backup dir for loose .md files → Default category
        try:
            for fe in os.scandir(bp):
                if fe.is_file() and fe.name.endswith(".md"):
                    title = fe.name[:-3]
                    if title.lower() not in existing_paths:
                        try:
                            with open(fe.path,"r",encoding="utf-8") as f:
                                body = f.read()
                            lines = body.splitlines()
                            if lines and lines[0].startswith("# "):
                                body = "\n".join(lines[1:]).lstrip("\n")
                            new_doc = {"id":str(uuid.uuid4()),"title":title,"body":body,
                                       "category":"Default",
                                       "created":now_dt().isoformat(timespec="seconds"),
                                       "deleted":False}
                            all_docs.insert(0, new_doc)
                            existing_paths[title.lower()] = new_doc["id"]
                            changed = True
                        except Exception:
                            pass
        except Exception:
            pass
        if changed:
            save_docs(all_docs)


    # ── Priority medals ─────────────────────────────────────────────────────
    _MEDAL_COLORS = {
        0: {"bg":"#fffbe6","bar":"#FFD700","badge":"#B8860B","label":"🥇 #1","ring":"#FFD700"},
        1: {"bg":"#f5f5f5","bar":"#C0C0C0","badge":"#707070","label":"🥈 #2","ring":"#C0C0C0"},
        2: {"bg":"#fff4eb","bar":"#CD7F32","badge":"#8B4513","label":"🥉 #3","ring":"#CD7F32"},
    }
    _MEDAL_DARK = {
        0: {"bg":"#2a2200","bar":"#FFD700","badge":"#FFD700","label":"🥇 #1","ring":"#FFD700"},
        1: {"bg":"#1e1e1e","bar":"#C0C0C0","badge":"#C0C0C0","label":"🥈 #2","ring":"#C0C0C0"},
        2: {"bg":"#221500","bar":"#CD7F32","badge":"#CD7F32","label":"🥉 #3","ring":"#CD7F32"},
    }

    def _pri_medal(self, rank):
        # was a hardcoded name set that listed four themes which do not exist
        # (void/lava/aurora/neon) and omitted eclipse + violet-night, where the
        # medal cards rendered at 1.08 contrast - literally unreadable.
        pool = self._MEDAL_DARK if self.T["is_dark"] else self._MEDAL_COLORS
        return pool.get(rank, {"bg":self.T["item_bg"],"bar":self.T["separator"],
                                "badge":self.T["muted"],"label":f"#{rank+1}","ring":self.T["separator"]})

    def _render_priorities(self, T):
        items = load_priorities()
        fn    = self.cfg.get("ui_font","Segoe UI Variable")
        view  = self.cfg.get("focus_view","list")

        VIEWS = ["📋 List","🟦 Cubes","🔺 Pyramid","🧘 Zen"]
        VIEW_KEYS = {"📋 List":"list","🟦 Cubes":"cubes","🔺 Pyramid":"pyramid","🧘 Zen":"zen"}
        VIEW_LABELS = {v:k for k,v in VIEW_KEYS.items()}

        # ── toolbar ─────────────────────────────────────────────────────────
        tb = tk.Frame(self.task_frame, bg=T["bg"]); tb.pack(fill="x", padx=8, pady=(8,2))
        tk.Label(tb, text="⭐  Focus Board", bg=T["bg"], fg=T["text"],
            font=(fn, 11, "bold")).pack(side="left")
        tk.Button(tb, text="+ Add Priority", command=lambda: self._add_priority_item(items),
            bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            font=(fn, 9), padx=10, pady=3, cursor="hand2",
            activebackground=T["btn_hover"]).pack(side="right")

        # View switcher
        view_var = tk.StringVar(value=VIEW_LABELS.get(view, "📋 List"))
        import tkinter.ttk as ttk
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception: pass
        try:
            style.configure("Pri.TCombobox", fieldbackground=T["entry_bg"],
                background=T["entry_bg"], foreground=T["entry_fg"],
                arrowcolor=T["text"], selectbackground=T["entry_bg"],
                selectforeground=T["entry_fg"], bordercolor=T["separator"],
                lightcolor=T["entry_bg"], darkcolor=T["entry_bg"])
            style.map("Pri.TCombobox",
                fieldbackground=[("readonly", T["entry_bg"])],
                foreground=[("readonly", T["entry_fg"])],
                background=[("readonly", T["entry_bg"]), ("active", T["item_hover"])],
                arrowcolor=[("readonly", T["text"])])
        except Exception: pass
        # dropdown listbox (popdown) colors — not covered by ttk style, needs option db
        try:
            self.root.option_add("*TCombobox*Listbox.background", T["entry_bg"])
            self.root.option_add("*TCombobox*Listbox.foreground", T["entry_fg"])
            self.root.option_add("*TCombobox*Listbox.selectBackground", T["btn_bg"])
            self.root.option_add("*TCombobox*Listbox.selectForeground", T["btn_fg"])
            self.root.option_add("*TCombobox*Listbox.font", (fn, 8))
        except Exception: pass
        vcb = ttk.Combobox(tb, textvariable=view_var, values=VIEWS,
            state="readonly", width=11, style="Pri.TCombobox",
            font=(fn, 8))
        vcb.pack(side="right", padx=(0,8))
        def _on_view_change(ev=None):
            key = VIEW_KEYS.get(view_var.get(), "list")
            self.cfg["focus_view"] = key; save_config(self.cfg)
            self._render_tasks()
        vcb.bind("<<ComboboxSelected>>", _on_view_change)

        if not items:
            tk.Label(self.task_frame,
                text="Your focus board is empty.\nClick + Add Priority to define what matters most.",
                bg=T["bg"], fg=T["muted"], font=(fn, 10), justify="center", pady=32).pack(fill="x")
            return

        if view == "cubes":
            self._render_pri_cubes(items, T, fn)
        elif view == "pyramid":
            self._render_pri_pyramid(items, T, fn)
        elif view == "zen":
            self._render_pri_zen(items, T, fn)
        else:
            self._render_pri_list(items, T, fn)

    # ── shared helper: one card row ──────────────────────────────────────────
    def _pri_card_row(self, items, item, rank, T, fn, parent=None, compact=False):
        med     = self._pri_medal(rank)
        ibg     = med["bg"] if rank < 3 else T["item_bg"]
        bar_col = med["bar"] if rank < 3 else T["separator"]
        host    = parent if parent else self.task_frame

        card = tk.Frame(host, bg=ibg, pady=0)
        card._pri_idx = rank
        if parent is None:
            card.pack(fill="x", pady=(2,0))

        accent = tk.Frame(card, bg=bar_col, width=5)
        accent.pack(side="left", fill="y")
        def _upd_accent(e, a=accent): a.configure(height=e.height)
        card.bind("<Configure>", _upd_accent, add="+")

        inner = tk.Frame(card, bg=ibg, padx=8, pady=3)
        inner.pack(side="left", fill="both", expand=True)

        top = tk.Frame(inner, bg=ibg); top.pack(fill="x")

        dh = tk.Label(top, text="⋮⋮", bg=ibg, fg=T["muted"], font=(fn,8), cursor="fleur", padx=2)
        dh.pack(side="left", padx=(0,4))
        dh.bind("<ButtonPress-1>", lambda e, i=rank: self._pri_drag_start(e, i, items))
        dh.bind("<Enter>", lambda e, w=dh: w.configure(fg=T["text"]))
        dh.bind("<Leave>", lambda e, w=dh: w.configure(fg=T["muted"]))

        badge_text = med["label"] if rank < 3 else f"#{rank+1}"
        badge_fg   = med["badge"] if rank < 3 else T["muted"]
        tk.Label(top, text=badge_text, bg=ibg, fg=badge_fg,
            font=(fn, 9, "bold"), width=5).pack(side="left", padx=(0,6))

        title_lbl = tk.Label(top, text=item.get("title","Priority"),
            bg=ibg, fg=T["text"], font=(fn, 11, "bold"), anchor="w", justify="left")
        title_lbl.pack(side="left", fill="x", expand=True)
        title_lbl.bind("<Double-Button-1>",
            lambda e, lbl=title_lbl, it=item, its=items:
                self._inline_edit_priority_title(lbl, it, its))

        def _del_pri(it=item, its=items, btn_ref=[None]):
            b = btn_ref[0]
            if b is None: return
            if getattr(b, "_confirm", False):
                its.remove(it); save_priorities(its); self._render_tasks()
            else:
                b._confirm = True; b.configure(text="Sure?", fg=T["close_hover"])
                b.after(2000, lambda: (setattr(b,"_confirm",False),
                    b.configure(text="✕", fg=T["muted"])) if b.winfo_exists() else None)
        del_b = tk.Button(top, text="✕", bg=ibg, fg=T["muted"], relief="flat", bd=0,
            padx=6, font=(fn,8), cursor="hand2", activebackground=T["item_hover"])
        del_b._confirm = False
        del_b.configure(command=lambda br=[del_b], it=item, its=items: _del_pri(it, its, br))
        del_b.pack(side="right")

        if not compact:
            sub_frame = tk.Frame(inner, bg=ibg); sub_frame.pack(fill="x", pady=(2,0))
            self._render_priority_subtasks(sub_frame, item, items, ibg, T)

            bot_row = tk.Frame(inner, bg=ibg); bot_row.pack(fill="x")
            add_sub_btn = tk.Label(bot_row, text="+ sub-item", bg=ibg, fg=T["muted"],
                font=(fn,7), cursor="hand2", pady=0)
            add_sub_btn.pack(side="left")
            add_sub_btn.bind("<Button-1>",
                lambda e, it=item, its=items, sf=sub_frame, ibg=ibg:
                    self._add_priority_subtask(it, its, sf, ibg))
            add_sub_btn.bind("<Enter>", lambda e, w=add_sub_btn: w.configure(fg=T["text"]))
            add_sub_btn.bind("<Leave>", lambda e, w=add_sub_btn: w.configure(fg=T["muted"]))

            note_text = item.get("notes","")
            note_preview = note_text[:120] + ("…" if len(note_text)>120 else "")
            note_lbl = tk.Label(inner, text=note_preview if note_text else "✏ note",
                bg=ibg, fg=T["muted"], font=(fn,7), anchor="w", justify="left",
                wraplength=1, pady=2, padx=0, cursor="hand2")
            note_lbl.pack(fill="x", anchor="w", pady=(2,0))
            def _upd_wrap(e, l=note_lbl): l.configure(wraplength=max(60,e.width-8))
            inner.bind("<Configure>", _upd_wrap, add="+")
            note_lbl.bind("<Button-1>",
                lambda e, it=item, its=items, lbl=note_lbl, ibg=ibg:
                    self._edit_priority_notes(it, its, lbl, ibg))
            inner.bind("<Button-1>",
                lambda e, it=item, its=items, lbl=note_lbl, ibg=ibg:
                    self._edit_priority_notes(it, its, lbl, ibg))
            card.bind("<Button-1>",
                lambda e, it=item, its=items, lbl=note_lbl, ibg=ibg:
                    self._edit_priority_notes(it, its, lbl, ibg))

        return card

    # ── LIST view ────────────────────────────────────────────────────────────
    def _render_pri_list(self, items, T, fn):
        for rank, item in enumerate(items):
            card = self._pri_card_row(items, item, rank, T, fn)
            tk.Frame(self.task_frame, bg=T["separator"], height=1).pack(fill="x")
        tk.Frame(self.task_frame, bg=T["bg"], height=40).pack(fill="x")

    # ── CUBES view ───────────────────────────────────────────────────────────
    def _render_pri_cubes(self, items, T, fn):
        grid_host = tk.Frame(self.task_frame, bg=T["bg"])
        grid_host.pack(fill="both", expand=True, padx=6, pady=6)
        COLS = 2
        for i, item in enumerate(items):
            r, c = divmod(i, COLS)
            med    = self._pri_medal(i)
            ibg    = med["bg"] if i < 3 else T["item_bg"]
            bar_col= med["bar"] if i < 3 else T["separator"]
            badge_text = med["label"] if i < 3 else f"#{i+1}"
            badge_fg   = med["badge"] if i < 3 else T["muted"]

            cube = tk.Frame(grid_host, bg=ibg, relief="flat",
                highlightthickness=2, highlightbackground=bar_col)
            cube._pri_idx = i
            cube.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            grid_host.grid_columnconfigure(c, weight=1)
            grid_host.grid_rowconfigure(r, weight=0)

            hdr = tk.Frame(cube, bg=bar_col, height=6)
            hdr.pack(fill="x")

            body = tk.Frame(cube, bg=ibg, padx=8, pady=6)
            body.pack(fill="both", expand=True)

            # badge + title row
            top = tk.Frame(body, bg=ibg); top.pack(fill="x")
            tk.Label(top, text=badge_text, bg=ibg, fg=badge_fg,
                font=(fn,8,"bold")).pack(side="left", padx=(0,4))
            title_lbl = tk.Label(top, text=item.get("title","Priority"),
                bg=ibg, fg=T["text"], font=(fn,10,"bold"),
                anchor="w", wraplength=120, cursor="hand2")
            title_lbl.pack(side="left", fill="x", expand=True)
            title_lbl.bind("<Double-Button-1>",
                lambda e, lbl=title_lbl, it=item, its=items:
                    self._inline_edit_priority_title(lbl, it, its))
            def _upd_cube_wrap(e, l=title_lbl):
                l.configure(wraplength=max(40, e.width-60))
            top.bind("<Configure>", _upd_cube_wrap, add="+")

            # subtask progress bar
            subs = item.get("subtasks",[])
            done = sum(1 for s in subs if s.get("done"))
            if subs:
                prog_bg = tk.Frame(body, bg=T["separator"], height=3)
                prog_bg.pack(fill="x", pady=(4,0))
                pct = done/len(subs)
                def _draw_prog(e, pb=prog_bg, p=pct, col=bar_col):
                    w=pb.winfo_width()
                    if w<4: return
                    for ch in pb.winfo_children(): ch.destroy()
                    if p>0: tk.Frame(pb,bg=col,height=3,width=max(1,int(w*p))).place(x=0,y=0)
                prog_bg.bind("<Configure>",_draw_prog,add="+")
                tk.Label(body, text=f"{done}/{len(subs)} done",
                    bg=ibg, fg=T["muted"], font=(fn,7)).pack(anchor="w")

            # note area — dedicated clickable widget (only this opens the note popup)
            note = item.get("notes","")
            note_preview = (note[:60] + ("…" if len(note)>60 else "")) if note else "✏ note"
            note_lbl = tk.Label(body, text=note_preview,
                bg=ibg, fg=T["muted"] if not note else T["text"], font=(fn,7),
                anchor="w", wraplength=120, justify="left", cursor="hand2")
            note_lbl.pack(fill="x", anchor="w", pady=(4,0))
            note_lbl.bind("<Button-1>",
                lambda e, it=item, its=items, ibg=ibg:
                    self._edit_priority_notes(it, its, e.widget, ibg))

            # delete (top-right corner)
            def _del(it=item, its=items, cr=[None]):
                b=cr[0]
                if b is None: return
                if getattr(b,"_confirm",False):
                    its.remove(it); save_priorities(its); self._render_tasks()
                else:
                    b._confirm=True; b.configure(text="✕?",fg=T["close_hover"])
                    b.after(1500,lambda:(setattr(b,"_confirm",False),b.configure(text="✕",fg=T["muted"])) if b.winfo_exists() else None)
            del_b=tk.Button(top,text="✕",bg=ibg,fg=T["muted"],relief="flat",bd=0,
                padx=4,font=(fn,7),cursor="hand2",activebackground=T["item_hover"])
            del_b._confirm=False
            del_b.configure(command=lambda br=[del_b],it=item,its=items:_del(it,its,br))
            del_b.pack(side="right")

        tk.Frame(self.task_frame, bg=T["bg"], height=20).pack(fill="x")

    # ── PYRAMID view ─────────────────────────────────────────────────────────
    def _render_pri_pyramid(self, items, T, fn):
        # #1 full width, #2+#3 side by side, rest as compact list
        def _mini_cube(parent, item, rank, col_weight=1):
            med    = self._pri_medal(rank)
            ibg    = med["bg"] if rank < 3 else T["item_bg"]
            bar_col= med["bar"] if rank < 3 else T["separator"]
            badge_text = med["label"] if rank < 3 else f"#{rank+1}"
            badge_fg   = med["badge"] if rank < 3 else T["muted"]
            cube = tk.Frame(parent, bg=ibg,
                highlightthickness=2, highlightbackground=bar_col)
            tk.Frame(cube, bg=bar_col, height=5).pack(fill="x")
            body = tk.Frame(cube, bg=ibg, padx=8, pady=5)
            body.pack(fill="both", expand=True)
            tk.Label(body, text=badge_text, bg=ibg, fg=badge_fg,
                font=(fn,8,"bold")).pack(anchor="w")
            title_lbl = tk.Label(body, text=item.get("title","Priority"), bg=ibg, fg=T["text"],
                font=(fn,10,"bold"), anchor="w", wraplength=200, cursor="hand2")
            title_lbl.pack(anchor="w")
            title_lbl.bind("<Double-Button-1>",
                lambda e, lbl=title_lbl, it=item, its=items:
                    self._inline_edit_priority_title(lbl, it, its))
            subs = item.get("subtasks",[])
            done = sum(1 for s in subs if s.get("done"))
            if subs:
                tk.Label(body, text=f"{done}/{len(subs)} done",
                    bg=ibg, fg=T["muted"], font=(fn,7)).pack(anchor="w")
            note = item.get("notes","")
            note_preview = (note[:80] + ("…" if len(note)>80 else "")) if note else "✏ note"
            note_lbl = tk.Label(body, text=note_preview,
                bg=ibg, fg=T["muted"] if not note else T["text"], font=(fn,7), wraplength=200,
                justify="left", cursor="hand2")
            note_lbl.pack(anchor="w", pady=(2,0))
            note_lbl.bind("<Button-1>",
                lambda e, it=item, its=items, ibg=ibg:
                    self._edit_priority_notes(it, its, e.widget, ibg))
            return cube

        if items:
            top_cube = _mini_cube(self.task_frame, items[0], 0)
            top_cube.pack(fill="x", padx=6, pady=(4,2))

        if len(items) >= 2:
            row2 = tk.Frame(self.task_frame, bg=T["bg"])
            row2.pack(fill="x", padx=6, pady=(0,2))
            for idx in range(1, min(3, len(items))):
                c = _mini_cube(row2, items[idx], idx)
                c.pack(side="left", fill="x", expand=True,
                       padx=(0,4) if idx==1 else (4,0))

        if len(items) > 3:
            tk.Label(self.task_frame, text="  ─── More ───",
                bg=T["bg"], fg=T["muted"], font=(fn,7)).pack(anchor="w", padx=12, pady=(4,0))
            for rank in range(3, len(items)):
                card = self._pri_card_row(items, items[rank], rank, T, fn, compact=True)
                card.pack(fill="x", pady=(1,0))
                tk.Frame(self.task_frame, bg=T["separator"], height=1).pack(fill="x")

        tk.Frame(self.task_frame, bg=T["bg"], height=20).pack(fill="x")

    # ── ZEN view (one priority at a time) ────────────────────────────────────
    def _render_pri_zen(self, items, T, fn):
        idx = self.cfg.get("focus_zen_idx", 0)
        if idx >= len(items): idx = 0
        item = items[idx]
        rank = idx
        med  = self._pri_medal(rank)
        ibg  = med["bg"] if rank < 3 else T["item_bg"]
        bar_col = med["bar"] if rank < 3 else T["separator"]

        # nav bar
        nav = tk.Frame(self.task_frame, bg=T["bg"])
        nav.pack(fill="x", padx=8, pady=(4,0))
        prev_b = tk.Button(nav, text="◀", bg=T["btn_bg"], fg=T["text"],
            relief="flat", font=(fn,9), padx=8, cursor="hand2",
            state="normal" if idx>0 else "disabled",
            activebackground=T["btn_hover"],
            command=lambda: self._zen_go(idx-1))
        prev_b.pack(side="left")
        tk.Label(nav, text=f"{idx+1} / {len(items)}", bg=T["bg"],
            fg=T["muted"], font=(fn,8)).pack(side="left", padx=8)
        next_b = tk.Button(nav, text="▶", bg=T["btn_bg"], fg=T["text"],
            relief="flat", font=(fn,9), padx=8, cursor="hand2",
            state="normal" if idx<len(items)-1 else "disabled",
            activebackground=T["btn_hover"],
            command=lambda: self._zen_go(idx+1))
        next_b.pack(side="left")

        # big focused card
        card = tk.Frame(self.task_frame, bg=ibg,
            highlightthickness=3, highlightbackground=bar_col)
        card.pack(fill="x", padx=10, pady=8)

        # top color strip
        tk.Frame(card, bg=bar_col, height=8).pack(fill="x")

        body = tk.Frame(card, bg=ibg, padx=16, pady=12)
        body.pack(fill="both", expand=True)

        badge_text = med["label"] if rank < 3 else f"#{rank+1}"
        badge_fg   = med["badge"] if rank < 3 else T["muted"]
        tk.Label(body, text=badge_text, bg=ibg, fg=badge_fg,
            font=(fn,14,"bold")).pack(anchor="w", pady=(0,4))
        title_lbl = tk.Label(body, text=item.get("title","Priority"),
            bg=ibg, fg=T["text"], font=(fn,16,"bold"),
            anchor="w", wraplength=1, justify="left")
        title_lbl.pack(fill="x", anchor="w", pady=(0,8))
        def _upd_zen_wrap(e, l=title_lbl): l.configure(wraplength=max(80,e.width-32))
        body.bind("<Configure>", _upd_zen_wrap, add="+")
        title_lbl.bind("<Double-Button-1>",
            lambda e, lbl=title_lbl, it=item, its=items:
                self._inline_edit_priority_title(lbl, it, its))

        # subtasks full list
        sub_frame = tk.Frame(body, bg=ibg)
        sub_frame.pack(fill="x", pady=(0,6))
        self._render_priority_subtasks(sub_frame, item, items, ibg, T)
        bot_row = tk.Frame(body, bg=ibg); bot_row.pack(fill="x")
        add_sub = tk.Label(bot_row, text="+ sub-item", bg=ibg, fg=T["muted"],
            font=(fn,8), cursor="hand2")
        add_sub.pack(side="left")
        add_sub.bind("<Button-1>",
            lambda e, it=item, its=items, sf=sub_frame, ibg=ibg:
                self._add_priority_subtask(it, its, sf, ibg))

        # note area (full, multi-line)
        tk.Frame(body, bg=T["separator"], height=1).pack(fill="x", pady=(6,4))
        note_text = item.get("notes","")
        note_lbl = tk.Label(body, text=note_text or "✏ Tap to add a note…",
            bg=ibg, fg=T["text"] if note_text else T["muted"],
            font=(fn,9), anchor="nw", justify="left", wraplength=1, pady=4,
            cursor="hand2")
        note_lbl.pack(fill="x", anchor="w")
        def _upd_n_wrap(e, l=note_lbl): l.configure(wraplength=max(80,e.width-32))
        body.bind("<Configure>", _upd_n_wrap, add="+")
        note_lbl.bind("<Button-1>",
            lambda e, it=item, its=items, lbl=note_lbl, ibg=ibg:
                self._edit_priority_notes(it, its, lbl, ibg))

        # dot indicators at bottom
        dot_row = tk.Frame(self.task_frame, bg=T["bg"])
        dot_row.pack(pady=(2,8))
        for di in range(len(items)):
            dot = tk.Label(dot_row,
                text="●" if di==idx else "○",
                bg=T["bg"],
                fg=bar_col if di==idx else T["muted"],
                font=(fn,8), cursor="hand2")
            dot.pack(side="left", padx=1)
            dot.bind("<Button-1>", lambda e, i=di: self._zen_go(i))

    def _zen_go(self, idx):
        self.cfg["focus_zen_idx"] = max(0, idx)
        save_config(self.cfg)
        self._render_tasks()

    def _render_priority_subtasks(self, sf, item, items, ibg, T):
        for w in sf.winfo_children(): w.destroy()
        fn = self.cfg.get("ui_font","Segoe UI Variable")
        for sub in item.get("subtasks", []):
            row = tk.Frame(sf, bg=ibg); row.pack(fill="x", anchor="w")
            var = tk.BooleanVar(value=sub.get("done", False))
            chk = tk.Checkbutton(row, variable=var, bg=ibg, activebackground=ibg,
                selectcolor=T["check_done"] if sub.get("done") else ibg,
                relief="flat", bd=0, highlightthickness=0,
                command=lambda v=var, s=sub, it=item, its=items, sf2=sf, ibg2=ibg:
                    self._toggle_priority_sub(s, v, it, its, sf2, ibg2))
            chk.pack(side="left")
            style = "overstrike" if sub.get("done") else "normal"
            color = T["muted"] if sub.get("done") else T["text"]
            lbl = tk.Label(row, text=sub.get("text",""), bg=ibg, fg=color,
                font=(fn, 8, style), anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            lbl.bind("<Double-Button-1>",
                lambda e, row=row, l=lbl, s=sub, it=item, its=items:
                    self._inline_edit_priority_sub(row, l, s, it, its))
            # tiny delete sub
            def _del_sub(s=sub, it=item, its=items, sf3=sf, ibg3=ibg):
                it.get("subtasks",[]).remove(s); save_priorities(its)
                self._render_priority_subtasks(sf3, it, its, ibg3, T)
            _x_lbl = tk.Label(row, text="✕", bg=ibg, fg=T["muted"], font=(fn,7),
                cursor="hand2")
            _x_lbl.pack(side="right", padx=2)
            _x_lbl.bind("<Button-1>", lambda e, fn=_del_sub: fn())

    def _toggle_priority_sub(self, sub, var, item, items, sf, ibg):
        sub["done"] = var.get()
        save_priorities(items)
        view = self.cfg.get("focus_view","list")
        if view != "list":
            self._render_tasks_debounced()
        else:
            self._render_priority_subtasks(sf, item, items, ibg, self.T)

    def _add_priority_subtask(self, item, items, sf, ibg):
        new_sub = {"id": str(uuid.uuid4()), "text": "", "done": False}
        item.setdefault("subtasks", []).append(new_sub)
        save_priorities(items)
        self._render_priority_subtasks(sf, item, items, ibg, self.T)
        # inline edit the new sub (works the same across all views since sf is a live widget)
        if sf.winfo_children():
            last_row = sf.winfo_children()[-1]
            lbls = [w for w in last_row.winfo_children() if isinstance(w, tk.Label) and w.cget("text") == ""]
            if lbls:
                self._inline_edit_priority_sub(last_row, lbls[0], new_sub, item, items)

    def _inline_edit_priority_title(self, lbl, item, items):
        T = self.T; fn = self.cfg.get("ui_font","Segoe UI Variable")
        old = item.get("title","")
        view = self.cfg.get("focus_view","list")
        lbl.pack_forget()
        var = tk.StringVar(value=old)
        e = tk.Entry(lbl.master, textvariable=var, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat", font=(fn,11,"bold"),
            highlightthickness=1, highlightbackground=T["check_done"])
        e.pack(side="left", fill="x", expand=True, ipady=2)
        e.focus_set(); e.select_range(0,"end")
        _done = [False]
        def finish(ev=None):
            if _done[0]: return
            _done[0] = True
            new = var.get().strip() or old
            item["title"] = new; save_priorities(items)
            if view != "list":
                self._render_tasks_debounced()
                return
            try: e.destroy()
            except Exception: pass
            lbl.configure(text=new); lbl.pack(side="left", fill="x", expand=True)
        e.bind("<Return>", finish); e.bind("<Escape>", lambda ev: finish())
        e.bind("<FocusOut>", lambda ev: self.root.after(60, finish))

    def _inline_edit_priority_sub(self, row, lbl, sub, item, items):
        T = self.T; fn = self.cfg.get("ui_font","Segoe UI Variable")
        old = sub.get("text","")
        view = self.cfg.get("focus_view","list")
        lbl.pack_forget()
        var = tk.StringVar(value=old)
        e = tk.Entry(row, textvariable=var, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat", font=(fn,8),
            highlightthickness=1, highlightbackground=T["check_done"])
        e.pack(side="left", fill="x", expand=True, ipady=2)
        e.focus_set(); e.select_range(0,"end")
        _done = [False]
        def finish(ev=None, discard=False):
            if _done[0]: return
            _done[0] = True
            new = var.get().strip()
            if discard or (not new and not old):
                if not old and not new:
                    item.get("subtasks",[]).remove(sub); save_priorities(items)
                    if view != "list":
                        self._render_tasks_debounced(); return
                    try: row.destroy()
                    except Exception: pass
                else:
                    if view != "list":
                        self._render_tasks_debounced(); return
                    try: e.destroy()
                    except Exception: pass
                    lbl.configure(text=old or ""); lbl.pack(side="left", fill="x", expand=True)
                return
            sub["text"] = new; save_priorities(items)
            if view != "list":
                self._render_tasks_debounced()
                return
            try: e.destroy()
            except Exception: pass
            lbl.configure(text=new); lbl.pack(side="left", fill="x", expand=True)
        e.bind("<Return>",   lambda ev: finish())
        e.bind("<Escape>",   lambda ev: finish(discard=True))
        e.bind("<FocusOut>", lambda ev: self.root.after(60, finish))

    def _edit_priority_notes(self, item, items, preview_lbl, ibg):
        T = self.T; fn = self.cfg.get("ui_font","Segoe UI Variable")
        old = item.get("notes","")
        view = self.cfg.get("focus_view","list")
        # In cubes/pyramid/zen: open a floating popup editor instead of inline swap
        if view != "list":
            self._edit_priority_notes_popup(item, items, ibg)
            return
        preview_lbl.pack_forget()
        txt = tk.Text(preview_lbl.master, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat", font=(fn,8),
            highlightthickness=1, highlightbackground=T["check_done"],
            wrap="word", height=4, padx=4, pady=4)
        txt.insert("1.0", old)
        txt.pack(fill="x", pady=(2,2))
        txt.focus_set()
        _done = [False]
        def finish(ev=None):
            if _done[0]: return
            _done[0] = True
            new = txt.get("1.0","end-1c").strip()
            item["notes"] = new; save_priorities(items)
            preview = new[:120] + ("…" if len(new)>120 else "")
            preview_lbl.configure(text=preview or "✏ note",
                fg=T["muted"] if not new else T["text"])
            try: txt.destroy()
            except Exception: pass
            preview_lbl.pack(fill="x", anchor="w", pady=(2,0))
        txt.bind("<Escape>", lambda e: finish())
        txt.bind("<FocusOut>", lambda e: self.root.after(80, finish))
        txt.bind("<Control-Return>", lambda e: finish())

    def _edit_priority_notes_popup(self, item, items, ibg):
        """Floating note editor for cubes/pyramid/zen — refreshes board on close."""
        T = self.T; fn = self.cfg.get("ui_font","Segoe UI Variable")
        old = item.get("notes","")
        win = tk.Toplevel(self.root)
        win.title(f"Note — {item.get('title','Priority')}")
        win.configure(bg=T["bg"])
        win.resizable(True, True)
        win.geometry("380x220")
        win.attributes("-topmost", True)
        # center over main window
        self.root.update_idletasks()
        rx = self.root.winfo_rootx() + self.root.winfo_width()//2 - 190
        ry = self.root.winfo_rooty() + self.root.winfo_height()//2 - 110
        win.geometry(f"380x220+{rx}+{ry}")

        hdr = tk.Frame(win, bg=T["header_bg"]); hdr.pack(fill="x")
        tk.Label(hdr, text=f"✏  {item.get('title','Priority')}",
            bg=T["header_bg"], fg=T["text"],
            font=(fn,10,"bold"), padx=10, pady=6).pack(side="left")
        # save icon in the header row itself — always visible regardless of window size
        _save_icon_btn = tk.Button(hdr, text="💾", bg=T["header_bg"], fg=T["text"],
            relief="flat", bd=0, font=(fn,11), padx=8, cursor="hand2",
            activebackground=T["btn_hover"])
        _save_icon_btn.pack(side="right", padx=(0,8))

        txt = tk.Text(win, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat", font=(fn,9),
            highlightthickness=0, wrap="word", padx=8, pady=8)
        txt.insert("1.0", old)
        txt.pack(fill="both", expand=True, padx=8, pady=(6,4))
        txt.focus_set()

        btn_row = tk.Frame(win, bg=T["bg"]); btn_row.pack(fill="x", padx=8, pady=(0,8))
        tk.Label(btn_row, text="Ctrl+Enter or Save to confirm",
            bg=T["bg"], fg=T["muted"], font=(fn,7)).pack(side="left")

        _saved = [False]
        def save_and_close(ev=None):
            if _saved[0]: return
            _saved[0] = True
            new = txt.get("1.0","end-1c").strip()
            item["notes"] = new; save_priorities(items)
            win.destroy()
            self._render_tasks()

        def save_flash(ev=None):
            new = txt.get("1.0","end-1c").strip()
            item["notes"] = new; save_priorities(items)
            if win.winfo_exists() and _save_icon_btn.winfo_exists():
                _save_icon_btn.configure(text="✅")
                win.after(700, lambda: _save_icon_btn.configure(text="💾") if _save_icon_btn.winfo_exists() else None)

        _save_icon_btn.configure(command=save_flash)

        tk.Button(btn_row, text="Save", command=save_and_close,
            bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            font=(fn,8), padx=10, pady=3, cursor="hand2",
            activebackground=T["btn_hover"]).pack(side="right")

        # autosave while typing (debounced)
        _autosave_job = [None]
        def _schedule_autosave(*_a):
            if _autosave_job[0]:
                try: win.after_cancel(_autosave_job[0])
                except Exception: pass
            _autosave_job[0] = win.after(900, save_flash)
        txt.bind("<KeyRelease>", _schedule_autosave)

        txt.bind("<Control-Return>", save_and_close)
        win.bind("<Escape>", lambda e: win.destroy())
        def _on_close():
            if _autosave_job[0]:
                try: win.after_cancel(_autosave_job[0])
                except Exception: pass
            new = txt.get("1.0","end-1c").strip()
            item["notes"] = new; save_priorities(items)
            win.destroy()
            self._render_tasks()
        win.protocol("WM_DELETE_WINDOW", _on_close)

    def _add_priority_item(self, items):
        new = {"id": str(uuid.uuid4()), "title": "New Priority",
               "notes": "", "subtasks": []}
        items.append(new); save_priorities(items)
        self._render_tasks()

    # ── priority drag-reorder ────────────────────────────────────────────────
    def _pri_drag_start(self, e, idx, items):
        self._drag_pri_idx   = idx
        self._drag_pri_start = e.y_root
        self._drag_pri_moved = False
        self._drag_pri_items = items
        self.root.bind("<B1-Motion>",       self._pri_drag_motion,    add="+")
        self.root.bind("<ButtonRelease-1>", self._pri_drag_end_root,  add="+")

    def _pri_drag_motion(self, e):
        if not hasattr(self,"_drag_pri_idx") or self._drag_pri_idx is None: return
        if abs(e.y_root - self._drag_pri_start) > 6:
            self._drag_pri_moved = True

    def _pri_drag_end_root(self, e):
        self.root.unbind("<B1-Motion>")
        self.root.unbind("<ButtonRelease-1>")
        if not hasattr(self,"_drag_pri_idx") or self._drag_pri_idx is None: return
        if not getattr(self,"_drag_pri_moved", False):
            self._drag_pri_idx = None; return
        src   = self._drag_pri_idx
        items = self._drag_pri_items
        self._drag_pri_idx = None; self._drag_pri_moved = False
        target = None
        for child in self.task_frame.winfo_children():
            if not hasattr(child,"_pri_idx"): continue
            cy = child.winfo_rooty()
            if cy <= e.y_root <= cy + child.winfo_height():
                target = child._pri_idx; break
        if target is None or target == src: return
        if src < len(items) and target < len(items):
            items.insert(target, items.pop(src))
            save_priorities(items)
            self._render_tasks()

    def _render_docs(self, T):
        all_docs = [d for d in load_docs() if not d.get("deleted")]
        # ensure every doc has a category
        for d in all_docs:
            d.setdefault("category","Default")

        # ensure config has categories list
        cats = self.cfg.setdefault("docs_categories",["Default"])
        if "Default" not in cats:
            cats.insert(0,"Default")
        active_cats = self.cfg.setdefault("docs_active_categories",[])

        # ── toolbar ──────────────────────────────────────────────────────
        tb = tk.Frame(self.task_frame,bg=T["bg"]); tb.pack(fill="x",padx=6,pady=(8,2))
        tk.Label(tb,text="📄  Docs",bg=T["bg"],fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),11,"bold")).pack(side="left")
        tk.Button(tb,text="⟳",command=lambda:(self._scan_docs_backup(), self._render_tasks()),
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),10),
            padx=6,pady=2,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right",padx=(2,0))
        tk.Button(tb,text="+ New",command=self._new_doc,
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=8,pady=3,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right",padx=(2,0))

        # ── category management row ───────────────────────────────────────
        cat_row = tk.Frame(self.task_frame,bg=T["bg"]); cat_row.pack(fill="x",padx=6,pady=(0,2))

        # helper: save cats and re-render
        def _save_cats():
            self.cfg["docs_categories"] = cats
            self.cfg["docs_active_categories"] = active_cats
            save_config(self.cfg)
            self._render_tasks()

        # "Categories ▾" dropdown button
        cat_lbl_text = "All Categories" if not active_cats else ", ".join(active_cats)
        if len(cat_lbl_text) > 22: cat_lbl_text = cat_lbl_text[:19]+"…"
        cat_dd_btn = tk.Button(cat_row, text=f"🗂 {cat_lbl_text} ▾",
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
            padx=6,pady=2,cursor="hand2",anchor="w",
            activebackground=T["btn_hover"])
        cat_dd_btn.pack(side="left",padx=(0,4))

        def _open_cat_dropdown(e=None):
            pop = tk.Toplevel(self.root)
            pop.overrideredirect(True)
            pop.configure(bg=T["separator"])
            pop.attributes("-topmost",True)
            bx = cat_dd_btn.winfo_rootx()
            by = cat_dd_btn.winfo_rooty() + cat_dd_btn.winfo_height() + 2
            pop.geometry(f"+{bx}+{by}")
            inner = tk.Frame(pop,bg=T["bg"],padx=4,pady=4)
            inner.pack(fill="both",expand=True,padx=1,pady=1)

            # "All" option (clear filter)
            def _toggle_all():
                active_cats.clear()
                _save_cats()
                try: pop.destroy()
                except Exception: pass
            all_var = tk.BooleanVar(value=not active_cats)
            tk.Checkbutton(inner,text="All (no filter)",variable=all_var,
                command=_toggle_all,
                bg=T["bg"],fg=T["text"],activebackground=T["bg"],
                selectcolor=T["entry_bg"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9)).pack(anchor="w")
            tk.Frame(inner,bg=T["separator"],height=1).pack(fill="x",pady=2)

            # per-category checkboxes
            for cat in list(cats):
                v = tk.BooleanVar(value=cat in active_cats)
                def _toggle_cat(c=cat, var=v):
                    if var.get():
                        if c not in active_cats: active_cats.append(c)
                    else:
                        if c in active_cats: active_cats.remove(c)
                    self.cfg["docs_active_categories"] = active_cats
                    save_config(self.cfg)
                    # refresh grid without closing popup
                    q2 = doc_search_var.get().strip().lower() if not ph_shown[0] else ""
                    filtered = _apply_filter(all_docs, q2)
                    self._doc_grid_docs = filtered
                    if hasattr(self,"_grid_job"): self.root.after_cancel(self._grid_job)
                    self._grid_job = self.root.after(80, lambda: self._relayout_doc_grid(
                        self._doc_grid_host.winfo_width() if hasattr(self,"_doc_grid_host") and self._doc_grid_host.winfo_exists() else 320))
                    # update button label
                    lbl2 = "All Categories" if not active_cats else ", ".join(active_cats)
                    if len(lbl2)>22: lbl2=lbl2[:19]+"…"
                    cat_dd_btn.configure(text=f"🗂 {lbl2} ▾")
                tk.Checkbutton(inner,text=cat,variable=v,command=_toggle_cat,
                    bg=T["bg"],fg=T["text"],activebackground=T["bg"],
                    selectcolor=T["entry_bg"],
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),9)).pack(anchor="w")

            tk.Frame(inner,bg=T["separator"],height=1).pack(fill="x",pady=2)

            # add new category
            new_cat_var = tk.StringVar()
            add_f = tk.Frame(inner,bg=T["bg"]); add_f.pack(fill="x",pady=(0,2))
            ne = tk.Entry(add_f,textvariable=new_cat_var,bg=T["entry_bg"],fg=T["entry_fg"],
                insertbackground=T["entry_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                highlightthickness=1,highlightbackground=T["separator"],width=14)
            ne.pack(side="left",ipady=3,padx=(0,2))
            ne.insert(0,"New category…")
            ne.bind("<FocusIn>", lambda e: ne.delete(0,"end") if ne.get()=="New category…" else None)
            def _add_cat(e=None):
                name = new_cat_var.get().strip()
                if name and name != "New category…" and name not in cats:
                    cats.append(name)
                    _save_cats()
                try: pop.destroy()
                except Exception: pass
            tk.Button(add_f,text="+",command=_add_cat,
                bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                padx=4,pady=2,cursor="hand2",activebackground=T["btn_hover"]).pack(side="left")
            ne.bind("<Return>", _add_cat)

            # delete category buttons
            for cat in [c for c in cats if c != "Default"]:
                df = tk.Frame(inner,bg=T["bg"]); df.pack(fill="x",pady=1)
                tk.Label(df,text=cat,bg=T["bg"],fg=T["muted"],
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),8)).pack(side="left")
                def _del_cat(c=cat):
                    if c in cats: cats.remove(c)
                    if c in active_cats: active_cats.remove(c)
                    _save_cats()
                    try: pop.destroy()
                    except Exception: pass
                tk.Button(df,text="✕",command=_del_cat,
                    bg=T["bg"],fg=T["muted"],relief="flat",bd=0,
                    font=(self.cfg.get("ui_font","Segoe UI Variable"),7),
                    cursor="hand2",activebackground=T["item_hover"]).pack(side="right")

            # close on click-outside
            def _close_pop(e=None):
                try: pop.destroy()
                except Exception: pass
            pop.bind("<FocusOut>", lambda e: self.root.after(100, _close_pop))
            ne.focus_set()

        cat_dd_btn.bind("<Button-1>", _open_cat_dropdown)

        # ── search bar ──────────────────────────────────────────────────
        sb = tk.Frame(self.task_frame,bg=T["bg"]); sb.pack(fill="x",padx=6,pady=(0,4))
        doc_search_var = tk.StringVar()
        se = tk.Entry(sb,textvariable=doc_search_var,bg=T["entry_bg"],fg=T["entry_fg"],
            insertbackground=T["entry_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            highlightthickness=1,highlightbackground=T["separator"],highlightcolor=T["check_done"])
        se.pack(side="left",fill="x",expand=True,ipady=4)
        ph_shown = [True]
        def _show_ph():
            if not se.winfo_exists(): return
            if not doc_search_var.get(): se.insert(0,"🔍 Search docs…"); ph_shown[0]=True
        def _hide_ph(e):
            if not se.winfo_exists(): return
            if ph_shown[0]: se.delete(0,"end"); ph_shown[0]=False

        def _apply_filter(docs_list, q):
            out = docs_list
            if active_cats:
                out = [d for d in out if d.get("category","Default") in active_cats]
            if q:
                out = [d for d in out if q in d.get("title","").lower() or q in d.get("body","").lower()]
            return out

        def _on_search(*_):
            q = doc_search_var.get().strip().lower()
            if ph_shown[0]: q=""
            filtered = _apply_filter(all_docs, q)
            self._doc_grid_docs = filtered
            if hasattr(self,"_grid_job"): self.root.after_cancel(self._grid_job)
            self._grid_job = self.root.after(80, lambda: self._relayout_doc_grid(
                self._doc_grid_host.winfo_width() if hasattr(self,"_doc_grid_host") and self._doc_grid_host.winfo_exists() else 320))
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

        filtered_docs = _apply_filter(all_docs, "")
        grid_host = tk.Frame(self.task_frame,bg=T["bg"]); grid_host.pack(fill="x",padx=6,pady=2)
        self._doc_grid_host = grid_host
        self._doc_grid_docs = filtered_docs
        self._doc_grid_T    = T
        def _debounce_grid(e, gh=grid_host):
            if hasattr(self,"_grid_job"): self.root.after_cancel(self._grid_job)
            self._grid_job = self.root.after(80, lambda: self._relayout_doc_grid(gh.winfo_width() if gh.winfo_exists() else 320))
        grid_host.bind("<Configure>", _debounce_grid)
        self.root.after(120, lambda: self._relayout_doc_grid(grid_host.winfo_width() if grid_host.winfo_exists() else 320))

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
            cat_tag = doc.get("category","Default") or "Default"
            tl = tk.Label(cell,text=title_txt,bg=T["item_bg"],fg=T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold"),
                anchor="nw",wraplength=max(40, cell_w-20),justify="left",padx=4,pady=3)
            tl.grid(row=0,column=0,sticky="ew",padx=0,pady=0)
            cl = tk.Label(cell,text=f"📂 {cat_tag}",bg=T["item_bg"],fg=T["archive"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),7),
                anchor="nw",padx=4,pady=0)
            cl.grid(row=1,column=0,sticky="ew",padx=0,pady=0)
            cell.rowconfigure(1,weight=0)
            cell.rowconfigure(2,weight=1)
            pl = tk.Label(cell,text=preview_raw,bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
                anchor="nw",wraplength=cell_w-8,justify="left",padx=4,pady=1)
            pl.grid(row=2,column=0,sticky="nsew",padx=0,pady=(0,16))
            def trash_doc(d=doc):
                all_docs=load_docs()
                for dd in all_docs:
                    if dd.get("id")==d.get("id"):
                        dd["deleted"]=True; dd["deleted_at"]=now_dt().isoformat(timespec="seconds"); break
                save_docs(all_docs)
                self._delete_doc_backup(d)
                self._render_tasks()
            del_btn = tk.Label(cell,text="✕",bg=T["item_bg"],fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),7),cursor="hand2",padx=2)
            del_btn.place(x=cell_w-16,y=3)
            del_btn.bind("<Button-1>", lambda e,fn=trash_doc: fn())
            tl.bind("<Button-1>",        lambda e,d=doc,l=tl: self._inline_rename_doc(d,l))
            tl.bind("<Double-Button-1>", lambda e,d=doc: self._open_doc(d))
            for w in (cell,pl,cl):
                w.bind("<Double-Button-1>", lambda e,d=doc: self._open_doc(d))
            def _enter(e, ww=(cell,tl,pl,cl,del_btn)):
                for w in ww[:4]: w.configure(bg=T["item_hover"])
                ww[4].configure(bg=T["item_hover"], fg=T["text"])
            def _leave(e, ww=(cell,tl,pl,cl,del_btn)):
                for w in ww[:4]: w.configure(bg=T["item_bg"])
                ww[4].configure(bg=T["item_bg"], fg=T["muted"])
            for w in (cell,tl,pl,cl):
                w.bind("<Enter>",_enter); w.bind("<Leave>",_leave)
            # Invisible drag zone — whole card is draggable, cursor shows it
            cell.configure(cursor="fleur")
            for w in (cell,tl,pl,cl):
                w.bind("<ButtonPress-1>",   lambda e,i=i: self._doc_drag_start(e,i))
                w.bind("<B1-Motion>",       self._doc_drag_motion)
                w.bind("<ButtonRelease-1>", self._doc_drag_end)
            # forward scroll events from card widgets to main canvas
            for w in (cell,tl,pl,cl,del_btn):
                for seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
                    try: w.bind(seq, self._scroll, add="+")
                    except Exception: pass
                for seq in ("<Control-MouseWheel>","<Control-Button-4>","<Control-Button-5>"):
                    try: w.bind(seq, self._ctrl_scroll, add="+")
                    except Exception: pass
        # bind scroll on the grid host itself too
        gh = self._doc_grid_host
        if gh.winfo_exists():
            for seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
                try: gh.bind(seq, self._scroll, add="+")
                except Exception: pass

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
            old_title = doc.get("title","")
            doc["title"]=new
            all_docs=load_docs()
            for i,d in enumerate(all_docs):
                if d.get("id")==doc.get("id"): all_docs[i]=doc; break
            save_docs(all_docs)
            # rename backup file: delete old name, write new name
            bp = self.cfg.get("docs_backup_path","").strip()
            if bp and old_title and old_title != new:
                import re as _re2
                cat = doc.get("category","Default") or "Default"
                cat_folder = os.path.join(bp, cat)
                old_safe = _re2.sub(r'[\\/:*?"<>|]',"_", old_title)[:60] or "Untitled"
                old_path = os.path.join(cat_folder, old_safe+".md")
                try:
                    if os.path.exists(old_path): os.remove(old_path)
                except Exception: pass
                self._sync_doc_backup(doc, cat_folder)
            if self.current_tab=="docs": self._render_tasks()
        e.bind("<Return>",finish)
        e.bind("<Escape>",lambda ev:(e.destroy(),))
        e.bind("<FocusOut>",lambda ev: self.root.after(80,finish))

    def _new_doc(self):
        # preselect category: use first active filter cat, else "Default"
        active_cats = self.cfg.get("docs_active_categories", [])
        cats = self.cfg.get("docs_categories", ["Default"])
        if "Default" not in cats: cats.insert(0, "Default")
        if active_cats:
            preset_cat = active_cats[0] if active_cats[0] in cats else "Default"
        else:
            preset_cat = "Default"
        d = {"id":str(uuid.uuid4()),"title":"","body":"",
             "created":now_dt().isoformat(timespec="seconds"),"deleted":False,
             "category":preset_cat}
        docs = load_docs(); docs.insert(0,d); save_docs(docs)
        self._open_doc(d, focus_title=True)

    def _open_doc(self, doc, focus_title=False):
        wid = doc.get("id","")
        for w in self.root.winfo_children():
            if isinstance(w,tk.Toplevel) and getattr(w,"_doc_id",None)==wid:
                w.lift(); w.focus_force(); return
        win = tk.Toplevel(self.root)
        win._doc_id = wid
        win.title(f"Doc - {doc.get('title','Untitled')}")
        # restore saved geometry or use default
        _saved_geo = self.cfg.get("doc_win_geometry", "500x520")
        win.geometry(_saved_geo)
        win.configure(bg=self.T["bg"])
        win.attributes("-topmost", True)
        def _save_win_geo(e=None):
            if win.winfo_exists():
                self.cfg["doc_win_geometry"] = win.geometry()
                save_config(self.cfg)
        win.bind("<Configure>", _save_win_geo)
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
        # always-visible save icon, next to the title so it's reachable even
        # if the window is small/unexpanded and the bottom Save button is hidden
        _save_icon_btn = tk.Button(tf, text="💾", bg=T["bg"], fg=T["text"],
            relief="flat", bd=0, font=(self.cfg.get("ui_font","Segoe UI Variable"),11),
            padx=6, cursor="hand2", activebackground=T["btn_hover"])
        _save_icon_btn.pack(side="left", padx=(2,0))
        if focus_title:
            win.after(50, lambda: (title_entry.focus_set(), title_entry.select_range(0,"end")))
        # category selector
        cat_row2 = tk.Frame(win,bg=T["bg"]); cat_row2.pack(fill="x",padx=10,pady=(0,2))
        tk.Label(cat_row2,text="Category:",bg=T["bg"],fg=T["muted"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9)).pack(side="left")
        _cats2 = self.cfg.get("docs_categories",["Default"])
        if "Default" not in _cats2: _cats2.insert(0,"Default")
        _cat_var = tk.StringVar(value=doc.get("category","Default") or "Default")
        _original_cat = [doc.get("category","Default") or "Default"]  # snapshot at open time
        cat_menu = ttk.Combobox(cat_row2,textvariable=_cat_var,values=_cats2,
            state="readonly",width=18,
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9))
        cat_menu.pack(side="left",padx=(6,4))
        # (category is read from _cat_var at save time — no eager mutation)
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
        def save_doc(flash=False):
            old_title = doc.get("title","")
            old_cat   = _original_cat[0]  # snapshot from window-open (or last save)
            doc["title"] = title_var.get().strip() or "Untitled"
            doc["body"]  = body_text.get("1.0","end-1c")
            doc["updated"] = now_dt().isoformat(timespec="seconds")
            doc["category"] = _cat_var.get()
            new_cat = doc["category"] or "Default"
            all_docs = load_docs()
            # remove old entry, prepend updated doc so it appears at top
            all_docs = [d for d in all_docs if d.get("id")!=doc.get("id")]
            all_docs.insert(0, doc)
            save_docs(all_docs)
            if win.winfo_exists():
                win.title(f"Doc - {doc['title']}")
            bp = self.cfg.get("docs_backup_path","").strip()
            if bp:
                import re as _re3
                new_cat_folder = os.path.join(bp, new_cat)
                # if category changed, remove file from old category folder
                if old_cat != new_cat:
                    old_safe = _re3.sub(r'[\\/:*?"<>|]',"_", old_title)[:60] or "Untitled"
                    old_path = os.path.join(bp, old_cat, old_safe+".md")
                    try:
                        if os.path.exists(old_path): os.remove(old_path)
                    except Exception: pass
                # if title changed within same category, delete old file
                elif old_title and old_title != doc["title"]:
                    old_safe = _re3.sub(r'[\\/:*?"<>|]',"_", old_title)[:60] or "Untitled"
                    old_path = os.path.join(new_cat_folder, old_safe+".md")
                    try:
                        if os.path.exists(old_path): os.remove(old_path)
                    except Exception: pass
                self._sync_doc_backup(doc, new_cat_folder)
            _original_cat[0] = new_cat  # update snapshot for next save
            if self.current_tab=="docs": self._render_tasks()
            if flash and win.winfo_exists() and _save_icon_btn.winfo_exists():
                _save_icon_btn.configure(text="✅")
                win.after(700, lambda: _save_icon_btn.configure(text="💾") if _save_icon_btn.winfo_exists() else None)

        def close_save():
            save_doc(); win.destroy()

        # ── autosave: debounced save while typing (title or body) ───────────
        _autosave_job = [None]
        def _schedule_autosave(*_a):
            if _autosave_job[0]:
                try: win.after_cancel(_autosave_job[0])
                except Exception: pass
            _autosave_job[0] = win.after(900, lambda: save_doc(flash=True))
        title_var.trace_add("write", _schedule_autosave)
        body_text.bind("<KeyRelease>", _schedule_autosave)
        _cat_var.trace_add("write", _schedule_autosave)

        if _done_btn_ref[0]:
            _done_btn_ref[0].configure(command=close_save)
        # Enter on title → done
        title_entry.bind("<Return>", lambda e: close_save())
        title_entry.bind("<Escape>", lambda e: close_save())
        # save icon (next to title) → manual save with flash feedback, keeps window open
        _save_icon_btn.configure(command=lambda: save_doc(flash=True))
        # Ctrl+Z / Ctrl+Y handled natively by tk.Text when undo=True

        bf = tk.Frame(win,bg=T["bg"]); bf.pack(fill="x",padx=10,pady=(0,10))
        tk.Button(bf,text="✓ Done",command=close_save,
            bg=T["check_done"],fg="#ffffff",relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9,"bold"),
            padx=12,pady=5,cursor="hand2",activebackground=T["check_done"]).pack(side="right")
        tk.Button(bf,text="💾 Save",command=lambda: save_doc(flash=True),
            bg=T["btn_bg"],fg=T["btn_fg"],relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),9),
            padx=10,pady=5,cursor="hand2",activebackground=T["btn_hover"]).pack(side="right",padx=(0,6))
        # auto-save on window close (no dialogs, just persists silently)
        def _on_close():
            if _autosave_job[0]:
                try: win.after_cancel(_autosave_job[0])
                except Exception: pass
            save_doc()
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)

    # ── feature 9: Habits ────────────────────────────────────────────────────
    def _render_habits(self, T):
        data    = load_habits()
        habits  = [h for h in data.get("habits",[]) if not h.get("deleted")]
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
            self._render_recurring(T)   # recurring list lives below habits
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
        _bar_drawn = [False]
        def _draw_today_bar(e=None, bh=bar_bg, p=pct_today, col=T["check_done"]):
            if not bh.winfo_exists(): return
            bw = bh.winfo_width()
            if bw < 4: bw = 200
            for w in bh.winfo_children(): w.destroy()
            if p > 0:
                tk.Frame(bh, bg=col, height=5, width=max(1, int(bw*p))).place(x=0, y=0)
        bar_bg.bind("<Configure>", _draw_today_bar)
        bar_bg.after(50, _draw_today_bar)

        for _h_idx, h in enumerate(habits):
            hid        = h["id"]
            done_today_h = hid in log.get(today,[])
            streak       = _habit_streak(hid,log)
            best         = _habit_best_streak(hid,log)
            total_h_days = _habit_total_days(hid,log)
            last_7       = _habit_last_n(hid,log,7)
            last_30      = _habit_last_n(hid,log,30)

            card = tk.Frame(self.task_frame,bg=T["item_bg"],pady=5,padx=8)
            card._habit_idx = _h_idx
            card.pack(fill="x",pady=2)

            # top row: drag-handle, flame+streak, name, done-btn, delete-btn
            top = tk.Frame(card,bg=T["item_bg"]); top.pack(fill="x")

            # tiny ⋮⋮ drag handle
            _hi = _h_idx
            drag_h = tk.Label(top, text="⋮⋮", bg=T["item_bg"], fg=T["muted"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"), 8),
                cursor="fleur", padx=2, pady=0)
            drag_h.pack(side="left", padx=(0,2))
            drag_h.bind("<ButtonPress-1>", lambda e,i=_hi,hl=habits,d=data: self._habit_drag_start(e,i,hl,d))

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
                    for hx in data["habits"]:
                        if hx["id"]==hid:
                            hx["deleted"] = True
                            hx["deleted_at"] = now_dt().isoformat(timespec="seconds")
                            break
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
                if hid in day_log:
                    day_log.remove(hid)
                    # revoke XP for un-marking
                    self.cfg["xp"] = max(0, self.cfg.get("xp",0) - 10)
                    save_config(self.cfg)
                else:
                    day_log.append(hid)
                    # award XP for marking done
                    self.cfg["xp"] = self.cfg.get("xp",0) + 10
                    save_config(self.cfg)
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

        self._render_recurring(T)       # recurring / reminders, below habits

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
    def _task_row(self, task, archived=False, trashed=False, searching=False, scheduled=False):
        T = self.T
        wrapper = tk.Frame(self.task_frame, bg=T["item_bg"]); wrapper.pack(fill="x", pady=2)
        row = tk.Frame(wrapper, bg=T["item_bg"], pady=3, padx=4); row.pack(fill="x")
        row._task_ref = task; wrapper._task_ref = task
        action_buttons = []

        def paint(bg):
            for w in _paint_widgets:
                try: w.configure(bg=bg)
                except Exception: pass
            for b in action_buttons:
                try: b.configure(bg=bg)
                except Exception: pass
            try: btn_overlay.configure(bg=bg)
            except Exception: pass
            if drag_lbl: drag_lbl.configure(bg=bg)

        def _bind_hover(widget):
            widget.bind("<Enter>", lambda e: paint(T["item_hover"]), add="+")
            widget.bind("<Leave>", lambda e: paint(T["item_bg"]), add="+")
        row.bind("<Enter>", lambda e: paint(T["item_hover"]))
        row.bind("<Leave>", lambda e: paint(T["item_bg"]))

        pri = task.get("priority","none")
        pri_color = T.get(pri, T["separator"]) if pri!="none" else T["separator"]
        _pri_bar = tk.Frame(wrapper, bg=pri_color, width=5)
        _pri_bar.place(x=0, y=4, width=5, height=10)  # real size set by _update_bar
        # keep bar updated when wrapper resizes
        def _update_bar(e, b=_pri_bar):
            pad = 4
            b.place(x=0, y=pad, width=5, height=max(4, e.height - pad*2))
        wrapper.bind("<Configure>", _update_bar)
        # offset row and date_row content so bar doesn't cover checkbox
        row.pack_configure(padx=(9,4))

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
        tw    = tk.Frame(row,bg=T["item_bg"])
        # tw.pack() is deferred — called after action buttons claim side=right space

        # Feature 4: wraplength uses full available width dynamically
        def _make_lbl(tw=tw,task=task,style=style,fg=fg):
            lbl = tk.Label(tw,text=task["text"],bg=T["item_bg"],fg=fg,
                font=style,anchor="w",justify="left",wraplength=1)
            lbl.pack(anchor="w",fill="x",expand=True)
            def _update_wrap(e,l=lbl): l.configure(wraplength=max(60,e.width-54))
            tw.bind("<Configure>", _update_wrap, add="+")
            lbl.bind("<Configure>", lambda e,l=lbl,t=tw: l.configure(wraplength=max(60,t.winfo_width()-54)))
            return lbl
        lbl = _make_lbl()

        _bind_hover(tw); _bind_hover(lbl); _bind_hover(chk); _bind_hover(wrapper)
        # raise text content above action buttons so text overlaps buttons, not vice versa

        if not archived and not trashed and not searching:
            lbl.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._inline_edit_task(p,l,t))
            tw.bind("<Double-Button-1>",  lambda e,p=tw,l=lbl,t=task: self._body_dblclick(e,p,l,t))
            row.bind("<Double-Button-1>", lambda e,p=tw,l=lbl,t=task: self._body_dblclick(e,p,l,t))

        for st in task.get("subtasks",[]):
            self._inject_subtask_row(tw, task, st, archived=archived, trashed=trashed, searching=searching)

        _WDAY = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

        def _fmt_short(iso_str):
            """Format YYYY-MM-DD or YYYY-MM-DDTHH:MM to 'Mon 12.07.26'"""
            try:
                d = _dtm.date.fromisoformat(iso_str[:10])
                return f"{_WDAY[d.weekday()]} {d.day:02d}.{d.month:02d}.{str(d.year)[2:]}"
            except Exception: return iso_str or ""

        def _fmt_short_time(iso_str, time_str):
            base = _fmt_short(iso_str)
            return f"{base} {time_str}" if time_str else base

        dt      = parse_iso(task["completed_at"]) if is_done and task.get("completed_at") else parse_iso(task["created"])
        _has_sd = bool(task.get("start_date"))
        _has_dd = bool(task.get("due_date"))
        _show_created = not (_has_sd or _has_dd)

        meta_fg = T["archive"] if archived else T["muted"]
        fn8 = (self.cfg.get("ui_font","Segoe UI Variable"), 8)

        # Build the meta/date combined row
        # If start/due not set → everything in one line (meta text + tiny buttons)
        # If start or due is set → hide created text, show only the date buttons line

        if not archived and not trashed and not searching:
            # Combined row: created text (if no dates set) + start/due buttons
            date_row = tk.Frame(wrapper, bg=T["item_bg"])
            date_row.pack(fill="x", padx=(28,0))  # indent to align with text content

            if _show_created:
                if is_done and task.get("completed_at"):
                    meta_txt = f"Resolved {_fmt_short(task['completed_at'])}"
                else:
                    _wday = _WDAY[dt.weekday()] if dt else ""
                    meta_txt = f"{_wday} {fmt_dt(dt)}" if dt else ""
                if trashed and task.get("deleted_at"):
                    remain = max(0, int((datetime.timedelta(hours=TRASH_HOURS)-(now_dt()-parse_iso(task["deleted_at"]))).total_seconds()//3600))
                    meta_txt += f" · ~{remain}h left"
                meta = tk.Label(date_row, text=meta_txt, bg=T["item_bg"], fg=meta_fg, font=fn8, anchor="w")
                meta.pack(side="left", padx=(0,6))
            else:
                meta = tk.Label(tw, text="", bg=T["item_bg"])  # invisible placeholder
        else:
            date_row = None
            if _show_created:
                if is_done and task.get("completed_at"):
                    meta_txt = f"Resolved {_fmt_short(task['completed_at'])}"
                else:
                    _wday = _WDAY[dt.weekday()] if dt else ""
                    meta_txt = f"{_wday} {fmt_dt(dt)}" if dt else ""
                if pri!="none": meta_txt += f" · {pri.capitalize()}"
                if trashed and task.get("deleted_at"):
                    remain = max(0, int((datetime.timedelta(hours=TRASH_HOURS)-(now_dt()-parse_iso(task["deleted_at"]))).total_seconds()//3600))
                    meta_txt += f" · ~{remain}h left"
                meta = tk.Label(tw, text=meta_txt, bg=T["item_bg"], fg=meta_fg, font=fn8, anchor="w")
                meta.pack(anchor="w")
            else:
                meta = tk.Label(tw, text="", bg=T["item_bg"])

        if not archived and not trashed and not searching:

            def _sd_text(t=task):
                sd = t.get("start_date")
                return ("▶ " + _fmt_short(sd)) if sd else "▶"
            def _dd_text(t=task):
                dd = t.get("due_date"); dt2 = t.get("due_time","")
                return ("⏰ " + _fmt_short_time(dd, dt2)) if dd else "⏰"

            sd_set = bool(task.get("start_date"))
            dd_set = bool(task.get("due_date"))

            sd_btn = tk.Button(date_row, text=_sd_text(),
                bg=T["item_bg"],
                fg=T["check_done"] if sd_set else T["muted"],
                relief="flat", bd=0,
                font=(self.cfg.get("ui_font","Segoe UI Variable"),7),
                padx=2, pady=0, cursor="hand2", activebackground=T["item_hover"])
            sd_btn.pack(side="left", padx=(0,8))

            dd_btn = tk.Button(date_row, text=_dd_text(),
                bg=T["item_bg"],
                fg=T["archive"] if dd_set else T["muted"],
                relief="flat", bd=0,
                font=(self.cfg.get("ui_font","Segoe UI Variable"),7),
                padx=2, pady=0, cursor="hand2", activebackground=T["item_hover"])
            dd_btn.pack(side="left")

            if pri != "none":
                _pri_lbl_w = tk.Label(date_row, text=f"· {pri.capitalize()}", bg=T["item_bg"],
                    fg=meta_fg, font=fn8)
                _pri_lbl_w.pack(side="left", padx=(6,0))
                if hasattr(self, "_task_widget_registry") and id(task) in self._task_widget_registry:
                    self._task_widget_registry[id(task)]["pri_lbl"] = _pri_lbl_w

            def _pick_start(t=task, b=sd_btn):
                init = _dtm.date.fromisoformat(t["start_date"]) if t.get("start_date") else None
                def _on_sel(d):
                    t["start_date"] = d.isoformat() if d else None
                    t["scheduled_jumped"] = False
                    b.configure(text=_sd_text(t),
                        fg=T["check_done"] if d else T["muted"])
                    save_tasks(self.tasks)
                    self._render_tasks()
                self._show_calendar_picker(b, init, _on_sel)

            def _pick_due(t=task, b=dd_btn):
                init = _dtm.date.fromisoformat(t["due_date"]) if t.get("due_date") else None
                init_time = t.get("due_time","")
                def _on_sel(result):
                    if result is None:
                        t["due_date"] = None; t["due_time"] = ""
                    elif isinstance(result, tuple):
                        d, tm = result
                        t["due_date"] = d.isoformat(); t["due_time"] = tm
                    else:
                        t["due_date"] = result.isoformat(); t["due_time"] = ""
                    t["due_jumped"] = False
                    b.configure(text=_dd_text(t),
                        fg=T["archive"] if t.get("due_date") else T["muted"])
                    save_tasks(self.tasks)
                    self._render_tasks()
                self._show_calendar_picker(b, init, _on_sel,
                    show_time=True, initial_time=init_time)

            sd_btn.configure(command=_pick_start)
            dd_btn.configure(command=_pick_due)

        _paint_widgets = [wrapper,row,tw,lbl,meta] + ([date_row] if date_row else [])
        # Register task widgets for in-place updates (priority, rename, subtask add)
        _reg = {"lbl": lbl, "pri_bar": _pri_bar, "tw": tw,
                "date_row": date_row, "pri_lbl": None, "wrapper": wrapper}
        if hasattr(self, "_task_widget_registry"):
            self._task_widget_registry[id(task)] = _reg

        # tw fills the full row width; btn_overlay floats via place() — zero impact on layout
        tw.pack(side="left", fill="both", expand=True)

        btn_overlay = tk.Frame(wrapper, bg=T["item_bg"])
        _OVERLAY_SZ = 48  # fixed square size — 2×2 grid of bigger, easy-to-click buttons
        _BIN = "x"        # small ASCII stand-in so emoji doesn't get clipped

        def mk_btn(txt, cmd_fn, r, c):
            b = tk.Button(btn_overlay, text=txt, command=cmd_fn, bg=T["item_bg"], fg=T["text"],
                relief="flat", bd=0, padx=0, pady=0, width=2,
                font=(self.cfg.get("ui_font","Segoe UI Variable"), 8),
                cursor="hand2", activebackground=T["item_hover"])
            b.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
            action_buttons.append(b); return b

        btn_overlay.grid_columnconfigure(0, weight=1, uniform="bq")
        btn_overlay.grid_columnconfigure(1, weight=1, uniform="bq")
        btn_overlay.grid_rowconfigure(0, weight=1, uniform="bq")
        btn_overlay.grid_rowconfigure(1, weight=1, uniform="bq")

        if trashed:
            mk_btn("↺", lambda t=task: self._recover_task(t), 0, 0)
            _del_btn_ref = [None]
            def _confirm_del_task(btn_r=_del_btn_ref, t=task):
                b = btn_r[0]
                if b is None: return
                if getattr(b,"_confirm",False):
                    self._delete_forever(t)
                else:
                    b._confirm = True; b.configure(text="?", fg=self.T["close_hover"])
                    b.after(2000, lambda: (setattr(b,"_confirm",False),
                        b.configure(text="🗑",fg=self.T["text"])) if b.winfo_exists() else None)
            _del_b = mk_btn("🗑", _confirm_del_task, 0, 1)
            if _del_b: _del_b._confirm=False; _del_btn_ref[0]=_del_b
        elif archived:
            mk_btn("↩", lambda t=task: self._unsolve_task(t), 0, 0)
            mk_btn("🗑", lambda t=task: self._trash_task(t),   0, 1)
        elif not searching:
            # 2×2 grid: [✎  !]
            #           [⊞  🗑]
            mk_btn("✎", lambda t=task,p=tw,l=lbl: self._inline_edit_task(p,l,t), 0, 0)
            mk_btn("!",  lambda t=task: self._cycle_priority(t),                  0, 1)
            mk_btn("⊞",  lambda t=task: self._add_subtask(t),                    1, 0)
            mk_btn("🗑",  lambda t=task: self._trash_task(t),                     1, 1)

        # Place overlay anchored to top-right of wrapper (not row) so it is never clipped
        def _place_overlay(e=None, bo=btn_overlay, w=wrapper, sz=_OVERLAY_SZ):
            try:
                if not bo.winfo_exists() or not w.winfo_exists(): return
                wh = w.winfo_height()
                if wh < 2: wh = w.winfo_reqheight()
                y_off = max(0, (wh - sz) // 2)
                bo.place(relx=1.0, x=-sz-2, y=y_off, width=sz, height=sz)
            except Exception: pass
        wrapper.bind("<Configure>", _place_overlay, add="+")
        btn_overlay.after(60, _place_overlay)


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
                changed = save and new and new != task.get("text","")
                try: ef.destroy()
                except Exception: pass
                if changed:
                    task["text"] = new
                    save_tasks(self.tasks)
                    np = self.cfg.get("obsidian_note_path","").strip()
                    if np: sync_note(np, task)
                    # Update label in-place — no full re-render
                    reg = getattr(self, "_task_widget_registry", {}).get(id(task))
                    if reg and reg.get("lbl") and reg["lbl"].winfo_exists():
                        reg["lbl"].configure(text=new)
                        label.pack(anchor="w", fill="x", expand=True)
                    else:
                        self._render_tasks(); return
                # restore label whether changed or not
                label.pack(anchor="w", fill="x", expand=True)
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
                changed = save and new and new != task.get("text","")
                try: entry.destroy()
                except Exception: pass
                if changed:
                    task["text"] = new
                    save_tasks(self.tasks)
                    np = self.cfg.get("obsidian_note_path","").strip()
                    if np: sync_note(np, task)
                    # Update label in-place — no full re-render
                    reg = getattr(self, "_task_widget_registry", {}).get(id(task))
                    if reg and reg.get("lbl") and reg["lbl"].winfo_exists():
                        reg["lbl"].configure(text=new)
                    else:
                        self._render_tasks(); return
                label.pack(anchor="w", fill="x", expand=True)
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
    def _inject_subtask_row(self, tw, task, st, archived=False, trashed=False, searching=False):
        """Build one subtask row widget into tw without a full re-render."""
        T = self.T
        sf = tk.Frame(tw, bg=T["item_bg"]); sf.pack(anchor="w", fill="x")
        sv = tk.BooleanVar(value=st.get("done", False))
        sc = tk.Checkbutton(sf, variable=sv, bg=T["item_bg"], activebackground=T["item_bg"],
            selectcolor=T["check_done"] if st.get("done") else T["item_bg"],
            relief="flat", bd=0, highlightthickness=0,
            state="disabled" if (archived or trashed or searching) else "normal",
            command=lambda sv=sv, sub=st, ta=task: self._toggle_subtask(ta, sub, sv))
        sc.pack(side="left")
        self._subtask_check_registry[id(st)] = sc
        sl = tk.Label(sf, text=st.get("text",""), bg=T["item_bg"],
            fg=T["muted"] if st.get("done") else T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"), 8,
                  "overstrike" if st.get("done") else "normal"),
            anchor="w", justify="left", wraplength=1)
        sl.pack(side="left", anchor="w", fill="x", expand=True)
        def _upd_sub_wrap(e, l=sl): l.configure(wraplength=max(40, e.width-54))
        sf.bind("<Configure>", _upd_sub_wrap, add="+")
        self._subtask_label_registry[id(st)] = sl
        if not archived and not trashed and not searching:
            sl.bind("<Double-Button-1>",
                lambda e, parent=sf, lab=sl, ta=task, sub=st:
                    self._inline_edit_subtask(parent, lab, ta, sub))
        if st.get("_editing"):
            self.root.after(10, lambda: self._inline_edit_subtask(sf, sl, task, st))
        return sf

    def _add_subtask(self, task):
        # flush any open subtask entry for THIS task before adding a new one
        self._flush_editing_subtasks(task)
        new_sub = {"id": str(uuid.uuid4()), "text": "", "done": False, "_editing": True}
        task.setdefault("subtasks", []).append(new_sub)
        save_tasks(self.tasks)
        np = self.cfg.get("obsidian_note_path","").strip()
        if np: sync_note(np, task)
        # Inject subtask row in-place if we have the tw widget
        reg = getattr(self, "_task_widget_registry", {}).get(id(task))
        if reg and reg.get("tw") and reg["tw"].winfo_exists():
            self._inject_subtask_row(reg["tw"], task, new_sub)
        else:
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
        save_tasks(self.tasks)
        T = self.T
        reg = getattr(self, "_task_widget_registry", {}).get(id(task))
        if not reg:
            self._render_tasks(); return
        pri = task["priority"]
        pri_color = T.get(pri, T["separator"]) if pri != "none" else T["separator"]
        # Update left colour bar
        try: reg["pri_bar"].configure(bg=pri_color)
        except Exception: pass
        # Update or create/remove the priority text label in date_row
        try:
            dr = reg.get("date_row")
            pl = reg.get("pri_lbl")
            meta_fg = T["muted"]
            fn8 = (self.cfg.get("ui_font","Segoe UI Variable"), 8)
            if pri != "none":
                if pl and pl.winfo_exists():
                    pl.configure(text=f"· {pri.capitalize()}")
                elif dr and dr.winfo_exists():
                    pl = tk.Label(dr, text=f"· {pri.capitalize()}", bg=T["item_bg"],
                                  fg=meta_fg, font=fn8)
                    pl.pack(side="left", padx=(6,0))
                    reg["pri_lbl"] = pl
            else:
                if pl and pl.winfo_exists():
                    pl.destroy()
                    reg["pri_lbl"] = None
        except Exception:
            self._render_tasks()

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
        # Stay on archive tab if that is where the delete was triggered from
        if self.current_tab != "archive":
            self.current_tab = "active"
        self._render_tasks()

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
            f = tk.Frame(sf,bg=self.T["bg"]); f.pack(fill="x",padx=(12,0),pady=4)
            l = tk.Label(f,text=label,bg=self.T["bg"],fg=self.T["text"],
                font=(self.cfg.get("ui_font","Segoe UI Variable"),9),anchor="w")
            l.pack(side="left", fill="x", expand=True)
            self._settings_widgets["frame_bg"].append(f); self._settings_widgets["label"].append(l)
            maker(f); return f

        section("Obsidian (Optional)")
        note_var = tk.StringVar(value=self.cfg.get("obsidian_note_path",""))
        note_var.trace_add("write", lambda *a:(self.cfg.__setitem__("obsidian_note_path",note_var.get().strip()),self._save_cfg_debounced()))
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
        docs_path_var.trace_add("write", lambda *a:(self.cfg.__setitem__("docs_backup_path",docs_path_var.get().strip()),self._save_cfg_debounced()))
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
            # was a 27-entry literal copy of btn_bg, rebuilt on every loop pass
            # and 4,100 lines away from the palette it duplicated.
            preview_bg = THEMES.get(name, {}).get("btn_bg", samp["check_done"])
            sw=tk.Label(f,text="  ",bg=preview_bg,width=2,relief="flat"); sw.pack(side="left",padx=(4,0))
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
        live_toggle("Use ⭐ Focus tab (replaces Archive tab):","use_priorities_tab",
            lambda v:(self._refresh_tabs(), self._render_tasks()))

        section("UI Scale")
        scale_var = tk.DoubleVar(value=float(self.cfg.get("ui_scale",1.0)))
        def scale_row(p):
            sc=tk.Scale(p,variable=scale_var,from_=0.5,to=3.0,resolution=0.05,orient="horizontal",
                bg=self.T["bg"],fg=self.T["text"],troughcolor=self.T["separator"],
                activebackground=self.T["btn_hover"],highlightthickness=0,bd=0,length=220,
                command=lambda v:(self._set_scale_debounced(float(v)),self.root.after(10,self._keep_settings_alive)))
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
                    "recurring": load_recurring(),
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
                        # merge, never overwrite: a bare save_habits(raw["habits"])
                        # destroyed every existing habit AND the whole completion log.
                        _inc = raw["habits"]
                        if isinstance(_inc, dict):
                            _cur = load_habits()
                            _have = {h.get("id") for h in _cur.get("habits", [])}
                            for _h in _inc.get("habits", []):
                                if _h.get("id") not in _have:
                                    _cur.setdefault("habits", []).append(_h)
                            _clog = _cur.setdefault("log", {})
                            for _day, _ids in (_inc.get("log", {}) or {}).items():
                                _merged = set(_clog.get(_day, [])) | set(_ids or [])
                                _clog[_day] = sorted(_merged)
                            save_habits(_cur)
                    if "recurring" in raw and isinstance(raw["recurring"], dict):
                        _cr = load_recurring()
                        _hr = {r.get("id") for r in _cr.get("rules", [])}
                        for _rr in raw["recurring"].get("rules", []):
                            if isinstance(_rr, dict) and _rr.get("id") not in _hr:
                                _cr.setdefault("rules", []).append(_rec_norm(_rr))
                        _rlog = _cr.setdefault("log", {})
                        for _k, _v in (raw["recurring"].get("log", {}) or {}).items():
                            _rlog[_k] = sorted(set(_rlog.get(_k, [])) | set(_v or []))
                        save_recurring(_cr)
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
        c.pack(side="right", padx=(0,245)); self._settings_widgets["check"].append(c); return c

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
        # cancel pomodoro timers cleanly before quit
        if self._pomo_running:
            self._pomo_accumulate()
        if self._pomo_job:
            try: self.root.after_cancel(self._pomo_job)
            except Exception: pass
        if self._pomo_tick_job:
            try: self.root.after_cancel(self._pomo_tick_job)
            except Exception: pass
        if getattr(self, "_maint_job", None):
            try: self.root.after_cancel(self._maint_job)
            except Exception: pass
        try: self._rec_cancel()
        except Exception: pass

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

    def _mark_tabs_dirty(self, tabs):
        """Single invalidation entry point, called from the save_* functions.
        Defensive: save_*() can fire from _purge_old_trash() during __init__,
        long before _tab_dirty exists.

        Dropping the registries matters: _task_widget_registry is keyed by
        id(task), and with per-tab retained registries a freed task dict's
        address can be reused by a newly allocated one, so a stale entry could
        point at the wrong row. A dirty tab is fully re-rendered anyway."""
        d = getattr(self, "_tab_dirty", None)
        if d is None:
            d = self._tab_dirty = set()
        d.update(tabs)
        reg = getattr(self, "_tab_reg", None)
        if reg:
            for n in tabs:
                reg.pop(n, None)

    # -- per-tab frame cache ------------------------------------------------
    def _init_tab_cache(self):
        self._tab_frames = {}          # tab -> tk.Frame (child of canvas)
        self._tab_dirty  = set(self._ALL_TABS)
        self._tab_scroll = {}          # tab -> canvas yview fraction
        self._tab_reg    = {}          # tab -> (task_reg, sub_lbl, sub_chk)
        self._current_frame_tab = None

    def _tab_frame(self, name):
        """Get-or-create the persistent container frame for one tab."""
        f = self._tab_frames.get(name)
        if f is not None:
            try:
                if f.winfo_exists(): return f
            except Exception: pass
        f = tk.Frame(self.canvas, bg=self.T["bg"])
        f.bind("<Configure>", lambda e: self._update_scroll())
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            f.bind(seq, self._scroll)
        f.bind("<Control-MouseWheel>", self._ctrl_scroll)
        self._tab_frames[name] = f
        self._tab_dirty.add(name)
        return f

    def _stash_tab_state(self, name):
        """Save the outgoing tab's scroll offset and in-place-update registries."""
        if not name: return
        try: self._tab_scroll[name] = self.canvas.yview()[0]
        except Exception: pass
        self._tab_reg[name] = (getattr(self, "_task_widget_registry", {}),
                               getattr(self, "_subtask_label_registry", {}),
                               getattr(self, "_subtask_check_registry", {}))

    def _bind_tab_context(self, name):
        """Point task_frame + the per-tab registries at one tab WITHOUT making
        it visible. The frame is a child of the canvas but is not the canvas
        window item, so anything built into it here is invisible.

        This is what makes a tab switch seamless: the old code mounted an EMPTY
        frame and then filled it, so the user watched ~40 rows land one at a
        time. Now the build happens off-screen and is swapped in atomically."""
        f = self._tab_frame(name)
        self.task_frame = f
        self._current_frame_tab = name
        # Registries are per-tab: _render_tasks resets them on every render
        # regardless of tab, so without this every in-place update
        # (_cycle_priority, _toggle_subtask) would degrade to a full re-render.
        tw, sl, sc = self._tab_reg.get(name, ({}, {}, {}))
        self._task_widget_registry   = tw
        self._subtask_label_registry = sl
        self._subtask_check_registry = sc
        return f

    def _mount_tab_frame(self, name):
        """Make one tab's frame the canvas window item - the single visible step."""
        f = self._tab_frame(name)
        if getattr(self, "_mounted_tab", None) != name or self.canvas.itemcget(self._cw, "window") == "":
            try: self.canvas.itemconfigure(self._cw, window=f)
            except Exception: pass
            self._mounted_tab = name

    def _show_tab_frame(self, name):
        """Bind + mount in one step. Kept for callers that are already showing
        content (the _render_tasks resync guard, _build_ui)."""
        self._bind_tab_context(name)
        self._mount_tab_frame(name)

    def _restore_scroll(self, name):
        """Re-apply this tab's remembered scroll offset, twice: once now and
        once after Tk's post-map relayout, which would otherwise clamp it."""
        off = self._tab_scroll.get(name, 0.0)
        def _apply():
            try:
                self._update_scroll()
                self.canvas.yview_moveto(off)
            except Exception: pass
        _apply()
        try: self.canvas.after_idle(_apply)
        except Exception: pass

    def _refresh_status_bar(self):
        """Extracted from the tail of _render_tasks so the cached-tab fast path
        can still update the counts without rendering."""
        cutoff = now_dt() - datetime.timedelta(days=1)
        open_count = archive_count = trash_count = 0
        for t in self.tasks:
            if t.get("deleted"):
                trash_count += 1
            elif t.get("done") and t.get("completed_at"):
                try:
                    if parse_iso(t["completed_at"]) < cutoff: archive_count += 1
                except Exception: pass
            elif not t.get("done"):
                open_count += 1
        parts = ["Tasks: %d" % open_count, "Archive: %d" % archive_count]
        if trash_count: parts.append("Trash: %d" % trash_count)
        self.status_var.set(" · ".join(parts))

    def _apply_date_jumps(self):
        """Was inlined in _render_tasks. Collects first, then reorders: the
        original mutated self.tasks while iterating it."""
        today = datetime.date.today()
        jump = []; changed = False
        for t in self.tasks:
            if t.get("deleted") or t.get("done"): continue
            hit = False
            sd = t.get("start_date")
            if sd and not t.get("scheduled_jumped"):
                try:
                    if datetime.date.fromisoformat(sd) <= today:
                        t["scheduled_jumped"] = True; hit = True
                except Exception: pass
            dd = t.get("due_date")
            if dd and not t.get("due_jumped"):
                try:
                    if datetime.date.fromisoformat(dd) == today:
                        t["due_jumped"] = True
                        pri = t.get("priority", "none")
                        if pri in ("none", "low"): t["priority"] = "medium"
                        elif pri == "medium":      t["priority"] = "high"
                        hit = True
                except Exception: pass
            if hit:
                jump.append(t); changed = True
        if changed:
            for t in reversed(jump):     # preserve relative order at the top
                try: self.tasks.remove(t)
                except ValueError: continue
                self.tasks.insert(0, t)
            save_tasks(self.tasks)

    def _maintenance_tick(self, first=False):
        """Mandatory companion to the frame cache: without its own clock the
        trash would never purge and scheduled tasks would never jump."""
        try:
            self._purge_old_trash()
            self._purge_old_doc_trash()
            self._purge_old_habit_trash()
            self._apply_date_jumps()
            self._rec_catch_up()          # C5: one clock, not two
        except Exception: pass
        if not first and self.current_tab in self._tab_dirty:
            self._render_tasks()
        self._maint_job = self.root.after(60000, self._maintenance_tick)


    # ── scale-aware primitives ───────────────────────────────────────────────
    def _px(self, n):
        """Scale a STRUCTURAL pixel value. Never use on font sizes — Tk's own
        `tk scaling` already scales point-sized fonts, so doing both double-scales."""
        if not n: return 0
        return max(1, int(round(n * float(self.cfg.get("ui_scale", 1.0)))))

    def _sp(self, k):
        """Spacing on the 4-px rhythm. _sp(2) == 8px at scale 1.0."""
        return self._px(SPACE.get(k, k))

    def _font(self, role="body", weight=None, over=False):
        size, w = TYPE_SCALE.get(role, TYPE_SCALE["body"])
        if weight is not None: w = weight
        if over: w = (w + " overstrike").strip()
        fam = self.cfg.get("ui_font", "Segoe UI Variable")
        return (fam, size, w) if w else (fam, size)

    # ── uniform interaction states ───────────────────────────────────────────
    def _interactive(self, w, base, hover, press=None, group=()):
        """Hover + pressed on one widget (and any siblings that must move with
        it). Replaces `activebackground`, which in Tk fires on PRESS, not hover
        — which is why 192 of the app's ~200 controls look dead until clicked."""
        T = self.T
        if press is None:
            press = lighten(hover, .10) if T["is_dark"] else darken(hover, .08)
        members = (w,) + tuple(group)
        def paint(c):
            for x in members:
                try: x.configure(bg=c)
                except Exception: pass
        w._ds_paint, w._ds_base, w._ds_hover = paint, base, hover
        w.bind("<Enter>",           lambda e: paint(hover), add="+")
        w.bind("<Leave>",           lambda e: paint(base),  add="+")
        w.bind("<ButtonPress-1>",   lambda e: paint(press), add="+")
        w.bind("<ButtonRelease-1>", lambda e: paint(hover), add="+")
        return w

    def _focusable(self, w, ring=None):
        """Keyboard focus ring. The 2-px highlight is ALWAYS reserved and merely
        recoloured, so gaining focus never reflows the layout."""
        T = self.T
        try:
            w.configure(takefocus=1, highlightthickness=self._px(2),
                        highlightbackground=w.cget("bg"),
                        highlightcolor=ring or T["focus"])
        except Exception: pass
        return w

    # ── factories ────────────────────────────────────────────────────────────
    def _hairline(self, parent, pad=0, color=None, vertical=False):
        T = self.T
        f = tk.Frame(parent, bg=color or T["divider"],
                     **({"width": 1} if vertical else {"height": 1}))
        f.pack(fill="y" if vertical else "x",
               padx=self._px(pad) if not vertical else 0,
               pady=0 if not vertical else self._px(pad))
        return f

    def _card(self, parent, rounded=None, radius=None, pad=None,
              fill=None, stroke=None, hover=False, on_click=None):
        """Returns (outer, body). Pack/grid `outer`; put content in `body`.

        rounded=False -> Frame-in-Frame 1-px hairline card. 2 widgets, no
                         redraw cost. Use this in long lists.
        rounded=True  -> RoundedCard canvas. Use for Focus / Stats / Docs.
        """
        T = self.T
        fill   = fill   or T["surface"]
        stroke = stroke or T["hairline"]
        radius = RADIUS if radius is None else radius
        pad    = self._sp(2) if pad is None else self._px(pad)
        if rounded is None:
            rounded = bool(self.cfg.get("ui_rounded", False))

        if rounded:
            outer = RoundedCard(parent, fill, stroke, T["bg"],
                                radius=self._px(radius), pad=pad)
            body  = outer.body
            if hover:
                hf, hs = T["surface_hover"], T["hairline_strong"]
                outer.bind("<Enter>", lambda e: outer.repaint(hf, hs), add="+")
                outer.bind("<Leave>", lambda e: outer.repaint(fill, stroke), add="+")
        else:
            outer = tk.Frame(parent, bg=stroke, bd=0, highlightthickness=0)
            body  = tk.Frame(outer, bg=fill, bd=0, highlightthickness=0)
            body.pack(fill="both", expand=True, padx=1, pady=1)
            if hover:
                self._interactive(body, fill, T["surface_hover"], group=(outer,))
        if on_click:
            for w in (outer, body):
                w.bind("<Button-1>", lambda e: on_click(), add="+")
                try: w.configure(cursor="hand2")
                except Exception: pass
        return outer, body

    def _btn(self, parent, text, command=None, kind="ghost", role="body_str",
             padx=None, pady=None, **kw):
        """kind: primary | accent | ghost | quiet | danger"""
        T = self.T
        table = {
            "primary": (T["accent"], T["on_accent"], T["accent_hi"]),
            "accent":  (T["accent_wash"], T["accent_text"], T["accent_soft"]),
            "ghost":   (T["btn_bg"], T["btn_fg"], T["btn_hover"]),
            "quiet":   (T["bg"], T["muted"], T["surface_hover"]),
            "danger":  (T["surface"], T["danger_text"],
                        mix(T["surface"], T["danger"], .20)),
        }
        bg, fg, hov = table.get(kind, table["ghost"])
        b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                      relief="flat", bd=0, highlightthickness=0, cursor="hand2",
                      font=self._font(role),
                      activebackground=hov, activeforeground=fg,
                      padx=self._sp(3) if padx is None else self._px(padx),
                      pady=self._px(6) if pady is None else self._px(pady), **kw)
        self._interactive(b, bg, hov)
        return b

    def _chip(self, parent, text, tone="neutral", icon=""):
        T = self.T
        tones = {
            "neutral": (T["surface_2"],                       T["muted"]),
            "accent":  (T["accent_wash"],                     T["accent_text"]),
            "success": (mix(T["surface"], T["success"], .16), T["success_text"]),
            "warn":    (mix(T["surface"], T["warning"], .16), T["warning_text"]),
            "danger":  (mix(T["surface"], T["danger"],  .16), T["danger_text"]),
        }
        bg, fg = tones.get(tone, tones["neutral"])
        return tk.Label(parent, text=(icon + " " + text).strip(), bg=bg, fg=fg,
                        font=self._font("caption_str"), bd=0,
                        padx=self._sp(1) + self._px(2), pady=self._px(2))

    def _section(self, parent, title, action=None, action_cmd=None,
                 track=True, pad_top=3):
        """One header for every tab (replaces the four different insets at
        1608 / 2081 / 2763 / 3250). Tk has no letter-spacing, so tracking is
        faked with U+2009 THIN SPACE between characters — the only way to get
        the wide-caps look, and it only reads well on SHORT upper-case labels."""
        T = self.T
        bar = tk.Frame(parent, bg=T["bg"])
        bar.pack(fill="x", padx=self._sp(2), pady=(self._sp(pad_top), self._sp(1)))
        label = title.upper()
        if track: label = " ".join(label)   # U+2009 THIN SPACE
        tk.Label(bar, text=label, bg=T["bg"], fg=T["muted"],
                 font=self._font("caption_str"), anchor="w").pack(side="left")
        if action and action_cmd:
            self._btn(bar, action, action_cmd, kind="accent",
                      role="caption_str", padx=2, pady=3).pack(side="right")
        return bar

    def _meter(self, parent, pct, height=6, color=None, track=None):
        """One meter to replace the four hand-rolled ones (1618 / 1694 / 3277 /
        4930). Redraws on resize; call `.set(pct)` to update in place instead of
        rebuilding the widget."""
        T = self.T
        color = color or T["accent"]
        track = track or T["surface_2"]
        h = self._px(height)
        c = tk.Canvas(parent, bg=T["bg"], bd=0, highlightthickness=0,
                      height=h, takefocus=0)
        c._pct = max(0.0, min(1.0, float(pct)))
        r = h / 2.0
        def draw(_e=None):
            w = c.winfo_width()
            if w < 4: return
            c.delete("all")
            c.create_polygon(*round_rect_pts(0, 0, w, h, r),
                             fill=track, outline=track, smooth=True)
            fw = w * c._pct
            if fw >= 2:
                c.create_polygon(*round_rect_pts(0, 0, max(fw, h), h, r),
                                 fill=color, outline=color, smooth=True)
        c.bind("<Configure>", draw, add="+")
        def _set(p):
            c._pct = max(0.0, min(1.0, float(p))); draw()
        c.set = _set
        return c

    def _empty(self, parent, glyph, headline, sub="", cta=None, cta_cmd=None):
        """Icon + headline + muted subline + a REAL button wired to the same
        command as the toolbar control the old text merely pointed at."""
        T = self.T
        box = tk.Frame(parent, bg=T["bg"])
        box.pack(fill="x", pady=self._sp(6))
        tk.Label(box, text=glyph, bg=T["bg"], fg=T["hairline_strong"],
                 font=self._font("hero")).pack()
        tk.Label(box, text=headline, bg=T["bg"], fg=T["text"],
                 font=self._font("body_str")).pack(pady=(self._sp(2), 0))
        if sub:
            tk.Label(box, text=sub, bg=T["bg"], fg=T["muted"],
                     font=self._font("caption"), justify="center").pack()
        if cta and cta_cmd:
            self._btn(box, cta, cta_cmd, kind="primary").pack(pady=(self._sp(3), 0))
        return box

    # ── tab strip ────────────────────────────────────────────────────────────
    def _mktab(self, parent, text, cmd, compact=False):
        """REPLACES the old _mktab. Returns the HOLDER frame — the pack /
        pack_forget calls in _refresh_tabs keep working on it unchanged; only
        the two `tab.configure(bg=..., fg=...)` lines become _paint_tab().

        BEFORE  selection = one bg swap, same fg for both states. Measured
                1.04 on `light`, under 1.31 on nine themes: on a third of the
                palette you cannot see which tab you are on.
        AFTER   inactive = muted label on tab_bg; active = full-strength label
                on `surface` with a 2-px `accent_ind` underline, guaranteed
                >= 3.08 contrast against tab_bg on every one of the 27 themes.
                Hover now lifts the label (Tk's activebackground never did).
        """
        T = self.T
        holder = tk.Frame(parent, bg=T["tab_bg"])
        # C8: identical to the values _refresh_tabs re-packs the flipped
        # archive/priorities tab with, so all tabs stay on the same offset.
        holder.pack(side="left", padx=(6, 0), pady=4)
        b = tk.Button(holder, text=text, command=cmd,
                      bg=T["tab_bg"], fg=T["muted"], relief="flat", bd=0,
                      highlightthickness=0, cursor="hand2",
                      padx=self._sp(2) if compact else self._sp(3),
                      pady=self._px(5), font=self._font("caption_str"),
                      activebackground=T["tab_hover"], activeforeground=T["text"])
        b.pack(fill="x")
        ind = tk.Frame(holder, bg=T["tab_bg"], height=self._px(2))
        ind.pack(fill="x", pady=(self._px(3), 0))
        holder.btn, holder.ind, holder.compact = b, ind, compact
        b._active = False
        b.bind("<Enter>", lambda e: None if b._active else
               b.configure(fg=self.T["text"], bg=self.T["tab_hover"]), add="+")
        b.bind("<Leave>", lambda e: None if b._active else
               b.configure(fg=self.T["muted"], bg=self.T["tab_bg"]), add="+")
        return holder

    def _paint_tab(self, tab, active):
        T = self.T
        b, ind = tab.btn, tab.ind
        b._active = active
        tab.configure(bg=T["tab_bg"])
        b.configure(bg=T["surface"] if active else T["tab_bg"],
                    fg=T["text"] if active else T["muted"],
                    activebackground=T["surface"] if active else T["tab_hover"],
                    font=self._font("caption_str"))
        ind.configure(bg=T["accent_ind"] if active else T["tab_bg"])

    # ── task row shell ───────────────────────────────────────────────────────
    def _task_shell(self, parent, priority="none", done=False):
        """Drop-in replacement for the first 8 lines of _task_row (3504-3512).

        BEFORE  wrapper = tk.Frame(bg=item_bg) packed on bg — measured contrast
                1.02-1.11, i.e. no visible card at all; a 5-px priority bar
                .place()d on top of it, kept in sync by a per-row <Configure>
                handler with two magic pads, plus row.pack_configure(padx=(9,4))
                to stop the bar covering the checkbox.
        AFTER   a hairline card (2 frames, 1.31 edge contrast on every theme)
                whose priority rail is a PACKED column: it fills to the row
                height for free and can never overlap the checkbox, so
                `_update_bar`, `wrapper.bind("<Configure>", _update_bar)` and the
                padx fudge are all deleted — one closure and one binding fewer
                per row, on exactly the render path the user complains about.
                Hover is one _interactive() call instead of the paint() closure.

        Returns (outer, body, content). Pack the old `row` / `tw` into `content`.
        """
        T = self.T
        outer, body = self._card(parent, rounded=False, hover=True)
        outer.pack(fill="x", pady=self._px(2))
        rail = T.get(priority, T["hairline"]) if priority != "none" else T["hairline"]
        bar = tk.Frame(body, width=self._px(3), bg=rail)
        bar.pack(side="left", fill="y")
        content = tk.Frame(body, bg=T["surface"])
        content.pack(side="left", fill="both", expand=True)
        outer._pri_bar = bar          # _cycle_priority: outer._pri_bar.configure(bg=...)
        return outer, body, content

    # ══════════════════════════════════════════════════════════════════════════
    # RECURRING — engine wiring (timer, catch-up, notification)
    # ══════════════════════════════════════════════════════════════════════════

    def _rec_init(self):
        """Call once at the end of __init__ (after _build_ui)."""
        self.cfg.setdefault("rec_sound", False)       # OFF by default: no audible surprise
        self.cfg.setdefault("rec_toast", True)
        self.cfg.setdefault("rec_tray_balloon", True)
        self.cfg.setdefault("rec_sound_file", "workstart.wav")
        self._rec_stop        = False
        self._rec_job         = None
        self._rec_quiet_until = None   # datetime; tick is a no-op until then
        self._rec_last_focus  = 0.0
        self._rec_badge       = None
        self._rec_pending     = 0
        self.root.bind("<FocusIn>", self._rec_on_focus, add="+")
        self.root.after(400, lambda: self._rec_catch_up(render=True))
        # C5: no second timer. _maintenance_tick (stage 5) is the single
        # 60s clock and calls _rec_catch_up() itself.

    def _rec_on_focus(self, e=None):
        """Window regained focus (also covers wake-from-sleep where after() drifts)."""
        if getattr(e, "widget", None) is not self.root: return
        now = now_dt().timestamp()
        if now - getattr(self, "_rec_last_focus", 0.0) < 30: return
        self._rec_last_focus = now
        self._rec_quiet_until = None
        try: self._rec_catch_up(render=True)
        except Exception: pass

    def _rec_task_keys(self):
        """Materialization keys already present in self.tasks (2nd idempotency guard)."""
        keys = set()
        for t in self.tasks:
            rid = t.get("rec_id")
            if rid: keys.add(rec_occ_key(rid, t.get("rec_date", "")))
        return keys

    def _rec_catch_up(self, render=False):
        """Idempotent. Safe to call as often as you like — the expensive path only
        runs when a rule actually crossed an occurrence boundary."""
        now = now_dt()
        qu  = getattr(self, "_rec_quiet_until", None)
        if qu and now < qu:
            return 0
        today = now.date()
        data  = load_recurring()                       # cached: no disk read
        rules = data.get("rules", [])
        if not rules:
            self._rec_quiet_until = now + datetime.timedelta(minutes=10)
            return 0

        spawns, updates, fired = rec_catch_up_plan(
            rules, today, self._rec_task_keys(), data.get("log", {}))

        if not spawns and not updates:
            # nothing until at least tomorrow -> sleep the tick until 00:01
            self._rec_quiet_until = datetime.datetime.combine(
                today + datetime.timedelta(days=1), datetime.time(0, 1))
            self._rec_update_badge()
            return 0
        self._rec_quiet_until = None

        by_id = {r.get("id"): r for r in rules}
        made  = []
        for sp in spawns:
            if sp.get("mode") != "task":
                continue
            iso   = sp["date"].isoformat()
            title = sp["title"]
            if sp.get("missed"):
                title = "%s  (+%d missed)" % (title, sp["missed"])
            t = _norm({
                "id":       str(uuid.uuid4()),
                "text":     title,
                "done":     False,
                "created":  now.isoformat(timespec="seconds"),
                "priority": sp.get("priority", "none"),
                "subtasks": [],
                "rec_id":   sp["rule_id"],
                "rec_date": iso,
                "due_date": iso,
                "due_time": sp.get("time", ""),
                # Opt out of the existing due-day priority ratchet at lines 929-930:
                # a weekly task must not creep one notch closer to "high" every week.
                "due_jumped":       True,
                "scheduled_jumped": True,
            })
            self.tasks.insert(0, t)
            made.append(t)

        for rid, patch in updates.items():
            r = by_id.get(rid)
            if r: r.update(patch)

        if made:
            save_tasks(self.tasks)
        save_recurring(data)

        if fired:
            self._rec_notify([by_id[i] for i in fired if i in by_id], len(made))
        self._rec_update_badge()
        if render and self.current_tab in ("active", "habits"):
            self._render_tasks_debounced(60)
        return len(made)

    # ── notification surfaces ────────────────────────────────────────────────
    def _rec_notify(self, rules, n_tasks):
        if not rules: return
        first = rules[0].get("title", "Reminder")
        body  = first if len(rules) == 1 else "%s  +%d more" % (first, len(rules) - 1)
        hidden = True
        try: hidden = (self.root.state() == "withdrawn") or not self.root.winfo_viewable()
        except Exception: pass

        if self.cfg.get("rec_sound", False):
            try: self._pomo_sound(self.cfg.get("rec_sound_file", "workstart.wav"))
            except Exception: pass

        if hidden and self.cfg.get("rec_tray_balloon", True) and self._tray_icon:
            try:
                self._tray_icon.notify(body, "LeoNote — due now")
                return
            except Exception:
                pass                                    # backend has no balloon: fall through

        if not hidden and self.cfg.get("rec_toast", True):
            self._rec_toast(body)

    def _rec_toast(self, msg):
        """Borderless self-dismissing toast — same shape as _pomo_skip's popup (4624-4666)."""
        T = self.T
        try:
            w = tk.Toplevel(self.root)
            w.overrideredirect(True)
            w.attributes("-topmost", True)
            w.configure(bg=T["header_bg"])
            f = tk.Frame(w, bg=T["item_bg"], padx=12, pady=8)
            f.pack(padx=1, pady=1)
            tk.Label(f, text="🔔  " + msg, bg=T["item_bg"], fg=T["text"],
                font=(self.cfg.get("ui_font", "Segoe UI Variable"), 9, "bold")).pack()
            w.update_idletasks()
            x = self.root.winfo_rootx() + max(0, self.root.winfo_width() - w.winfo_width() - 14)
            y = self.root.winfo_rooty() + max(0, self.root.winfo_height() - w.winfo_height() - 40)
            w.geometry("+%d+%d" % (x, y))
            w.bind("<Button-1>", lambda e: (self._set_tab("habits"), w.destroy()))
            self.root.after(3500, lambda: w.winfo_exists() and w.destroy())
        except Exception:
            pass

    def _rec_update_badge(self):
        """Status-bar pill: '🔔 2'. Created lazily so _build_ui is left untouched."""
        try:
            today = datetime.date.today()
            data  = load_recurring()
            open_ids, n = set(), 0
            for t in self.tasks:
                if t.get("rec_id") and not t.get("done") and not t.get("deleted"):
                    open_ids.add(t["rec_id"]); n += 1
            for r in data.get("rules", []):
                if r.get("deleted") or not r.get("active", True): continue
                if r.get("id") in open_ids: continue      # already counted as a task
                d, _over = rec_next_due(r, today)
                if d is not None and d <= today: n += 1
            self._rec_pending = n
            b = getattr(self, "_rec_badge", None)
            if b is None or not b.winfo_exists():
                if not n: return
                parent = self.status_lbl.master
                b = tk.Label(parent, text="", bg=self.T["header_bg"], fg=self.T["archive"],
                    font=(self.cfg.get("ui_font", "Segoe UI Variable"), 8, "bold"),
                    padx=6, pady=4, cursor="hand2")
                b.bind("<Button-1>", lambda e: self._set_tab("habits"))
                self._rec_badge = b
            if n:
                b.configure(text="🔔 %d" % n, bg=self.T["header_bg"], fg=self.T["archive"])
                if not b.winfo_ismapped(): b.pack(side="right")
            else:
                if b.winfo_ismapped(): b.pack_forget()
        except Exception:
            pass

    def _rec_cancel(self):
        """Call from _close() next to the pomodoro after_cancel block."""
        self._rec_stop = True
        job = getattr(self, "_rec_job", None)
        if job:
            try: self.root.after_cancel(job)
            except Exception: pass
        self._rec_job = None

    # ── XP, awarded once per (rule, occurrence) ──────────────────────────────
    def _rec_award(self, rid, iso, amount=10):
        """The completion log IS the ledger: no entry -> award, entry -> no-op.
        This is the only place recurring XP is granted — see the drift note in risks."""
        if not rid or not iso: return False
        data = load_recurring()
        lst  = data.setdefault("log", {}).setdefault(rid, [])
        if iso in lst:
            return False
        lst.append(iso)
        if amount:
            self.cfg["xp"] = self.cfg.get("xp", 0) + amount
            self._save_cfg_debounced(200)
        save_recurring(data)
        return True

    def _rec_unaward(self, rid, iso, amount=10):
        if not rid or not iso: return False
        data = load_recurring()
        lst  = data.setdefault("log", {}).setdefault(rid, [])
        if iso not in lst:
            return False
        lst.remove(iso)
        if amount:
            self.cfg["xp"] = max(0, self.cfg.get("xp", 0) - amount)
            self._save_cfg_debounced(200)
        save_recurring(data)
        return True

    # ── row actions ──────────────────────────────────────────────────────────
    def _rec_mark_done(self, rid):
        """Complete THIS occurrence. Resolves 'today' at CLICK time, never at render
        time — toggle_habit's closed-over `today` (3247 -> 3348) is exactly that bug."""
        today = datetime.date.today()
        data  = load_recurring()
        r = next((x for x in data.get("rules", []) if x.get("id") == rid), None)
        if not r: return
        # An open spawned task pins WHICH occurrence this click closes; otherwise use
        # the pending one; a future-only rule is refused.
        occ  = None
        open_t = [t for t in self.tasks
                  if t.get("rec_id") == rid and t.get("rec_date")
                  and not t.get("done") and not t.get("deleted")]
        if open_t:
            open_t.sort(key=lambda t: t.get("rec_date", ""))
            occ = _rec_date(open_t[0]["rec_date"])
        if occ is None:
            d, _over = rec_next_due(r, today)
            if d is None or d > today:
                return          # nothing pending — refuse (this is the XP-farm guard)
            occ = d
        iso = occ.isoformat()
        if iso in data.setdefault("log", {}).setdefault(rid, []):
            return                          # this occurrence is already completed
        lf = _rec_date(r.get("last_fired"))
        if lf is None or occ > lf:
            r["last_fired"] = iso           # done early -> do not fire again for this one
        r["snooze_until"] = None
        closed = False
        for t in open_t:
            if t.get("rec_date") == iso:
                t["done"] = True
                t["completed_at"] = now_dt().isoformat(timespec="seconds")
                self.cfg["tasks_done"] = self.cfg.get("tasks_done", 0) + 1
                self.cfg["xp"] = self.cfg.get("xp", 0) + 15    # same rate as _toggle
                save_tasks(self.tasks)
                closed = True
                break
        # ledger entry always; XP only when no task has already paid for it
        self._rec_award(rid, iso, amount=(0 if closed else 10))
        save_recurring(data)
        self._rec_quiet_until = None
        self._rec_update_badge()
        self._render_tasks_debounced(30)

    def _rec_snooze(self, rid, days=1):
        today = datetime.date.today()
        data  = load_recurring()
        r = next((x for x in data.get("rules", []) if x.get("id") == rid), None)
        if not r: return
        r["snooze_until"] = (today + datetime.timedelta(days=days - 1)).isoformat() \
            if days > 1 else today.isoformat()
        save_recurring(data)
        self._rec_quiet_until = None
        self._rec_update_badge()
        self._render_tasks_debounced(30)

    def _rec_skip_next(self, rid):
        """Wave off the pending occurrence — it will not fire and will not count
        against the streak's denominator."""
        today = datetime.date.today()
        data  = load_recurring()
        r = next((x for x in data.get("rules", []) if x.get("id") == rid), None)
        if not r: return
        d, _over = rec_next_due(r, today)
        if d is None: return
        iso = d.isoformat()
        if iso not in r.setdefault("skip", []):
            r["skip"].append(iso)
        r["skip"] = r["skip"][-60:]
        lf = _rec_date(r.get("last_fired"))
        if d <= today and (lf is None or d > lf):
            r["last_fired"] = iso
        save_recurring(data)
        self._rec_quiet_until = None
        self._rec_update_badge()
        self._render_tasks_debounced(30)

    def _rec_toggle_active(self, rid):
        data = load_recurring()
        r = next((x for x in data.get("rules", []) if x.get("id") == rid), None)
        if not r: return
        r["active"] = not r.get("active", True)
        save_recurring(data)
        self._rec_quiet_until = None
        self._render_tasks_debounced(30)

    def _rec_delete(self, rid):
        """Soft delete — mirrors habits so a mis-click is recoverable from the file."""
        data = load_recurring()
        r = next((x for x in data.get("rules", []) if x.get("id") == rid), None)
        if not r: return
        r["deleted"] = True
        r["deleted_at"] = now_dt().isoformat(timespec="seconds")
        r["active"] = False
        save_recurring(data)
        self._rec_update_badge()
        self._render_tasks_debounced(30)

    # ══════════════════════════════════════════════════════════════════════════
    # RECURRING — render (appended at the bottom of the Habits tab)
    # ══════════════════════════════════════════════════════════════════════════

    def _render_recurring(self, T):
        """Called from the END of _render_habits. Purely additive: it does not read
        or touch the habits file, the habit loop, or any habit helper."""
        fnt   = self.cfg.get("ui_font", "Segoe UI Variable")
        data  = load_recurring()                       # cached: no disk read
        rules = [r for r in data.get("rules", []) if not r.get("deleted")]
        log   = data.get("log", {})
        today = datetime.date.today()

        tk.Frame(self.task_frame, bg=T["separator"], height=1).pack(fill="x", pady=(10, 6), padx=2)

        hdr = tk.Frame(self.task_frame, bg=T["bg"]); hdr.pack(fill="x", padx=6, pady=(0, 4))
        tk.Label(hdr, text="🔁  Recurring", bg=T["bg"], fg=T["text"],
            font=(fnt, 11, "bold")).pack(side="left")
        tk.Button(hdr, text="+ Recurring", command=lambda: self._rec_dialog(None),
            bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=(fnt, 9),
            padx=8, pady=3, cursor="hand2", activebackground=T["btn_hover"]).pack(side="right")

        if not rules:
            tk.Label(self.task_frame,
                text="Nothing repeating yet.\ne.g. \"check marketplace sales\" every Tuesday",
                bg=T["bg"], fg=T["muted"], font=(fnt, 9), justify="center",
                pady=18).pack(fill="x")
            return

        # order: overdue first, then due today, then by next date
        def _sort_key(r):
            d, over = rec_next_due(r, today)
            if d is None:  return (3, datetime.date.max)
            if over:       return (0, d)
            if d == today: return (1, d)
            return (2, d)
        for r in sorted(rules, key=_sort_key):
            self._rec_row(T, r, log, today)

    def _rec_row(self, T, r, log, today):
        fnt = self.cfg.get("ui_font", "Segoe UI Variable")
        rid = r.get("id")
        d, overdue = rec_next_due(r, today)
        active  = r.get("active", True)
        due_now = active and d is not None and d <= today
        streak  = rec_streak(r, log, today)
        hits, tot = rec_rate(r, log, today, window=8)

        card = tk.Frame(self.task_frame, bg=T["item_bg"], pady=5, padx=8)
        card.pack(fill="x", pady=2)
        top = tk.Frame(card, bg=T["item_bg"]); top.pack(fill="x")

        pip = "🔥 %d" % streak if streak else "🔁"
        tk.Label(top, text=pip, bg=T["item_bg"],
            fg=(T["check_done"] if streak else T["muted"]),
            font=(fnt, 9, "bold"), width=5, anchor="w").pack(side="left")

        title_wrap = tk.Frame(top, bg=T["item_bg"]); title_wrap.pack(side="left", fill="x", expand=True)
        name = tk.Label(title_wrap, text=r.get("title", ""), bg=T["item_bg"],
            fg=(T["text"] if active else T["muted"]), font=(fnt, 10), anchor="w", justify="left")
        name.pack(anchor="w", fill="x")
        name.bind("<Double-Button-1>", lambda e, i=rid: self._rec_dialog(i))

        # right-hand buttons (packed right-to-left)
        del_b = tk.Button(top, text="✕", bg=T["item_bg"], fg=T["muted"], relief="flat", bd=0,
            padx=4, font=(fnt, 8), cursor="hand2", activebackground=T["item_hover"])
        del_b._confirm = False
        def _del(b=del_b, i=rid):
            if not b._confirm:
                b._confirm = True
                b.configure(text="sure?", fg=T["close_hover"])
                self.root.after(2600, lambda: (b.winfo_exists() and b._confirm and
                    (setattr(b, "_confirm", False), b.configure(text="✕", fg=T["muted"]))))
                return
            self._rec_delete(i)
        del_b.configure(command=_del)
        del_b.pack(side="right")

        tk.Button(top, text="⋯", command=lambda i=rid: self._rec_dialog(i),
            bg=T["item_bg"], fg=T["muted"], relief="flat", bd=0, padx=4,
            font=(fnt, 9), cursor="hand2", activebackground=T["item_hover"]).pack(side="right")

        if due_now:
            tk.Button(top, text="✓ Done", command=lambda i=rid: self._rec_mark_done(i),
                bg=T["check_done"], fg="#ffffff", relief="flat", font=(fnt, 9),
                padx=8, pady=3, cursor="hand2",
                activebackground=T["btn_hover"]).pack(side="right", padx=(0, 6))
            tk.Button(top, text="⏰", command=lambda i=rid: self._rec_snooze(i, 1),
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=(fnt, 8),
                padx=5, pady=3, cursor="hand2",
                activebackground=T["btn_hover"]).pack(side="right", padx=(0, 4))
            tk.Button(top, text="↷", command=lambda i=rid: self._rec_skip_next(i),
                bg=T["btn_bg"], fg=T["btn_fg"], relief="flat", font=(fnt, 8),
                padx=5, pady=3, cursor="hand2",
                activebackground=T["btn_hover"]).pack(side="right", padx=(0, 4))
        else:
            tk.Button(top, text=("on" if active else "off"),
                command=lambda i=rid: self._rec_toggle_active(i),
                bg=(T["btn_bg"] if active else T["separator"]), fg=T["btn_fg"],
                relief="flat", font=(fnt, 8), padx=6, pady=3, cursor="hand2",
                activebackground=T["btn_hover"]).pack(side="right", padx=(0, 6))

        # meta line: cadence · next: Tue 3 Sep · 6/8
        if not active:
            nxt, col = "paused", T["muted"]
        elif d is None:
            nxt, col = "finished", T["muted"]
        elif overdue:
            nxt, col = "overdue · was %s" % rec_fmt_date(d, today), T["high"]
        elif d == today:
            nxt, col = "due today", T["check_done"]
        else:
            nxt, col = "next: %s" % rec_fmt_date(d, today), T["muted"]
        sn = _rec_date(r.get("snooze_until"))
        if sn and sn >= today and active:
            nxt, col = "snoozed → %s" % rec_fmt_date(sn + datetime.timedelta(days=1), today), T["medium"]

        meta = tk.Frame(card, bg=T["item_bg"]); meta.pack(fill="x", pady=(1, 0))
        tk.Label(meta, text="     " + rec_describe(r), bg=T["item_bg"], fg=T["muted"],
            font=(fnt, 8)).pack(side="left")
        tk.Label(meta, text="  ·  " + nxt, bg=T["item_bg"], fg=col,
            font=(fnt, 8, "bold")).pack(side="left")
        if tot:
            tk.Label(meta, text="%d/%d" % (hits, tot), bg=T["item_bg"], fg=T["muted"],
                font=(fnt, 8)).pack(side="right")

    # ══════════════════════════════════════════════════════════════════════════
    # RECURRING — add / edit dialog
    # ══════════════════════════════════════════════════════════════════════════

    def _rec_dialog(self, rid=None):
        T     = self.T
        fnt   = self.cfg.get("ui_font", "Segoe UI Variable")
        data  = load_recurring()
        today = datetime.date.today()
        editing = None
        if rid:
            editing = next((x for x in data.get("rules", []) if x.get("id") == rid), None)
        draft = _rec_norm(dict(editing) if editing else
                          {"title": "", "anchor": today.isoformat(),
                           "rule": {"kind": "weekly", "days": [today.weekday()], "interval": 1}})

        win = tk.Toplevel(self.root)
        win.title("Recurring")
        win.configure(bg=T["bg"])
        win.attributes("-topmost", True)
        win.transient(self.root)
        win.resizable(False, False)

        body = tk.Frame(win, bg=T["bg"], padx=14, pady=12); body.pack(fill="both", expand=True)

        def _lbl(txt, parent=None):
            tk.Label(parent or body, text=txt, bg=T["bg"], fg=T["muted"],
                font=(fnt, 8, "bold"), anchor="w").pack(fill="x", pady=(8, 2))

        _lbl("What repeats?")
        title_var = tk.StringVar(value=draft.get("title", ""))
        ent = tk.Entry(body, textvariable=title_var, bg=T["entry_bg"], fg=T["entry_fg"],
            insertbackground=T["entry_fg"], relief="flat", font=(fnt, 10),
            highlightthickness=1, highlightbackground=T["separator"], width=34)
        ent.pack(fill="x", ipady=4)
        ent.focus_set()

        _lbl("Repeats")
        kind_var = tk.StringVar(value=draft["rule"]["kind"])
        krow = tk.Frame(body, bg=T["bg"]); krow.pack(fill="x")

        wk_frame  = tk.Frame(body, bg=T["bg"])
        day_state = {i: (i in draft["rule"].get("days", [])) for i in range(7)}
        chips     = {}
        int_frame = tk.Frame(body, bg=T["bg"])
        int_var   = tk.StringVar(value=str(draft["rule"].get("interval", 1)))
        dom_frame = tk.Frame(body, bg=T["bg"])
        dom_var   = tk.StringVar(value=str(draft["rule"].get("day", today.day)))

        anchor_state = [_rec_date(draft.get("anchor")) or today]
        time_var   = tk.StringVar(value=draft.get("time", ""))
        pri_var    = tk.StringVar(value=draft.get("priority", "none"))
        mode_var   = tk.StringVar(value=draft.get("mode", "task"))
        cu_var     = tk.StringVar(value=draft.get("catchup", "collapse"))
        notify_var = tk.BooleanVar(value=bool(draft.get("notify", True)))

        preview = tk.Label(body, text="", bg=T["bg"], fg=T["check_done"],
            font=(fnt, 9, "bold"), anchor="w", justify="left", wraplength=300)

        def _collect():
            """Build a normalized rule dict from the current widget state."""
            k = kind_var.get()
            try: iv = max(1, min(52, int(int_var.get() or 1)))
            except Exception: iv = 1
            try: dm = max(1, min(31, int(dom_var.get() or 1)))
            except Exception: dm = 1
            rule = {"kind": k, "interval": iv}
            if k == "weekly":
                rule["days"] = [i for i in range(7) if day_state[i]] or [anchor_state[0].weekday()]
            elif k == "monthly":
                rule["day"] = dm
            out = dict(draft)
            out.update({
                "title":    title_var.get().strip() or "Recurring task",
                "rule":     rule,
                "anchor":   anchor_state[0].isoformat(),
                "time":     time_var.get().strip(),
                "priority": pri_var.get(),
                "mode":     mode_var.get(),
                "catchup":  cu_var.get(),
                "notify":   bool(notify_var.get()),
            })
            return _rec_norm(out)

        def _refresh(*_a):
            k = kind_var.get()
            for f in (wk_frame, int_frame, dom_frame):
                f.pack_forget()
            if k != "once":     int_frame.pack(fill="x", pady=(4, 0))
            if k == "weekly":   wk_frame.pack(fill="x", pady=(6, 0))
            if k == "monthly":  dom_frame.pack(fill="x", pady=(6, 0))
            nxt = next_occurrences(_collect(), today, 3)
            if nxt:
                preview.configure(
                    text="Next:  " + " · ".join(rec_fmt_date(x, today) for x in nxt),
                    fg=T["check_done"])
            else:
                preview.configure(text="Never occurs — check the start date.", fg=T["high"])

        for key, label in (("daily", "Every N days"), ("weekly", "Weekly"),
                           ("monthly", "Monthly"), ("once", "Once")):
            tk.Radiobutton(krow, text=label, value=key, variable=kind_var,
                bg=T["bg"], fg=T["text"], selectcolor=T["entry_bg"],
                activebackground=T["bg"], font=(fnt, 9), command=_refresh
            ).pack(side="left", padx=(0, 6))

        tk.Label(int_frame, text="every", bg=T["bg"], fg=T["muted"], font=(fnt, 9)).pack(side="left")
        tk.Spinbox(int_frame, from_=1, to=52, width=3, textvariable=int_var,
            bg=T["entry_bg"], fg=T["entry_fg"], relief="flat", font=(fnt, 9),
            command=_refresh).pack(side="left", padx=4)
        int_unit = tk.Label(int_frame, text="", bg=T["bg"], fg=T["muted"], font=(fnt, 9))
        int_unit.pack(side="left")
        int_var.trace_add("write", lambda *a: (int_unit.configure(
            text={"daily": "day(s)", "weekly": "week(s)", "monthly": "month(s)"}
                 .get(kind_var.get(), "")), _refresh()))

        for i, nm in enumerate(REC_WD_SHORT):
            def _tog(i=i):
                day_state[i] = not day_state[i]
                c = chips[i]
                c.configure(bg=(T["check_done"] if day_state[i] else T["item_bg"]),
                            fg=("#ffffff" if day_state[i] else T["muted"]))
                _refresh()
            c = tk.Button(wk_frame, text=nm, command=_tog, width=3, relief="flat",
                font=(fnt, 8, "bold"), cursor="hand2", padx=2, pady=3,
                bg=(T["check_done"] if day_state[i] else T["item_bg"]),
                fg=("#ffffff" if day_state[i] else T["muted"]),
                activebackground=T["btn_hover"])
            c.pack(side="left", padx=1)
            chips[i] = c

        tk.Label(dom_frame, text="on day", bg=T["bg"], fg=T["muted"], font=(fnt, 9)).pack(side="left")
        tk.Spinbox(dom_frame, from_=1, to=31, width=3, textvariable=dom_var,
            bg=T["entry_bg"], fg=T["entry_fg"], relief="flat", font=(fnt, 9),
            command=_refresh).pack(side="left", padx=4)
        tk.Label(dom_frame, text="(31 = last day of every month)", bg=T["bg"],
            fg=T["muted"], font=(fnt, 8)).pack(side="left")
        dom_var.trace_add("write", lambda *a: _refresh())

        _lbl("Starts")
        drow = tk.Frame(body, bg=T["bg"]); drow.pack(fill="x")
        date_btn = tk.Button(drow, text="", bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            font=(fnt, 9), padx=8, pady=3, cursor="hand2", activebackground=T["btn_hover"])
        def _pick():
            def _on(sel):
                d = sel[0] if isinstance(sel, tuple) else sel
                anchor_state[0] = d
                date_btn.configure(text=d.strftime("%d.%m.%Y"))
                _refresh()
            self._show_calendar_picker(date_btn, anchor_state[0], _on)
        date_btn.configure(text=anchor_state[0].strftime("%d.%m.%Y"), command=_pick)
        date_btn.pack(side="left")
        tk.Label(drow, text="  at", bg=T["bg"], fg=T["muted"], font=(fnt, 9)).pack(side="left")
        tk.Entry(drow, textvariable=time_var, width=6, bg=T["entry_bg"], fg=T["entry_fg"],
            relief="flat", font=(fnt, 9), highlightthickness=1,
            highlightbackground=T["separator"]).pack(side="left", padx=4, ipady=2)
        tk.Label(drow, text="HH:MM (optional)", bg=T["bg"], fg=T["muted"],
            font=(fnt, 8)).pack(side="left")

        preview.pack(fill="x", pady=(10, 2))

        # options (folded away — the defaults are right for almost everyone)
        adv_open = [False]
        adv = tk.Frame(body, bg=T["bg"])
        adv_lbl = tk.Label(body, text="▸ Options", bg=T["bg"], fg=T["muted"],
            font=(fnt, 8, "bold"), anchor="w", cursor="hand2")
        adv_lbl.pack(fill="x", pady=(8, 0))
        def _toggle_adv(e=None):
            adv_open[0] = not adv_open[0]
            if adv_open[0]:
                adv.pack(fill="x", pady=(4, 0)); adv_lbl.configure(text="▾ Options")
            else:
                adv.pack_forget(); adv_lbl.configure(text="▸ Options")
        adv_lbl.bind("<Button-1>", _toggle_adv)

        o1 = tk.Frame(adv, bg=T["bg"]); o1.pack(fill="x", pady=2)
        tk.Label(o1, text="Creates", bg=T["bg"], fg=T["muted"], font=(fnt, 8),
            width=10, anchor="w").pack(side="left")
        for v, lab in (("task", "a real task"), ("reminder", "reminder only")):
            tk.Radiobutton(o1, text=lab, value=v, variable=mode_var, bg=T["bg"], fg=T["text"],
                selectcolor=T["entry_bg"], activebackground=T["bg"],
                font=(fnt, 8)).pack(side="left", padx=(0, 6))

        o2 = tk.Frame(adv, bg=T["bg"]); o2.pack(fill="x", pady=2)
        tk.Label(o2, text="Priority", bg=T["bg"], fg=T["muted"], font=(fnt, 8),
            width=10, anchor="w").pack(side="left")
        ttk.Combobox(o2, textvariable=pri_var, state="readonly", width=8,
            values=["none", "low", "medium", "high"]).pack(side="left")

        o3 = tk.Frame(adv, bg=T["bg"]); o3.pack(fill="x", pady=2)
        tk.Label(o3, text="If missed", bg=T["bg"], fg=T["muted"], font=(fnt, 8),
            width=10, anchor="w").pack(side="left")
        ttk.Combobox(o3, textvariable=cu_var, state="readonly", width=22,
            values=["collapse", "all", "skip"]).pack(side="left")
        tk.Label(adv, text="collapse = one task for the newest missed date (recommended)\n"
                           "all = one task per missed date   ·   skip = only fire on the day",
            bg=T["bg"], fg=T["muted"], font=(fnt, 7), justify="left",
            anchor="w").pack(fill="x", pady=(2, 4))

        tk.Checkbutton(adv, text="Notify me (badge / toast / tray)", variable=notify_var,
            bg=T["bg"], fg=T["text"], selectcolor=T["entry_bg"], activebackground=T["bg"],
            font=(fnt, 8), anchor="w").pack(fill="x")

        btns = tk.Frame(body, bg=T["bg"]); btns.pack(fill="x", pady=(12, 0))
        def _save():
            out = _collect()
            if editing:
                editing.update(out)
                editing["snooze_until"] = None      # a cadence edit clears the snooze
            else:
                out["created"]    = today.isoformat()
                out["last_fired"] = None
                data.setdefault("rules", []).append(out)
            save_recurring(data)
            self._rec_quiet_until = None
            win.destroy()
            self._rec_catch_up(render=False)
            self._rec_update_badge()
            self._render_tasks_debounced(30)
        tk.Button(btns, text="Save", command=_save, bg=T["check_done"], fg="#ffffff",
            relief="flat", font=(fnt, 9, "bold"), padx=14, pady=4,
            cursor="hand2").pack(side="right")
        tk.Button(btns, text="Cancel", command=win.destroy, bg=T["btn_bg"], fg=T["btn_fg"],
            relief="flat", font=(fnt, 9), padx=10, pady=4,
            cursor="hand2").pack(side="right", padx=(0, 6))

        ent.bind("<Return>", lambda e: _save())
        win.bind("<Escape>", lambda e: win.destroy())
        kind_var.trace_add("write", lambda *a: _refresh())
        _refresh()
        win.update_idletasks()
        win.geometry("+%d+%d" % (self.root.winfo_rootx() + 30, self.root.winfo_rooty() + 60))

    # ── debounced work (coalesce bursts into one job) ─────────────────────────
    def _save_cfg_debounced(self, delay=500):
        """Settings entries fire trace_add on every keystroke - one write per pause."""
        job = getattr(self, "_save_cfg_job", None)
        if job:
            try: self.root.after_cancel(job)
            except Exception: pass
        self._save_cfg_job = self.root.after(delay, lambda: save_config(self.cfg))

    def _render_tasks_debounced(self, delay=30):
        """Coalesce list rebuilds - search fires on every KeyRelease."""
        job = getattr(self, "_render_job", None)
        if job:
            try: self.root.after_cancel(job)
            except Exception: pass
        self._render_job = self.root.after(delay, self._render_tasks)

    def _on_configure(self, e=None):
        if e and e.widget==self.root and not self._is_maximized:
            self.cfg.update(window_x=self.root.winfo_x(),window_y=self.root.winfo_y(),
                window_w=self.root.winfo_width(),window_h=self.root.winfo_height())
            if hasattr(self,"_save_cfg_job"): self.root.after_cancel(self._save_cfg_job)
            self._save_cfg_job = self.root.after(500, lambda: save_config(self.cfg))

    def _keep_settings_alive(self):
        if self._settings_win and self._settings_win.winfo_exists():
            try:
                self._settings_win.deiconify()  # restores if minimized
                self._settings_win.state("normal")
                self._settings_win.lift()
                self._settings_win.focus_force()
                self._settings_win.attributes("-topmost", True)
            except Exception: pass


    # ══════════════════════════════════════════════════════════════════════════
    # POMODORO
    # ══════════════════════════════════════════════════════════════════════════

    def _pomo_init_mixer(self):
        pass  # no-op: using winsound (built-in, no dependencies)

    def _pomo_sound(self, name, volume=0.8):
        """Play sounds/<name>.wav non-blocking using winsound (built-in, Windows only)."""
        import threading
        path = resource_path(os.path.join("sounds", name))
        if not os.path.exists(path): return
        def _play():
            try:
                import winsound
                winsound.PlaySound(path,
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            except Exception:
                try:  # macOS/Linux fallback
                    import subprocess as _sp
                    _sp.Popen(["afplay", path], stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
                except Exception: pass
        threading.Thread(target=_play, daemon=True).start()

    def _pomo_toggle(self):
        if self._pomo_running:
            self._pomo_pause()
        else:
            self._pomo_start()

    def _pomo_start(self):
        first_start = not getattr(self, "_pomo_ever_started", False)
        self._pomo_ever_started = True
        self._pomo_running = True
        self._pomo_phase_start = now_dt()
        if self._pomo_play_btn and self._pomo_play_btn.winfo_exists():
            self._pomo_play_btn.configure(text="⏸", fg="#ef4444",
                activeforeground="#ef4444")
        if first_start and self.cfg.get("pomo_alert_enabled", True):
            self._pomo_sound("workstart.wav",
                volume=self.cfg.get("pomo_alert_volume", 0.8))
        self._pomo_schedule_tick()
        self._pomo_schedule_step()

    def _pomo_pause(self):
        # accumulate elapsed time into totals before pausing
        self._pomo_accumulate()
        self._pomo_running = False
        if self._pomo_job:
            self.root.after_cancel(self._pomo_job); self._pomo_job = None
        if self._pomo_tick_job:
            self.root.after_cancel(self._pomo_tick_job); self._pomo_tick_job = None
        if self._pomo_play_btn and self._pomo_play_btn.winfo_exists():
            self._pomo_play_btn.configure(text="▶", fg=self.T["text"],
                activeforeground=self.T["text"])
        self._pomo_update_label()
        save_config(self.cfg)

    def _pomo_accumulate(self):
        """Add elapsed seconds since phase_start to totals + daily log; grant 1 XP per work minute."""
        if self._pomo_phase_start is None: return
        elapsed = int((now_dt() - self._pomo_phase_start).total_seconds())
        if elapsed <= 0: return
        today_key = datetime.date.today().isoformat()
        daily = self.cfg.setdefault("pomo_daily", {})
        day   = daily.setdefault(today_key, {"work": 0, "break": 0})
        if self._pomo_phase == "work":
            prev_work = self.cfg.get("pomo_total_work_secs", 0)
            new_work  = prev_work + elapsed
            self.cfg["pomo_total_work_secs"] = new_work
            day["work"] = day.get("work", 0) + elapsed
            # 1 XP per complete work minute
            xp_gained = (new_work // 60) - (prev_work // 60)
            if xp_gained > 0:
                self.cfg["xp"] = self.cfg.get("xp", 0) + xp_gained
        else:
            self.cfg["pomo_total_break_secs"] = self.cfg.get("pomo_total_break_secs", 0) + elapsed
            day["break"] = day.get("break", 0) + elapsed
        self._pomo_phase_start = now_dt()  # reset so we don't double-count

    def _pomo_schedule_step(self):
        """Called every second to countdown the timer."""
        if not self._pomo_running: return
        self._pomo_secs -= 1
        self._pomo_update_label()
        if self._pomo_secs <= 0:
            self._pomo_accumulate()
            self._pomo_next_phase()
        else:
            self._pomo_job = self.root.after(1000, self._pomo_schedule_step)

    def _pomo_next_phase(self):
        alert_vol = self.cfg.get("pomo_alert_volume", 0.8)
        if self._pomo_phase == "work":
            self._pomo_phase = "break"
            self._pomo_secs  = self.cfg.get("pomo_break_mins", 3) * 60
            if self.cfg.get("pomo_alert_enabled", True):
                self._pomo_sound("breakstart.wav", volume=alert_vol)
        else:
            self._pomo_phase = "work"
            self._pomo_secs  = self.cfg.get("pomo_work_mins", 20) * 60
            if self.cfg.get("pomo_alert_enabled", True):
                self._pomo_sound("workstart.wav", volume=alert_vol)
        self._pomo_phase_start = now_dt()
        self._pomo_update_label()
        self._pomo_job = self.root.after(1000, self._pomo_schedule_step)

    def _pomo_skip(self, event=None):
        """Right-click handler: show a 2-second skip confirmation near the cursor."""
        # Don't show if timer not running
        if not self._pomo_running: return
        T = self.T
        skip_win = tk.Toplevel(self.root)
        skip_win.overrideredirect(True)
        skip_win.attributes("-topmost", True)
        skip_win.configure(bg=T["header_bg"])
        phase_name = "Work" if self._pomo_phase == "work" else "Break"
        next_name  = "Break" if self._pomo_phase == "work" else "Work"
        f = tk.Frame(skip_win, bg=T["header_bg"], padx=10, pady=8); f.pack()
        tk.Label(f, text=f"Skip {phase_name} → {next_name}?",
            bg=T["header_bg"], fg=T["text"],
            font=(self.cfg.get("ui_font","Segoe UI Variable"), 9, "bold")).pack(pady=(0,6))
        btn_f = tk.Frame(f, bg=T["header_bg"]); btn_f.pack()
        _confirmed = [False]
        def _do_skip():
            _confirmed[0] = True
            skip_win.destroy()
            # accumulate current phase time before skipping
            self._pomo_accumulate()
            if self._pomo_job:
                self.root.after_cancel(self._pomo_job); self._pomo_job = None
            self._pomo_next_phase()
        def _cancel():
            skip_win.destroy()
        tk.Button(btn_f, text=f"⏭ Skip to {next_name}", command=_do_skip,
            bg=T["check_done"], fg="#ffffff", relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"), 8),
            padx=8, pady=3, cursor="hand2",
            activebackground=T["btn_hover"]).pack(side="left", padx=(0,6))
        tk.Button(btn_f, text="✕", command=_cancel,
            bg=T["header_bg"], fg=T["muted"], relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"), 8),
            padx=6, pady=3, cursor="hand2").pack(side="left")
        # position near cursor
        skip_win.update_idletasks()
        x = event.x_root - skip_win.winfo_reqwidth() // 2
        y = event.y_root - skip_win.winfo_reqheight() - 8
        skip_win.geometry(f"+{x}+{y}")
        # auto-dismiss after 2 seconds if no action
        skip_win.after(2000, lambda: skip_win.destroy() if skip_win.winfo_exists() and not _confirmed[0] else None)

    def _pomo_schedule_tick(self):
        """Play a random tick sound (1–16) every second if enabled and running."""
        if not self._pomo_running: return
        is_break = (self._pomo_phase == "break")
        no_tick_break = bool(self.cfg.get("pomo_no_tick_break", True))
        tick_enabled  = bool(self.cfg.get("pomo_tick_enabled", True))
        if tick_enabled and not (is_break and no_tick_break):
            import random as _rnd
            n = _rnd.randint(1, 16)
            self._pomo_sound(f"clockticksound{n}.wav",
                volume=self.cfg.get("pomo_tick_volume", 0.15))
        self._pomo_tick_job = self.root.after(1000, self._pomo_schedule_tick)

    def _pomo_update_label(self):
        if not (self._pomo_lbl and self._pomo_lbl.winfo_exists()): return
        if not self._pomo_running and self._pomo_secs == self.cfg.get("pomo_work_mins",20)*60:
            self._pomo_lbl.configure(text="")
            return
        m, s = divmod(max(0, self._pomo_secs), 60)
        phase_color = self.cfg.get("pomo_work_color","#e05c5c") if self._pomo_phase=="work" else self.cfg.get("pomo_break_color","#4caf88")
        icon = "💼" if self._pomo_phase == "work" else "☕"
        self._pomo_lbl.configure(text=f"{icon} {m:02d}:{s:02d}", fg=phase_color)

    def _fmt_duration(self, total_secs):
        h = total_secs // 3600
        m = (total_secs % 3600) // 60
        if h > 0: return f"{h}h {m:02d}m"
        return f"{m}m"

    def _open_pomo_settings(self):
        # singleton – if already open, bring to front unconditionally
        for w in self.root.winfo_children():
            if isinstance(w, tk.Toplevel) and getattr(w, "_is_pomo_win", False):
                w.deiconify(); w.lift(); w.focus_force()
                w.attributes("-topmost", True)
                return
        T = self.T
        win = tk.Toplevel(self.root)
        win._is_pomo_win = True
        win.title("Pomodoro")
        win.configure(bg=T["bg"])
        win.attributes("-topmost", True)
        # restore saved geometry or use a larger default
        _pomo_geo = self.cfg.get("pomo_win_geometry", "400x720")
        win.geometry(_pomo_geo)
        win.resizable(True, True)
        def _save_pomo_geo(e=None):
            if win.winfo_exists():
                self.cfg["pomo_win_geometry"] = win.geometry()
                save_config(self.cfg)
        win.bind("<Configure>", _save_pomo_geo)

        font_n  = (self.cfg.get("ui_font","Segoe UI Variable"), 9)
        font_b  = (self.cfg.get("ui_font","Segoe UI Variable"), 9, "bold")
        font_lg = (self.cfg.get("ui_font","Segoe UI Variable"), 36, "bold")

        def lbl(parent, text, **kw):
            return tk.Label(parent, text=text, bg=T["bg"], fg=T["text"], font=font_n, **kw)
        def sec_lbl(parent, text):
            f = tk.Frame(parent, bg=T["header_bg"]); f.pack(fill="x", pady=(8,2))
            tk.Label(f, text=text, bg=T["header_bg"], fg=T["text"],
                font=font_b, anchor="w", padx=8, pady=3).pack(fill="x")
            return f

        scroll_canvas = tk.Canvas(win, bg=T["bg"], bd=0, highlightthickness=0)
        vsb = ttk.Scrollbar(win, orient="vertical", command=scroll_canvas.yview,
            style="LeSticky.Vertical.TScrollbar")
        scroll_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(scroll_canvas, bg=T["bg"])
        _cw2 = scroll_canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: scroll_canvas.configure(
            scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.bind("<Configure>", lambda e: scroll_canvas.itemconfig(_cw2, width=e.width))
        for w in (scroll_canvas, inner):
            w.bind("<MouseWheel>", lambda e: scroll_canvas.yview_scroll(
                -1 if e.delta>0 else 1, "units"))

        # ── TIMER DISPLAY ─────────────────────────────────────────────────
        sec_lbl(inner, "⏱  Timer")
        timer_frame = tk.Frame(inner, bg=T["bg"]); timer_frame.pack(fill="x", padx=12, pady=6)
        phase_color = self.cfg.get("pomo_work_color","#e05c5c") if self._pomo_phase=="work" else self.cfg.get("pomo_break_color","#4caf88")
        m0, s0 = divmod(max(0, self._pomo_secs), 60)
        timer_lbl = tk.Label(timer_frame, text=f"{m0:02d}:{s0:02d}",
            bg=T["bg"], fg=phase_color, font=font_lg)
        timer_lbl.pack()
        phase_indicator = tk.Label(timer_frame,
            text=("💼 Work" if self._pomo_phase=="work" else "☕ Break"),
            bg=T["bg"], fg=T["muted"], font=font_n)
        phase_indicator.pack()

        # play/pause button inside popup
        _popup_btn_colors = {"run": "#ef4444", "idle": T["check_done"]}
        _popup_toggle_btn = [None]
        def _toggle_in_win():
            self._pomo_toggle()
            if _popup_toggle_btn[0] and _popup_toggle_btn[0].winfo_exists():
                if self._pomo_running:
                    _popup_toggle_btn[0].configure(text="⏸ Pause",
                        bg=_popup_btn_colors["run"])
                else:
                    _popup_toggle_btn[0].configure(text="▶ Start",
                        bg=_popup_btn_colors["idle"])
        _init_bg = _popup_btn_colors["run"] if self._pomo_running else _popup_btn_colors["idle"]
        _init_txt = "⏸ Pause" if self._pomo_running else "▶ Start"
        _ptbtn = tk.Button(timer_frame, text=_init_txt, command=_toggle_in_win,
            bg=_init_bg, fg="#ffffff", relief="flat",
            font=font_b, padx=16, pady=6, cursor="hand2",
            activebackground=T["btn_hover"])
        _ptbtn.pack(pady=(8,0))
        _ptbtn.bind("<Button-3>", self._pomo_skip)
        _popup_toggle_btn[0] = _ptbtn

        # live-update the timer label every second
        _timer_job = [None]
        def _refresh_timer():
            if not win.winfo_exists(): return
            pc = self.cfg.get("pomo_work_color","#e05c5c") if self._pomo_phase=="work" else self.cfg.get("pomo_break_color","#4caf88")
            m2, s2 = divmod(max(0, self._pomo_secs), 60)
            timer_lbl.configure(text=f"{m2:02d}:{s2:02d}", fg=pc)
            phase_indicator.configure(text="💼 Work" if self._pomo_phase=="work" else "☕ Break")
            if _popup_toggle_btn[0] and _popup_toggle_btn[0].winfo_exists():
                if self._pomo_running:
                    _popup_toggle_btn[0].configure(text="⏸ Pause",
                        bg=_popup_btn_colors["run"])
                else:
                    _popup_toggle_btn[0].configure(text="▶ Start",
                        bg=_popup_btn_colors["idle"])
            _timer_job[0] = win.after(500, _refresh_timer)
        _refresh_timer()
        win.protocol("WM_DELETE_WINDOW", lambda: (
            win.after_cancel(_timer_job[0]) if _timer_job[0] else None, win.destroy()))

        # ── SETTINGS ──────────────────────────────────────────────────────
        sec_lbl(inner, "⚙  Settings")
        sf = tk.Frame(inner, bg=T["bg"]); sf.pack(fill="x", padx=12, pady=4)

        def _autosave():
            save_config(self.cfg)

        # Work interval
        lbl(sf, "Work interval (minutes):").grid(row=0, column=0, sticky="w", pady=2)
        work_var = tk.IntVar(value=self.cfg.get("pomo_work_mins",20))
        tk.Spinbox(sf, from_=1, to=120, textvariable=work_var, width=5,
            bg=T["entry_bg"], fg=T["entry_fg"], buttonbackground=T["btn_bg"],
            relief="flat", font=font_n).grid(row=0, column=1, sticky="w", padx=(8,0), pady=2)

        # Break interval
        lbl(sf, "Break interval (minutes):").grid(row=1, column=0, sticky="w", pady=2)
        break_var = tk.IntVar(value=self.cfg.get("pomo_break_mins",3))
        tk.Spinbox(sf, from_=1, to=60, textvariable=break_var, width=5,
            bg=T["entry_bg"], fg=T["entry_fg"], buttonbackground=T["btn_bg"],
            relief="flat", font=font_n).grid(row=1, column=1, sticky="w", padx=(8,0), pady=2)

        # Save intervals button (only this requires explicit save)
        def _save_intervals():
            self.cfg["pomo_work_mins"]  = int(work_var.get())
            self.cfg["pomo_break_mins"] = int(break_var.get())
            if not self._pomo_running:
                self._pomo_phase = "work"
                self._pomo_secs  = self.cfg["pomo_work_mins"] * 60
                self._pomo_update_label()
            save_config(self.cfg)
        tk.Button(sf, text="💾 Save intervals", command=_save_intervals,
            bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
            font=font_b, padx=12, pady=4, cursor="hand2",
            activebackground=T["btn_hover"]).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(6,8))

        # ── Tick sound ──
        lbl(sf, "── Tick sound ──").grid(row=3, column=0, columnspan=2, sticky="w", pady=(4,0))
        tick_var = tk.BooleanVar(value=self.cfg.get("pomo_tick_enabled",True))
        def _on_tick_toggle():
            self.cfg["pomo_tick_enabled"] = tick_var.get(); _autosave()
        tk.Checkbutton(sf, text="Ticking sound enabled", variable=tick_var,
            command=_on_tick_toggle,
            bg=T["bg"], fg=T["text"], activebackground=T["bg"],
            selectcolor=T["entry_bg"], font=font_n).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=2)

        no_tick_break_var = tk.BooleanVar(value=self.cfg.get("pomo_no_tick_break", True))
        def _on_no_tick_break():
            val = no_tick_break_var.get()
            self.cfg["pomo_no_tick_break"] = val
            save_config(self.cfg)
        tk.Checkbutton(sf, text="No ticking during break", variable=no_tick_break_var,
            command=_on_no_tick_break,
            bg=T["bg"], fg=T["text"], activebackground=T["bg"],
            selectcolor=T["entry_bg"], font=font_n).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=2)

        lbl(sf, "Volume: use system mixer").grid(row=6, column=0, columnspan=2, sticky="w", pady=2)

        # ── Alert sounds (work/break start) ──
        lbl(sf, "── Alert sounds ──").grid(row=7, column=0, columnspan=2, sticky="w", pady=(8,0))
        alert_var = tk.BooleanVar(value=self.cfg.get("pomo_alert_enabled",True))
        def _on_alert_toggle():
            self.cfg["pomo_alert_enabled"] = alert_var.get(); _autosave()
        tk.Checkbutton(sf, text="Work/break start sounds enabled", variable=alert_var,
            command=_on_alert_toggle,
            bg=T["bg"], fg=T["text"], activebackground=T["bg"],
            selectcolor=T["entry_bg"], font=font_n).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=2)

        lbl(sf, "Volume: use system mixer").grid(row=8, column=0, columnspan=2, sticky="w", pady=2)

        # ── Colors ──
        lbl(sf, "── Timer colors ──").grid(row=9, column=0, columnspan=2, sticky="w", pady=(8,0))
        work_col_var = [self.cfg.get("pomo_work_color","#e05c5c")]
        work_col_btn = tk.Button(sf, text="  ", bg=work_col_var[0], relief="flat",
            width=3, cursor="hand2")
        lbl(sf, "Work-time color:").grid(row=10, column=0, sticky="w", pady=2)
        work_col_btn.grid(row=10, column=1, sticky="w", padx=(8,0), pady=2)
        def _pick_work_color():
            from tkinter import colorchooser
            c = colorchooser.askcolor(color=work_col_var[0], parent=win, title="Work color")
            if c and c[1]:
                work_col_var[0] = c[1]; work_col_btn.configure(bg=c[1])
                self.cfg["pomo_work_color"] = c[1]; _autosave()
        work_col_btn.configure(command=_pick_work_color)

        lbl(sf, "Break-time color:").grid(row=11, column=0, sticky="w", pady=2)
        break_col_var = [self.cfg.get("pomo_break_color","#4caf88")]
        break_col_btn = tk.Button(sf, text="  ", bg=break_col_var[0], relief="flat",
            width=3, cursor="hand2")
        break_col_btn.grid(row=11, column=1, sticky="w", padx=(8,0), pady=2)
        def _pick_break_color():
            from tkinter import colorchooser
            c = colorchooser.askcolor(color=break_col_var[0], parent=win, title="Break color")
            if c and c[1]:
                break_col_var[0] = c[1]; break_col_btn.configure(bg=c[1])
                self.cfg["pomo_break_color"] = c[1]; _autosave()
        break_col_btn.configure(command=_pick_break_color)

        # ── STATISTICS ────────────────────────────────────────────────────
        sec_lbl(inner, "📊  Statistics")
        stf = tk.Frame(inner, bg=T["bg"]); stf.pack(fill="x", padx=12, pady=8)

        def _stat_row(parent, label, value, row):
            tk.Label(parent, text=label, bg=T["bg"], fg=T["muted"],
                font=font_n, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
            tk.Label(parent, text=value, bg=T["bg"], fg=T["text"],
                font=font_b, anchor="e").grid(row=row, column=1, sticky="e", padx=(16,0), pady=3)

        work_secs  = self.cfg.get("pomo_total_work_secs",0)
        break_secs = self.cfg.get("pomo_total_break_secs",0)
        total_secs = work_secs + break_secs
        work_pct   = int(100 * work_secs / total_secs) if total_secs > 0 else 0
        break_pct  = 100 - work_pct if total_secs > 0 else 0

        _stat_row(stf, "Total focused work time:", self._fmt_duration(work_secs), 0)
        _stat_row(stf, "Total break time:",        self._fmt_duration(break_secs), 1)
        _stat_row(stf, "Total tracked time:",      self._fmt_duration(total_secs), 2)
        _stat_row(stf, "Work ratio:",              f"{work_pct}%", 3)
        _stat_row(stf, "Break ratio:",             f"{break_pct}%", 4)
        stf.columnconfigure(0, weight=1)
        stf.columnconfigure(1, weight=0)

        # mini bar chart
        if total_secs > 0:
            bar_frame = tk.Frame(inner, bg=T["bg"]); bar_frame.pack(fill="x", padx=12, pady=(0,8))
            bar_canvas = tk.Canvas(bar_frame, bg=T["bg"], height=18,
                bd=0, highlightthickness=0)
            bar_canvas.pack(fill="x")
            def _draw_bar(e=None):
                w2 = bar_canvas.winfo_width() or 280
                bar_canvas.delete("all")
                work_w = int(w2 * work_pct / 100)
                if work_w > 0:
                    bar_canvas.create_rectangle(0, 0, work_w, 18,
                        fill=self.cfg.get("pomo_work_color","#e05c5c"), outline="")
                if work_w < w2:
                    bar_canvas.create_rectangle(work_w, 0, w2, 18,
                        fill=self.cfg.get("pomo_break_color","#4caf88"), outline="")
            bar_canvas.bind("<Configure>", _draw_bar)
            win.after(100, _draw_bar)

        # Reset stats button
        _reset_btn_ref = [None]
        def _reset_stats(btn_ref=_reset_btn_ref):
            b = btn_ref[0]
            if b is None: return
            if not getattr(b, "_confirm", False):
                b._confirm = True
                b.configure(text="Sure? 🗑", fg=T["close_hover"])
                b.after(2500, lambda: (
                    setattr(b, "_confirm", False),
                    b.configure(text="🗑 Reset statistics", fg=T["muted"])
                ) if b.winfo_exists() else None)
            else:
                # second click → popup with "No" as default
                dlg = tk.Toplevel(win)
                dlg.title("Confirm reset")
                dlg.configure(bg=T["bg"])
                dlg.attributes("-topmost", True)
                dlg.resizable(False, False)
                dlg.grab_set()
                font_n = (self.cfg.get("ui_font","Segoe UI Variable"), 9)
                font_b = (self.cfg.get("ui_font","Segoe UI Variable"), 9, "bold")
                tk.Label(dlg, text="Reset ALL pomodoro statistics?\nThis cannot be undone.",
                    bg=T["bg"], fg=T["text"], font=font_n,
                    padx=20, pady=14, justify="center").pack()
                bf = tk.Frame(dlg, bg=T["bg"]); bf.pack(pady=(0,12))
                def _do_reset():
                    self.cfg["pomo_total_work_secs"]  = 0
                    self.cfg["pomo_total_break_secs"] = 0
                    self.cfg["pomo_daily"] = {}
                    save_config(self.cfg)
                    dlg.destroy(); win.destroy()
                    self._open_pomo_settings()
                yes_btn = tk.Button(bf, text="Yes, reset", command=_do_reset,
                    bg="#e05c5c", fg="#ffffff", relief="flat",
                    font=font_n, padx=10, pady=4, cursor="hand2")
                yes_btn.pack(side="left", padx=(0,8))
                no_btn = tk.Button(bf, text="No, keep", command=dlg.destroy,
                    bg=T["btn_bg"], fg=T["btn_fg"], relief="flat",
                    font=font_b, padx=10, pady=4, cursor="hand2")
                no_btn.pack(side="left")
                no_btn.focus_set()  # "No" is focused/highlighted by default
                dlg.bind("<Return>", lambda e: dlg.destroy())
                dlg.bind("<Escape>", lambda e: dlg.destroy())
                # center on screen
                dlg.update_idletasks()
                sw = dlg.winfo_screenwidth()
                sh = dlg.winfo_screenheight()
                dlg.geometry(f"320x150+{(sw-320)//2}+{(sh-150)//2}")
        _reset_btn = tk.Button(inner, text="🗑 Reset statistics", command=_reset_stats,
            bg=T["bg"], fg=T["muted"], relief="flat",
            font=(self.cfg.get("ui_font","Segoe UI Variable"),8),
            padx=8, pady=3, cursor="hand2",
            activebackground=T["item_hover"])
        _reset_btn.pack(pady=(0,10))
        _reset_btn._confirm = False
        _reset_btn_ref[0] = _reset_btn


    def run(self):
        self.entry.focus_set(); self.root.mainloop()


if __name__ == "__main__":
    App().run()
