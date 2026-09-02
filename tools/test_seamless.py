import sys, os, shutil, tempfile
sys.path.insert(0, r"E:\Projects\LeoNote")
import sticky_notes as sn

tmp = tempfile.mkdtemp(); home = os.path.expanduser("~")
for attr, base in (("CONFIG_FILE", ".leonote_config.json"), ("TASKS_FILE", ".leonote_tasks.json"),
                   ("DOCS_FILE", ".leonote_docs.json"), ("HABITS_FILE", ".leonote_habits.json"),
                   ("PRIORITIES_FILE", ".leonote_priorities.json")):
    s, d = os.path.join(home, base), os.path.join(tmp, base)
    if os.path.exists(s): shutil.copy2(s, d)
    setattr(sn, attr, d)
sn.RECUR_FILE = os.path.join(tmp, ".leonote_recurring.json"); sn._rec_cache = None
sn.invalidate_data_cache()

fails = []
def check(label, cond, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label + (("   -> " + str(extra)) if not cond else ""))
    if not cond: fails.append(label)

app = sn.App(); app.root.update()

# Instrument: record whether the frame under construction was ALSO the frame
# currently displayed by the canvas. If it ever is, the user sees it fill in.
observations = []
_orig_row = sn.App._task_row
def spy_row(self, task, *a, **k):
    try:
        shown = self.canvas.itemcget(self._cw, "window")
        observations.append((str(self.task_frame), str(shown)))
    except Exception:
        pass
    return _orig_row(self, task, *a, **k)
sn.App._task_row = spy_row

# --- first visit to a dirty tab: the expensive, previously-chunky path -------
app._set_tab("habits"); app.root.update()
app._tab_dirty.add("active")
observations.clear()
app._set_tab("active"); app.root.update()

built_while_visible = [o for o in observations if o[0] == o[1]]
check("rows are built while the frame is OFF-SCREEN (%d rows, %d visible)"
      % (len(observations), len(built_while_visible)),
      len(observations) > 0 and not built_while_visible,
      built_while_visible[:3])

# --- and the result is actually correct + mounted afterwards -----------------
check("after the swap the built frame IS the canvas window item",
      str(app.canvas.itemcget(app._cw, "window")) == str(app._tab_frames["active"]),
      (app.canvas.itemcget(app._cw, "window"), str(app._tab_frames["active"])))
check("active tab has its content", len(app._tab_frames["active"].winfo_children()) > 5,
      len(app._tab_frames["active"].winfo_children()))
check("_mounted_tab tracks reality", app._mounted_tab == "active", app._mounted_tab)

# --- the previous tab must remain intact and on-screen during the build ------
app._tab_dirty.add("priorities")
observations.clear()
prev_children = len(app._tab_frames["active"].winfo_children())
app._set_tab("priorities"); app.root.update()
check("previous tab's widgets were not destroyed by the swap",
      len(app._tab_frames["active"].winfo_children()) == prev_children,
      (prev_children, len(app._tab_frames["active"].winfo_children())))

# --- cached (clean) switches still work -------------------------------------
app._set_tab("active"); app.root.update()
check("cached switch back to active mounts correctly",
      app._mounted_tab == "active" and
      str(app.canvas.itemcget(app._cw, "window")) == str(app._tab_frames["active"]))

# --- scrollregion must be right after an off-screen build -------------------
app._tab_dirty.add("habits")
app._set_tab("habits"); app.root.update(); app.root.update_idletasks()
sr = app.canvas.cget("scrollregion")
check("scrollregion is set after an off-screen build (%s)" % sr, bool(str(sr).strip()), sr)

# --- every tab renders through the new path ---------------------------------
for t in ("active", "archive", "priorities", "habits", "docs", "stats", "search"):
    app._tab_dirty.add(t)
    try:
        app._set_tab(t); app.root.update()
        ok = len(app.task_frame.winfo_children()) >= 1
    except Exception as e:
        ok = False; print("      exception on %s: %r" % (t, e))
    check("tab %-11s builds and mounts cleanly" % t, ok)

sn.App._task_row = _orig_row
try: app._destroy_tray()
except Exception: pass
print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES: %s" % (len(fails), fails)))
sys.stdout.flush()
os._exit(1 if fails else 0)
