"""Network Scanner - Kali Tools"""
import subprocess, os
def nmap(target, ports='1-1000', flags='-sV'):
    if not os.path.exists('/usr/bin/nmap'): return 'Nmap not installed'
    r = subprocess.run(['nmap', flags, '-p', ports, target], capture_output=True, text=True, timeout=60)
    return r.stdout[:3000] or r.stderr
def quick_scan(t): return nmap(t, '80,443,22', '-sV')
def ports(t, s=1, e=100): return nmap(t, f'{s}-{e}')
