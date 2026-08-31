import sys, os, shutil, tempfile, time, json, io
sys.path.insert(0, r"E:\Projects\LeoNote")
import sticky_notes as sn

tmp = tempfile.mkdtemp(); home = os.path.expanduser("~")
for attr, base in (("CONFIG_FILE", ".leonote_config.json"), ("TASKS_FILE", ".leonote_tasks.json"),
                   ("DOCS_FILE", ".leonote_docs.json"), ("HABITS_FILE", ".leonote_habits.json"),
                   ("PRIORITIES_FILE", ".leonote_priorities.json")):
    src, dst = os.path.join(home, base), os.path.join(tmp, base)
    if os.path.exists(src): shutil.copy2(src, dst)
    setattr(sn, attr, dst)
sn.invalidate_data_cache()

fails = []
def check(label, cond, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label + (("   -> " + str(extra)) if not cond else ""))
    if not cond: fails.append(label)

app = sn.App(); app.root.update()
TABS = ["active", "priorities", "habits", "docs", "stats"]

# ---- 1. every tab renders real content -----------------------------------
for t in TABS:
    app._set_tab(t); app.root.update()
    n = len(app.task_frame.winfo_children())
    check("tab %-11s renders content (%d widgets)" % (t, n), n > 1, n)

# ---- 2. each tab got its OWN frame ---------------------------------------
frames = {t: id(app._tab_frames.get(t)) for t in TABS}
check("each tab has a distinct cached frame", len(set(frames.values())) == len(TABS), frames)

# ---- 3. timing: first visit vs cached revisit -----------------------------
def timed_switch(t):
    app._set_tab("active"); app.root.update()
    t0 = time.perf_counter(); app._set_tab(t); app.root.update()
    return (time.perf_counter() - t0) * 1000

warm = {}
for t in ["priorities", "habits", "docs"]:
    samples = [timed_switch(t) for _ in range(5)]
    warm[t] = min(samples)
    # absolute ms is machine/load dependent; the meaningful claim is the ratio
    # against a full render, asserted below.
    print("      cached switch to %-11s = %.1f ms" % (t, warm[t]))

# force a full re-render for comparison
app._set_tab("active"); app.root.update()
t0 = time.perf_counter(); app._render_tasks(); app.root.update()
full = (time.perf_counter() - t0) * 1000
print("      [full _render_tasks of active = %.1f ms; cached switches above]" % full)
check("cached switch beats a full render by >5x",
      full / max(warm.get("habits", 1e-9), 1e-9) > 5, "full=%.1f warm=%.1f" % (full, warm.get("habits", 0)))

# ---- 4. dirty-flag invalidation --------------------------------------------
app._set_tab("habits"); app.root.update()
check("habits clean after render", "habits" not in app._tab_dirty)
d = sn.load_habits(); d.setdefault("habits", []).append({"id": "zz", "name": "TestHabit"})
sn.save_habits(d)
check("save_habits() marks habits dirty", "habits" in app._tab_dirty)
app._set_tab("active"); app._set_tab("habits"); app.root.update()
labels = []
def walk(w):
    for c in w.winfo_children():
        try:
            if c.cget("text"): labels.append(str(c.cget("text")))
        except Exception: pass
        walk(c)
walk(app.task_frame)
check("new habit actually appears after invalidation", any("TestHabit" in x for x in labels))

# ---- 5. per-tab scroll retention -------------------------------------------
app._set_tab("active"); app.root.update(); app.canvas.update_idletasks()
for _ in range(8): app.root.event_generate("<MouseWheel>", delta=-120, x=100, y=200)
app.root.update()
off_active = app.canvas.yview()[0]
app._set_tab("habits"); app.root.update()
app._set_tab("active"); app.root.update(); app.root.update_idletasks()
back = app.canvas.yview()[0]
check("scroll position survives a tab round-trip (%.3f -> %.3f)" % (off_active, back),
      off_active > 0 and abs(back - off_active) < 0.05, (off_active, back))

# ---- 6. C2: emptying the bin must not leave 'active' blank-but-clean --------
app.current_tab = "trash"
app._show_tab_frame("trash")
app._tab_dirty.add("trash")
app._render_tasks(); app.root.update()
# _refresh_tabs flips trash->active when the bin is empty
if app.current_tab != "trash":
    check("C2: after trash->active flip, active is NOT marked clean-but-empty",
          "active" in app._tab_dirty or len(app._tab_frames["active"].winfo_children()) > 1,
          "dirty=%s children=%d" % ("active" in app._tab_dirty,
                                    len(app._tab_frames["active"].winfo_children())))
else:
    print("SKIP  C2 flip (bin not empty in this dataset)")

# ---- 7. resync guard: direct current_tab assignment ------------------------
app._set_tab("habits"); app.root.update()
app.current_tab = "active"          # bypass _set_tab, like _add_task does
app._render_tasks(); app.root.update()
check("resync guard mounts the right frame on direct tab assignment",
      app._current_frame_tab == "active" and app.task_frame is app._tab_frames["active"])
check("habits frame was NOT overwritten by active content",
      app._tab_frames["habits"] is not app._tab_frames["active"])

# ---- 8. maintenance tick is self-rescheduling and safe ---------------------
app._maintenance_tick(first=True)
check("maintenance tick runs and schedules itself", app._maint_job is not None)

# ---- 9. theme change rebuilds every tab -----------------------------------
app._retheme_main_only(); app.root.update()
check("theme change re-dirties all tabs", len(app._tab_dirty) >= len(app._ALL_TABS) - 2,
      sorted(app._tab_dirty))
app._set_tab("habits"); app.root.update()
check("habits still renders after a theme change", len(app.task_frame.winfo_children()) > 1)

# ---- 10. no synchronous config write on tab switch -------------------------
writes = {"n": 0}
_orig = sn.save_config
def counting_save(cfg):
    writes["n"] += 1; return _orig(cfg)
sn.save_config = counting_save
for t in ["active", "habits", "docs", "priorities", "active"]:
    app._set_tab(t); app.root.update()
# writes are debounced at 500ms, so the exact count depends on how long the
# renders take; the property that matters is that they COALESCE - strictly
# fewer writes than switches, and none synchronous inside _set_tab.
check("5 tab switches coalesce to fewer writes (%d < 5)" % writes["n"],
      writes["n"] < 5, writes["n"])
import inspect
# strip comments: the method carries a "# was a synchronous save_config()" note
_code = [l.split("#")[0] for l in inspect.getsource(sn.App._set_tab).splitlines()]
check("_set_tab contains no direct save_config call (code, not comments)",
      not any("save_config" in l for l in _code),
      [l.strip() for l in _code if "save" in l])
sn.save_config = _orig

try: app.root.destroy()
except Exception: pass
print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)
