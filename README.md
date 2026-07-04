# 📝 Le'Sticky Notes

A **lightweight, standalone sticky notes / task app for Windows** with optional **Obsidian** integration.

Made for the “let me jot this down real quick” moments — without Electron bloat, cloud accounts, or productivity theater.

<img width="2029" height="1384" alt="Le'Sticky Notes screenshot" src="https://github.com/user-attachments/assets/29d6684b-e5ab-4b4c-b995-53ed7a7d9b3c" />

---

## ✨ Features

- ✅ Fast **tasks + subtasks**
- 🚦 **Priority levels** (none → low → medium → high) with color indicator
- ✍️ **Inline editing** (double-click to rename)
- 🧷 **Drag & drop reordering**
- 🗂️ **Tasks / Archive** tabs (completed tasks go to Archive)
- 🗑️ **Trash with recovery** (auto-purges after ~24h)
- 🎨 Multiple **themes** (Yellow / Dark / Light / Sakura / Mint / Ocean)
- 🔍 **UI scaling** (Ctrl + Scroll)
- 📌 **Always on top** toggle
- 🔔 Optional **system tray** support
- 📥 **Import / Export** tasks as JSON
- 🪨 **Local-first**: saves config + tasks as JSON in your home folder

---

## 🪨 Obsidian integration (optional)

Point Le'Sticky Notes to a Markdown note in your vault, and it will sync tasks into that file.
Open and completed tasks are kept in separate sections, and tasks are updated by internal IDs to avoid duplicates.

No cloud. No accounts. Your vault stays yours.

---

## 🚀 How to run

### Option 1: Run the included `.exe`
Download and launch the executable — no install needed.

### Option 2: Run from source
```bash
python sticky_notes.py
```

> Tray mode is optional and may require extra deps (e.g. `pystray`, `Pillow`).  
> The app still works fine without tray support.

---

## 🛠️ Build

This repo includes both the source and build setup.

To build the `.exe`, run the included batch script:
```bat
build.bat
```

(If your script has a different name — replace it here.)

---

## ⌨️ Quick reference

| Action | How |
|---|---|
| Add task | Type + `Enter` / **Add** button |
| Edit task/subtask | Double-click it |
| Add subtask | ⊞ button |
| Cycle priority | `!` button |
| Reorder | Drag the grip handle |
| Zoom UI | `Ctrl + Scroll` |
| Trash / recover | 🗑️ (within ~24h) |

---

## 💡 Summary

- Tiny sticky task window that stays out of your way  
- Tasks, subtasks, priorities, archive & recoverable trash  
- Optional Obsidian sync (Markdown note)  
- Fully local storage (JSON)  
- Open source + prebuilt `.exe` + build via `.bat`

> “I’ll just remember it” is a lie. Write it down.


## 🪨 Obsidian integration (optional)

Le'Sticky Notes works **fully standalone** — Obsidian is not required.

If you *do* use Obsidian, just set a target Markdown note and the app will sync tasks into it.
Works with **any Obsidian vault** (yours, mine, portable vault on a USB stick — doesn’t matter).

### How to hook it up

Open **⚙ Settings → Obsidian** and choose a `.md` file inside your vault, for example:

```text
E:\Productivity\ObsidianUltimate\Diary\LeStickyTasks.md
```

What happens next:

- Open tasks go into the **OPEN** section, completed tasks into **CLOSED**
- Subtasks are rendered inline as `[ ]` / `[x]`
- Tasks are tracked by internal IDs, so edits update in place (no duplicate spam)
- Trashing a task removes its line from the note

### Recommended vault (optional): ObsidianUltimate

If you want a ready-to-use productivity vault template, I maintain:

👉 ObsidianUltimate: <PUT_YOUR_REPO_LINK_HERE>

Le'Sticky Notes is not locked to ObsidianUltimate — it just pairs nicely with it.

> ⚠️ ObsidianUltimate note: don’t rename `Diary` or `Utilities` (some automations depend on them).
