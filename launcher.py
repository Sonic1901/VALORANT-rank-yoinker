# launcher.py
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

import sys

def enable_per_monitor_dpi():
    if os.name != "nt":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        awareness_context = ctypes.c_void_p(-4)  # PER_MONITOR_AWARE_V2
        if user32.SetProcessDpiAwarenessContext(awareness_context):
            return
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError, ValueError):
        # Older Windows builds may not expose either API.
        pass

enable_per_monitor_dpi()


_instance_mutex = None


def ensure_single_instance():
    global _instance_mutex
    if os.name != "nt":
        return True
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.argtypes = (
        wintypes.LPVOID,
        wintypes.BOOL,
        wintypes.LPCWSTR,
    )
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    _instance_mutex = kernel32.CreateMutexW(
        None,
        False,
        "Local\\VRY-Rank-Yoinker",
    )
    if not _instance_mutex:
        raise OSError("Unable to create the VRY single-instance mutex")
    return kernel32.GetLastError() != 183


VRY_APPDATA = os.path.join(os.getenv('APPDATA'), 'vry')
os.makedirs(VRY_APPDATA, exist_ok=True)

if getattr(sys, 'frozen', False):
    log_file = open(os.path.join(VRY_APPDATA, 'output.log'), 'w', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

import threading
import time
import webview
from src.refresh_control import request_menu_check

class TrackerApi:
    def get_tracker_url(self):
        return os.environ.get("VRY_TRACKER_URL", "")

    def refresh(self):
        request_menu_check()
        return True

def run_backend():
    try:
        import main
    except SystemExit:
        pass
    except Exception:
        import traceback
        with open(os.path.join(VRY_APPDATA, 'launcher_error.txt'), "w") as f:
            f.write(traceback.format_exc())

def wait_for_backend(timeout=30):
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", 1100), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False

if __name__ == "__main__":
    if not ensure_single_instance():
        sys.exit("VRY is already running.")

    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    html_path = os.path.join(base, "vry-gui.html")

    window = webview.create_window(
        title="VALORANT rank yoinker",
        url=f"file:///{html_path}",
        js_api=TrackerApi(),
        width=1440,
        height=900,
        resizable=True,
        min_size=(1000, 650),
        background_color='#0a0b0f',
    )

    webview.start(gui='edgechromium')