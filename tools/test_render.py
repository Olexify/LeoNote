import sys, os, shutil, tempfile
sys.path.insert(0, r"E:\Projects\LeoNote")
import sticky_notes as sn
import tkinter as tk

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
app.current_tab = "active"; app._tab_dirty.add("active")
app._render_tasks(); app.root.update()

# ---- instrument: is the frame being built ever the one on screen? ----------
obs = []
_orig_row = sn.App._task_row
def spy(self, task, *a, **k):
    try: obs.append((str(self.task_frame), str(self.canvas.itemcget(self._cw, "window"))))
    except Exception: pass
    return _orig_row(self, task, *a, **k)
sn.App._task_row = spy

# a DIRECT render - exactly what a rename / toggle / delete triggers
shown_before = str(app.canvas.itemcget(app._cw, "window"))
obs.clear()
app._render_tasks(); app.root.update()
visible_builds = [o for o in obs if o[0] == o[1]]
check("direct _render_tasks builds OFF-SCREEN (%d rows, %d visible)"
      % (len(obs), len(visible_builds)), len(obs) > 0 and not visible_builds, visible_builds[:2])

shown_after = str(app.canvas.itemcget(app._cw, "window"))
check("canvas swapped to the NEW frame after the build", shown_after != shown_before,
      (shown_before, shown_after))
check("the old frame was destroyed (no leak)",
      not app.root.tk.call("winfo", "exists", shown_before), shown_before)
check("mounted frame is the live cached frame",
      shown_after == str(app._tab_frames["active"]))

# ---- repeated renders must not leak frames --------------------------------
before_kids = len(app.canvas.winfo_children())
for _ in range(6):
    app._render_tasks(); app.root.update()
after_kids = len(app.canvas.winfo_children())
check("6 renders do not accumulate canvas children (%d -> %d)" % (before_kids, after_kids),
      after_kids <= before_kids, (before_kids, after_kids))

# ---- scroll survives a direct render (rename must not jump to top) --------
app.canvas.update_idletasks()
for _ in range(8): app.root.event_generate("<MouseWheel>", delta=-120, x=100, y=200)
app.root.update()
off = app.canvas.yview()[0]
app._render_tasks(); app.root.update(); app.root.update_idletasks()
after_off = app.canvas.yview()[0]
check("scroll survives a direct re-render (%.3f -> %.3f)" % (off, after_off),
      off > 0 and abs(after_off - off) < 0.06, (off, after_off))

sn.App._task_row = _orig_row

# ---- inline editors -------------------------------------------------------
app._tab_dirty.add("active"); app._render_tasks(); app.root.update()
task = next(t for t in app.tasks if not t.get("deleted") and not t.get("done"))
reg = app._task_widget_registry[id(task)]

def find_editor(root_w, want):
    out = []
    def walk(w):
        for c in w.winfo_children():
            if c.winfo_class() == want: out.append(c)
            walk(c)
    walk(root_w)
    return out

# long text -> Text widget, cursor at end
long_task = dict(task); long_task["text"] = "x" * 80
task["text"] = "This is a fairly long note that should definitely get a real editor box"
app._inline_edit_task(reg["tw"], reg["lbl"], task)
app.root.update()
texts = find_editor(reg["tw"], "Text")
check("long task opens a MULTI-LINE Text box", len(texts) == 1, len(texts))
if texts:
    t = texts[0]
    check("multi-line cursor sits at the END, not the start",
          t.index("insert") == t.index("end-1c"), (t.index("insert"), t.index("end-1c")))
    check("multi-line box grew past 1 row", int(str(t.cget("height"))) >= 3, t.cget("height"))
    t.event_generate("<Escape>"); app.root.update()

# short text -> Entry, cursor at end and NOT select-all
app._tab_dirty.add("active"); app._render_tasks(); app.root.update()
task2 = next(t for t in app.tasks if not t.get("deleted") and not t.get("done"))
task2["text"] = "short one"
reg2 = app._task_widget_registry[id(task2)]
app._inline_edit_task(reg2["tw"], reg2["lbl"], task2)
app.root.update()
ents = find_editor(reg2["tw"], "Entry")
check("short task opens a single-line Entry", len(ents) == 1, len(ents))
if ents:
    e = ents[0]
    check("single-line cursor at END", e.index("insert") == len(e.get()), (e.index("insert"), len(e.get())))
    check("text is NOT select-all'd (typing appends, not wipes)",
          not e.selection_present(), e.selection_present())
    e.event_generate("<Escape>"); app.root.update()

# ---- subtasks now get the same treatment ----------------------------------
host = next((t for t in app.tasks if t.get("subtasks")), None)
if host:
    st = host["subtasks"][0]
    st["text"] = "a long subtask note that used to be stuck in a tiny one line entry box"
    app._tab_dirty.add("active"); app._render_tasks(); app.root.update()
    holder = tk.Frame(app.task_frame); holder.pack()
    lab = tk.Label(holder, text=st["text"]); lab.pack(side="left")
    app._inline_edit_subtask(holder, lab, host, st)
    app.root.update()
    stexts = find_editor(holder, "Text")
    check("long SUBTASK opens a multi-line box (was always single-line)",
          len(stexts) == 1, len(stexts))
    if stexts:
        t = stexts[0]
        check("subtask multi-line cursor at END",
              t.index("insert") == t.index("end-1c"), (t.index("insert"), t.index("end-1c")))
        t.event_generate("<Escape>"); app.root.update()
else:
    print("SKIP  subtask checks (no task with subtasks)")

try: app._destroy_tray()
except Exception: pass
print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES: %s" % (len(fails), fails)))
sys.stdout.flush()
os._exit(1 if fails else 0)
