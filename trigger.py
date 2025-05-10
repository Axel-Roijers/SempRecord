import tray
import recorder
import threading
import settings
from time import sleep
from util import getForegroundWindowTitle
import bouncer


# ==========AUTO-TRIGGER==========
_thread = None
def trigger_thread(interval=5):
    """Automatically starts and stops recording based on the foreground window title."""
    sleep(interval)
    while settings.USE_AUTOTRIGGER:
        sleep(interval)
        window_title = getForegroundWindowTitle()
        if bouncer.isWhiteListed(window_title) and recorder.ACTIVE_RECORDER is None:
            tray.start()

def enable():
    """start the recording trigger thread"""
    settings.USE_AUTOTRIGGER = True
    _thread =  threading.Thread(target=trigger_thread, name="Auto Trigger Thread", daemon=False)
    _thread.start()

def disable():
    """stop the recording trigger thread"""
    global _thread
    settings.USE_AUTOTRIGGER = False
    if _thread is not None:
        _thread.join()
        _thread = None

enable()