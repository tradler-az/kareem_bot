"""
Bosco Core - Human-like Navigator
Navigate PC and Web like humans do - click, scroll, select, browse
"""

import os
import subprocess
import time
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


class HumanNavigator:
    """
    Human-like navigation for PC and Web
    Simulates how humans interact with computers
    """

    def __init__(self):
        self.platform = os.uname().sysname
        self.last_click_position = None
        
        # Check available tools
        self.has_pyautogui = False
        self.has_xdotool = False
        self.has_selenium = False
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check what automation tools are available"""
        try:
            import pyautogui
            self.has_pyautogui = True
        except:
            pass
        
        # Check xdotool
        result = subprocess.run('which xdotool', shell=True, capture_output=True)
        self.has_xdotool = result.returncode == 0
        
        # Check selenium
        try:
            from selenium import webdriver
            self.has_selenium = True
        except:
            pass

    def _run_cmd(self, cmd: str) -> str:
        """Run shell command"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout + result.stderr
        except:
            return ""

    # === MOUSE OPERATIONS (Human-like) ===
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> str:
        """Move mouse to position with human-like speed"""
        if self.has_pyautogui:
            import pyautogui
            pyautogui.moveTo(x, y, duration=duration)
            self.last_click_position = (x, y)
            return f"Moved mouse to ({x}, {y})"
        
        if self.has_xdotool:
            self._run_cmd(f"xdotool mousemove {x} {y}")
            self.last_click_position = (x, y)
            return f"Moved mouse to ({x}, {y})"
        
        return "No mouse control available"
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', double: bool = False) -> str:
        """
        Click at position or current position
        
        Args:
            x, y: Optional coordinates
            button: left, right, middle
            double: Double click
        """
        if x is not None and y is not None:
            self.move_mouse(x, y)
        
        clicks = 2 if double else 1
        btn = button
        
        if self.has_pyautogui:
            import pyautogui
            for _ in range(clicks):
                pyautogui.click(button=btn)
                time.sleep(0.1)
            return f"Clicked {button} at ({x}, {y})" if x else f"Clicked {button}"
        
        if self.has_xdotool:
            cmd = f"xdotool click 1"  # left
            if button == 'right':
                cmd = f"xdotool click 3"
            elif button == 'middle':
                cmd = f"xdotool click 2"
            
            if double:
                cmd += " && xdotool click 1"
            
            self._run_cmd(cmd)
            return f"Clicked {button}"
        
        return "No click control available"
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Double click"""
        return self.click(x, y, double=True)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Right click"""
        return self.click(x, y, button='right')
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> str:
        """Drag from one position to another"""
        if self.has_pyautogui:
            import pyautogui
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=0.5)
            pyautogui.mouseUp()
            return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
        
        if self.has_xdotool:
            self._run_cmd(f"xdotool mousemove {start_x} {start_y}")
            self._run_cmd("xdotool mousedown 1")
            self._run_cmd(f"xdotool mousemove {end_x} {end_y}")
            self._run_cmd("xdotool mouseup 1")
            return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
        
        return "No drag control available"
    
    def hover(self, x: int, y: int, duration: float = 1.0) -> str:
        """Hover over position"""
        self.move_mouse(x, y)
        time.sleep(duration)
        return f"Hovered at ({x}, {y}) for {duration}s"
    
    # === KEYBOARD OPERATIONS (Human-like) ===
    
    def type_text(self, text: str, delay: float = 0.05) -> str:
        """Type text with slight delays (human-like)"""
        if self.has_pyautogui:
            import pyautogui
            pyautogui.write(text, interval=delay)
            return f"Typed: {text}"
        
        if self.has_xdotool:
            # Escape special characters
            text = text.replace("'", "\\'")
            self._run_cmd(f"xdotool type '{text}'")
            return f"Typed: {text}"
        
        return "No keyboard control available"
    
    def press_key(self, key: str) -> str:
        """Press a key"""
        if self.has_pyautogui:
            import pyautogui
            pyautogui.press(key)
            return f"Pressed: {key}"
        
        if self.has_xdotool:
            self._run_cmd(f"xdotool key {key}")
            return f"Pressed: {key}"
        
        return "No key control available"
    
    def press_keys(self, *keys) -> str:
        """Press multiple keys together (e.g., ctrl+c)"""
        combo = '+'.join(keys)
        return self.press_key(combo)
    
    def hotkey(self, *keys) -> str:
        """Press hotkey combination"""
        return self.press_keys(*keys)
    
    # === SCROLL OPERATIONS (Human-like) ===
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """
        Scroll up or down
        
        Args:
            clicks: Positive = up, Negative = down
            x, y: Optional position to scroll at
        """
        if x is not None and y is not None:
            self.move_mouse(x, y)
        
        if self.has_pyautogui:
            import pyautogui
            pyautogui.scroll(clicks)
            direction = "up" if clicks > 0 else "down"
            return f"Scrolled {direction} {abs(clicks)} clicks"
        
        if self.has_xdotool:
            # 4 = up, 5 = down for xdotool
            button = 4 if clicks > 0 else 5
            for _ in range(abs(clicks)):
                self._run_cmd(f"xdotool click {button}")
            direction = "up" if clicks > 0 else "down"
            return f"Scrolled {direction} {abs(clicks)} clicks"
        
        return "No scroll control available"
    
    def scroll_up(self, clicks: int = 3) -> str:
        """Scroll up"""
        return self.scroll(clicks)
    
    def scroll_down(self, clicks: int = 3) -> str:
        """Scroll down"""
        return self.scroll(-clicks)
    
    def page_up(self) -> str:
        """Page up"""
        return self.press_key('Prior')
    
    def page_down(self) -> str:
        """Page down"""
        return self.press_key('Next')
    
    # === SELECTION OPERATIONS ===
    
    def select_all(self) -> str:
        """Select all (Ctrl+A)"""
        return self.hotkey('ctrl', 'a')
    
    def copy(self) -> str:
        """Copy (Ctrl+C)"""
        return self.hotkey('ctrl', 'c')
    
    def paste(self) -> str:
        """Paste (Ctrl+V)"""
        return self.hotkey('ctrl', 'v')
    
    def cut(self) -> str:
        """Cut (Ctrl+X)"""
        return self.hotkey('ctrl', 'x')
    
    def select_text(self, start_x: int, start_y: int, end_x: int, end_y: int) -> str:
        """Select text by dragging"""
        return self.drag(start_x, start_y, end_x, end_y)
    
    # === WINDOW OPERATIONS ===
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        if self.has_pyautogui:
            import pyautogui
            return pyautogui.size()
        
        if self.has_xdotool:
            output = self._run_cmd("xdotool getdisplaygeometry")
            parts = output.strip().split()
            if len(parts) >= 2:
                return (int(parts[0]), int(parts[1]))
        
        return (1920, 1080)  # Default
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position"""
        if self.has_pyautogui:
            import pyautogui
            return pyautogui.position()
        
        if self.has_xdotool:
            output = self._run_cmd("xdotool getmouselocation")
            match = re.search(r'x:(\d+)\s+y:(\d+)', output)
            if match:
                return (int(match.group(1)), int(match.group(2)))
        
        return (0, 0)
    
    def open_window(self, app: str) -> str:
        """Open a window (app)"""
        # Use xdg-open for generic opening
        result = self._run_cmd(f"xdg-open {app} &")
        return f"Opened: {app}"
    
    def close_window(self) -> str:
        """Close current window (Alt+F4)"""
        return self.hotkey('alt', 'f4')
    
    def minimize_window(self) -> str:
        """Minimize current window"""
        return self.hotkey('super', 'down')
    
    def maximize_window(self) -> str:
        """Maximize current window"""
        return self.hotkey('super', 'up')
    
    def switch_window(self) -> str:
        """Switch to next window (Alt+Tab)"""
        return self.hotkey('alt', 'tab')
    
    # === WEB NAVIGATION ===
    
    def open_browser(self, url: str = "https://google.com") -> str:
        """Open web browser"""
        browsers = ['firefox', 'google-chrome', 'brave-browser', 'chromium']
        
        for browser in browsers:
            result = subprocess.run(
                f"which {browser}",
                shell=True,
                capture_output=True
            )
            if result.returncode == 0:
                self._run_cmd(f"{browser} '{url}' &")
                return f"Opened {browser} with {url}"
        
        # Fallback to xdg-open
        self._run_cmd(f"xdg-open '{url}'")
        return f"Opened browser with {url}"
    
    def navigate_to(self, url: str) -> str:
        """Navigate to URL (opens in browser)"""
        return self.open_browser(url)
    
    def click_link(self, link_text: str) -> str:
        """Click a link by text (simulated)"""
        # This would require more complex DOM interaction
        # For now, just type and enter
        self.type_text(link_text)
        self.press_key('Enter')
        return f"Searched for: {link_text}"
    
    def fill_form(self, field_value_dict: Dict[str, str]) -> str:
        """Fill form fields"""
        for field, value in field_value_dict.items():
            self.type_text(value)
            self.press_key('Tab')
        return f"Filled {len(field_value_dict)} fields"
    
    # === COMMON HUMAN WORKFLOWS ===
    
    def find_and_click(self, image_name: str) -> str:
        """Find image on screen and click it (if screenshot available)"""
        if not self.has_pyautogui:
            return "Image recognition not available"
        
        try:
            import pyautogui
            location = pyautogui.locateOnScreen(f"images/{image_name}.png")
            if location:
                center = pyautogui.center(location)
                self.click(center.x, center.y)
                return f"Found and clicked {image_name}"
        except:
            pass
        
        return f"Could not find {image_name} on screen"
    
    def wait_for_image(self, image_name: str, timeout: int = 10) -> bool:
        """Wait for image to appear on screen"""
        if not self.has_pyautogui:
            return False
        
        try:
            import pyautogui
            location = pyautogui.locateOnScreen(f"images/{image_name}.png", timeout=timeout)
            return location is not None
        except:
            return False
    
    # === COORDINATE HELPERS ===
    
    def get_center_of_screen(self) -> Tuple[int, int]:
        """Get center of screen"""
        width, height = self.get_screen_size()
        return (width // 2, height // 2)
    
    def click_center(self) -> str:
        """Click center of screen"""
        x, y = self.get_center_of_screen()
        return self.click(x, y)
    
    def click_menu(self) -> str:
        """Click menu button (usually top left)"""
        return self.click(50, 50)
    
    def click_close_button(self) -> str:
        """Click window close button (usually top right)"""
        width, _ = self.get_screen_size()
        return self.click(width - 50, 50)
    
    # === STATUS ===
    
    def get_status(self) -> Dict[str, Any]:
        """Get navigator status"""
        x, y = self.get_cursor_position()
        width, height = self.get_screen_size()
        
        return {
            'cursor_position': {'x': x, 'y': y},
            'screen_size': {'width': width, 'height': height},
            'tools': {
                'pyautogui': self.has_pyautogui,
                'xdotool': self.has_xdotool,
                'selenium': self.has_selenium
            }
        }


# Global instance
_navigator = None

def get_human_navigator() -> HumanNavigator:
    """Get human navigator instance"""
    global _navigator
    if _navigator is None:
        _navigator = HumanNavigator()
    return _navigator


# Convenience functions
def move_mouse(x: int, y: int) -> str:
    return get_human_navigator().move_mouse(x, y)

def click(x: int = None, y: int = None) -> str:
    return get_human_navigator().click(x, y)

def double_click(x: int = None, y: int = None) -> str:
    return get_human_navigator().double_click(x, y)

def type_text(text: str) -> str:
    return get_human_navigator().type_text(text)

def press_key(key: str) -> str:
    return get_human_navigator().press_key(key)

def scroll(clicks: int) -> str:
    return get_human_navigator().scroll(clicks)

def scroll_up(clicks: int = 3) -> str:
    return get_human_navigator().scroll_up(clicks)

def scroll_down(clicks: int = 3) -> str:
    return get_human_navigator().scroll_down(clicks)

def open_browser(url: str = "https://google.com") -> str:
    return get_human_navigator().open_browser(url)


if __name__ == "__main__":
    print("=== Human Navigator Test ===\n")
    
    nav = HumanNavigator()
    
    print("Status:")
    print(nav.get_status())
    
    print("\nScreen size:", nav.get_screen_size())
    print("Cursor position:", nav.get_cursor_position())

