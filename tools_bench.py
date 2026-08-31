"""Measure a FRESH app's first active-tab render + cached tab switches.

Usage: bench.py <path-to-sticky_notes.py> <label>
Nothing else runs in the process, so no accumulation from prior tests.
"""
import sys, os, shutil, tempfile, time, importlib.util

src_path, label = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("bench_mod", src_path)
sn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sn)

tmp = tempfile.mkdtemp(); home = os.path.expanduser("~")
for attr, base in (("CONFIG_FILE", ".leonote_config.json"), ("TASKS_FILE", ".leonote_tasks.json"),
                   ("DOCS_FILE", ".leonote_docs.json"), ("HABITS_FILE", ".leonote_habits.json"),
                   ("PRIORITIES_FILE", ".leonote_priorities.json")):
    s, d = os.path.join(home, base), os.path.join(tmp, base)
    if os.path.exists(s): shutil.copy2(s, d)
    setattr(sn, attr, d)
if hasattr(sn, "RECUR_FILE"):
    sn.RECUR_FILE = os.path.join(tmp, ".leonote_recurring.json")
    sn._rec_cache = None
if hasattr(sn, "invalidate_data_cache"): sn.invalidate_data_cache()

app = sn.App(); app.root.update()
app.current_tab = "active"
app._render_tasks(); app.root.update()          # warm Tk font/layout caches

# full render of the active tab, best of 5
best = 1e9
for _ in range(5):
    t0 = time.perf_counter()
    app._render_tasks()
    app.root.update()
    best = min(best, (time.perf_counter() - t0) * 1000)
print("%-10s  full active render : %7.1f ms" % (label, best))

# cached switch, if this build has the tab cache
if hasattr(app, "_tab_frames"):
    for t in ("habits", "priorities"):
        app._set_tab(t); app.root.update()
    swb = 1e9
    for _ in range(6):
        app._set_tab("active"); app.root.update()
        t0 = time.perf_counter(); app._set_tab("habits"); app.root.update()
        swb = min(swb, (time.perf_counter() - t0) * 1000)
    print("%-10s  cached tab switch  : %7.1f ms" % (label, swb))
else:
    swb = 1e9
    for _ in range(6):
        app._set_tab("active"); app.root.update()
        t0 = time.perf_counter(); app._set_tab("habits"); app.root.update()
        swb = min(swb, (time.perf_counter() - t0) * 1000)
    print("%-10s  tab switch (no cache): %5.1f ms" % (label, swb))

try:
    app._destroy_tray()
except Exception:
    pass
sys.stdout.flush()      # os._exit skips buffer flushing
sys.stderr.flush()
os._exit(0)
