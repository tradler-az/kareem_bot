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
║         ★ ML-POWERED NEURAL BRAIN + FULL PC CONTROL ★        ║
║                      + KALI LINUX SUPPORT                    ║
║                           v{VERSION}                           ║
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

# Import NEW modules for enhanced features
try:
    from bosco_os.capabilities.network.url_scanner import get_url_scanner
    url_scanner = get_url_scanner()
    print("[+] URL Port Scanner loaded")
except Exception as e:
    print(f"[-] URL Scanner: {e}")
    url_scanner = None

try:
    from bosco_os.capabilities.system.app_manager import get_app_manager
    app_manager = get_app_manager()
    print("[+] App Manager loaded")
except Exception as e:
    print(f"[-] App Manager: {e}")
    app_manager = None

# Import Music Player
try:
    from bosco_os.capabilities.system.music_player import (
        get_music_player, play_music, stop_music, 
        pause_music, resume_music, music_status
    )
    music_player = get_music_player()
    print("[+] Music Player loaded")
except Exception as e:
    print(f"[-] Music Player: {e}")
    play_music = None
    stop_music = None

# Import NEW feature modules
try:
    from bosco_os.capabilities.system.background_executor import get_background_executor
    background_executor = get_background_executor()
    print("[+] Background Executor loaded")
except Exception as e:
    print(f"[-] Background Executor: {e}")
    background_executor = None

try:
    from bosco_os.capabilities.system.smart_launcher import get_smart_launcher
    smart_launcher = get_smart_launcher()
    print("[+] Smart Launcher loaded")
except Exception as e:
    print(f"[-] Smart Launcher: {e}")
    smart_launcher = None

try:
    from bosco_os.capabilities.system.root_manager import get_root_manager
    root_manager = get_root_manager()
    print("[+] Root Manager loaded")
except Exception as e:
    print(f"[-] Root Manager: {e}")
    root_manager = None

try:
    from bosco_os.capabilities.system.human_navigator import get_human_navigator
    human_navigator = get_human_navigator()
    print("[+] Human Navigator loaded")
except Exception as e:
    print(f"[-] Human Navigator: {e}")
    human_navigator = None

try:
    from bosco_os.capabilities.system.project_builder import get_project_builder
    project_builder = get_project_builder()
    print("[+] Project Builder loaded")
except Exception as e:
    print(f"[-] Project Builder: {e}")
    project_builder = None

try:
    from bosco_os.brain.conversation_memory import get_conversation_memory
    conversation_memory = get_conversation_memory()
    print("[+] Conversation Memory loaded")
except Exception as e:
    print(f"[-] Conversation Memory: {e}")
    conversation_memory = None

try:
    from bosco_os.core.self_update import get_update_manager
    update_manager = get_update_manager()
    print("[+] Self-Update System loaded")
except Exception as e:
    print(f"[-] Self-Update: {e}")
    update_manager = None

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
        
        # NEW: Port scanning
        if 'scan' in cmd and 'port' in cmd:
            target = cmd.replace('scan', '').replace('ports', '').replace('on', '').strip()
            if target and url_scanner:
                return url_scanner.quick_scan(target)
            return "What do you want to scan?"
        
        # ========== NEW FEATURE: BACKGROUND EXECUTOR ==========
        # Run commands in background
        if 'run in background' in cmd or 'run background' in cmd:
            command = cmd.replace('run in background', '').replace('run background', '').strip()
            if command and background_executor:
                return background_executor.execute_background(command, task_name=command[:30])
            return "What command to run in background?"
        
        if 'background tasks' in cmd or 'list tasks' in cmd:
            if background_executor:
                return background_executor.list_tasks()
            return "Background executor not available"
        
        if cmd.startswith('task status '):
            task_id = cmd.replace('task status', '').strip()
            if task_id and background_executor:
                status = background_executor.get_task_status(task_id)
                return f"Task: {status.get('name', 'Unknown')}\nStatus: {status.get('status', 'N/A')}\nOutput: {status.get('output', 'N/A')[:200]}"
            return "Which task?"
        
        if cmd.startswith('cancel task '):
            task_id = cmd.replace('cancel task', '').strip()
            if task_id and background_executor:
                return background_executor.cancel_task(task_id)
            return "Which task to cancel?"
        
        # ========== NEW FEATURE: ROOT MANAGER ==========
        # Sudo password handling
        if 'cache sudo password' in cmd or 'set sudo password' in cmd:
            return "Please provide your sudo password: say 'my sudo password is [password]'"
        
        if cmd.startswith('my sudo password is '):
            password = cmd.replace('my sudo password is', '').strip()
            if password and root_manager:
                return root_manager.set_sudo_password(password)
            return "No root manager available"
        
        if 'sudo' in cmd and root_manager:
            # Extract command after 'sudo'
            sudo_cmd = cmd.replace('sudo', '').strip()
            if sudo_cmd:
                return root_manager.run_as_root(sudo_cmd)
        
        if 'system update' in cmd or 'update system' in cmd:
            if root_manager and root_manager.is_sudo_valid():
                return "Running system update...\n" + root_manager.apt_update() + "\n" + root_manager.apt_upgrade()
            return "Please cache your sudo password first. Say 'my sudo password is [your password]'"
        
        if 'restart service' in cmd:
            service = cmd.replace('restart service', '').strip()
            if service and root_manager:
                return root_manager.restart_service(service)
            return "Which service to restart?"
        
        if 'stop service' in cmd:
            service = cmd.replace('stop service', '').strip()
            if service and root_manager:
                return root_manager.stop_service(service)
            return "Which service to stop?"
        
        if 'ufw' in cmd:
            if root_manager and root_manager.is_sudo_valid():
                if 'status' in cmd:
                    return root_manager.ufw_status()
                if 'enable' in cmd:
                    return root_manager.ufw_enable()
                if 'disable' in cmd:
                    return root_manager.ufw_disable()
                if 'allow' in cmd:
                    port = cmd.replace('ufw allow', '').strip()
                    return root_manager.ufw_allow(port)
            return "Please cache sudo password first"
        
        # ========== NEW FEATURE: SMART LAUNCHER ==========
        # Smart app launching
        if 'open' in cmd or 'launch' in cmd:
            app_name = cmd.replace('open', '').replace('launch', '').strip()
            if app_name and smart_launcher:
                return smart_launcher.smart_launch(app_name, auto_install=True)
            if app_name and open_app:
                return open_app(app_name)
            return "What to open?"
        
        if 'install' in cmd:
            app_name = cmd.replace('install', '').strip()
            if app_name and smart_launcher:
                return smart_launcher.install_app(app_name)
            if app_name and install_package:
                return install_package(app_name)
            return "What to install?"
        
        if 'search app' in cmd or 'find app' in cmd:
            query = cmd.replace('search app', '').replace('find app', '').strip()
            if query and smart_launcher:
                return smart_launcher.search_for_app(query)
            return "What app to search?"
        
        if 'list apps' in cmd or 'installed apps' in cmd:
            if smart_launcher:
                return smart_launcher.list_installed_apps()
            if app_manager:
                return app_manager.list_installed_apps(50)
            return "No app manager available"
        
        # ========== NEW FEATURE: HUMAN NAVIGATOR ==========
        # Mouse and keyboard control
        if 'click' in cmd:
            if human_navigator:
                # Parse coordinates if provided
                import re
                coords = re.findall(r'\d+', cmd)
                if len(coords) >= 2:
                    return human_navigator.click(int(coords[0]), int(coords[1]))
                return human_navigator.click()
            return "Navigator not available"
        
        if 'double click' in cmd:
            if human_navigator:
                return human_navigator.double_click()
            return "Navigator not available"
        
        if 'right click' in cmd:
            if human_navigator:
                return human_navigator.right_click()
            return "Navigator not available"
        
        if 'scroll up' in cmd:
            if human_navigator:
                return human_navigator.scroll_up(3)
            return "Navigator not available"
        
        if 'scroll down' in cmd:
            if human_navigator:
                return human_navigator.scroll_down(3)
            return "Navigator not available"
        
        if 'type' in cmd and not 'type text' in cmd:
            text = cmd.replace('type', '').strip()
            if text and human_navigator:
                return human_navigator.type_text(text)
            return "What to type?"
        
        if 'press key' in cmd:
            key = cmd.replace('press key', '').strip()
            if key and human_navigator:
                return human_navigator.press_key(key)
            return "Which key?"
        
        if 'hotkey' in cmd or 'shortcut' in cmd:
            keys = cmd.replace('hotkey', '').replace('shortcut', '').strip().split()
            if keys and human_navigator:
                return human_navigator.hotkey(*keys)
            return "Which keys?"
        
        if 'open website' in cmd or 'go to' in cmd:
            url = cmd.replace('open website', '').replace('go to', '').strip()
            if url and human_navigator:
                if not url.startswith('http'):
                    url = 'https://' + url
                return human_navigator.open_browser(url)
            return "Which website?"
        
        if 'close window' in cmd:
            if human_navigator:
                return human_navigator.close_window()
            return "Navigator not available"
        
        if 'minimize window' in cmd:
            if human_navigator:
                return human_navigator.minimize_window()
            return "Navigator not available"
        
        if 'maximize window' in cmd:
            if human_navigator:
                return human_navigator.maximize_window()
            return "Navigator not available"
        
        if 'switch window' in cmd or 'alt tab' in cmd:
            if human_navigator:
                return human_navigator.switch_window()
            return "Navigator not available"
        
        # ========== NEW FEATURE: PROJECT BUILDER ==========
        # Help build projects
        if 'build project' in cmd or 'create project' in cmd or 'help me build' in cmd:
            idea = cmd.replace('build project', '').replace('create project', '').replace('help me build', '').strip()
            if idea and project_builder:
                return project_builder.build_project(idea)
            if project_builder:
                return "What project do you want to build? Example: 'build project a machine learning app'"
            return "Project builder not available"
        
        if 'analyze idea' in cmd:
            idea = cmd.replace('analyze idea', '').strip()
            if idea and project_builder:
                analysis = project_builder.analyze_idea(idea)
                return f"Suggested type: {analysis['project_name']}\nTech stack: {', '.join(analysis['tech_stack'])}"
            return "What idea to analyze?"
        
        if cmd.startswith('create project '):
            # Parse: create project [name] as [type]
            parts = cmd.replace('create project', '').split(' as ')
            name = parts[0].strip() if parts else ''
            ptype = parts[1].strip() if len(parts) > 1 else 'web_app'
            if name and project_builder:
                return project_builder.create_project(name, ptype)
            return "Usage: create project [name] as [web_app/mobile_app/api/cli_tool/etc]"
        
        if 'project structure' in cmd:
            ptype = cmd.replace('project structure', '').strip()
            if project_builder:
                return project_builder.generate_project_structure(ptype or 'web_app', 'example')
            return "Project builder not available"
        
        if 'learning path' in cmd or 'how to learn' in cmd:
            # Extract project type from command
            for ptype in ['web_app', 'mobile_app', 'api', 'machine_learning', 'game', 'cli_tool']:
                if ptype.replace('_', ' ') in cmd:
                    if project_builder:
                        path = project_builder.get_learning_path(ptype)
                        result = f"Learning path for {ptype}:\n\n"
                        for item in path:
                            result += f"Week {item['step']}: {item['topic']} ({item['duration']})\n"
                        return result
            return "Which project type? Example: 'learning path for web development'"
        
        if 'documentation' in cmd and 'project' in cmd:
            for ptype in ['web_app', 'mobile_app', 'api', 'machine_learning']:
                if ptype.replace('_', ' ') in cmd:
                    if project_builder:
                        docs = project_builder.get_documentation_links(ptype)
                        result = f"Documentation for {ptype}:\n\n"
                        for name, url in docs.items():
                            result += f"• {name}: {url}\n"
                        return result
            return "Which project type?"
        
        # NEW: App listing
        if cmd in ['list apps', 'show apps', 'all apps']:
            if app_manager:
                return app_manager.list_installed_apps(30)
            return "App manager not available"
        
        if 'running apps' in cmd or 'running applications' in cmd:
            if app_manager:
                return app_manager.list_running_apps()
            return "App manager not available"
        
        if 'find app' in cmd:
            name = cmd.replace('find app', '').strip()
            if name and app_manager:
                return app_manager.find_app(name)
            return "Which app?"
        
        # NEW: Memory commands
        if cmd.startswith('remember '):
            info = cmd.replace('remember ', '').strip()
            if info and conversation_memory:
                return conversation_memory.remember(info)
            return "What should I remember?"
        
        if 'what did i tell you' in cmd:
            topic = cmd.replace('what did i tell you about', '').strip()
            if topic and conversation_memory:
                return conversation_memory.recall(topic)
            return "What topic?"
        
        if 'what did we discuss' in cmd or 'what did we talk about' in cmd:
            if conversation_memory:
                return conversation_memory.what_did_we_discuss()
            return "No memory available"
        
        if 'recent talk' in cmd or 'show memory' in cmd:
            if conversation_memory:
                return conversation_memory.get_recent_summary()
            return "No memory available"
        
        # NEW: Update commands
        if 'update yourself' in cmd or 'check for updates' in cmd:
            if update_manager:
                result = update_manager.check_for_updates()
                if result.get('available'):
                    return f"Update available: {result.get('current')} -> {result.get('latest')}"
                return "You're up to date!"
            return "Update system not available"
        
        # NEW: Mode commands
        if 'go online' in cmd:
            return "Switching to online mode"
        
        if 'go offline' in cmd:
            return "Switching to offline mode"
        
        if cmd == 'status':
            status = f"{AI_NAME} v{VERSION}\n"
            if kali_control:
                status += f"Kali: {'Yes' if kali_control.is_kali else 'No'}\n"
            if conversation_memory:
                stats = conversation_memory.get_stats()
                status += f"Conversations: {stats.get('total', 0)}"
            return status
        
        if 'help' in cmd:
            return get_help_text()
        
        if 'joke' in cmd:
            # Use Kali personality for jokes
            if get_kali_personality:
                return get_kali_personality().get_joke()
            from bosco_os.brain.neural_brain import NormalHumanPersonality
            return NormalHumanPersonality().get_joke()
        
        # MUSIC COMMANDS
        if 'play' in cmd or 'music' in cmd or 'song' in cmd:
            # Handle play music commands
            if play_music:
                # Parse the command to extract song and artist
                parsed = music_player.parse_song_command(cmd)
                song = parsed.get('song', '')
                artist = parsed.get('artist', '')
                
                if song:
                    return play_music(song, artist)
            else:
                return "Music player not available. Please install yt-dlp."
        
        if 'stop' in cmd and 'music' in cmd:
            if stop_music:
                return stop_music()
        
        if 'pause' in cmd and 'music' in cmd:
            if pause_music:
                return pause_music()
        
        if 'resume' in cmd or 'continue' in cmd:
            if resume_music:
                return resume_music()
        
        if 'now playing' in cmd or 'what song' in cmd:
            if music_status:
                return music_status()
        
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
╔══════════════════════════════════════════════════════════════════════════╗
║                  {AI_NAME} Full Control + Kali Linux Commands              ║
╚══════════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────┐
│ 🖥️ TERMINAL:                                                          │
│   • "run [command]" - Execute terminal command                         │
│   • "open terminal" - Open terminal app                                │
│   • "run background [command]" - Run command in background            │
│   • "background tasks" - List running background tasks                 │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 🌐 WEB:                                                                │
│   • "search [query]" - Search the web                                  │
│   • "wikipedia [topic]" - Get Wikipedia info                           │
│   • "weather" - Check weather                                         │
│   • "news" - Latest news                                              │
│   • "open website [url]" - Open website in browser                     │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 📂 FILES:                                                              │
│   • "list files [path]" - List directory                              │
│   • "find file [name]" - Search for files                             │
│   • "read file [path]" - Read file content                            │
│   • "delete file [path]" - Delete a file                              │
│   • "create file [name] with [content]" - Create file                 │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 📱 APP LAUNCHER (Smart):                                              │
│   • "open [app]" - Open app, install if not found                     │
│   • "install [app]" - Install application                              │
│   • "search app [name]" - Search for app                              │
│   • "list apps" - List installed applications                          │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 💻 SYSTEM:                                                             │
│   • "system info" - Full system information                           │
│   • "processes" / "list processes" - Running processes               │
│   • "screenshot" - Take screenshot                                   │
│   • "cpu" / "memory" / "disk" - Quick stats                         │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ ⌨️ INPUT (Human-like Navigation):                                     │
│   • "click" - Mouse click                                            │
│   • "click [x] [y]" - Click at coordinates                           │
│   • "double click" - Double click                                     │
│   • "right click" - Right click                                       │
│   • "scroll up/down" - Scroll                                         │
│   • "type [text]" - Type text                                        │
│   • "press key [key]" - Press a key                                   │
│   • "hotkey [keys]" - Press hotkey (e.g., ctrl c)                    │
│   • "close/minimize/maximize window" - Window control                │
│   • "switch window" - Alt+Tab                                         │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 📋 CLIPBOARD:                                                          │
│   • "clipboard" - Show clipboard                                      │
│   • "copy [text]" - Copy to clipboard                                 │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 🔐 ROOT / SUDO (Full System Control):                                  │
│   • "cache sudo password" - Cache sudo password                      │
│   • "my sudo password is [password]" - Set sudo password             │
│   • "sudo [command]" - Run command as sudo                           │
│   • "system update" - Update system (apt update && upgrade)          │
│   • "restart service [name]" - Restart system service                 │
│   • "stop service [name]" - Stop system service                      │
│   • "ufw status/enable/disable" - Firewall control                   │
│   • "ufw allow [port]" - Allow port in firewall                      │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 📦 SYSTEM MAINTENANCE:                                                 │
│   • "install [package]" - Install package (needs sudo)                │
│   • "update" - Update system (apt update)                            │
│   • "git clone [url]" - Clone repository                              │
│   • "download [url]" - Download file                                  │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 🚀 PROJECT BUILDER:                                                    │
│   • "build project [idea]" - Get full project guide                   │
│   • "create project [name] as [type]" - Create project structure    │
│   • "analyze idea [description]" - Analyze project idea              │
│   • "learning path [type]" - Get learning path                        │
│   • "project structure [type]" - Show project structure               │
│   • "documentation [type]" - Get documentation links                   │
│                                                                        │
│   Project types: web_app, mobile_app, api, cli_tool,                   │
│                 machine_learning, game, automation, iot, desktop_app   │
└────────────────────────────────────────────────────────────────────────┘

  ═══════════════════════════ KALI LINUX SPECIFIC ═══════════════════════

┌────────────────────────────────────────────────────────────────────────┐
│ 🛠️ PROCESS MANAGEMENT:                                                │
│   • "list processes" - Show top processes                             │
│   • "find process [name]" - Find process by name                     │
│   • "kill process [PID]" - Kill a process                             │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 🌐 NETWORK OPERATIONS:                                                 │
│   • "network status" / "check network" - Network config               │
│   • "listening ports" / "check ports" - Show open ports               │
│   • "connections" - Show active connections                           │
│   • "nmap scan [target]" - Run nmap scan                             │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ ⚙️ SERVICES:                                                          │
│   • "list services" - Show running services                           │
│   • "service status [name]" - Check service status                    │
│   • "start service [name]" - Start a service                         │
│   • "stop service [name]" - Stop a service                           │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 📦 PACKAGE MANAGEMENT:                                                │
│   • "check package [name]" - Check if package installed               │
│   • "list packages" - List installed packages                         │
│   • "apt update" - Update package lists                              │
│   • "apt upgrade" - Upgrade system                                   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 🛡️ SECURITY & FIREWALL:                                               │
│   • "check iptables" - Show iptables rules                            │
│   • "ufw status" - Show UFW status                                  │
│   • "check root" - Check if running as root                          │
│   • "kali tools" - Check installed Kali tools                        │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 📝 LOGS & ANALYSIS:                                                   │
│   • "system logs" / "logs" - Show system logs                         │
│   • "auth logs" - Show authentication logs                           │
│   • "dmesg" / "kernel logs" - Show kernel messages                   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ 💬 CONVERSATION:                                                      │
│   • Just talk naturally!                                              │
│   • "joke" - Tell a joke                                             │
│   • "help" - Show this menu                                          │
└────────────────────────────────────────────────────────────────────────┘

🔴 Say "exit" to quit
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

