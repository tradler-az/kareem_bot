#!/usr/bin/env python3
"""
Bosco Core v3.0 - ML-Powered AI Assistant with Full PC Control + Kali Linux
CLI-based with neural brain, learning, terminal access, and web browsing
"""

import os
import sys
import json
import time
import warnings

# Suppress audio warnings - MUST be set before any audio imports
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['JACK_NO_AUDIO_RESERVATION'] = '1'
os.environ['JACK_NO_START_SERVER'] = '1'
os.environ['JACK_SERVER_NAME'] = 'none'
os.environ['PULSE_PROP'] = 'application.name=Bosco'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Load configuration
def load_config():
    for path in ['config.json', 'bosco_os/config.json']:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    return {}

config = load_config()
AI_NAME = config.get('ai_name', 'Bosco')
VERSION = config.get('version', '3.0.0')

print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██╗   ██╗███████╗██████╗ ████████╗███████╗██╗  ██╗       ║
║     ██║   ██║██╔════╝██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝       ║
║     ██║   ██║█████╗  ██████╔╝   ██║   █████╗   ╚███╔╝        ║
║     ╚██╗ ██╔╝██╔══╝  ██╔══██╗   ██║   ██╔══╝   ██╔██╗        ║
║      ╚████╔╝ ███████╗██║  ██║   ██║   ███████╗██╔╝ ██╗       ║
║       ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝       ║
║                                                              ║
║        ML-POWERED NEURAL BRAIN + FULL PC CONTROL             ║
║                    + KALI LINUX SUPPORT                      ║
║                        v{VERSION}                            ║
╚══════════════════════════════════════════════════════════════╝
""")

# Import brain modules
try:
    from bosco_os.brain.neural_brain import (
        get_brain, get_learning_engine, get_predictive_engine,
        process_input, NeuralNetworkBrain
    )
    print("[+] Neural Brain Module loaded")
except ImportError as e:
    print(f"[-] Neural Brain: {e}")
    get_brain = None

try:
    from bosco_os.brain.llm_client import get_llm
    print("[+] LLM Client loaded")
except:
    get_llm = None

# Import Kali Linux control
try:
    from bosco_os.capabilities.system.kali_control import get_kali_control
    kali_control = get_kali_control()
    print(f"[+] Kali Linux Control loaded (Kali: {kali_control.is_kali})")
except Exception as e:
    print(f"[-] Kali Control: {e}")
    kali_control = None

# Import Linux command handler
try:
    from bosco_os.brain.linux_command_handler import get_linux_handler, process_linux_command
    print("[+] Linux Command Handler loaded")
except Exception as e:
    print(f"[-] Linux Handler: {e}")
    process_linux_command = None

# Import Kali personality
try:
    from bosco_os.brain.kali_personality import get_kali_personality
    print("[+] Kali Personality loaded")
except Exception as e:
    print(f"[-] Kali Personality: {e}")
    get_kali_personality = None

# Import full system control
try:
    from bosco_os.capabilities.system.full_control import (
        system, run_command, search_web, browse_url, wikipedia,
        open_app, close_app, list_files, find_file, read_file,
        create_file, delete_file, system_info, processes,
        screenshot, get_clipboard, set_clipboard, type_text,
        press_key, click, install_package, update_system,
        git_clone, download_file
    )
    print("[+] Full System Control loaded")
except Exception as e:
    print(f"[-] System Control: {e}")
    system = None

# Import basic system info
try:
    from bosco_os.capabilities.system.control import cpu
except:
    cpu = lambda: "N/A"

try:
    from bosco_os.brain.voice_online import memory_info, storage_info
except:
    memory_info = storage_info = lambda: {"error": "unavailable"}

# Initialize voice - use voice_online module to avoid dual output
try:
    from bosco_os.brain.voice_online import speak as voice_speak
    # Test that it works
    voice_speak("test")
    print("[+] Voice module loaded")
except Exception as e:
    print(f"[-] Voice module: {e}")
    voice_speak = None

voice_engine = None


def speak(text):
    """Voice output"""
    print(f"🔊 {AI_NAME}: {text}")
    
    # Use voice_online module to avoid dual sound output
    if voice_speak:
        try:
            voice_speak(text)
        except Exception as e:
            print(f"Voice error: {e}")
            # Fallback to espeak only
            try:
                import subprocess
                subprocess.Popen(['espeak', '-s', '120', text], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
    elif voice_engine:
        # Fallback to local engine if voice_online failed
        try:
            voice_engine.stop()
            voice_engine.say(text)
            voice_engine.runAndWait()
        except:
            pass


def listen():
    """Voice input"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=3.5)
            audio = r.listen(source, timeout=5)
        cmd = r.recognize_google(audio).lower()
        print(f"👤 You: {cmd}")
        return cmd
    except:
        return input("Type: ")


def process_command(cmd):
    """Process commands with full system control + Kali Linux"""
    if not cmd:
        return "I didn't catch that."
    
    cmd = cmd.lower().strip()
    
    # First, try Linux command handler for system commands
    if process_linux_command:
        linux_result, linux_conf = process_linux_command(cmd)
        if linux_conf > 0.5:
            return linux_result
    
    # Use neural brain for intent
    if get_brain:
        result = get_brain().process(cmd)
        intent = result['intent']
        
        # Handle specific intents with full system control
        if intent == 'search' or 'search' in cmd:
            query = cmd.replace('search', '').replace('search for', '').strip()
            if query:
                return search_web(query)
        
        if 'wikipedia' in cmd or 'what is' in cmd or 'who is' in cmd:
            topic = cmd.replace('wikipedia', '').replace('what is', '').replace('who is', '').replace('tell me about', '').strip()
            if topic:
                return wikipedia(topic)
        
        if 'open' in cmd:
            app = cmd.replace('open', '').strip()
            if app:
                return open_app(app)
        
        if 'close' in cmd or 'kill' in cmd:
            app = cmd.replace('close', '').replace('kill', '').strip()
            if app:
                return close_app(app)
        
        if 'run' in cmd or 'execute' in cmd:
            command = cmd.replace('run', '').replace('execute', '').strip()
            if command:
                # Check if it's a Linux command
                if kali_control:
                    return kali_control.execute_command(command)
                return run_command(command)
        
        if 'terminal' in cmd or 'cmd' in cmd:
            return open_app('terminal')
        
        if 'screenshot' in cmd:
            return screenshot()
        
        if 'system info' in cmd or 'check system' in cmd:
            if kali_control:
                return kali_control.get_system_info()
            return system_info()
        
        if 'processes' in cmd or 'running' in cmd:
            if kali_control:
                return kali_control.list_processes()
            return processes()
        
        if 'files' in cmd or 'list' in cmd:
            path = cmd.replace('list files', '').replace('ls', '').strip() or '.'
            return list_files(path)
        
        if 'find' in cmd and 'file' in cmd:
            name = cmd.replace('find file', '').replace('search for', '').strip()
            if name:
                return find_file(name)
        
        if 'read' in cmd and 'file' in cmd:
            filepath = cmd.replace('read file', '').replace('show', '').strip()
            if filepath:
                return read_file(filepath)
        
        if 'create' in cmd and 'file' in cmd:
            return "Please specify filename and content: create file [name] with [content]"
        
        if 'delete' in cmd or 'remove' in cmd:
            filepath = cmd.replace('delete', '').replace('remove', '').strip()
            if filepath:
                return delete_file(filepath)
        
        if 'clipboard' in cmd:
            if 'get' in cmd or 'show' in cmd or 'read' in cmd:
                return get_clipboard()
            if 'copy' in cmd or 'set' in cmd:
                text = cmd.replace('copy to clipboard', '').replace('set clipboard', '').strip()
                if text:
                    return set_clipboard(text)
        
        if 'type' in cmd:
            text = cmd.replace('type', '').replace('write', '').strip()
            if text:
                return type_text(text)
        
        if 'press' in cmd and 'key' in cmd:
            key = cmd.replace('press key', '').replace('press', '').strip()
            if key:
                return press_key(key)
        
        if 'click' in cmd:
            return click()
        
        if 'install' in cmd:
            package = cmd.replace('install', '').strip()
            if package:
                return install_package(package)
        
        if 'update' in cmd:
            if kali_control:
                return kali_control.apt_update()
            return update_system()
        
        if 'clone' in cmd and 'git' in cmd:
            repo = cmd.replace('git clone', '').replace('clone', '').strip()
            if repo:
                return git_clone(repo)
        
        if 'download' in cmd:
            url = cmd.replace('download', '').strip()
            if url:
                return download_file(url)
        
        if 'weather' in cmd:
            return browse_url("https://wttr.in")
        
        if 'news' in cmd:
            return search_web("latest news")
        
        if 'cpu' in cmd or 'memory' in cmd or 'disk' in cmd:
            if kali_control:
                cpu_info = kali_control.cpu_info()
                mem_info = kali_control.memory_info()
                disk_info = kali_control.disk_usage()
                return f"{cpu_info}\n\n{mem_info}\n\n{disk_info}"
            m = memory_info()
            s = storage_info()
            return f"CPU: {cpu()}, RAM: {m.get('percent', 'N/A')}%, Storage: {s.get('percent', 'N/A')}%"
        
        # Kali-specific commands
        if 'kali tools' in cmd:
            if kali_control:
                return kali_control.get_kali_tools()
            return "Kali control not available"
        
        if 'check root' in cmd or 'root access' in cmd:
            if kali_control:
                return kali_control.check_root()
            return "Kali control not available"
        
        if 'network' in cmd:
            if kali_control:
                return kali_control.get_network_info()
            return system_info()
        
        if 'ports' in cmd or 'listening' in cmd:
            if kali_control:
                return kali_control.check_listening_ports()
            return "Kali control not available"
        
        if 'services' in cmd:
            if kali_control:
                return kali_control.list_services()
            return "Kali control not available"
        
        if 'logs' in cmd:
            if kali_control:
                return kali_control.system_logs()
            return "Kali control not available"
        
        if 'help' in cmd:
            return get_help_text()
        
        if 'joke' in cmd:
            # Use Kali personality for jokes
            if get_kali_personality:
                return get_kali_personality().get_joke()
            from bosco_os.brain.neural_brain import NormalHumanPersonality
            return NormalHumanPersonality().get_joke()
        
        # Return neural brain response for conversation
        # Use Kali personality if available
        if get_kali_personality and kali_control and kali_control.is_kali:
            return get_kali_personality().converse(cmd, result.get('sentiment', 0))
        
        return result['response']
    
    # Fallback to pattern matching
    return pattern_match_command(cmd)


def pattern_match_command(cmd):
    """Fallback pattern-based command processing"""
    
    # Direct terminal commands
    if cmd.startswith('run ') or cmd.startswith('exec ') or cmd.startswith('! '):
        cmd_text = cmd.replace('run ', '').replace('exec ', '').replace('! ', '')
        return run_command(cmd_text)
    
    # Search
    if 'search' in cmd:
        query = cmd.replace('search', '').strip()
        if query:
            return search_web(query)
    
    # Wikipedia
    if 'what is' in cmd or 'who is' in cmd:
        topic = cmd.replace('what is', '').replace('who is', '').strip()
        if topic:
            return wikipedia(topic)
    
    # Open/Close apps
    if cmd.startswith('open '):
        return open_app(cmd.replace('open ', ''))
    
    if cmd.startswith('close ') or cmd.startswith('kill '):
        return close_app(cmd.replace('close ', '').replace('kill ', ''))
    
    # System info
    if 'system' in cmd or 'status' in cmd:
        return system_info()
    
    # Help
    if 'help' in cmd:
        return get_help_text()
    
    # LLM fallback
    if get_llm:
        return get_llm().chat(cmd, get_system_prompt())
    
    # Default
    from bosco_os.brain.neural_brain import NormalHumanPersonality
    return NormalHumanPersonality().converse(cmd, 0.0)


def get_system_prompt():
    return f"""You are {AI_NAME}, an advanced AI assistant with full PC control.

Your capabilities:
- Execute terminal commands
- Search the web and browse websites
- Read/write files
- Open/close applications
- Take screenshots
- Manage clipboard
- Type text and press keys
- System monitoring
- Install packages
- Download files

Be helpful and execute user requests!"""


def get_help_text():
    return f"""
╔════════════ {AI_NAME} Full Control + Kali Linux Commands ════════════╗
║                                                                      ║
║     🖥️ TERMINAL:                                                     ║
║       • "run [command]" - Execute terminal command                   ║
║       • "open terminal" - Open terminal app                          ║
║                                                                      ║
║     🌐 WEB:                                                          ║
║       • "search [query]" - Search the web                            ║
║       • "wikipedia [topic]" - Get Wikipedia info                     ║
║       • "weather" - Check weather                                    ║
║       • "news" - Latest news                                         ║
║                                                                      ║
║     📂 FILES:                                                        ║
║       • "list files [path]" - List directory                         ║
║       • "find file [name]" - Search for files                        ║
║       • "read file [path]" - Read file content                       ║
║       • "delete file [path]" - Delete a file                         ║
║       • "create file [name] with [content]" - Create file            ║
║                                                                      ║
║     📱 APPS:                                                         ║
║       • "open [app]" - Open application                              ║
║       • "close [app]" - Close application                            ║
║                                                                      ║
║     💻 SYSTEM:                                                       ║
║       • "system info" - Full system information                      ║
║       • "processes" / "list processes" - Running processes           ║
║       • "screenshot" - Take screenshot                               ║
║       • "cpu" / "memory" / "disk" - Quick stats                      ║
║                                                                      ║
║     ⌨️ INPUT:                                                        ║
║       • "type [text]" - Type text                                    ║
║       • "press [key]" - Press a key                                  ║
║       • "click" - Mouse click                                        ║
║                                                                      ║
║     📋 CLIPBOARD:                                                    ║
║       • "clipboard" - Show clipboard                                 ║
║       • "copy [text]" - Copy to clipboard                            ║
║                                                                      ║
║     📦 SYSTEM MAINTENANCE:                                           ║
║       • "install [package]" - Install package (needs sudo)           ║
║       • "update" - Update system (apt update)                        ║
║       • "git clone [url]" - Clone repository                         ║
║       • "download [url]" - Download file                             ║
║                                                                      ║
║  ═══════════════════════ KALI LINUX SPECIFIC ═══════════════════════ ║
║                                                                      ║
║     🛠️ PROCESS MANAGEMENT:                                           ║   
║       • "list processes" - Show top processes                        ║   
║       • "find process [name]" - Find process by name                 ║   
║       • "kill process [PID]" - Kill a process                        ║   
║                                                                      ║   
║     🌐 NETWORK OPERATIONS:                                           ║   
║       • "network status" / "check network" - Network config          ║   
║       • "listening ports" / "check ports" - Show open ports          ║   
║       • "connections" - Show active connections                      ║   
║       • "nmap scan [target]" - Run nmap scan                         ║   
║                                                                      ║   
║     ⚙️ SERVICES:                                                     ║   
║       • "list services" - Show running services                      ║   
║       • "service status [name]" - Check service status               ║   
║       • "start service [name]" - Start a service                     ║   
║       • "stop service [name]" - Stop a service                       ║   
║                                                                      ║   
║     📦 PACKAGE MANAGEMENT:                                           ║   
║       • "check package [name]" - Check if package installed          ║   
║       • "list packages" - List installed packages                    ║   
║       • "apt update" - Update package lists                          ║   
║       • "apt upgrade" - Upgrade system                               ║   
║                                                                      ║   
║     🛡️ SECURITY & FIREWALL:                                          ║   
║       • "check iptables" - Show iptables rules                       ║   
║       • "ufw status" - Show UFW status                               ║   
║       • "check root" - Check if running as root                      ║   
║       • "kali tools" - Check installed Kali tools                    ║   
║                                                                      ║   
║     📝 LOGS & ANALYSIS:                                              ║   
║       • "system logs" / "logs" - Show system logs                    ║   
║       • "auth logs" - Show authentication logs                       ║   
║       • "dmesg" / "kernel logs" - Show kernel messages               ║   
║                                                                      ║   
║     👥 USER MANAGEMENT:                                              ║   
║       • "list users" - Show system users                             ║   
║       • "list groups" - Show system groups                           ║   
║                                                                      ║   
║     💾 DISK & FILES:                                                 ║   
║       • "disk usage" - Show disk space                               ║   
║       • "mounts" - Show mount points                                 ║   
║       • "find large files" - Find big files                          ║   
║       • "file info [path]" - Show file permissions                   ║   
║                                                                      ║   
║     💬 CONVERSATION:                                                 ║   
║       • Just talk naturally!                                         ║   
║       • "joke" - Tell a joke                                         ║   
║       • "help" - Show this menu                                      ║   
║                                                                      ║   
║     🔴 Say "exit" to quit                                            ║
╚══════════════════════════════════════════════════════════════════════╝
"""


def main():
    print(f"\n🤖 {AI_NAME} Core v{VERSION} - ML + Full PC Control\n")
    
    if get_brain:
        print(f"🧠 Neural Brain initialized")
        print(f"   Memory: {get_brain().get_memory_stats()}")
    
    if system:
        print(f"💻 Full System Control ready")
    
    print("\n" + "="*60)
    print("COMMANDS: search, run [cmd], open [app], system info,")
    print("          files, clipboard, type, click, and more!")
    print("="*60)
    print("Or just talk naturally! Say 'exit' to quit\n")
    
    # Greeting
    if get_brain:
        from bosco_os.brain.neural_brain import NormalHumanPersonality
        greeting = NormalHumanPersonality().get_greeting()
    else:
        greeting = f"{AI_NAME} online - Full PC Control ready!"
    
    print(f"🤖: {greeting}")
    speak(greeting)
    
    # Main loop
    while True:
        try:
            cmd = listen()
            
            if not cmd:
                continue
            
            if cmd in ['exit', 'quit', 'bye']:
                farewell = NormalHumanPersonality().get_farewell() if get_brain else "Goodbye!"
                print(f"🤖: {farewell}")
                speak(farewell)
                break
            
            print(f"🤖: Processing...")
            response = process_command(cmd)
            print(f"🤖: {response}")
            speak(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

