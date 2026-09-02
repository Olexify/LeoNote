import sys, os, shutil, tempfile, json, io, datetime as dt
sys.path.insert(0, r"E:\Projects\LeoNote")
import sticky_notes as sn

tmp = tempfile.mkdtemp(); home = os.path.expanduser("~")
for attr, base in (("CONFIG_FILE", ".leonote_config.json"), ("TASKS_FILE", ".leonote_tasks.json"),
                   ("DOCS_FILE", ".leonote_docs.json"), ("HABITS_FILE", ".leonote_habits.json"),
                   ("PRIORITIES_FILE", ".leonote_priorities.json")):
    src, dst = os.path.join(home, base), os.path.join(tmp, base)
    if os.path.exists(src): shutil.copy2(src, dst)
    setattr(sn, attr, dst)
sn.RECUR_FILE = os.path.join(tmp, ".leonote_recurring.json")
sn._rec_cache = None
sn.invalidate_data_cache()

fails = []
def check(label, cond, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label + (("   -> " + str(extra)) if not cond else ""))
    if not cond: fails.append(label)

def texts(w, out=None):
    out = [] if out is None else out
    for c in w.winfo_children():
        try:
            t = c.cget("text")
            if t: out.append(str(t))
        except Exception: pass
        texts(c, out)
    return out

app = sn.App(); app.root.update()
# _rec_init schedules a catch-up via after(400). Drain it now so it cannot
# race the assertions below (the temp recurring file is still empty, so this
# is a no-op that just parks the quiet window; save_recurring clears it).
app._rec_catch_up(render=False)

# ---- 1. wiring exists ------------------------------------------------------
check("_rec_init ran (badge state present)", hasattr(app, "_rec_pending"))
check("single 60s clock (no _rec_job timer chain)",
      getattr(app, "_rec_job", None) is None)
check("_maintenance_tick drives catch-up",
      "_rec_catch_up" in sn.App._maintenance_tick.__code__.co_names,
      sn.App._maintenance_tick.__code__.co_names)

# ---- 2. the user's exact scenario ------------------------------------------
d = sn.load_recurring(force=True)
d["rules"].append(sn._rec_norm({
    "title": "Check free sales on marketplace",
    "rule": {"kind": "weekly", "days": [1]},      # every Tuesday
    "mode": "task", "catchup": "collapse",
    "anchor": "2026-08-01", "created": "2026-08-01",
    "last_fired": "2026-08-18",   # so Tue 25 Aug IS due as of Mon 31 Aug
}))
sn.save_recurring(d)
check("save_recurring dirtied the habits tab (C3)", "habits" in app._tab_dirty)

app._set_tab("habits"); app.root.update()
labels = texts(app.task_frame)
check("recurring rule appears in the Habits tab",
      any("Check free sales on marketplace" in x for x in labels), labels[:14])
check("cadence is described in the UI",
      any("Weekly" in x or "Tu" in x for x in labels), labels[:14])

# ---- 3. catch-up spawns a real task ----------------------------------------
# NOTE: _rec_init's after(400) timer can fire during any update() above and do
# the catch-up itself, so a before/after delta is racy. Assert the invariant
# instead: exactly ONE task exists for this rule, whoever spawned it.
app._rec_catch_up(render=True); app.root.update()
rid = sn.load_recurring()["rules"][0]["id"]
mine = [t for t in app.tasks if t.get("rec_id") == rid]
spawned = [t for t in app.tasks if t.get("rec_id")]
check("catch-up produced exactly one task for the rule (not one per missed week)",
      len(mine) == 1, len(mine))
check("spawned task carries rec_id + rec_date for idempotency",
      spawned and spawned[0].get("rec_id") and spawned[0].get("rec_date"),
      spawned[:1])
check("spawned task title matches the rule",
      spawned and "Check free sales on marketplace" in spawned[0].get("text", ""),
      spawned[0].get("text") if spawned else None)

# ---- 4. idempotency: a second catch-up must not duplicate -------------------
n1 = len(app.tasks)
for _ in range(4):
    app._rec_catch_up(render=False)
check("4 further catch-ups spawn nothing (idempotent)", len(app.tasks) == n1,
      "%d -> %d" % (n1, len(app.tasks)))

# ---- 4b. a rule created during the "nothing due" quiet window must still fire
app._rec_quiet_until = dt.datetime.now() + dt.timedelta(days=1)   # park the tick
d = sn.load_recurring(force=True)
d["rules"].append(sn._rec_norm({
    "title": "Created during quiet window", "rule": {"kind": "daily", "interval": 1},
    "mode": "task", "anchor": "2026-08-01", "created": "2026-08-01",
    "last_fired": "2026-08-29",
}))
sn.save_recurring(d)
check("save_recurring clears the quiet window", app._rec_quiet_until is None)
nq = len(app.tasks)
app._rec_catch_up(render=False)
check("rule added during the quiet window fires immediately",
      any("Created during quiet window" in t.get("text","") for t in app.tasks),
      "%d -> %d" % (nq, len(app.tasks)))

# ---- 5. app closed for a month must still spawn ONE ------------------------
d = sn.load_recurring(force=True)
d["rules"][0]["last_fired"] = "2026-06-01"       # ~3 months of missed Tuesdays
sn.save_recurring(d)                             # also clears the quiet window
for t in list(app.tasks):
    if t.get("rec_id"): app.tasks.remove(t)
n2 = len(app.tasks)
app._rec_catch_up(render=False)
check("closed ~3 months -> collapse spawns ONE task, not ~13",
      len(app.tasks) - n2 == 1, "%d -> %d" % (n2, len(app.tasks)))

# ---- 6. reminder mode renders but does not spawn ---------------------------
d = sn.load_recurring(force=True)
d["rules"].append(sn._rec_norm({
    "title": "Reminder only row", "rule": {"kind": "daily", "interval": 1},
    "mode": "reminder", "anchor": "2026-08-01", "created": "2026-08-01",
    "last_fired": "2026-08-29",
}))
sn.save_recurring(d)
n3 = len(app.tasks)
app._rec_catch_up(render=False)
made = [t for t in app.tasks if "Reminder only row" in t.get("text", "")]
check("mode='reminder' does not spawn a task", not made, made)

# ---- 7. rendering is stable across repeated visits -------------------------
for _ in range(3):
    app._set_tab("active"); app._set_tab("habits"); app.root.update()
labels = texts(app.task_frame)
n_occurrences = sum(1 for x in labels if "Check free sales on marketplace" in x)
check("rule renders exactly once after 3 round-trips (no duplication)",
      n_occurrences == 1, n_occurrences)

# ---- 8. persistence round-trip through the real file -----------------------
raw = json.load(io.open(sn.RECUR_FILE, encoding="utf-8"))
# 3 rules by now: marketplace, quiet-window, reminder-only
check("rules persisted to .leonote_recurring.json", len(raw.get("rules", [])) == 3,
      [r.get("title") for r in raw.get("rules", [])])

# ---- 9. teardown is clean --------------------------------------------------
try:
    app._rec_cancel()
    check("_rec_cancel() is safe", True)
except Exception as e:
    check("_rec_cancel() is safe", False, e)

try: app.root.destroy()
except Exception: pass
print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)
