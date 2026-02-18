"""
Bosco Core - Full System Control Module
Complete PC control with terminal access, web browsing, and system management
"""

import os
import sys
import subprocess
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import urllib.request
import urllib.parse

# For web scraping
try:
    from bs4 import BeautifulSoup
    BS_AVAILABLE = True
except:
    BS_AVAILABLE = False

# For GUI automation
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    PYAUTOGUI_AVAILABLE = True
except:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except:
    pyperclip = None


class TerminalControl:
    """Execute terminal commands with full system access"""
    
    def __init__(self):
        self.command_history = []
        
    def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a terminal command and return output"""
        self.command_history.append(command)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out',
                'stdout': '',
                'stderr': 'Timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': str(e)
            }
    
    def run_background(self, command: str):
        """Run command in background"""
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return f"Running in background: {command}"
    
    def get_output(self, command: str) -> str:
        """Get command output as string"""
        result = self.execute(command)
        if result['success']:
            output = result['stdout'] or result['stderr']
            return output[:2000] if output else "Command executed successfully (no output)"
        return f"Error: {result.get('error', 'Unknown error')}"


class WebBrowser:
    """Web browsing and scraping capabilities"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web and return results"""
        try:
            # Use DuckDuckGo HTML
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            req = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read()
            
            if BS_AVAILABLE:
                soup = BeautifulSoup(html, 'html.parser')
                results = []
                
                for result in soup.select('.result__body')[:num_results]:
                    title_elem = result.select_one('.result__a')
                    snippet_elem = result.select_one('.result__snippet')
                    link_elem = result.select_one('.result__url')
                    
                    if title_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': title_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                        })
                
                return results
            else:
                # Fallback to simple text parsing
                return [{'title': 'Search results available', 'url': url, 'snippet': 'Install beautifulsoup4 for better results'}]
                
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_page_content(self, url: str) -> str:
        """Get content of a webpage"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read()
            
            if BS_AVAILABLE:
                soup = BeautifulSoup(html, 'html.parser')
                # Remove script and style
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                # Clean whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                return text[:3000]
            else:
                return html.decode('utf-8', errors='ignore')[:3000]
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_wikipedia(self, topic: str) -> str:
        """Get Wikipedia summary"""
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(req, timeout=10)
            data = json.loads(response.read())
            return f"{data.get('extract', 'No information found')}\n\nSource: Wikipedia"
        except Exception as e:
            return f"Error getting Wikipedia: {str(e)}"


class FullSystemControl:
    """Complete system control - all PC operations"""
    
    def __init__(self):
        self.terminal = TerminalControl()
        self.browser = WebBrowser()
        
        # Application database
        self.apps = {
            # Web browsers
            'chrome': 'google-chrome',
            'google chrome': 'google-chrome',
            'firefox': 'firefox',
            'brave': 'brave-browser',
            
            # Development
            'vscode': 'code',
            'vs code': 'code',
            'visual studio': 'code',
            'terminal': 'gnome-terminal',
            'term': 'gnome-terminal',
            'vim': 'vim',
            'nano': 'nano',
            
            # Communication
            'discord': 'discord',
            'slack': 'slack',
            'teams': 'teams',
            'zoom': 'zoom',
            
            # Media
            'spotify': 'spotify',
            'vlc': 'vlc',
            'music': 'spotify',
            'video': 'vlc',
            
            # Office
            'libreoffice': 'libreoffice',
            'office': 'libreoffice',
            'writer': 'libreoffice --writer',
            
            # System tools
            'files': 'nautilus',
            'file manager': 'nautilus',
            'settings': 'gnome-control-center',
            'preferences': 'gnome-control-center',
        }
    
    # === TERMINAL COMMANDS ===
    def run_command(self, cmd: str) -> str:
        """Run any terminal command"""
        return self.terminal.get_output(cmd)
    
    def run_background(self, cmd: str) -> str:
        """Run command in background"""
        return self.terminal.run_background(cmd)
    
    # === WEB BROWSING ===
    def search_web(self, query: str) -> str:
        """Search the web"""
        results = self.browser.search(query)
        if not results:
            return "No results found."
        
        output = f"🔍 Search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            if 'error' in r:
                return f"Error: {r['error']}"
            output += f"{i}. {r.get('title', 'N/A')}\n"
            output += f"   {r.get('snippet', 'N/A')}\n"
            output += f"   URL: {r.get('url', 'N/A')}\n\n"
        
        return output
    
    def browse_url(self, url: str) -> str:
        """Get content from a URL"""
        content = self.browser.get_page_content(url)
        return f"📄 Content from {url}:\n\n{content[:2000]}"
    
    def wikipedia(self, topic: str) -> str:
        """Get Wikipedia info"""
        return self.browser.get_wikipedia(topic)
    
    # === APPLICATION CONTROL ===
    def open_app(self, app_name: str) -> str:
        """Open any application"""
        app_cmd = self.apps.get(app_name.lower(), app_name)
        
        try:
            subprocess.Popen(
                app_cmd.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return f"✅ Opened: {app_name}"
        except Exception as e:
            # Try as generic command
            try:
                subprocess.Popen(
                    app_name.split(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return f"✅ Opened: {app_name}"
            except:
                return f"❌ Could not open {app_name}: {str(e)}"
    
    def close_app(self, app_name: str) -> str:
        """Close any application"""
        result = self.terminal.execute(f"pkill -f '{app_name}'")
        if result['success']:
            return f"✅ Closed: {app_name}"
        return f"❌ Could not close {app_name}"
    
    # === FILE OPERATIONS ===
    def list_files(self, path: str = ".") -> str:
        """List files in directory"""
        return self.terminal.get_output(f"ls -la {path}")
    
    def find_file(self, name: str, path: str = "/home") -> str:
        """Find files by name"""
        result = self.terminal.execute(f"find {path} -name '*{name}*' 2>/dev/null | head -20")
        if result['success'] and result['stdout']:
            return f"📁 Found files:\n{result['stdout']}"
        return "No files found."
    
    def read_file(self, filepath: str) -> str:
        """Read file content"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return f"📄 {filepath}:\n\n{content[:2000]}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def create_file(self, filepath: str, content: str) -> str:
        """Create or write to a file"""
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return f"✅ Created/updated: {filepath}"
        except Exception as e:
            return f"Error writing file: {str(e)})"
    
    def delete_file(self, filepath: str) -> str:
        """Delete a file"""
        result = self.terminal.execute(f"rm '{filepath}'")
        if result['success']:
            return f"✅ Deleted: {filepath}"
        return f"❌ Error: {result.get('error', 'Could not delete')}"
    
    # === SYSTEM INFO ===
    def system_info(self) -> str:
        """Get system information"""
        info = []
        
        # CPU
        result = self.terminal.execute("top -bn1 | head -5")
        info.append(f"🖥️ CPU:\n{result['stdout'][:200]}")
        
        # Memory
        result = self.terminal.execute("free -h")
        info.append(f"💾 Memory:\n{result['stdout']}")
        
        # Disk
        result = self.terminal.execute("df -h")
        info.append(f"💿 Disk:\n{result['stdout']}")
        
        # Network
        result = self.terminal.execute("ip addr")
        info.append(f"🌐 Network:\n{result['stdout'][:300]}")
        
        return "\n\n".join(info)
    
    def processes(self) -> str:
        """List running processes"""
        result = self.terminal.execute("ps aux --sort=-%cpu | head -15")
        return f"📊 Top Processes:\n\n{result['stdout']}"
    
    # === SCREEN CONTROL ===
    def screenshot(self) -> str:
        """Take screenshot"""
        path = f"/home/tradler/Pictures/screenshot_{int(time.time())}.png"
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.screenshot(path)
                return f"📸 Screenshot saved: {path}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Fallback
        result = self.terminal.execute(f"scrot {path}")
        if result['success']:
            return f"📸 Screenshot saved: {path}"
        return "Could not take screenshot"
    
    # === CLIPBOARD ===
    def get_clipboard(self) -> str:
        """Get clipboard content"""
        if PYPERCLIP_AVAILABLE:
            return f"📋 Clipboard: {pyperclip.paste()}"
        
        result = self.terminal.execute("xclip -selection clipboard -o")
        return f"📋 Clipboard: {result['stdout'][:500]}"
    
    def set_clipboard(self, text: str) -> str:
        """Set clipboard content"""
        if PYPERCLIP_AVAILABLE:
            pyperclip.copy(text)
            return "✅ Copied to clipboard"
        
        self.terminal.run_background(f"echo '{text}' | xclip -selection clipboard")
        return "✅ Copied to clipboard"
    
    # === KEYBOARD/MOUSE ===
    def type_text(self, text: str) -> str:
        """Type text"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.write(text)
            return f"✅ Typed: {text}"
        
        # Fallback
        self.terminal.run_background(f"xdotool type '{text}'")
        return f"✅ Typed: {text}"
    
    def press_key(self, key: str) -> str:
        """Press a key"""
        if PYAUTOGUI_AVAILABLE:
            pyautogui.press(key)
            return f"✅ Pressed: {key}"
        
        self.terminal.run_background(f"xdotool key {key}")
        return f"✅ Pressed: {key}"
    
    def click(self, x: int = None, y: int = None) -> str:
        """Click at position"""
        if PYAUTOGUI_AVAILABLE:
            if x and y:
                pyautogui.click(x, y)
            else:
                pyautogui.click()
            pos = f" at {x},{y}" if x and y else ""
            return f"✅ Clicked{pos}"
        
        if x and y:
            self.terminal.run_background(f"xdotool mousemove {x} {y} click 1")
        else:
            self.terminal.run_background("xdotool click 1")
        return "✅ Clicked"
    
    # === SPECIAL OPERATIONS ===
    def install_package(self, package: str) -> str:
        """Install a package (apt)"""
        if os.geteuid() != 0:
            return "Need sudo. Try: sudo apt install " + package
        result = self.terminal.execute(f"sudo apt install -y {package}")
        return f"📦 Installation result:\n{result['stdout'][:500]}"
    
    def update_system(self) -> str:
        """Update system packages"""
        if os.geteuid() != 0:
            return "Need sudo. Try: sudo apt update"
        result = self.terminal.execute("sudo apt update")
        return f"🔄 Update result:\n{result['stdout'][:500]}"
    
    def git_clone(self, repo_url: str, path: str = ".") -> str:
        """Clone a git repository"""
        cmd = f"git clone {repo_url} {path}"
        result = self.terminal.execute(cmd)
        if result['success']:
            return f"✅ Cloned: {repo_url}"
        return f"❌ Error: {result.get('stderr', 'Unknown')}"
    
    def download_file(self, url: str, path: str = ".") -> str:
        """Download a file"""
        filename = url.split('/')[-1]
        cmd = f"wget -O {path}/{filename} {url}"
        result = self.terminal.execute(cmd)
        if result['success']:
            return f"✅ Downloaded: {filename}"
        return f"❌ Error: {result.get('stderr', 'Unknown')}"


# Global instance
system = FullSystemControl()


# Quick access functions
def run_command(cmd: str) -> str:
    return system.run_command(cmd)

def search_web(query: str) -> str:
    return system.search_web(query)

def browse_url(url: str) -> str:
    return system.browse_url(url)

def wikipedia(topic: str) -> str:
    return system.wikipedia(topic)

def open_app(app: str) -> str:
    return system.open_app(app)

def close_app(app: str) -> str:
    return system.close_app(app)

def list_files(path: str = ".") -> str:
    return system.list_files(path)

def find_file(name: str) -> str:
    return system.find_file(name)

def read_file(filepath: str) -> str:
    return system.read_file(filepath)

def create_file(filepath: str, content: str) -> str:
    return system.create_file(filepath, content)

def delete_file(filepath: str) -> str:
    return system.delete_file(filepath)

def system_info() -> str:
    return system.system_info()

def processes() -> str:
    return system.processes()

def screenshot() -> str:
    return system.screenshot()

def get_clipboard() -> str:
    return system.get_clipboard()

def set_clipboard(text: str) -> str:
    return system.set_clipboard(text)

def type_text(text: str) -> str:
    return system.type_text(text)

def press_key(key: str) -> str:
    return system.press_key(key)

def click(x: int = None, y: int = None) -> str:
    return system.click(x, y)

def install_package(package: str) -> str:
    return system.install_package(package)

def update_system() -> str:
    return system.update_system()

def git_clone(repo_url: str) -> str:
    return system.git_clone(repo_url)

def download_file(url: str) -> str:
    return system.download_file(url)


if __name__ == "__main__":
    print("Full System Control Module Ready")
    
    # Test web search
    print("\nTesting web search...")
    results = system.search_web("Python programming")
    print(results[:500])

