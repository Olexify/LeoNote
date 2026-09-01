# LeoNote — Build Instructions

## Requirements
- Python 3.9+  (tested up to 3.14)
- Windows 10+

## Install dependencies
```bat
pip install pyinstaller pystray pillow
```

## Icon files (required for proper EXE icon)
Place both files in the project root before building:
- `icon.ico`  — used as the EXE/taskbar icon by Windows
- `icon.png`  — used by the running app window and system tray

## Build
```bat
cd E:\Projects\LeoNote
pyinstaller --clean --noconfirm build.spec
```

Output: `dist\LeoNote\LeoNote.exe`

## Why onedir (not onefile)
The build is **onedir**: the EXE sits in `dist\LeoNote\` next to its DLLs and
data, and UPX is off.

Onefile re-extracts the whole ~20 MB bundle to a fresh `%TEMP%\_MEIxxxxx`
folder on *every* launch, then Defender rescans it (new path each time, so the
scan never caches). Measured on the dev machine, warm:

| build   | launch to visible window | on disk |
|---------|--------------------------|---------|
| onefile | ~2870 ms                 | 20.7 MB |
| onedir  | ~1350 ms                 | 44.8 MB |

Trading disk space for ~2.4x faster startup. Do not re-enable `upx` or drop
the `COLLECT` block without re-measuring.

To distribute, zip `dist\LeoNote\` or wrap it in an installer — the EXE alone
will not run.

## If you get WinError 5 (access denied on old EXE)
The old EXE is still running or locked by Explorer/antivirus:
```bat
taskkill /IM LeoNote.exe /F
rmdir /S /Q dist\LeoNote
pyinstaller --clean --noconfirm build.spec
```

## Shortcuts point into dist\LeoNote\
`LeoNote.lnk`, `Leo Note.lnk`, and the Startup entry
(`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LeoNote.bat`)
all target `dist\LeoNote\LeoNote.exe`. The app's own **Run at startup** toggle
rewrites that .bat from `sys.executable`, so it stays correct on rebuild.

## Data files (stored in user home)
- `%USERPROFILE%\.leonote_config.json`      — settings
- `%USERPROFILE%\.leonote_tasks.json`       — tasks
- `%USERPROFILE%\.leonote_docs.json`        — docs
- `%USERPROFILE%\.leonote_habits.json`      — habits
- `%USERPROFILE%\.leonote_priorities.json`  — priorities
