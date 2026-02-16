"""Docker"""
import subprocess
def ps(): r=subprocess.run(['docker','ps'], capture_output=True,text=True); return r.stdout
def images(): r=subprocess.run(['docker','images'], capture_output=True,text=True); return r.stdout
def run_img(img, cmd=''): r=subprocess.run(['docker','run','-it',img]+cmd.split(), capture_output=True,text=True); return r.stdout
def stop(c): r=subprocess.run(['docker','stop',c], capture_output=True,text=True); return r.stdout
