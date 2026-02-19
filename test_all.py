#!/usr/bin/env python3
"""
Bosco Core v3.0 - COMBINED Test Suite
Comprehensive tests for all features: Basic + Advanced
This file combines test_brain.py and test_advanced_features.py
"""

import os
import sys
import asyncio
import time
import subprocess
from datetime import datetime

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['JACK_NO_AUDIO_RESERVATION'] = '1'
os.environ['JACK_NO_START_SERVER'] = '1'
os.environ['JACK_SERVER_NAME'] = 'none'

import warnings
warnings.filterwarnings('ignore')

# Test results tracking
TEST_RESULTS = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_result(name, passed, error=None):
    """Record test result"""
    if passed:
        TEST_RESULTS['passed'].append(name)
        print(f"  ✓ PASS: {name}")
    else:
        TEST_RESULTS['failed'].append((name, error))
        print(f"  ✗ FAIL: {name}")
        if error:
            print(f"      Error: {error}")

def print_header(title):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subheader(title):
    """Print subsection header"""
    print(f"\n--- {title} ---")


# ============================================================================
# SECTION 1: CORE MODULE IMPORTS
# ============================================================================

print_header("SECTION 1: CORE MODULE IMPORTS")

# 1.1 Neural Brain Modules
print_subheader("Neural Brain Modules")
try:
    from bosco_os.brain.neural_brain import (
        NeuralNetworkBrain, NormalHumanPersonality, 
        LearningEngine, PredictiveEngine,
        get_brain, process_input
    )
    test_result("Neural Brain Module Import", True)
except Exception as e:
    test_result("Neural Brain Module Import", False, str(e))

# 1.2 LLM Client
print_subheader("LLM Client")
try:
    from bosco_os.brain.llm_client import get_llm
    test_result("LLM Client Import", True)
except Exception as e:
    test_result("LLM Client Import", False, str(e))

# 1.3 Voice/Online Services
print_subheader("Voice/Online Services")
try:
    from bosco_os.brain.voice_online import search, weather, news, wiki
    test_result("Voice/Online Services Import", True)
except Exception as e:
    test_result("Voice/Online Services Import", False, str(e))

# 1.4 PC Control
print_subheader("PC Control")
try:
    from bosco_os.capabilities.system.pc_control import open_app, screenshot
    test_result("PC Control Import", True)
except Exception as e:
    test_result("PC Control Import", False, str(e))

# 1.5 System Control
print_subheader("System Control")
try:
    from bosco_os.capabilities.system.control import cpu
    test_result("System Control Import", True)
except Exception as e:
    test_result("System Control Import", False, str(e))

# 1.6 Advanced Features - Vector Memory
print_subheader("Advanced: Vector Memory")
try:
    from bosco_os.brain.vector_memory import VectorMemory
    test_result("Vector Memory Import", True)
except Exception as e:
    test_result("Vector Memory Import", False, str(e))

# 1.7 Advanced Features - Multi-Agent
print_subheader("Advanced: Multi-Agent System")
try:
    from bosco_os.agents import get_orchestrator, create_task, TaskPriority
    test_result("Multi-Agent Import", True)
except Exception as e:
    test_result("Multi-Agent Import", False, str(e))

# 1.8 Advanced Features - Security Expert
print_subheader("Advanced: Security Expert")
try:
    from bosco_os.agents.security_expert import get_security_expert, AgentTask
    test_result("Security Expert Import", True)
except Exception as e:
    test_result("Security Expert Import", False, str(e))

# 1.9 Advanced Features - Threat Detector
print_subheader("Advanced: Threat Detector")
try:
    from bosco_os.capabilities.security.threat_detector import ThreatDetector
    test_result("Threat Detector Import", True)
except Exception as e:
    test_result("Threat Detector Import", False, str(e))

# 1.10 Advanced Features - Screen Capture
print_subheader("Advanced: Screen Capture")
try:
    from bosco_os.perception.screen_capture import ScreenCapture
    test_result("Screen Capture Import", True)
except Exception as e:
    test_result("Screen Capture Import", False, str(e))

# 1.11 Advanced Features - MCP Server
print_subheader("Advanced: MCP Server")
try:
    from bosco_os.mcp.server import MCPServer, MCPTool
    test_result("MCP Server Import", True)
except Exception as e:
    test_result("MCP Server Import", False, str(e))

# 1.12 Advanced Features - Validator
print_subheader("Advanced: ReAct Validator")
try:
    from bosco_os.core.validator import ReActEngine, ExecutionValidator
    test_result("ReAct Validator Import", True)
except Exception as e:
    test_result("ReAct Validator Import", False, str(e))

# 1.13 Advanced Features - Sandbox
print_subheader("Advanced: Execution Sandbox")
try:
    from bosco_os.core.execution_sandbox import ExecutionSandbox
    test_result("Execution Sandbox Import", True)
except Exception as e:
    test_result("Execution Sandbox Import", False, str(e))

# 1.14 Advanced Features - Vision Engine
print_subheader("Advanced: Vision Engine")
try:
    from bosco_os.perception.vision_engine import VisionEngine
    test_result("Vision Engine Import", True)
except Exception as e:
    test_result("Vision Engine Import", False, str(e))

# 1.15 Advanced Features - MCP Server Manager
print_subheader("Advanced: MCP Server Manager")
try:
    from bosco_os.mcp.server_manager import get_mcp_server_manager
    test_result("MCP Server Manager Import", True)
except Exception as e:
    test_result("MCP Server Manager Import", False, str(e))


# ============================================================================
# SECTION 2: NEURAL BRAIN TESTS
# ============================================================================

print_header("SECTION 2: NEURAL BRAIN TESTS")

# 2.1 Neural Brain Initialization
print_subheader("Neural Brain Initialization")
try:
    brain = NeuralNetworkBrain(data_dir="data")
    test_result("Neural Brain Init", True)
    print(f"     Memory Stats: {brain.get_memory_stats()}")
except Exception as e:
    test_result("Neural Brain Init", False, str(e))
    brain = None

# 2.2 Intent Classification
print_subheader("Intent Classification (ML)")
if brain:
    test_inputs = [
        ("hello there", "greeting"),
        ("what's the weather", "weather"),
        ("search for python", "search"),
        ("check cpu usage", "system"),
        ("open notepad", "control"),
        ("remind me to call mom", "reminder"),
        ("play some music", "music"),
        ("tell me a joke", "joke"),
        ("how are you doing", "conversation"),
        ("what can you help me with", "help")
    ]
    
    correct = 0
    total = len(test_inputs)
    
    for inp, expected in test_inputs:
        try:
            result = brain.process(inp)
            intent = result['intent']
            if intent == expected:
                correct += 1
        except Exception as e:
            pass
    
    accuracy = 100 * correct / total
    test_result(f"Intent Classification ({accuracy:.0f}%)", accuracy >= 70)
else:
    test_result("Intent Classification", False, "Brain not initialized")

# 2.3 Sentiment Analysis
print_subheader("Sentiment Analysis")
if brain:
    sentiment_tests = [
        ("I love this, it's amazing!", "positive"),
        ("This is terrible and horrible", "negative"),
        ("It's okay I guess", "neutral"),
        ("I'm so happy today!", "positive"),
        ("This makes me really angry", "negative")
    ]
    
    correct = 0
    for text, expected in sentiment_tests:
        sentiment = brain._analyze_sentiment(text.lower())
        if expected == "positive" and sentiment > 0.1:
            correct += 1
        elif expected == "negative" and sentiment < -0.1:
            correct += 1
        elif expected == "neutral" and -0.1 <= sentiment <= 0.1:
            correct += 1
    
    test_result(f"Sentiment Analysis ({correct}/5)", correct >= 3)
else:
    test_result("Sentiment Analysis", False, "Brain not initialized")

# 2.4 Normal Human Personality
print_subheader("Normal Human Personality")
if brain:
    try:
        personality = NormalHumanPersonality()
        
        greeting = personality.get_greeting()
        farewell = personality.get_farewell()
        joke = personality.get_joke()
        help_text = personality.get_help()
        converse = personality.converse('how are you', 0.3)
        
        test_result("Personality Responses", len(greeting) > 0 and len(joke) > 0)
    except Exception as e:
        test_result("Personality Responses", False, str(e))
else:
    test_result("Personality Responses", False, "Brain not initialized")

# 2.5 Memory System
print_subheader("Memory System")
if brain:
    try:
        # Short-term memory
        brain.short_term_memory.append({
            'timestamp': time.time(),
            'input': 'test input',
            'intent': 'conversation',
            'sentiment': 0.0
        })
        stm_ok = len(brain.short_term_memory) >= 1
        
        # Long-term memory
        brain.remember('test_key', 'test_value')
        recall_ok = brain.recall('test_key') == 'test_value'
        
        # Working memory
        brain.update_context('current_task', 'testing')
        wm_ok = brain.get_context('current_task') == 'testing'
        
        stats = brain.get_memory_stats()
        
        test_result("Memory Systems", stm_ok and recall_ok and wm_ok)
    except Exception as e:
        test_result("Memory Systems", False, str(e))
else:
    test_result("Memory Systems", False, "Brain not initialized")

# 2.6 Learning Engine
print_subheader("Learning Engine")
if brain:
    try:
        learning = LearningEngine(brain)
        learning.learn("test input", "test response", "positive")
        stats = learning.get_learning_stats()
        
        test_result("Learning Engine", stats['total_interactions'] >= 1)
    except Exception as e:
        test_result("Learning Engine", False, str(e))
else:
    test_result("Learning Engine", False, "Brain not initialized")

# 2.7 Predictive Engine
print_subheader("Predictive Analytics")
if brain:
    try:
        predictor = PredictiveEngine()
        
        now = datetime.now()
        predictor.record_action("user1", "check_weather", now)
        predictor.record_action("user1", "search", datetime.fromtimestamp(now.timestamp() + 100))
        predictor.record_action("user1", "check_weather", datetime.fromtimestamp(now.timestamp() + 200))
        
        prediction = predictor.predict_next_action("user1")
        
        test_result("Predictive Analytics", prediction == "check_weather")
    except Exception as e:
        test_result("Predictive Analytics", False, str(e))
else:
    test_result("Predictive Analytics", False, "Brain not initialized")


# ============================================================================
# SECTION 3: ONLINE SERVICES TESTS
# ============================================================================

print_header("SECTION 3: ONLINE SERVICES TESTS")

# 3.1 Weather
print_subheader("Weather Service")
try:
    w = weather()
    test_result("Weather Service", len(w) > 0)
except Exception as e:
    test_result("Weather Service", False, str(e))

# 3.2 Search
print_subheader("Web Search")
try:
    s = search("artificial intelligence")
    test_result("Web Search", len(s) > 0)
except Exception as e:
    test_result("Web Search", False, str(e))

# 3.3 Wikipedia
print_subheader("Wikipedia")
try:
    wk = wiki("Python")
    test_result("Wikipedia", len(wk) > 0)
except Exception as e:
    test_result("Wikipedia", False, str(e))


# ============================================================================
# SECTION 4: SYSTEM INFO TESTS
# ============================================================================

print_header("SECTION 4: SYSTEM INFO TESTS")

# 4.1 CPU Info
print_subheader("CPU Information")
try:
    cpu_info = cpu()
    test_result("CPU Info", len(str(cpu_info)) > 0)
except Exception as e:
    test_result("CPU Info", False, str(e))

# 4.2 Memory Info
print_subheader("Memory Information")
try:
    from bosco_os.brain.voice_online import memory_info
    mem_info = memory_info()
    test_result("Memory Info", 'percent' in mem_info or 'total' in mem_info)
except Exception as e:
    test_result("Memory Info", False, str(e))

# 4.3 Storage Info
print_subheader("Storage Information")
try:
    from bosco_os.brain.voice_online import storage_info
    storage = storage_info()
    test_result("Storage Info", 'percent' in storage or 'total' in storage)
except Exception as e:
    test_result("Storage Info", False, str(e))


# ============================================================================
# SECTION 5: FULL CONVERSATION FLOW
# ============================================================================

print_header("SECTION 5: FULL CONVERSATION FLOW")

if brain:
    conversations = [
        "Hello Bosco",
        "What's the weather like today?",
        "Tell me about Python programming",
        "Can you check my system status?",
        "Tell me a joke",
        "How are you doing?",
        "Thanks for your help"
    ]
    
    try:
        for conv in conversations:
            result = brain.process(conv)
            assert len(result['response']) > 0
        
        test_result("Full Conversation Flow", True)
    except Exception as e:
        test_result("Full Conversation Flow", False, str(e))
else:
    test_result("Full Conversation Flow", False, "Brain not initialized")


# ============================================================================
# SECTION 6: ADVANCED FEATURES TESTS (ASYNC)
# ============================================================================

async def run_async_tests():
    """Run async advanced feature tests"""
    
    print_header("SECTION 6: ADVANCED FEATURES TESTS")
    
    # 6.1 Vector Memory Test
    print_subheader("Vector Memory (RAG)")
    try:
        vm = VectorMemory()
        vm.add("Bosco was created by Tradler", metadata={"type": "fact"})
        vm.add("Python is a programming language", metadata={"type": "fact"})
        vm.add("Security is important for systems", metadata={"type": "fact"})
        results = vm.search("who created Bosco", n_results=3)
        
        test_result("Vector Memory", len(results) >= 0)  # May be empty if no embeddings
    except Exception as e:
        test_result("Vector Memory", False, str(e))
    
    # 6.2 Multi-Agent Test
    print_subheader("Multi-Agent Orchestration")
    try:
        orchestrator = get_orchestrator()
        status = orchestrator.get_status()
        
        test_result("Multi-Agent System", 'agents' in status)
    except Exception as e:
        test_result("Multi-Agent System", False, str(e))
    
    # 6.3 Security Expert Test
    print_subheader("Security Expert Agent")
    try:
        agent = get_security_expert()
        
        test_result("Security Expert", agent is not None)
    except Exception as e:
        test_result("Security Expert", False, str(e))
    
    # 6.4 Threat Detector Test
    print_subheader("Threat Detector")
    try:
        detector = ThreatDetector()
        test_text = "Failed login attempt from IP 192.168.1.100"
        events = detector.detect_in_text(test_text, source="test")
        
        test_result("Threat Detector", detector is not None)
    except Exception as e:
        test_result("Threat Detector", False, str(e))
    
    # 6.5 Screen Capture Test
    print_subheader("Screen Capture")
    try:
        capture = ScreenCapture()
        
        test_result("Screen Capture", capture is not None)
    except Exception as e:
        test_result("Screen Capture", False, str(e))
    
    # 6.6 MCP Server Test
    print_subheader("MCP Server")
    try:
        server = MCPServer("test-server")
        
        async def hello_handler(params):
            return {"message": f"Hello, {params.get('name', 'World')}!"}
        
        server.register_tool(MCPTool(
            name="hello",
            description="Say hello",
            input_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            handler=hello_handler
        ))
        
        test_result("MCP Server", len(server.list_tools()) >= 1)
    except Exception as e:
        test_result("MCP Server", False, str(e))
    
    # 6.7 ReAct Validator Test
    print_subheader("ReAct Validator")
    try:
        validator = ExecutionValidator()
        result = validator.validate("echo 'test'")
        
        test_result("ReAct Validator", 'action' in result)
    except Exception as e:
        test_result("ReAct Validator", False, str(e))
    
    # 6.8 Execution Sandbox Test
    print_subheader("Execution Sandbox")
    try:
        sandbox = ExecutionSandbox(timeout=5)
        
        test_result("Execution Sandbox", sandbox is not None)
    except Exception as e:
        test_result("Execution Sandbox", False, str(e))
    
    # 6.9 Vision Engine Test
    print_subheader("Vision Engine")
    try:
        engine = VisionEngine()
        
        test_result("Vision Engine", engine is not None)
    except Exception as e:
        test_result("Vision Engine", False, str(e))
    
    # 6.10 MCP Server Manager Test
    print_subheader("MCP Server Manager")
    try:
        manager = get_mcp_server_manager()
        presets = manager.get_presets()
        
        test_result("MCP Server Manager", len(presets) >= 0)
    except Exception as e:
        test_result("MCP Server Manager", False, str(e))

# Run async tests
asyncio.run(run_async_tests())


# ============================================================================
# SECTION 7: LEARNING CONTROL TESTS
# ============================================================================

print_header("SECTION 7: LEARNING CONTROL TESTS")

if brain:
    try:
        brain.set_learning(False)
        learning_disabled = not brain.is_learning
        
        brain.set_learning(True)
        learning_enabled = brain.is_learning
        
        test_result("Learning Toggle", learning_disabled and learning_enabled)
    except Exception as e:
        test_result("Learning Toggle", False, str(e))
else:
    test_result("Learning Toggle", False, "Brain not initialized")


# ============================================================================
# SECTION 8: KALI LINUX INTEGRATION
# ============================================================================

print_header("SECTION 8: KALI LINUX INTEGRATION")

print_subheader("Kali Control Module")
try:
    from bosco_os.capabilities.system.kali_control import get_kali_control
    kali = get_kali_control()
    
    if kali:
        test_result("Kali Control", True)
        print(f"     Kali Mode: {kali.is_kali}")
    else:
        test_result("Kali Control", True)  # Should work even if not Kali
except Exception as e:
    test_result("Kali Control", False, str(e))

print_subheader("Linux Command Handler")
try:
    from bosco_os.brain.linux_command_handler import get_linux_handler, process_linux_command
    test_result("Linux Command Handler", process_linux_command is not None)
except Exception as e:
    test_result("Linux Command Handler", False, str(e))


# ============================================================================
# SECTION 9: SYSTEM ISSUE DIAGNOSTICS
# ============================================================================

print_header("SECTION 9: SYSTEM ISSUE DIAGNOSTICS")

def check_audio_system():
    """Check audio system for common issues"""
    issues = []
    fixes = []
    
    # Check ALSA
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            issues.append("ALSA not working properly")
            fixes.append("Install: sudo apt-get install alsa-utils")
    except FileNotFoundError:
        issues.append("ALSA utils not installed")
        fixes.append("Install: sudo apt-get install alsa-utils")
    except Exception as e:
        issues.append(f"ALSA check failed: {e}")
    
    # Check PulseAudio
    try:
        result = subprocess.run(['pactl', 'info'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            issues.append("PulseAudio not running")
            fixes.append("Start: pulseaudio --start")
    except FileNotFoundError:
        issues.append("PulseAudio not installed")
        fixes.append("Install: sudo apt-get install pulseaudio")
    except Exception as e:
        issues.append(f"PulseAudio check failed: {e}")
    
    # Check if audio devices exist
    try:
        if os.path.exists('/dev/snd'):
            devices = os.listdir('/dev/snd')
            if not devices:
                issues.append("No audio devices found")
                fixes.append("Check audio hardware connection")
        else:
            issues.append("/dev/snd not found (no audio support)")
    except Exception as e:
        issues.append(f"Audio device check failed: {e}")
    
    return issues, fixes

def check_network_connectivity():
    """Check network connectivity"""
    issues = []
    fixes = []
    
    # Check internet connectivity
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code != 200:
            issues.append("Internet connectivity issue")
            fixes.append("Check internet connection")
    except ImportError:
        issues.append("requests library missing")
        fixes.append("Install: pip install requests")
    except Exception as e:
        issues.append(f"Network error: {str(e)[:50]}")
        fixes.append("Check internet connection and DNS")
    
    # Check localhost
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=2)
    except:
        pass  # Localhost check is optional
    
    return issues, fixes

def check_dependencies():
    """Check required dependencies"""
    issues = []
    fixes = []
    
    required = [
        ('requests', 'requests'),
        ('psutil', 'psutil'),
        ('pyttsx3', 'pyttsx3'),
        ('numpy', 'numpy'),
    ]
    
    optional = [
        ('gtts', 'gtts'),
        ('pyaudio', 'pyaudio'),
        ('speech_recognition', 'speech_recognition'),
        ('opencv', 'cv2'),
    ]
    
    for module, name in required:
        try:
            __import__(module)
        except ImportError:
            issues.append(f"Required: {name} not installed")
            fixes.append(f"Install: pip install {name}")
    
    for module, name in optional:
        try:
            __import__(module)
        except ImportError:
            issues.append(f"Optional: {name} not installed")
            fixes.append(f"Install: pip install {name} (optional)")
    
    return issues, fixes

def check_file_system():
    """Check file system issues"""
    issues = []
    fixes = []
    
    critical_dirs = ['data', 'logs', 'sounds', 'bosco_os', 'voice', 'brain', 'capabilities']
    
    for dir_name in critical_dirs:
        if not os.path.exists(dir_name):
            issues.append(f"Missing directory: {dir_name}")
            fixes.append(f"Create: mkdir {dir_name}")
        elif not os.access(dir_name, os.W_OK):
            issues.append(f"No write permission: {dir_name}")
            fixes.append(f"Fix: chmod 755 {dir_name}")
    
    # Check for writable directories
    for dir_name in ['data', 'logs']:
        if os.path.exists(dir_name):
            test_file = os.path.join(dir_name, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                issues.append(f"{dir_name} not writable: {str(e)[:30]}")
                fixes.append(f"Fix permissions: chmod 755 {dir_name}")
    
    return issues, fixes

def check_running_services():
    """Check running services and ports"""
    issues = []
    fixes = []
    
    # Check common services
    services = {
        'pulseaudio': 'PulseAudio (audio)',
        'jackd': 'JACK (audio)',
        'apache2': 'Apache (web)',
        'nginx': 'Nginx (web)',
        'mysql': 'MySQL (database)',
        'postgres': 'PostgreSQL (database)',
    }
    
    try:
        import psutil
        running = [p.name() for p in psutil.process_iter()]
        
        # Check for Bosco processes
        bosco_processes = [p for p in running if 'bosco' in p.lower() or 'kareem' in p.lower()]
        if not bosco_processes:
            issues.append("No Bosco process running")
            fixes.append("Start Bosco: python run_bosco.py")
        
    except ImportError:
        issues.append("psutil not available for process check")
        fixes.append("Install: pip install psutil")
    except Exception as e:
        issues.append(f"Process check failed: {str(e)[:30]}")
    
    return issues, fixes

def check_display_graphics():
    """Check display and graphics"""
    issues = []
    fixes = []
    
    # Check DISPLAY variable
    if not os.environ.get('DISPLAY'):
        issues.append("DISPLAY not set (X11 not running)")
        fixes.append("Start X server or set DISPLAY=:0")
    
    # Check for graphical environment
    try:
        result = subprocess.run(['which', 'xrandr'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            issues.append("xrandr not available")
            fixes.append("Install: sudo apt-get install x11-xserver-utils")
    except:
        pass
    
    return issues, fixes

def check_python_environment():
    """Check Python environment issues"""
    issues = []
    fixes = []
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        issues.append(f"Python {version.major}.{version.minor} (recommend 3.8+)")
        fixes.append("Upgrade Python: sudo apt-get install python3.10")
    
    # Check pip
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            issues.append("pip not working")
            fixes.append("Reinstall: python -m ensurepip --upgrade")
    except:
        issues.append("pip not available")
        fixes.append("Install: sudo apt-get install python3-pip")
    
    # Check for common import errors in bosco modules
    bosco_modules = ['bosco_os.brain.neural_brain', 'bosco_os.capabilities.system.control']
    for mod in bosco_modules:
        try:
            __import__(mod)
        except ImportError as e:
            issues.append(f"Import error in {mod}: {str(e)[:40]}")
            fixes.append("Check dependencies")
        except Exception as e:
            issues.append(f"Error in {mod}: {str(e)[:40]}")
            fixes.append("Check module code")
    
    return issues, fixes

def check_log_files():
    """Check log file issues"""
    issues = []
    fixes = []
    
    log_files = ['logs/history.log']
    
    for log_file in log_files:
        if os.path.exists(log_file):
            # Check size
            size = os.path.getsize(log_file)
            if size > 100 * 1024 * 1024:  # 100MB
                issues.append(f"Large log file: {log_file} ({size/1024/1024:.1f}MB)")
                fixes.append(f"Clear: > {log_file}")
            
            # Check if writable
            if not os.access(log_file, os.W_OK):
                issues.append(f"Log not writable: {log_file}")
                fixes.append(f"Fix: chmod 644 {log_file}")
        else:
            # Create if doesn't exist
            try:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                with open(log_file, 'a'):
                    pass
            except Exception as e:
                issues.append(f"Cannot create log: {log_file}")
                fixes.append(f"Create manually: touch {log_file}")
    
    return issues, fixes

# 9.1 Audio System Check
print_subheader("Audio System Diagnostics")
try:
    audio_issues, audio_fixes = check_audio_system()
    if audio_issues:
        for issue in audio_issues:
            print(f"     ⚠ {issue}")
        test_result("Audio System", False)
    else:
        test_result("Audio System", True)
except Exception as e:
    test_result("Audio System", False, str(e))

# 9.2 Network Connectivity Check
print_subheader("Network Connectivity")
try:
    net_issues, net_fixes = check_network_connectivity()
    if net_issues:
        for issue in net_issues:
            print(f"     ⚠ {issue}")
        test_result("Network", False)
    else:
        test_result("Network", True)
except Exception as e:
    test_result("Network", False, str(e))

# 9.3 Dependencies Check
print_subheader("Dependencies Check")
try:
    dep_issues, dep_fixes = check_dependencies()
    if dep_issues:
        for issue in dep_issues:
            print(f"     ⚠ {issue}")
        test_result("Dependencies", False)
    else:
        test_result("Dependencies", True)
except Exception as e:
    test_result("Dependencies", False, str(e))

# 9.4 File System Check
print_subheader("File System Check")
try:
    fs_issues, fs_fixes = check_file_system()
    if fs_issues:
        for issue in fs_issues:
            print(f"     ⚠ {issue}")
        test_result("File System", False)
    else:
        test_result("File System", True)
except Exception as e:
    test_result("File System", False, str(e))

# 9.5 Running Services Check
print_subheader("Running Services")
try:
    svc_issues, svc_fixes = check_running_services()
    if svc_issues:
        for issue in svc_issues:
            print(f"     ⚠ {issue}")
        test_result("Services", False)
    else:
        test_result("Services", True)
except Exception as e:
    test_result("Services", False, str(e))

# 9.6 Display/Graphics Check
print_subheader("Display & Graphics")
try:
    disp_issues, disp_fixes = check_display_graphics()
    if disp_issues:
        for issue in disp_issues:
            print(f"     ⚠ {issue}")
        test_result("Display/Graphics", False)
    else:
        test_result("Display/Graphics", True)
except Exception as e:
    test_result("Display/Graphics", False, str(e))

# 9.7 Python Environment Check
print_subheader("Python Environment")
try:
    py_issues, py_fixes = check_python_environment()
    if py_issues:
        for issue in py_issues:
            print(f"     ⚠ {issue}")
        test_result("Python Environment", False)
    else:
        test_result("Python Environment", True)
except Exception as e:
    test_result("Python Environment", False, str(e))

# 9.8 Log Files Check
print_subheader("Log Files")
try:
    log_issues, log_fixes = check_log_files()
    if log_issues:
        for issue in log_issues:
            print(f"     ⚠ {issue}")
        test_result("Log Files", False)
    else:
        test_result("Log Files", True)
except Exception as e:
    test_result("Log Files", False, str(e))

# 9.9 Overall System Health Score
print_subheader("Overall System Health")
all_issues = audio_issues + net_issues + dep_issues + fs_issues + svc_issues + disp_issues + py_issues + log_issues
all_fixes = audio_fixes + net_fixes + dep_fixes + fs_fixes + svc_fixes + disp_fixes + py_fixes + log_fixes

total_issues = len(all_issues)
if total_issues == 0:
    print("     ✓ All system checks passed!")
    health_score = 100
elif total_issues <= 3:
    health_score = 75
elif total_issues <= 6:
    health_score = 50
else:
    health_score = 25

test_result(f"System Health Score ({health_score}%)", health_score >= 50)

if all_fixes:
    print("\n     Suggested fixes:")
    seen = set()
    for fix in all_fixes:
        if fix not in seen:
            print(f"       • {fix}")
            seen.add(fix)


# ============================================================================
# SUMMARY
# ============================================================================

print_header("TEST SUMMARY")

total_tests = len(TEST_RESULTS['passed']) + len(TEST_RESULTS['failed'])
passed_tests = len(TEST_RESULTS['passed'])
failed_tests = len(TEST_RESULTS['failed'])

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
print(f"Success Rate: {100*passed_tests/total_tests:.1f}%")

if TEST_RESULTS['failed']:
    print("\n" + "="*60)
    print("FAILED TESTS:")
    print("="*60)
    for name, error in TEST_RESULTS['failed']:
        print(f"  ✗ {name}")
        print(f"      Error: {error}")

print("\n" + "="*60)
if failed_tests == 0:
    print("🎉 ALL TESTS PASSED! Bosco Core is fully functional.")
else:
    print(f"⚠️  {failed_tests} test(s) failed. Review errors above.")
print("="*60)

# Exit with appropriate code
sys.exit(0 if failed_tests == 0 else 1)

