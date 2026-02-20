"""
Bosco Core - Smart App Launcher
Opens apps if they exist, installs them if they don't
"""

import os
import subprocess
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class SmartAppLauncher:
    """
    Smart application launcher - opens if exists, installs if not
    """

    def __init__(self):
        self.platform = os.uname().sysname
        self.package_managers = ['apt', 'snap', 'flatpak', 'pip', 'npm']
        
        # Known apps database with install commands
        self.app_database = {
            # Web Browsers
            'chrome': {'name': 'Google Chrome', 'apt': 'google-chrome-stable', 'snap': 'google-chrome', 'category': 'browser'},
            'firefox': {'name': 'Mozilla Firefox', 'apt': 'firefox', 'snap': 'firefox', 'category': 'browser'},
            'brave': {'name': 'Brave Browser', 'apt': 'brave-browser', 'snap': 'brave', 'category': 'browser'},
            'edge': {'name': 'Microsoft Edge', 'apt': 'microsoft-edge', 'category': 'browser'},
            'chromium': {'name': 'Chromium', 'apt': 'chromium', 'snap': 'chromium', 'category': 'browser'},
            
            # Development
            'vscode': {'name': 'VS Code', 'apt': 'code', 'snap': 'code', 'category': 'development'},
            'visual studio': {'name': 'VS Code', 'apt': 'code', 'category': 'development'},
            'vs code': {'name': 'VS Code', 'apt': 'code', 'category': 'development'},
            'sublime': {'name': 'Sublime Text', 'apt': 'sublime-text', 'category': 'development'},
            'atom': {'name': 'Atom', 'apt': 'atom', 'category': 'development'},
            'pycharm': {'name': 'PyCharm', 'apt': 'pycharm-community', 'snap': 'pycharm-community', 'category': 'development'},
            'intellij': {'name': 'IntelliJ IDEA', 'snap': 'intellij-idea-community', 'category': 'development'},
            'git': {'name': 'Git', 'apt': 'git', 'category': 'development'},
            'docker': {'name': 'Docker', 'apt': 'docker.io', 'category': 'development'},
            'postman': {'name': 'Postman', 'apt': 'postman', 'snap': 'postman', 'category': 'development'},
            'node': {'name': 'Node.js', 'apt': 'nodejs', 'category': 'development'},
            'python': {'name': 'Python', 'apt': 'python3', 'category': 'development'},
            
            # Communication
            'discord': {'name': 'Discord', 'apt': 'discord', 'snap': 'discord', 'category': 'communication'},
            'slack': {'name': 'Slack', 'apt': 'slack', 'snap': 'slack', 'category': 'communication'},
            'teams': {'name': 'Microsoft Teams', 'apt': 'teams', 'snap': 'teams-for-linux', 'category': 'communication'},
            'zoom': {'name': 'Zoom', 'apt': 'zoom', 'snap': 'zoom-client', 'category': 'communication'},
            'telegram': {'name': 'Telegram', 'apt': 'telegram-desktop', 'snap': 'telegram-desktop', 'category': 'communication'},
            'whatsapp': {'name': 'WhatsApp', 'snap': 'whatsapp', 'category': 'communication'},
            'signal': {'name': 'Signal', 'apt': 'signal-desktop', 'snap': 'signal-desktop', 'category': 'communication'},
            'skype': {'name': 'Skype', 'apt': 'skypeforlinux', 'category': 'communication'},
            
            # Media
            'spotify': {'name': 'Spotify', 'apt': 'spotify-client', 'snap': 'spotify', 'category': 'media'},
            'vlc': {'name': 'VLC Media Player', 'apt': 'vlc', 'snap': 'vlc', 'category': 'media'},
            'gimp': {'name': 'GIMP', 'apt': 'gimp', 'snap': 'gimp', 'category': 'media'},
            'inkscape': {'name': 'Inkscape', 'apt': 'inkscape', 'category': 'media'},
            'blender': {'name': 'Blender', 'apt': 'blender', 'snap': 'blender', 'category': 'media'},
            
            # Office
            'libreoffice': {'name': 'LibreOffice', 'apt': 'libreoffice', 'category': 'office'},
            'office': {'name': 'LibreOffice', 'apt': 'libreoffice', 'category': 'office'},
            'onlyoffice': {'name': 'OnlyOffice', 'apt': 'onlyoffice-desktopeditors', 'snap': 'onlyoffice-desktopeditors', 'category': 'office'},
            'notion': {'name': 'Notion', 'snap': 'notion-snap', 'category': 'office'},
            
            # System Tools
            'terminal': {'name': 'GNOME Terminal', 'apt': 'gnome-terminal', 'category': 'system'},
            'files': {'name': 'Files (Nautilus)', 'apt': 'nautilus', 'category': 'system'},
            'file manager': {'name': 'Files (Nautilus)', 'apt': 'nautilus', 'category': 'system'},
            'settings': {'name': 'Settings', 'apt': 'gnome-control-center', 'category': 'system'},
            'nvidia': {'name': 'NVIDIA Settings', 'apt': 'nvidia-settings', 'category': 'system'},
            
            # Utilities
            'calculator': {'name': 'Calculator', 'apt': 'gnome-calculator', 'category': 'utility'},
            'calendar': {'name': 'Calendar', 'apt': 'gnome-calendar', 'category': 'utility'},
            'notes': {'name': 'Notes', 'apt': 'gnome-notes', 'category': 'utility'},
            'sticky notes': {'name': 'Sticky Notes', 'apt': 'stickynotes', 'category': 'utility'},
            'clipboard': {'name': 'Clipboard Manager', 'apt': 'clipit', 'category': 'utility'},
            
            # Games
            'steam': {'name': 'Steam', 'apt': 'steam', 'category': 'game'},
            'minecraft': {'name': 'Minecraft', 'snap': 'minecraft', 'category': 'game'},
        }
        
        # Desktop file search paths
        self.desktop_paths = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            os.path.expanduser('~/.local/share/applications')
        ]

    def _run_command(self, cmd: str, timeout: int = 30) -> Tuple[bool, str]:
        """Run command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "Command timed out")
        except Exception as e:
            return (False, str(e))

    def find_app(self, name: str) -> List[Dict[str, str]]:
        """
        Search for an application by name
        Returns list of matching apps with their launch commands
        """
        name_lower = name.lower()
        matches = []
        
        # Search in desktop files
        for desktop_dir in self.desktop_paths:
            if not os.path.exists(desktop_dir):
                continue
                
            for f in os.listdir(desktop_dir):
                if not f.endswith('.desktop'):
                    continue
                    
                filepath = os.path.join(desktop_dir, f)
                try:
                    with open(filepath, 'r') as file:
                        content = file.read()
                        
                        # Extract app info
                        app_name = ''
                        exec_cmd = ''
                        icon = ''
                        categories = ''
                        
                        for line in content.split('\n'):
                            if line.startswith('Name='):
                                app_name = line.replace('Name=', '')
                            elif line.startswith('Exec='):
                                exec_cmd = line.replace('Exec=', '').split()[0]
                            elif line.startswith('Icon='):
                                icon = line.replace('Icon=', '')
                            elif line.startswith('Categories='):
                                categories = line.replace('Categories=', '')
                        
                        # Check if matches search
                        if name_lower in app_name.lower() or name_lower in f.lower():
                            matches.append({
                                'name': app_name,
                                'exec': exec_cmd,
                                'icon': icon,
                                'categories': categories,
                                'source': 'Desktop'
                            })
                except:
                    pass
        
        # Also search in known database
        for key, info in self.app_database.items():
            if name_lower in key or name_lower in info.get('name', '').lower():
                matches.append({
                    'name': info['name'],
                    'exec': key,
                    'category': info.get('category', 'unknown'),
                    'source': 'Database'
                })
        
        return matches[:20]  # Limit results

    def is_app_installed(self, name: str) -> bool:
        """Check if an application is installed"""
        # Check desktop files first
        for desktop_dir in self.desktop_paths:
            if not os.path.exists(desktop_dir):
                continue
                
            for f in os.listdir(desktop_dir):
                if not f.endswith('.desktop'):
                    continue
                    
                try:
                    with open(os.path.join(desktop_dir, f), 'r') as file:
                        content = file.read()
                        for line in content.split('\n'):
                            if line.startswith('Name='):
                                app_name = line.replace('Name=', '')
                                if name.lower() in app_name.lower():
                                    return True
                except:
                    pass
        
        # Check if command is available
        success, _ = self._run_command(f"which {name}")
        if success:
            return True
            
        return False

    def get_install_command(self, name: str) -> Optional[Dict[str, str]]:
        """Get installation command for an app"""
        name_lower = name.lower()
        
        # Check database first
        if name_lower in self.app_database:
            app_info = self.app_database[name_lower]
            commands = {}
            
            if 'apt' in app_info:
                commands['apt'] = f"sudo apt install -y {app_info['apt']}"
            if 'snap' in app_info:
                commands['snap'] = f"snap install {app_info['snap']}"
            if 'flatpak' in app_info:
                commands['flatpak'] = f"flatpak install -y {app_info['flatpak']}"
                
            return {
                'name': app_info['name'],
                'commands': commands,
                'category': app_info.get('category', 'unknown')
            }
        
        # Generic apt search
        success, output = self._run_command(f"apt-cache search {name}")
        if success and output.strip():
            first_match = output.split('\n')[0]
            if first_match:
                pkg_name = first_match.split(' - ')[0].strip()
                return {
                    'name': name,
                    'commands': {
                        'apt': f"sudo apt install -y {pkg_name}",
                        'search': f"Search: {output[:200]}"
                    },
                    'category': 'unknown'
                }
        
        return None

    def install_app(self, name: str, method: str = 'apt') -> str:
        """
        Install an application
        
        Args:
            name: App name
            method: Package manager (apt, snap, flatpak, pip, npm)
            
        Returns:
            Installation result
        """
        # Get install info
        install_info = self.get_install_command(name)
        
        if not install_info:
            return f"Could not find installation method for '{name}'. Try searching first."
        
        # Build command based on method
        commands = install_info['commands']
        
        if method == 'apt' and 'apt' in commands:
            cmd = commands['apt']
        elif method == 'snap' and 'snap' in commands:
            cmd = commands['snap']
        elif method == 'flatpak' and 'flatpak' in commands:
            cmd = commands['flatpak']
        elif method in commands:
            cmd = commands[method]
        else:
            # Use first available method
            cmd = list(commands.values())[0] if commands else None
            
        if not cmd:
            return f"No install command found for {name}"
        
        # Run installation in background
        success, output = self._run_command(cmd, timeout=300)
        
        if success:
            return f"✅ Successfully installed {install_info['name']}\n\nCommand: {cmd}"
        else:
            return f"❌ Installation failed:\n{output[:500]}"

    def open_app(self, name: str, install_if_missing: bool = True) -> str:
        """
        Open an application - smart launch
        
        Args:
            name: App name
            install_if_missing: If True, try to install if not found
            
        Returns:
            Result message
        """
        # First, check if already installed
        if self.is_app_installed(name):
            # Try to launch
            # Check desktop files first
            for desktop_dir in self.desktop_paths:
                if not os.path.exists(desktop_dir):
                    continue
                    
                for f in os.listdir(desktop_dir):
                    if not f.endswith('.desktop'):
                        continue
                        
                    try:
                        with open(os.path.join(desktop_dir, f), 'r') as file:
                            content = file.read()
                            for line in content.split('\n'):
                                if line.startswith('Name='):
                                    app_name = line.replace('Name=', '')
                                    if name.lower() in app_name.lower():
                                        # Try gtk-launch first
                                        app_id = f[:-8]  # Remove .desktop
                                        success, _ = self._run_command(f"gtk-launch '{app_id}'")
                                        if success:
                                            return f"✅ Opened: {app_name}"
                                        
                                        # Fallback to xdg-open
                                        success, _ = self._run_command(f"xdg-open '{os.path.join(desktop_dir, f)}'")
                                        if success:
                                            return f"✅ Opened: {app_name}"
                    except:
                        pass
            
            # Try direct command
            success, _ = self._run_command(f"{name} &")
            if success:
                return f"✅ Opened: {name}"
        
        # App not found
        if install_if_missing:
            # Get install info
            install_info = self.get_install_command(name)
            if install_info:
                return (f"📦 '{name}' is not installed.\n\n"
                       f"Would you like me to install it?\n"
                       f"App: {install_info['name']}\n"
                       f"Category: {install_info['category']}\n\n"
                       f"Available install methods:\n" +
                       '\n'.join([f"  • {k}: {v}" for k, v in install_info['commands'].items()]))
        
        return f"❌ Could not find or open: {name}"

    def smart_launch(self, name: str, auto_install: bool = True) -> str:
        """
        Smart launch - open if exists, install if not
        """
        # Check if installed
        if self.is_app_installed(name):
            return self.open_app(name, install_if_missing=False)
        
        if auto_install:
            # Auto-install and open
            install_result = self.install_app(name)
            if 'Successfully installed' in install_result:
                # Try to open after install
                return self.open_app(name, install_if_missing=False) + "\n\n" + install_result
            return install_result
        
        return self.open_app(name, install_if_missing=True)

    def list_installed_apps(self, category: Optional[str] = None) -> str:
        """List installed applications"""
        apps = []
        
        for desktop_dir in self.desktop_paths:
            if not os.path.exists(desktop_dir):
                continue
                
            for f in os.listdir(desktop_dir):
                if not f.endswith('.desktop'):
                    continue
                    
                try:
                    with open(os.path.join(desktop_dir, f), 'r') as file:
                        content = file.read()
                        name = ''
                        categories = ''
                        
                        for line in content.split('\n'):
                            if line.startswith('Name='):
                                name = line.replace('Name=', '')
                            elif line.startswith('Categories='):
                                categories = line.replace('Categories=', '')
                        
                        if name:
                            apps.append({
                                'name': name,
                                'categories': categories
                            })
                except:
                    pass
        
        # Filter by category if specified
        if category:
            apps = [a for a in apps if category.lower() in a['categories'].lower()]
        
        if not apps:
            return "No applications found"
        
        result = f"Installed Applications ({len(apps)}):\n\n"
        for i, app in enumerate(sorted(apps, key=lambda x: x['name'])[:50], 1):
            result += f"{i:2}. {app['name']}\n"
        
        return result

    def search_for_app(self, query: str) -> str:
        """Search for an app (installed or available)"""
        # First check if installed
        installed = self.find_app(query)
        
        result = f"🔍 Search results for '{query}':\n\n"
        
        if installed:
            result += "📱 INSTALLED:\n"
            for app in installed[:10]:
                result += f"  • {app['name']}\n"
            result += "\n"
        
        # Check for install options
        install_info = self.get_install_command(query)
        if install_info:
            result += f"📦 AVAILABLE TO INSTALL:\n"
            result += f"  App: {install_info['name']}\n"
            result += f"  Category: {install_info['category']}\n\n"
            result += "  Install commands:\n"
            for method, cmd in install_info['commands'].items():
                if method != 'search':
                    result += f"    • {method}: {cmd[:60]}...\n"
        else:
            result += "No install options found. Try a different search term."
        
        return result


# Global instance
_app_launcher = None

def get_smart_launcher() -> SmartAppLauncher:
    """Get smart app launcher instance"""
    global _app_launcher
    if _app_launcher is None:
        _app_launcher = SmartAppLauncher()
    return _app_launcher


# Convenience functions
def smart_open(name: str, auto_install: bool = True) -> str:
    """Smart open an app"""
    return get_smart_launcher().smart_launch(name, auto_install)

def install_app(name: str, method: str = 'apt') -> str:
    """Install an app"""
    return get_smart_launcher().install_app(name, method)

def find_app(name: str) -> str:
    """Find an app"""
    matches = get_smart_launcher().find_app(name)
    if matches:
        result = f"Found {len(matches)} apps:\n\n"
        for m in matches[:10]:
            result += f"• {m['name']} [{m.get('source', 'Desktop')}]\n"
        return result
    return f"No apps found matching '{name}'"


if __name__ == "__main__":
    launcher = SmartAppLauncher()
    
    print("=== Smart App Launcher Test ===\n")
    
    print("--- Search for 'code' ---")
    print(launcher.search_for_app('code'))
    
    print("\n--- Check if VS Code is installed ---")
    print(f"VS Code installed: {launcher.is_app_installed('vscode')}")
    
    print("\n--- List installed apps ---")
    print(launcher.list_installed_apps()[:500])

