# LeoNote — Ubuntu/Linux build package

This updated package matches the latest LeoNote Python source and Windows spec naming.

## Included
- sticky_notes.py
- build-linux.spec
- build-linux.sh
- requirements-linux.txt
- README-linux-build.md

## Build on Ubuntu
1. Put `icon.png` in this folder if desired.
2. Run `bash build-linux.sh`
3. Output: `dist/LeoNote/`

## Notes
- App name is `LeoNote` in the updated Windows spec.
- Linux uses a native executable, not `.exe`.
- Linux build excludes Windows-only modules and does not use Windows version metadata.
- The updated source stores data in `~/.leonote_config.json` and `~/.leonote_tasks.json`.
- The updated source also adds `run_at_startup` and more themes such as `peach`, `rose`, `lavender`, `sky`, `slate`, and dark variants. 
