# 📝 Leo Note

A **lightweight, standalone sticky notes / task app for Windows** with optional **Obsidian** integration.

Made for the “let me jot this down real quick” moments - without Electron bloat, cloud accounts, or productivity theater. On image you can see the Obsidian live integration as backup of solved tasks.

<img width="1904" height="1440" alt="LeoNote screenshot" src="https://github.com/user-attachments/assets/51683988-0b99-4197-885e-b099a5ad3639" />

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
<!-- 
---

## 🪨 Obsidian integration (optional)

Point LeoNote to a Markdown note in your vault, and it will sync tasks into that file.
Open and completed tasks are kept in separate sections, and tasks are updated by internal IDs to avoid duplicates.

No cloud. No accounts. Your vault stays yours.
-->
---

## 🚀 How to run

### Option 1: Run the included `.exe`
Download and launch the executable - no install needed.

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

(If your script has a different name - replace it here.)

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

LeoNote works **fully standalone** - Obsidian is not required.

If you *do* use Obsidian, just set a target Markdown note and the app will sync tasks into it.
Works with **any Obsidian vault** (yours, mine, portable vault on a USB stick - doesn’t matter).

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

👉 ObsidianUltimate: <a href="https://github.com/Olexify/ObsidianUltimate">Github Repo</a>

LeoNote is not locked to ObsidianUltimate - it just pairs nicely with it as notes backup.

> ⚠️ ObsidianUltimate note: don’t rename `Diary` or `Utilities` (some automations depend on them).


---


## 🪟 Windows StartUP 🚀 (Resolved in settings now, but left in guide for curious ones)

If you want LeoNote to open automatically when Windows starts, you can add it to the **Startup** folder.

This is useful if you want your sticky tasks ready immediately after login.

<img width="1364" height="846" alt="Opening the Windows Startup folder with shell:startup and placing the LeStickyNotes shortcut there" src="https://github.com/user-attachments/assets/d1d6ffc5-74ab-4c84-89aa-131d32b232cb" />

### Method 1: Add shortcut to Startup folder

1. Press:

```text
Win + R
```

2. Type:

```text
shell:startup
```

3. Press **OK**

This opens the Windows Startup folder.

4. Create a shortcut to `LeoNote.exe`

You can do this by:

- Right-clicking the `.exe`
- Choosing **Create shortcut**
- Moving that shortcut into the Startup folder

Once the shortcut is inside that folder, Windows will launch Leo Notes automatically on login.

### ⚠️ Important note

Make sure the shortcut points to the correct `.exe` location.

If you later move the app to another folder, the startup shortcut may stop working until you recreate it.

### Optional in-app tray behavior

If you want LeoNote to start more quietly, you can combine Windows startup with:

- **Show in tray**
- **Start hidden to tray**

That way the app launches with Windows without immediately opening a full window.

---


<img width="1800" height="170" alt="image" src="https://github.com/user-attachments/assets/8acecd7e-c0d2-41c0-9fcc-0893d07bbbf3" />
</p>

<p align="center">
<i>"I-it's so lightweight"</i> ✨
</p>

