"""
Le'Sticky Notes — lightweight sticky task app with Obsidian integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, datetime, uuid, ctypes, sys

try:
    import pystray as _pystray
    from PIL import Image as _PILImage
    _TRAY_OK = True
except Exception:
    _TRAY_OK = False

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".lesticky_config.json")
TASKS_FILE = os.path.join(os.path.expanduser("~"), ".lesticky_tasks.json")

# Replace this file with your full current sticky_notes.py source if needed.
# This package's purpose is to provide the updated Linux build scaffolding that matches the new Windows build.
