"""
Bosco Core - Enhanced Automation Module
"""

import subprocess
import time
import os
import re

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    PYAUTOGUI_AVAILABLE = True
except:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False


class EnhancedAutomation:
    def __init__(self):
        self.command_history = []
        self.app_commands = {
            'notepad': 'notepad',
            'text editor': 'notepad',
            'terminal': 'gnome-terminal',
            'cmd': 'cmd',
            'vscode': 'code',
            'chrome': 'google-chrome',
            'browser': 'google-chrome',
            'firefox': 'firefox',
        }
    
    def parse_command(self, command):
        command = command.lower().strip()
        self.command_history.append(command)
        actions = []
        
        # Pattern: "open [app] and write [text]"
        match = re.search(r'open\s+(?:the\s+)?(\w+)\s+and\s+(?:write|type)\s+(.+)', command)
        if match:
            actions.append(('open_app', match.group(1)))
            actions.append(('wait', 1.5))
            actions.append(('type_text', match.group(2).strip()))
            return actions
        
        # Pattern: "open [app]"
        match = re.search(r'open\s+(?:the\s+)?(\w+(?:\s+\w+)?)', command)
        if match and 'write' not in command and 'type' not in command:
            actions.append(('open_app', match.group(1)))
            return actions
        
        # Pattern: "write [text]" or "type [text]"
        if command.startswith('write ') or command.startswith('type '):
            actions.append(('type_text', command.replace('write ', '').replace('type ', '').strip()))
            return actions
        
        # Pattern: "run [command]"
        if command.startswith('run '):
            actions.append(('run_terminal', command.replace('run ', '').strip()))
            return actions
        
        # Screenshot
        if 'screenshot' in command:
            actions.append(('screenshot',))
        
        return actions
    
    def execute_actions(self, actions):
        results = []
        for action in actions:
            if action[0] == 'open_app':
                results.append(self.open_app(action[1]))
            elif action[0] == 'wait':
                time.sleep(action[1])
            elif action[0] == 'type_text':
                results.append(self.type_text(action[1]))
            elif action[0] == 'run_terminal':
                results.append(self.run_terminal(action[1]))
            elif action[0] == 'screenshot':
                results.append(self.screenshot())
            time.sleep(0.3)
        return results
    
    def process_command(self, command):
        actions = self.parse_command(command)
        if not actions:
            return [f"Could not understand: {command}"]
        return self.execute_actions(actions)
    
    def open_app(self, app_name):
        app = app_name.lower().strip()
        cmd = self.app_commands.get(app, app)
        try:
            if os.name == 'nt':
                subprocess.Popen(cmd, shell=True)
            else:
                subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opened {app_name}"
        except Exception as e:
            return f"Error: {e}"
    
    def type_text(self, text):
        try:
            if PYPERCLIP_AVAILABLE:
                pyperclip.copy(text)
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.hotkey('ctrl', 'v')
                return f"Typed: {text}"
            elif PYAUTOGUI_AVAILABLE:
                pyautogui.write(text)
                return f"Typed: {text}"
            return "No typing available"
        except Exception as e:
            return f"Error: {e}"
    
    def run_terminal(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            out = result.stdout[:500] if result.stdout else result.stderr[:500]
            return out if out else "Done"
        except Exception as e:
            return f"Error: {e}"
    
    def screenshot(self):
        try:
            if PYAUTOGUI_AVAILABLE:
                path = f"{os.path.expanduser('~')}/Pictures/bosco_screenshot_{int(time.time())}.png"
                pyautogui.screenshot(path)
                return f"Saved: {path}"
            return "Not available"
        except Exception as e:
            return f"Error: {e}"


automation = EnhancedAutomation()


def process_command(cmd):
    return automation.process_command(cmd)


if __name__ == "__main__":
    print("Enhanced Automation Ready")
    for cmd in ["open notepad", "type hello world", "run ls"]:
        print(f"> {cmd}")
        print(f"  {process_command(cmd)}")
