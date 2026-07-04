"""
LeoNote — lightweight sticky task app with Obsidian integration
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

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".leonote_config.json")
TASKS_FILE = os.path.join(os.path.expanduser("~"), ".leonote_tasks.json")
