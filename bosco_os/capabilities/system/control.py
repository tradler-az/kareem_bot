"""System Control"""
import psutil, os
def cpu(): return f"CPU: {psutil.cpu_percent()}%"
def memory(): return f"Memory: {psutil.virtual_memory().percent}%"
def disk(): return f"Disk: {psutil.disk_usage('/').percent}%"
def battery():
    b = psutil.sensors_battery()
    if b is None:
        return "No battery"
    return f"Battery: {b.percent}%"
def processes(): return [p.info for p in psutil.process_iter(['pid','name'])[:5]]
def kill(pid): 
    try: psutil.Process(pid).kill(); return f'Killed {pid}'
    except: return 'Failed'
