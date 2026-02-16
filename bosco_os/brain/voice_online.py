"""Kareem OS - Voice & Online Services"""
import os
import warnings
# Suppress ALSA/PulseAudio warnings for cleaner output
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings('ignore', category=DeprecationWarning)

import requests
import json
import subprocess

class VoiceEngine:
    """Text to speech engine with ALSA/PulseAudio handling"""
    
    def __init__(self):
        self.rate = 180
        self.engine = None
        self.use_sound = True
        self._init_engine()
    
    def _init_engine(self):
        try:
            import pyttsx3
            # Initialize with explicit driver to avoid ALSA issues
            self.engine = pyttsx3.init('espeak')
            self.engine.setProperty('rate', self.rate)
            # Try to set a working voice
            try:
                voices = self.engine.getProperty('voices')
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
            except:
                pass
        except Exception as e:
            # Fallback: try default driver
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.rate)
            except Exception as e2:
                print(f"Voice init warning: {e2}")
                self.engine = None
    
    def speak(self, text):
        """Speak text aloud"""
        # Just print if no sound
        if not self.use_sound:
            print(f"🔊 {text}")
            return
            
        if self.engine:
            try:
                self.engine.stop()
                self.engine.say(text)
                # Use runAndWait with timeout handling
                self.engine.runAndWait()
                return
            except RuntimeError as e:
                # Handle "run loop already started" error
                try:
                    self.engine.stop()
                except:
                    pass
            except Exception as e:
                pass
        
        # Silent fallback - just print
        print(f"🔊 {text}")
    
    def set_rate(self, rate):
        self.rate = rate
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass


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


# Global instances
voice = VoiceEngine()
online = OnlineServices()
storage = StorageManager()
quiz = QuizGame()

# Quick functions
def speak(text): return voice.speak(text)
def search(query): return online.search_web(query)
def weather(city="local"): return online.get_weather(city)
def news(topic="technology"): return online.get_news(topic)
def wiki(topic): return online.get_wikipedia(topic)
def stock(symbol): return online.get_stock(symbol)
def ip_info(): return online.get_ip_info()
def storage_info(): return storage.get_storage_info()
def memory_info(): return storage.get_memory_info()
def quiz_question(): return quiz.get_question()
def quiz_answer(ans): return quiz.check_answer(ans)
def reset_quiz(): return quiz.reset()

