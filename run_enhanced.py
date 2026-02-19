#!/usr/bin/env parameters. python3
"""Bosco Core v3.1 - Enhanced Runner with All New Features"""

import os, sys, json, warnings
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["JACK_NO_AUDIO_RESERVATION"] = "1"
warnings.filterwarnings("ignore")

def load_config():
    for p in ["config.json", "bosco_os/config.json"]:
        if os.path.exists(p):
            with open(p) as f: return json.load(f)
    return {}

C = load_config()
NAME = C.get("ai_name", "Bosco")
VER = C.get("version", "3.1.0")
print(f"Bosco v{VER} Enhanced Edition Loaded")

# Load new modules
url_scanner = app_manager = conv_mem = updater = None
try:
    from bosco_os.capabilities.network.url_scanner import get_url_scanner
    url_scanner = get_url_scanner()
    print("[+] URL Port Scanner")
except: pass

try:
    from bosco_os.capabilities.system.app_manager import get_app_manager
    app_manager = get_app_manager()
    print("[+] App Manager")
except: pass

try:
    from bosco_os.brain.conversation_memory import get_conversation_memory
    conv_mem = get_conversation_memory()
    print("[+] Conversation Memory")
except: pass

try:
    from bosco_os.core.self_update import get_update_manager
    updater = get_update_manager()
    print("[+] Self-Update System")
except: pass

# Load existing modules
brain = kali = lin_cmd = None
try:
    from bosco_os.brain.neural_brain import get_brain
    brain = get_brain()
except: pass

try:
    from bosco_os.capabilities.system.kali_control import get_kali_control
    kali = get_kali_control()
except: pass

try:
    from bosco_os.brain.linux_command_handler import process_linux_command
    lin_cmd = process_linux_command
except: pass

try:
    from bosco_os.capabilities.system.full_control import search_web, open_app, close_app, list_files, screenshot, type_text, click, get_clipboard
except: pass

voice = None
try:
    from bosco_os.brain.voice_online import speak as voice
    voice("test")
except: pass

mode = "online"

def speak(t):
    print(f" {NAME}: {t}")
    if voice:
        try: voice(t)
        except: pass

def listen():
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as s:
            print("Listening...")
            r.adjust_for_ambient_noise(s, 2)
            a = r.listen(s, timeout=5)
        cmd = r.recognize_google(a).lower()
        print(f"You: {cmd}")
        return cmd
    except: return input("Type: ")

def proc(cmd):
    if not cmd: return "Didnt hear"
    c = cmd.lower().strip()
    if conv_mem: conv_mem.add_message("user", cmd)
    
    # NEW COMMANDS
    if "scan" in c and "port" in c:
        t = c.replace("scan","").replace("ports","").replace("on","").strip()
        if t and url_scanner: return url_scanner.quick_scan(t)
        return "What to scan?"
    
    if c in ["list apps","show apps","all apps"]:
        if app_manager: return app_manager.list_installed_apps(30)
        return "No app manager"
    
    if "running apps" in c:
        if app_manager: return app_manager.list_running_apps()
        return "No"
    
    if "find app" in c:
        n = c.replace("find app","").strip()
        if n and app_manager: return app_manager.find_app(n)
    
    if c.startswith("remember"):
        i = c.replace("remember","").strip()
        if i and conv_mem: return conv_mem.remember(i)
    
    if "what did i tell you" in c:
        t = c.replace("what did i tell you about","").strip()
        if t and conv_mem: return conv_mem.recall(t)
    
    if "what did we discuss" in c or "what did we talk" in c:
        if conv_mem: return conv_mem.what_did_we_discuss()
    
    if "update yourself" in c or "check for updates" in c:
        if updater:
            r = updater.check_for_updates()
            if r.get("available"): return "Update: " + r.get("current") + " -> " + r.get("latest")
            return "Up to date"
    
    if "go online" in c: return "Online mode"
    if "go offline" in c: return "Offline mode"
    
    if c == "status":
        return f"{NAME} {VER}\nMode: {mode}\nKali: {kali and kali.is_kali}"
    
    if "help" in c:
        return """COMMANDS:
scan ports [url/ip] - Scan ports
list apps - Installed apps
running apps - Running apps  
find app [name] - Find app
remember [info] - Remember info
what did we discuss - Recent topics
update yourself - Check updates
go online/offline - Mode
status - Status
"""
    
    # EXISTING COMMANDS
    if lin_cmd:
        r, conf = lin_cmd(c)
        if conf > 0.5: return r
    
    if brain:
        r = brain.process(c)
        if "search" in c:
            q = c.replace("search","").strip()
            if q: return search_web(q)
        if "open" in c:
            a = c.replace("open","").strip()
            if a: return open_app(a)
        if "close" in c or "kill" in c:
            a = c.replace("close","").replace("kill","").strip()
            if a: return close_app(a)
        if "system info" in c and kali: return kali.get_system_info()
        if "processes" in c and kali: return kali.list_processes()
        if "files" in c or "list" in c: return list_files(c.replace("list files","").strip() or ".")
        if "screenshot" in c: return screenshot()
        if "type" in c:
            t = c.replace("type","").strip()
            if t: return type_text(t)
        if "click" in c: return click()
        if "clipboard" in c and "get" in c: return get_clipboard()
        if "weather" in c: return search_web("weather")
        if "news" in c: return search_web("latest news")
        if "cpu" in c or "memory" in c and kali: return kali.cpu_info() + "\n" + kali.memory_info()
        if "network" in c and kali: return kali.get_network_info()
        if "ports" in c and kali: return kali.check_listening_ports()
        if "services" in c and kali: return kali.list_services()
        if "logs" in c and kali: return kali.system_logs()
        if "joke" in c:
            from bosco_os.brain.neural_brain import NormalHumanPersonality
            return NormalHumanPersonality().get_joke()
        resp = r.get("response","Got it!")
        if conv_mem: conv_mem.add_message("assistant", resp)
        return resp
    return "Say help"

print(f"\n{NAME} v{VER} ready!\n")
speak("Ready")
while 1:
    try:
        cmd = listen()
        if not cmd: continue
        if cmd in ["exit","quit","bye"]:
            speak("Bye!")
            break
        print("...")
        resp = proc(cmd)
        print(f"{NAME}: {resp}")
        speak(resp)
    except KeyboardInterrupt:
        print("\nBye")
        break
    except Exception as e:
        print(f"Error: {e}")
