import sys, datetime as dt, tempfile, os
sys.path.insert(0, r"E:\Projects\LeoNote")
import sticky_notes as sn

D = dt.date
fails = []
def check(label, cond, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label + (("   -> " + str(extra)) if not cond else ""))
    if not cond: fails.append(label)

def rule(**kw):
    # `created` must be set explicitly: _rec_norm defaults it to the real today,
    # which correctly floors catch-up (a rule cannot back-fill to before it
    # existed) but would silently invalidate these fixtures.
    base = {"title": "t", "anchor": "2026-01-01"}
    base.update(kw)
    base.setdefault("created", base["anchor"])
    return sn._rec_norm(base)

def plan(r, today, keys=(), log=None):
    return sn.rec_catch_up_plan([r], today, set(keys), log or {})

# ---- weekly ---------------------------------------------------------------
r = rule(rule={"kind": "weekly", "days": [1]})              # Tuesday
nx = sn.next_occurrences(r, D(2026, 8, 31), 3)              # from a Monday
check("weekly Tue -> next 3 are Tuesdays", [d.weekday() for d in nx] == [1, 1, 1], nx)
check("weekly Tue -> 7 days apart", (nx[1]-nx[0]).days == 7 and (nx[2]-nx[1]).days == 7, nx)
check("user's example describes correctly",
      sn.rec_describe(rule(rule={"kind": "weekly", "days": [1]})).startswith("Weekly"),
      sn.rec_describe(r))

r = rule(rule={"kind": "weekly", "days": [0, 2, 4]})        # Mon/Wed/Fri
nx = sn.next_occurrences(r, D(2026, 8, 31), 4)
check("weekly multi-day Mon/Wed/Fri", [d.weekday() for d in nx] == [0, 2, 4, 0], nx)

r = rule(rule={"kind": "weekly", "days": [1], "interval": 2})
nx = sn.next_occurrences(r, D(2026, 8, 31), 3)
check("weekly interval=2 -> 14 days apart", (nx[1]-nx[0]).days == 14, nx)

# ---- monthly incl. month-end clamping (from_date is INCLUSIVE) ------------
r = rule(rule={"kind": "monthly", "day": 31}, anchor="2026-01-31")
nx = sn.next_occurrences(r, D(2026, 1, 31), 3)
check("monthly day=31 -> Feb clamps to 28 (2026 not leap)", nx[1] == D(2026, 2, 28), nx)
check("monthly day=31 -> Mar returns to 31 (clamp is not sticky)", nx[2] == D(2026, 3, 31), nx)

r = rule(rule={"kind": "monthly", "day": 31}, anchor="2024-01-31")
nx = sn.next_occurrences(r, D(2024, 1, 31), 2)
check("monthly day=31 -> Feb 2024 clamps to 29 (leap)", nx[1] == D(2024, 2, 29), nx)

r = rule(rule={"kind": "monthly", "day": 15})
nx = sn.next_occurrences(r, D(2026, 8, 31), 2)
check("monthly day=15", [d.day for d in nx] == [15, 15], nx)

# ---- daily / once ---------------------------------------------------------
r = rule(rule={"kind": "daily", "interval": 3}, anchor="2026-08-31")
nx = sn.next_occurrences(r, D(2026, 8, 31), 3)
check("daily interval=3", [(nx[i+1]-nx[i]).days for i in range(2)] == [3, 3], nx)

r = rule(rule={"kind": "once"}, anchor="2026-09-10")
nx = sn.next_occurrences(r, D(2026, 8, 31), 3)
check("once fires exactly one occurrence", len(nx) == 1 and nx[0] == D(2026, 9, 10), nx)

# ---- THE catch-up case: app closed for a week ------------------------------
for mode, expect, why in (("collapse", 1, "one task, not seven"),
                          ("all",      7, "every missed day"),
                          ("skip",     1, "today only, missed ones dropped")):
    r = rule(rule={"kind": "daily", "interval": 1}, anchor="2026-08-01",
             catchup=mode, last_fired="2026-08-24")
    spawns, updates, fired = plan(r, D(2026, 8, 31))
    check("catchup=%-9s after 7 days closed -> %d spawn(s), %s" % (mode, expect, why),
          len(spawns) == expect, [s["date"] for s in spawns])

# collapse must report how many were missed, so the UI can say "6 missed"
r = rule(rule={"kind": "daily", "interval": 1}, anchor="2026-08-01",
         catchup="collapse", last_fired="2026-08-24")
spawns, updates, fired = plan(r, D(2026, 8, 31))
check("collapse reports missed count", spawns[0]["missed"] == 6, spawns[0]["missed"])

# ---- idempotency ----------------------------------------------------------
r = rule(rule={"kind": "weekly", "days": [1]}, anchor="2026-08-01",
         catchup="collapse", last_fired="2026-08-24")
spawns, updates, fired = plan(r, D(2026, 9, 2))
check("first run spawns", len(spawns) == 1, spawns)
r.update(updates[r["id"]])                      # apply last_fired advance
spawns2, _, _ = plan(r, D(2026, 9, 2))
check("2nd run after last_fired advance spawns nothing", len(spawns2) == 0, spawns2)

# existing_keys is the second idempotency guard
r = rule(rule={"kind": "weekly", "days": [1]}, anchor="2026-08-01", last_fired="2026-08-24")
s1, _, _ = plan(r, D(2026, 9, 2))
key = s1[0]["key"]
s2, _, _ = plan(r, D(2026, 9, 2), keys=[key])
check("existing occurrence key blocks a duplicate spawn", len(s2) == 0, s2)

# a completed occurrence is never re-spawned
r = rule(rule={"kind": "weekly", "days": [1]}, anchor="2026-08-01", last_fired="2026-08-24")
s3, _, _ = plan(r, D(2026, 9, 2), log={r["id"]: ["2026-09-01"]})
check("already-completed occurrence is not re-spawned", len(s3) == 0, s3)

# snoozed rule produces nothing and does NOT advance
r = rule(rule={"kind": "daily"}, anchor="2026-08-01", snooze_until="2026-09-05",
         last_fired="2026-08-24")
s4, u4, _ = plan(r, D(2026, 8, 31))
check("snoozed rule spawns nothing and does not advance", not s4 and not u4, (s4, u4))

# inactive / deleted
for flag in ({"active": False}, {"deleted": True}):
    r = rule(rule={"kind": "daily"}, anchor="2026-08-01", last_fired="2026-08-24", **flag)
    s5, _, _ = plan(r, D(2026, 8, 31))
    check("rule with %s spawns nothing" % flag, len(s5) == 0, s5)

# spawn cap + truncation flag
r = rule(rule={"kind": "daily", "interval": 1}, anchor="2020-01-01", catchup="all")
occ, trunc = sn.due_occurrences(r, None, D(2026, 8, 31))
check("spawn capped at REC_MAX_SPAWN (%d) and flags truncation" % sn.REC_MAX_SPAWN,
      len(occ) <= sn.REC_MAX_SPAWN and trunc, (len(occ), trunc))

# ---- skip / until ---------------------------------------------------------
r = rule(rule={"kind": "weekly", "days": [1]}, anchor="2026-08-01",
         skip=["2026-09-01"], catchup="all", last_fired="2026-08-25")
occ, _ = sn.due_occurrences(r, r["last_fired"], D(2026, 9, 1))
check("skipped occurrence is not returned", D(2026, 9, 1) not in occ, occ)

r = rule(rule={"kind": "weekly", "days": [1]}, anchor="2026-08-01", until="2026-09-01")
nx = sn.next_occurrences(r, D(2026, 9, 2), 3)
check("until= stops future occurrences", nx == [], nx)

# ---- malformed input must never raise --------------------------------------
ok = True
for bad in ({"kind": "weekly", "days": ["x", None, 99]}, {"kind": "zzz"},
            {"kind": "monthly", "day": 0}, {}, None, [], "nope"):
    try:
        rr = sn._rec_norm({"rule": bad})
        sn.next_occurrences(rr, D(2026, 8, 31), 2)
        sn.rec_describe(rr)
        sn.rec_next_due(rr, D(2026, 8, 31))
        plan(rr, D(2026, 8, 31))
    except Exception as e:
        ok = False
        check("malformed rule %r does not raise" % (bad,), False, e)
check("all 7 malformed rule shapes normalized without raising", ok)

# ---- persistence -----------------------------------------------------------
sn.RECUR_FILE = os.path.join(tempfile.mkdtemp(), "rec.json")
sn._rec_cache = None
d = sn.load_recurring(force=True)
d["rules"].append(rule(title="Check free sales on marketplace",
                       rule={"kind": "weekly", "days": [1]}))
sn.save_recurring(d)
sn._rec_cache = None
back = sn.load_recurring(force=True)
check("save/load round-trip preserves the rule",
      len(back["rules"]) == 1 and back["rules"][0]["title"] == "Check free sales on marketplace", back)
check("atomic write left no .tmp behind", not os.path.exists(sn.RECUR_FILE + ".tmp"))

# corrupt file must not crash
open(sn.RECUR_FILE, "w").write("{not json")
sn._rec_cache = None
check("corrupt recurring file -> empty default, no crash",
      sn.load_recurring(force=True)["rules"] == [])

print("\n%s" % ("ALL PASSED" if not fails else "%d FAILURES: %s" % (len(fails), fails)))
sys.exit(1 if fails else 0)
