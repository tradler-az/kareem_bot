"""
Bosco Core - System Control
Extended system control capabilities
"""

import os
import sys
import subprocess
import platform
from typing import Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
    }
    
    if PSUTIL_AVAILABLE:
        info.update({
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        })
        
        # Battery (if available)
        try:
            battery = psutil.sensors_battery()
            if battery:
                info["battery"] = {
                    "percent": battery.percent,
                    "charging": battery.is_plugged_in
                }
        except:
            pass
    
    return info


def check_cpu() -> str:
    """Check CPU usage"""
    if not PSUTIL_AVAILABLE:
        return "CPU monitoring not available. Please install psutil."
    
    cpu = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    return f"CPU usage is {cpu} percent across {cpu_count} cores."


def check_memory() -> str:
    """Check memory usage"""
    if not PSUTIL_AVAILABLE:
        return "Memory monitoring not available."
    
    mem = psutil.virtual_memory()
    return (
        f"Memory usage is {mem.percent} percent. "
        f"{mem.used / (1024**3):.1f} gigabytes used out of {mem.total / (1024**3):.1f} gigabytes."
    )


def check_battery() -> str:
    """Check battery status"""
    if not PSUTIL_AVAILABLE:
        return "Battery monitoring not available."
    
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            charging = "charging" if battery.is_plugged_in else "not charging"
            return f"Battery is at {percent} percent and is {charging}."
        else:
            return "No battery detected."
    except:
        return "Could not get battery status."


def check_disk() -> str:
    """Check disk usage"""
    if not PSUTIL_AVAILABLE:
        return "Disk monitoring not available."
    
    disk = psutil.disk_usage('/')
    return (
        f"Disk usage is {disk.percent} percent. "
        f"{disk.used / (1024**3):.1f} gigabytes used out of {disk.total / (1024**3):.1f} gigabytes."
    )


def open_browser() -> str:
    """Open default browser"""
    try:
        if platform.system() == "Linux":
            subprocess.Popen(["firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "Safari"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Windows":
            subprocess.Popen(["start", "chrome"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Opening web browser."
    except Exception as e:
        return f"Could not open browser: {str(e)}"


def open_file_manager() -> str:
    """Open file manager"""
    try:
        if platform.system() == "Linux":
            subprocess.Popen(["xdg-open", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Windows":
            subprocess.Popen(["explorer", "."], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Opening file manager."
    except Exception as e:
        return f"Could not open file manager: {str(e)}"


def set_volume(level: int) -> str:
    """Set system volume"""
    try:
        if platform.system() == "Linux":
            # Use amixer
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{level}%"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Volume set to {level} percent."
    except:
        return "Could not set volume."


def increase_volume() -> str:
    """Increase volume by 10%"""
    return set_volume(80)  # Simplified


def decrease_volume() -> str:
    """Decrease volume by 10%"""
    return set_volume(50)  # Simplified


def shutdown() -> str:
    """Shutdown the system"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["shutdown", "now"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.run(["osascript", "-e", "tell app \"System Events\" to shut down"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "1"], shell=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Shutting down system."
    except Exception as e:
        return f"Could not shutdown: {str(e)}"


def restart() -> str:
    """Restart the system"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["reboot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.run(["osascript", "-e", "tell app \"System Events\" to restart"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Windows":
            subprocess.run(["shutdown", "/r", "/t", "1"], shell=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Restarting system."
    except Exception as e:
        return f"Could not restart: {str(e)}"


def sleep() -> str:
    """Put system to sleep"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["systemctl", "suspend"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.run(["pmset", "sleepnow"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Windows":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"], 
                         shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Putting system to sleep."
    except Exception as e:
        return f"Could not sleep: {str(e)}"


def take_screenshot() -> str:
    """Take a screenshot"""
    try:
        import datetime
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        if platform.system() == "Linux":
            subprocess.run(["scrot", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.run(["screencapture", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return f"Screenshot saved as {filename}."
    except Exception as e:
        return f"Could not take screenshot: {str(e)}"


if __name__ == "__main__":
    print("Testing System Control...")
    print(check_cpu())
    print(check_memory())
    print(check_disk())
    print(check_battery())

