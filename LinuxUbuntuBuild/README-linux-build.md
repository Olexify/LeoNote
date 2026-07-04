# Le'Sticky Notes — Ubuntu/Linux build package

This package updates the Linux build to match the current Windows build layout.

## Included
- `sticky_notes.py` — app source filename expected by the spec
- `build-linux.sh` — Ubuntu build script
- `build-linux.spec` — Linux PyInstaller spec
- `requirements-linux.txt` — Python dependencies
- `README-linux-build.md` — notes

## Ubuntu packages
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tk python3-dev
```

## Build
```bash
bash build-linux.sh
```

## Output
```bash
dist/LeStickyNotes/
```

## Notes
- Linux build uses `icon.png` if present.
- Windows-only EXE metadata from `version_info.txt` and `.ico` EXE icon embedding are omitted on Linux.
- The source contains Windows DPI calls via `ctypes.windll`, but they are wrapped in exception handling, so they should fail safely on Linux.
- Tray support depends on the Linux desktop environment; GNOME may need extensions or AppIndicator compatibility for tray icons.
