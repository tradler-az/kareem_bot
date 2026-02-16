"""Kareem OS - Full PC Control Module"""
import subprocess
import os
import time
from pathlib import Path

# Try importing GUI libraries, with fallbacks
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    PYAUTOGUI_AVAILABLE = True
except Exception as e:
    print(f"Note: pyautogui not available: {e}")
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False


class PCControl:
    """Full PC control - mouse, keyboard, windows, apps, files"""
    
    def __init__(self):
        pass
        
    # === MOUSE CONTROL ===
    def move_mouse(self, x, y):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.moveTo(x, y)
        return f"Move to {x}, {y}"
    
    def click(self, x=None, y=None, button='left'):
        """Click at position or current position"""
        if PYAUTOGUI_AVAILABLE:
            try:
                if x is not None and y is not None:
                    pyautogui.click(x, y, button=button)
                else:
                    pyautogui.click(button=button)
            except Exception as e:
                return f"Click error: {e}"
        return f"Clicked {button}"
    
    def double_click(self, x=None, y=None):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.doubleClick(x, y)
        return "Double clicked"
    
    def right_click(self, x=None, y=None):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.rightClick(x, y)
        return "Right clicked"
    
    def scroll(self, amount):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.scroll(amount)
        return f"Scrolled {amount}"
    
    # === KEYBOARD CONTROL ===
    def type_text(self, text):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.write(text)
        return f"Typed: {text}"
    
    def press_key(self, key):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press(key)
        return f"Pressed {key}"
    
    def hotkey(self, *keys):
        if PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey(*keys)
        return f"Hotkey: {'+'.join(keys)}"
    
    # === WINDOW CONTROL ===
    def get_screen_size(self):
        if PYAUTOGUI_AVAILABLE:
            return pyautogui.size()
        return (1920, 1080)  # Default
    
    def screenshot(self, path=None):
        if not path:
            path = f"/home/tradler/Pictures/screenshot_{int(time.time())}.png"
        if PYAUTOGUI_AVAILABLE:
            pyautogui.screenshot(path)
        return f"Saved: {path}"
    
    # === APPLICATION CONTROL ===
    def open_app(self, app_name):
        apps = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "vscode": "code",
            "terminal": "gnome-terminal",
            "file manager": "nautilus",
            "spotify": "spotify",
            "discord": "discord",
        }
        cmd = apps.get(app_name.lower(), app_name)
        subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opened {app_name}"
    
    def close_app(self, app_name):
        subprocess.run(["pkill", "-f", app_name], stdout=subprocess.DEVNULL)
        return f"Closed {app_name}"
    
    # === FILE OPERATIONS ===
    def find_file(self, name, path="/home"):
        result = []
        try:
            for p in Path(path).rglob(f"*{name}*"):
                result.append(str(p))
        except:
            pass
        return result[:10]
    
    def open_file(self, filepath):
        subprocess.Popen(["xdg-open", filepath], stdout=subprocess.DEVNULL)
        return f"Opened {filepath}"
    
    # === SYSTEM ===
    def get_clipboard(self):
        if PYPERCLIP_AVAILABLE:
            return pyperclip.paste()
        return ""
    
    def set_clipboard(self, text):
        if PYPERCLIP_AVAILABLE:
            pyperclip.copy(text)
        return "Copied to clipboard"
    
    def open_url(self, url):
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL)
        return f"Opened {url}"
    
    # === REAL-TIME ANALYSIS ===
    def analyze_screen(self):
        if PYAUTOGUI_AVAILABLE:
            screenshot = pyautogui.screenshot()
            return f"Screen captured, size: {screenshot.size}"
        return "Screen analysis ready"


# Global instance
_pc = PCControl()

# Quick functions
def click(x=None, y=None): return _pc.click(x, y)
def type_text(text): return _pc.type_text(text)
def press_key(key): return _pc.press_key(key)
def hotkey(*keys): return _pc.hotkey(*keys)
def screenshot(): return _pc.screenshot()
def open_app(app): return _pc.open_app(app)
def close_app(app): return _pc.close_app(app)
def find_file(name): return _pc.find_file(name)
def open_file(path): return _pc.open_file(path)
def get_clipboard(): return _pc.get_clipboard()
def set_clipboard(text): return _pc.set_clipboard(text)
def open_url(url): return _pc.open_url(url)
def analyze_screen(): return _pc.analyze_screen()

if __name__ == "__main__":
    print("PC Control module ready")
    print("Screen size:", _pc.get_screen_size())

