#!/usr/bin/env python3
"""
Bosco Core v3.0 - ML-Powered AI Assistant with Full PC Control
CLI-based with neural brain, learning, terminal access, and web browsing
"""

import os
import sys
import json
import time
import warnings

# Suppress audio warnings
os.environ['SDL_AUDIODRIVER'] = 'dummy'
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
║     ██╗   ██╗███████╗██████╗ ████████╗███████╗██╗  ██╗    ║
║     ██║   ██║██╔════╝██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝    ║
║     ██║   ██║█████╗  ██████╔╝   ██║   █████╗   ╚███╔╝     ║
║     ╚██╗ ██╔╝██╔══╝  ██╔══██╗   ██║   ██╔══╝   ██╔██╗     ║
║      ╚████╔╝ ███████╗██║  ██║   ██║   ███████╗██╔╝ ██╗    ║
║       ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝    ║
║                                                              ║
║        ML-POWERED NEURAL BRAIN + FULL PC CONTROL            ║
║                        v{VERSION}                             ║
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

# Initialize voice
voice_engine = None
def init_voice():
    try:
        import pyttsx3
        for driver in ['espeak', 'nsss', 'dummy']:
            try:
                v = pyttsx3.init(driver)
                v.setProperty('rate', 180)
                print(f"[+] TTS: {driver}")
                return v
            except:
                continue
    except:
        pass
    return None

voice_engine = init_voice()


def speak(text):
    """Voice output"""
    print(f"🔊 {AI_NAME}: {text}")
    if voice_engine:
        try:
            voice_engine.stop()
            voice_engine.say(text)
            voice_engine.runAndWait()
        except:
            pass
    # Fallback
    try:
        import subprocess
        text_escaped = text.replace('"', '\\"')
        subprocess.Popen(['espeak', '-s', '120', text_escaped], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass


def listen():
    """Voice input"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5)
        cmd = r.recognize_google(audio).lower()
        print(f"👤 You: {cmd}")
        return cmd
    except:
        return input("⌨️ Type: ")


def process_command(cmd):
    """Process commands with full system control"""
    if not cmd:
        return "I didn't catch that."
    
    cmd = cmd.lower().strip()
    
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
                return run_command(command)
        
        if 'terminal' in cmd or 'cmd' in cmd:
            return open_app('terminal')
        
        if 'screenshot' in cmd:
            return screenshot()
        
        if 'system info' in cmd or 'check system' in cmd:
            return system_info()
        
        if 'processes' in cmd or 'running' in cmd:
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
            m = memory_info()
            s = storage_info()
            return f"CPU: {cpu()}, RAM: {m.get('percent', 'N/A')}%, Storage: {s.get('percent', 'N/A')}%"
        
        if 'help' in cmd:
            return get_help_text()
        
        if 'joke' in cmd:
            from bosco_os.brain.neural_brain import NormalHumanPersonality
            return NormalHumanPersonality().get_joke()
        
        # Return neural brain response for conversation
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
╔══════════════════ {AI_NAME} Full Control Commands ══════════════════╗
║                                                                 ║
║  🖥️ TERMINAL:                                                   ║
║    • "run [command]" - Execute terminal command               ║
║    • "open terminal" - Open terminal app                       ║
║                                                                 ║
║  🌐 WEB:                                                        ║
║    • "search [query]" - Search the web                        ║
║    • "wikipedia [topic]" - Get Wikipedia info                  ║
║    • "weather" - Check weather                                 ║
║    • "news" - Latest news                                      ║
║                                                                 ║
║  📂 FILES:                                                      ║
║    • "list files [path]" - List directory                      ║
║    • "find file [name]" - Search for files                     ║
║    • "read file [path]" - Read file content                   ║
║    • "delete file [path]" - Delete a file                     ║
║    • "create file [name] with [content]" - Create file        ║
║                                                                 ║
║  📱 APPS:                                                       ║
║    • "open [app]" - Open application                           ║
║    • "close [app]" - Close application                         ║
║                                                                 ║
║  💻 SYSTEM:                                                     ║
║    • "system info" - Full system information                   ║
║    • "processes" - Running processes                            ║
║    • "screenshot" - Take screenshot                            ║
║    • "cpu" / "memory" / "disk" - Quick stats                  ║
║                                                                 ║
║  ⌨️ INPUT:                                                      ║
║    • "type [text]" - Type text                                 ║
║    • "press [key]" - Press a key                               ║
║    • "click" - Mouse click                                     ║
║                                                                 ║
║  📋 CLIPBOARD:                                                  ║
║    • "clipboard" - Show clipboard                              ║
║    • "copy [text]" - Copy to clipboard                         ║
║                                                                 ║
║  📦 SYSTEM MAINTENANCE:                                         ║
║    • "install [package]" - Install package (needs sudo)        ║
║    • "update" - Update system                                   ║
║    • "git clone [url]" - Clone repository                      ║
║    • "download [url]" - Download file                          ║
║                                                                 ║
║  💬 CONVERSATION:                                               ║
║    • Just talk naturally!                                      ║
║    • "joke" - Tell a joke                                     ║
║    • "help" - Show this menu                                   ║
║                                                                 ║
║  🔴 Say "exit" to quit                                        ║
╚══════════════════════════════════════════════════════════════════╝
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

