"""
Kareem OS v2.1 - Full Voice AI Assistant
With online capabilities, voice, storage, and quiz!
"""
import sys
import os
import json

# Suppress ALSA/PulseAudio/Jack warnings before importing audio libraries
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Use dummy audio driver
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='pyttsx3')

# Load config
def load_config():
    for path in ['config.json', 'bosco_os/config.json']:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    return {}

config = load_config()
AI_NAME = config.get('ai_name', 'Kareem')

# Import modules
from bosco_os.brain.llm_client import get_llm
from bosco_os.brain.personality import get_greeting, acknowledge, processing, witty
from bosco_os.brain.voice_online import (
    search, weather, news, wiki, stock, ip_info, storage_info,
    memory_info, quiz as quiz_game, speak as voice_speak
)
from bosco_os.capabilities.system.pc_control import (
    open_app, close_app, type_text, click, screenshot
)
from bosco_os.capabilities.system.control import cpu

# Initialize voice engine safely with proper audio backend
voice_engine = None
try:
    import pyttsx3
    # Try different drivers for Linux/Kali
    for driver in ['espeak', 'nsss', 'dummy']:
        try:
            voice_engine = pyttsx3.init(driver)
            # Test if it works
            voice_engine.setProperty('rate', 180)
            print(f"TTS initialized with {driver} driver")
            break
        except Exception as e:
            continue
except Exception as e:
    print(f"Warning: TTS engine not available: {e}")

def speak(text):
    """Voice output"""
    print(f"🔊 {AI_NAME}: {text}")
    
    # Try pyttsx3 first
    if voice_engine:
        try:
            voice_engine.stop()
            voice_engine.say(text)
            voice_engine.runAndWait()
            return
        except Exception as e:
            pass
    
    # Fallback to espeak command-line
    try:
        import subprocess
        # Escape text for shell
        text_escaped = text.replace('"', '\\"').replace('$', '\\$')
        subprocess.Popen(
            ['espeak', '-s', '120', '-a', '100', text_escaped],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        pass

def listen():
    """Voice input"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5)
        cmd = r.recognize_google(audio).lower()
        print(f"👤 You: {cmd}")
        return cmd
    except ImportError:
        print("Speech recognition not available. Using text input.")
        return input("⌨️ Type: ")
    except Exception as e:
        print(f"Listening error: {e}")
        return input("⌨️ Type: ")

def process_command(cmd):
    """Process commands with online + AI"""
    cmd = cmd.lower()
    llm = get_llm()
    
    # === VOICE COMMANDS ===
    if 'speak' in cmd or 'say' in cmd:
        text = cmd.replace('speak', '').replace('say', '').strip()
        return text
    
    # === ONLINE SEARCH ===
    if 'search' in cmd or 'look up' in cmd:
        query = cmd.replace('search', '').replace('look up', '').strip()
        return search(query)
    
    # === WIKIPEDIA ===
    if 'what is' in cmd or 'who is' in cmd or 'tell me about' in cmd:
        topic = cmd.replace('what is', '').replace('who is', '').replace('tell me about', '').strip()
        return wiki(topic)
    
    # === WEATHER ===
    if 'weather' in cmd:
        return weather()
    
    # === NEWS ===
    if 'news' in cmd:
        return news()
    
    # === STOCK ===
    if 'stock' in cmd or 'price of' in cmd:
        symbol = cmd.replace('stock', '').replace('price of', '').strip().upper()
        return stock(symbol)
    
    # === IP INFO ===
    if 'ip address' in cmd or 'my ip' in cmd:
        return ip_info()
    
    # === STORAGE ===
    if 'storage' in cmd or 'disk space' in cmd:
        info = storage_info()
        return f"Storage: {info.get('used')}/{info.get('total')} used ({info.get('percent')}%)"
    
    # === MEMORY/RAM ===
    if 'ram' in cmd or 'memory' in cmd:
        info = memory_info()
        return f"Memory: {info.get('used')}/{info.get('total')} used ({info.get('percent')}%)"
    
    # === QUIZ ===
    if 'quiz' in cmd:
        if 'start' in cmd or 'new' in cmd:
            quiz_game.reset()
            q = quiz_game.get_question()
            return f"Quiz time! {q}"
        elif 'answer' in cmd:
            answer = cmd.replace('answer', '').strip()
            return quiz_game.check_answer(answer)
        else:
            return quiz_game.get_question()
    
    # === PC CONTROL ===
    if 'open' in cmd:
        app = cmd.replace('open', '').strip()
        return open_app(app)
    
    if 'close' in cmd:
        app = cmd.replace('close', '').strip()
        return close_app(app)
    
    if 'type' in cmd or 'write' in cmd:
        text = cmd.replace('type', '').replace('write', '').strip()
        type_text(text)
        return f"Typed: {text}"
    
    if 'click' in cmd:
        click()
        return "Clicked! 🔥"
    
    if 'screenshot' in cmd:
        path = screenshot()
        return f"Screenshot saved! 💀"
    
    # === SYSTEM STATUS ===
    if 'status' in cmd or 'check' in cmd:
        m = memory_info()
        s = storage_info()
        return f"CPU: {cpu()}, RAM: {m.get('percent')}% used, Storage: {s.get('percent')}%"
    
    # === HELP ===
    if 'help' in cmd:
        return """
🔥 VOICE & ONLINE:
• "search [topic]" - Search web
• "weather" - Get weather
• "news" - Latest news
• "what is [topic]" - Wikipedia
• "quiz" - Start trivia

💀 PC CONTROL:
• "open [app]" - Open app
• "type [text]" - Type text
• "screenshot" - Capture screen

💾 STORAGE:
• "storage" - Check disk
• "memory" - Check RAM

Just talk naturally! 🔥
"""
    
    # === AI FALLBACK ===
    system_prompt = """You are Kareem, a cool AI. 
Use slang like 'lil bih', 'we made it', '💀', '🔥'.
Keep responses short and helpful."""
    
    return llm.chat(cmd, system_prompt)


def main():
    print(f"\n🔥💀 {AI_NAME} OS v2.1 - VOICE AI 💀🔥\n")
    
    greet = get_greeting()
    print(f"🤖: {greet}")
    speak(greet)
    
    print("\nCommands: search, weather, news, quiz, storage, memory, open, type, status")
    print("Or just talk naturally! Say 'exit' to quit\n")
    
    while True:
        try:
            cmd = listen()
            
            if not cmd:
                continue
            
            if cmd in ['exit', 'quit', 'bye']:
                speak("Later, we made it! 💀🔥")
                break
            
            print(f"🤖: {processing()}")
            response = process_command(cmd)
            print(f"🤖: {response}")
            speak(response)
            
        except KeyboardInterrupt:
            print("\n💀 We out 💀")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

