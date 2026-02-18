"""Kareem OS - Voice & Online Services"""
import os
import sys
import threading
import warnings

# Suppress ALSA/PulseAudio/Jack warnings for cleaner output
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Suppress warnings before importing audio libraries
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import requests
import json
import subprocess

# Thread lock for TTS
_tts_lock = threading.Lock()


class VoiceEngine:
    """Text to speech engine with proper Linux/Kali audio handling"""
    
    def __init__(self):
        self.rate = 180
        self.volume = 1.0
        self.engine = None
        self.use_sound = True
        self.is_speaking = False
        self._init_engine()
    
    def _init_engine(self):
        """Initialize TTS engine with multiple fallback options"""
        # Try pyttsx3 with different drivers
        drivers = ['espeak', 'nsss', 'dummy']
        
        for driver in drivers:
            try:
                import pyttsx3
                self.engine = pyttsx3.init(driver)
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                
                # Try to set a good voice
                try:
                    voices = self.engine.getProperty('voices')
                    if voices:
                        # Try to find English voice
                        for voice in voices:
                            if 'english' in voice.name.lower():
                                self.engine.setProperty('voice', voice.id)
                                break
                        else:
                            self.engine.setProperty('voice', voices[0].id)
                except:
                    pass
                    
                print(f"TTS initialized with {driver} driver")
                return
            except Exception as e:
                continue
        
        # If all drivers fail, use command-line fallback
        print("pyttsx3 initialization failed, using command-line fallback")
        self.engine = None
    
    def speak(self, text):
        """Speak text aloud - thread-safe"""
        if not text:
            return
            
        # Print to console as fallback or when sound disabled
        if not self.use_sound:
            print(f"🔊 {text}")
            return
        
        with _tts_lock:
            self.is_speaking = True
            try:
                if self.engine:
                    try:
                        self.engine.stop()
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except RuntimeError as e:
                        # Handle "run loop already started" error
                        if "run loop" in str(e).lower():
                            # Reinitialize engine
                            try:
                                self._init_engine()
                                if self.engine:
                                    self.engine.say(text)
                                    self.engine.runAndWait()
                            except:
                                pass
                        else:
                            raise
                    except Exception as e:
                        # Fallback to command-line TTS
                        self._fallback_speak(text)
                else:
                    # No engine, use fallback
                    self._fallback_speak(text)
            finally:
                self.is_speaking = False
    
    def _fallback_speak(self, text):
        """Command-line TTS fallback using espeak or say"""
        try:
            # Linux: try espeak
            if sys.platform == 'linux' or sys.platform == 'linux2':
                # Check if espeak is available
                result = subprocess.run(['which', 'espeak'], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.Popen(
                        ['espeak', '-s', str(self.rate//30), '-a', str(int(self.volume*100)), text],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return
            
            # macOS: try say command
            if sys.platform == 'darwin':
                subprocess.Popen(
                    ['say', text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
            
            # Windows: try PowerShell
            if sys.platform == 'win32':
                subprocess.Popen(
                    ['powershell', '-Command', f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{text}")'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
                
        except:
            pass
        
        # Ultimate fallback: just print
        print(f"🔊 {text}")
    
    def interrupt(self):
        """Interrupt current speech"""
        with _tts_lock:
            self.is_speaking = False
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
    
    def set_rate(self, rate):
        self.rate = rate
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass
    
    def set_volume(self, volume):
        self.volume = volume
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
            except:
                pass
    
    def get_voices(self):
        """Get available voices"""
        if self.engine:
            try:
                return [(v.id, v.name) for v in self.engine.getProperty('voices')]
            except:
                pass
        return []


class OnlineServices:
    """Online capabilities - search, facts, weather, news"""
    
    def __init__(self):
        self.llm = None
    
    def search_web(self, query):
        """Search the web using DuckDuckGo"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            
            if data.get('AbstractText'):
                return data['AbstractText']
            elif data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:3]:
                    if 'Text' in topic:
                        return topic['Text']
            return "Couldn't find info on that"
        except Exception as e:
            return f"Search error: {e}"
    
    def get_weather(self, city="local"):
        """Get weather info"""
        try:
            # Use wttr.in (no API key needed)
            resp = requests.get(f"https://wttr.in/{city}?format=%c%t+%h", timeout=5)
            return resp.text.strip()
        except:
            return "Weather unavailable"
    
    def get_news(self, topic="technology"):
        """Get news headlines"""
        try:
            # Use Hacker News API (free, no API key needed)
            resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5)
            story_ids = resp.json()[:10]
            
            results = []
            for story_id in story_ids:
                story_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
                story = story_resp.json()
                if story.get('title'):
                    results.append(f"• {story['title']}")
            
            return '\n'.join(results) if results else "No news found"
        except Exception as e:
            return f"News unavailable: {e}"
    
    def get_wikipedia(self, topic):
        """Get Wikipedia summary"""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
            headers = {"User-Agent": "BoscoOS/2.1 (https://github.com/bosco; contact@bosco.ai)"}
            resp = requests.get(url, timeout=5, headers=headers)
            data = resp.json()
            return data.get('extract', 'No info found')
        except:
            return "Wikipedia unavailable"
    
    def get_stock(self, symbol):
        """Get stock price"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return f"{symbol}: ${price}"
        except:
            return "Stock unavailable"
    
    def get_ip_info(self):
        """Get public IP info"""
        try:
            resp = requests.get("https://ipinfo.io/json", timeout=5)
            data = resp.json()
            return f"IP: {data.get('ip')}, City: {data.get('city')}, Country: {data.get('country')}"
        except:
            return "IP info unavailable"


class StorageManager:
    """Storage and memory management"""
    
    def __init__(self):
        self.data_dir = "kareem_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_storage_info(self):
        """Get storage info"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                "total": f"{disk.total / (1024**3):.1f} GB",
                "used": f"{disk.used / (1024**3):.1f} GB", 
                "free": f"{disk.free / (1024**3):.1f} GB",
                "percent": disk.percent
            }
        except:
            return {"error": "Storage info unavailable"}
    
    def get_memory_info(self):
        """Get memory info"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total": f"{mem.total / (1024**3):.1f} GB",
                "used": f"{mem.used / (1024**3):.1f} GB",
                "free": f"{mem.free / (1024**3):.1f} GB",
                "percent": mem.percent
            }
        except:
            return {"error": "Memory info unavailable"}
    
    def save_data(self, key, value):
        """Save data to storage"""
        try:
            with open(f"{self.data_dir}/{key}.json", 'w') as f:
                json.dump(value, f)
            return True
        except:
            return False
    
    def load_data(self, key):
        """Load data from storage"""
        try:
            with open(f"{self.data_dir}/{key}.json", 'r') as f:
                return json.load(f)
        except:
            return None
    
    def list_files(self):
        """List stored files"""
        try:
            return os.listdir(self.data_dir)
        except:
            return []


class QuizGame:
    """Quiz/trivia game"""
    
    def __init__(self):
        self.questions = [
            {"q": "What is the capital of France?", "a": "Paris"},
            {"q": "Who wrote Romeo and Juliet?", "a": "Shakespeare"},
            {"q": "What is 7 x 8?", "a": "56"},
            {"q": "What year did COVID-19 start?", "a": "2020"},
            {"q": "Who is the CEO of Tesla?", "a": "Musk"},
            {"q": "What planet is closest to the Sun?", "a": "Mercury"},
            {"q": "What is H2O?", "a": "Water"},
            {"q": "Who painted the Mona Lisa?", "a": "Da Vinci"},
            {"q": "What is the largest ocean?", "a": "Pacific"},
            {"q": "How many legs does a spider have?", "a": "8"},
        ]
        self.score = 0
        self.current = None
    
    def get_question(self):
        """Get random question"""
        import random
        self.current = random.choice(self.questions)
        return self.current["q"]
    
    def check_answer(self, answer):
        """Check answer"""
        if not self.current:
            return "No active question"
        
        correct = self.current["a"].lower()
        user_answer = answer.lower().strip()
        
        if correct in user_answer or user_answer in correct:
            self.score += 1
            return f"Correct! Score: {self.score}"
        else:
            return f"Wrong! Answer was: {self.current['a']}. Score: {self.score}"
    
    def reset(self):
        """Reset game"""
        self.score = 0
        self.current = None


# Global instances - lazy loaded to avoid blocking on import
_voice = None
_online = None
_storage = None
_quiz = None

def _get_voice():
    """Lazy load VoiceEngine"""
    global _voice
    if _voice is None:
        _voice = VoiceEngine()
    return _voice

def _get_online():
    """Lazy load OnlineServices"""
    global _online
    if _online is None:
        _online = OnlineServices()
    return _online

def _get_storage():
    """Lazy load StorageManager"""
    global _storage
    if _storage is None:
        _storage = StorageManager()
    return _storage

def _get_quiz():
    """Lazy load QuizGame"""
    global _quiz
    if _quiz is None:
        _quiz = QuizGame()
    return _quiz

# Quick functions - lazy loaded
def speak(text): return _get_voice().speak(text)
def search(query): return _get_online().search_web(query)
def weather(city="local"): return _get_online().get_weather(city)
def news(topic="technology"): return _get_online().get_news(topic)
def wiki(topic): return _get_online().get_wikipedia(topic)
def stock(symbol): return _get_online().get_stock(symbol)
def ip_info(): return _get_online().get_ip_info()
def storage_info(): return _get_storage().get_storage_info()
def memory_info(): return _get_storage().get_memory_info()
def quiz_question(): return _get_quiz().get_question()
def quiz_answer(ans): return _get_quiz().check_answer(ans)
def reset_quiz(): return _get_quiz().reset()

