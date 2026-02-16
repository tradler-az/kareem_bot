"""Audit Log"""
import datetime
logs = []
def log(action, user='system', details=''):
    logs.append({'time': datetime.datetime.now().isoformat(), 'action': action, 'user': user, 'details': details})
def get_logs(n=10): return logs[-n:]
