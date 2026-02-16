"""Kali Tools"""
import subprocess, os
def run(tool, args, timeout=30):
    if not os.path.exists(f'/usr/bin/{tool}'): return f'{tool} not found'
    r = subprocess.run(f'{tool} {args}', shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout[:5000] or r.stderr[:5000]
def hydra(target, user, wordlist='/usr/share/wordlists/rockyou.txt'): 
    return run('hydra', f'-l {user} -P {wordlist} {target} ssh', 120)
def sqlmap(url): return run('sqlmap', f'-u {url} --batch', 120)
def nikto(url): return run('nikto', f'-h {url}', 60)
def gobuster(url, wl='/usr/share/wordlists/dirb/common.txt'): 
    return run('gobuster', f'dir -u {url} -w {wl}', 60)
