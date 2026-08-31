"""Contrast floors + factory smoke test for the LeoNote design token layer.

Keep this in the repo and re-run after ANY palette edit.
"""
import sys, os, shutil, tempfile
sys.path.insert(0, r"E:\Projects\LeoNote")
import sticky_notes as sn

fails = []
def bad(msg):
    fails.append(msg); print("FAIL  " + msg)

names = sorted(sn.THEMES)
print("themes: %d" % len(names))

# ---- 1. contrast floors ---------------------------------------------------
FLOORS = [
    ("hairline vs surface",   lambda T: sn.contrast(T["hairline"], T["surface"]),      1.25),
    ("surface_hover vs surf", lambda T: sn.contrast(T["surface_hover"], T["surface"]), 1.05),
    ("accent vs bg",          lambda T: sn.contrast(T["accent"], T["bg"]),             2.15),
    ("accent_ind vs tab_bg",  lambda T: sn.contrast(T["accent_ind"], T["tab_bg"]),     2.55),
    ("on_accent vs accent",   lambda T: sn.contrast(T["on_accent"], T["accent"]),      3.00),
    ("focus vs surface",      lambda T: sn.contrast(T["focus"], T["surface"]),         2.90),
]
worst = {label: (99.0, None) for label, _, _ in FLOORS}
for n in names:
    T = sn.tokens(n)
    for label, fn, floor in FLOORS:
        v = fn(T)
        if v < worst[label][0]: worst[label] = (v, n)
        if v < floor:
            bad("%-22s %-14s = %.2f  (floor %.2f)" % (label, n, v, floor))

# *_text tones must be legible on their own chip
for n in names:
    T = sn.tokens(n)
    for k in ("success", "warning", "danger", "info", "accent"):
        chip = sn.mix(T["surface"], T[k], .16)
        v = sn.contrast(T[k + "_text"], chip)
        if v < 4.40:
            bad("%s_text on its chip  %-14s = %.2f (floor 4.40)" % (k, n, v))

print("\nworst case across all %d themes:" % len(names))
for label, (v, n) in worst.items():
    print("  %-22s %.2f  (%s)" % (label, v, n))

# ---- 2. is_dark sanity ----------------------------------------------------
dark = [n for n in names if sn.tokens(n)["is_dark"]]
print("\nclassified dark (%d): %s" % (len(dark), ", ".join(dark)))
for n in ("dark", "eclipse"):
    if n in names and not sn.tokens(n)["is_dark"]:
        bad("%s should classify as dark" % n)
for n in ("light", "yellow", "sakura"):
    if n in names and sn.tokens(n)["is_dark"]:
        bad("%s should NOT classify as dark" % n)

# ---- 3. every legacy key survives ----------------------------------------
for n in names:
    T = sn.tokens(n)
    missing = [k for k in sn.THEMES[n] if k not in T or T[k] != sn.THEMES[n][k]]
    if missing:
        bad("%s lost/changed legacy keys: %s" % (n, missing))
print("\nlegacy key preservation: OK across all themes" if not fails else "")

# ---- 4. factory smoke test: 27 themes x 4 scales --------------------------
tmp = tempfile.mkdtemp(); home = os.path.expanduser("~")
for attr, base in (("CONFIG_FILE", ".leonote_config.json"), ("TASKS_FILE", ".leonote_tasks.json"),
                   ("DOCS_FILE", ".leonote_docs.json"), ("HABITS_FILE", ".leonote_habits.json"),
                   ("PRIORITIES_FILE", ".leonote_priorities.json")):
    src, dst = os.path.join(home, base), os.path.join(tmp, base)
    if os.path.exists(src): shutil.copy2(src, dst)
    setattr(sn, attr, dst)
sn.invalidate_data_cache()

import tkinter as tk
app = sn.App()
app.root.withdraw()
combos = 0
for n in names:
    app.T = sn.tokens(n)
    for scale in (0.5, 1.0, 2.0, 3.0):
        app.cfg["ui_scale"] = scale
        host = tk.Frame(app.root)
        try:
            app._card(host)
            app._btn(host, "Go", kind="primary")
            app._btn(host, "Cancel", kind="ghost")
            app._chip(host, "chip", tone="success")
            app._chip(host, "chip", tone="danger")
            app._section(host, "Section", action="+ Add")
            app._meter(host, 0.42)
            app._empty(host, "*", "Nothing here", "sub text")
            app._mktab(host, "Tab", lambda: None)
            app._task_shell(host, "high", False)
            app._task_shell(host, "none", True)
            app._hairline(host)
            app._font("body"); app._font("title"); app._sp(2); app._px(3)
            app.root.update_idletasks()
            combos += 1
        except Exception as e:
            bad("factory %s @ scale %s: %r" % (n, scale, e))
        finally:
            host.destroy()
print("factory smoke: %d/%d combinations built cleanly" % (combos, len(names) * 4))
try: app.root.destroy()
except Exception: pass

print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES" % len(fails)))
sys.exit(1 if fails else 0)
