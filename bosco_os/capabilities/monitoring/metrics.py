"""Monitoring"""
import psutil, datetime
def metrics():
    return {'time': datetime.datetime.now().isoformat(), 'cpu': psutil.cpu_percent(), 
             'mem': psutil.virtual_memory().percent, 'disk': psutil.disk_usage('/').percent}
def alert(thresh=80):
    c = psutil.cpu_percent()
    return f'ALERT: CPU {c}%' if c > thresh else f'OK: CPU {c}%'
