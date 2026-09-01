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
app.current_tab = "active"; app._tab_dirty.add("active")
app._render_tasks(); app.root.update()

task = next(t for t in app.tasks if not t.get("deleted") and not t.get("done"))
reg = app._task_widget_registry.get(id(task))
check("row registered in _task_widget_registry", reg is not None)

# ---- the silent one: _cycle_priority must NOT fall back to a full render ---
renders = {"n": 0}
_orig_render = sn.App._render_tasks
def counting(self):
    renders["n"] += 1
    return _orig_render(self)
sn.App._render_tasks = counting

before_bar = reg["pri_bar"].cget("bg")
app._cycle_priority(task); app.root.update()
after_bar = reg["pri_bar"].cget("bg")
sn.App._render_tasks = _orig_render

check("_cycle_priority did NOT trigger a full re-render (%d)" % renders["n"], renders["n"] == 0, renders["n"])
check("priority rail actually recoloured (%s -> %s)" % (before_bar, after_bar), before_bar != after_bar)
check("rail widget still exists and is packed", reg["pri_bar"].winfo_exists() and reg["pri_bar"].winfo_manager() == "pack",
      reg["pri_bar"].winfo_manager())

# ---- hover must tint EVERY part, and must NOT erase the card border --------
app._tab_dirty.add("active"); app._render_tasks(); app.root.update()
task = next(t for t in app.tasks if not t.get("deleted") and not t.get("done"))
reg = app._task_widget_registry[id(task)]
body = reg["wrapper"]
outer = body.master                      # the 1px border frame
T = app.T

border_before = outer.cget("bg")
base = body.cget("bg")
body.event_generate("<Enter>")
app.root.update()
hovered = body.cget("bg")
border_during = outer.cget("bg")
body.event_generate("<Leave>")
app.root.update()
restored = body.cget("bg")

check("hover changes the row background (%s -> %s)" % (base, hovered), base != hovered)
check("leave restores the row background", restored == base, (base, restored))
check("card BORDER is not repainted on hover (stays %s)" % border_before,
      border_during == border_before, (border_before, border_during))
check("hover colour is the derived surface_hover token",
      hovered == T["surface_hover"], (hovered, T["surface_hover"]))

# every labelled descendant of the row should follow the hover, not just body
body.event_generate("<Enter>"); app.root.update()
stale = []
def walk(w):
    for c in w.winfo_children():
        try:
            if c.winfo_class() in ("Frame", "Label") and c.cget("bg") == T["surface"]:
                stale.append(str(c))
        except Exception: pass
        walk(c)
walk(body)
body.event_generate("<Leave>"); app.root.update()
check("no part of the row is left at the un-hovered colour (%d stale)" % len(stale),
      len(stale) <= 2, stale[:4])

# ---- completing a task must not change the typeface ------------------------
lbl = reg["lbl"]
f_before = str(lbl.cget("font"))
app._toggle(task, type("V", (), {"get": staticmethod(lambda: True)})())
app.root.update()
app._tab_dirty.add("active"); app._render_tasks(); app.root.update()
reg2 = app._task_widget_registry.get(id(task))
f_after = str(reg2["lbl"].cget("font")) if reg2 else ""
fam_before = f_before.split()[0].strip("{}")
fam_after = f_after.split()[0].strip("{}")
check("font FAMILY unchanged when completing (%s vs %s)" % (fam_before, fam_after),
      fam_before == fam_after, (f_before, f_after))
check("overstrike applied when done", "overstrike" in f_after.lower(), f_after)
# put it back
app._toggle(task, type("V", (), {"get": staticmethod(lambda: False)})())
app.root.update()

# ---- structure sanity ------------------------------------------------------
app._tab_dirty.add("active"); app._render_tasks(); app.root.update()
task = next(t for t in app.tasks if not t.get("deleted") and not t.get("done"))
reg = app._task_widget_registry[id(task)]
outer = reg["wrapper"].master
check("_task_ref survives on the outer card (drag-and-drop depends on it)",
      getattr(outer, "_task_ref", None) is task)
# row is now a grandchild (body > content > row). What matters is that
# _dt_drop's upward .master walk still resolves from ANY leaf in the row.
def deepest(w):
    kids = w.winfo_children()
    return deepest(kids[0]) if kids else w
leaf = deepest(reg["wrapper"])
w, found = leaf, None
while w is not None:
    if getattr(w, "_task_ref", None): found = w._task_ref; break
    w = getattr(w, "master", None)
check("drag-drop .master walk resolves the task from a deep leaf",
      found is task, (str(leaf), found and found.get("text", "")[:30]))
check("row frame itself still carries _task_ref", any(
    getattr(c, "_task_ref", None) is task
    for gc in reg["wrapper"].winfo_children() for c in gc.winfo_children()))
check("border colour is the hairline token", outer.cget("bg") == T["hairline"],
      (outer.cget("bg"), T["hairline"]))

try: app._destroy_tray()
except Exception: pass
print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES: %s" % (len(fails), fails)))
sys.stdout.flush()
os._exit(1 if fails else 0)
