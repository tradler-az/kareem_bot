# Bosco Core - Next-Gen AI Assistant (2025/2026)

<p align="center">
  <img src="https://img.shields.io/badge/Version-4.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Multi--Agent-Ready-purple.svg" alt="Multi-Agent">
  <img src="https://img.shields.io/badge/Self--Updating-orange.svg" alt="Self-Updating">
</p>

Bosco Core is an advanced AI assistant with neural brain capabilities, multi-agent orchestration, semantic memory, full PC control, and Kali Linux support. It combines machine learning for natural conversation with powerful system automation features and specialized AI agents.

## ✨ Features

### 🧠 Neural Brain
- ML-powered intent recognition
- Learning from conversations
- Predictive responses
- Natural language understanding
- **NEW**: Vector memory with semantic search (RAG)
- **NEW**: Local embeddings with ChromaDB

### 🤖 Multi-Agent Orchestration
- **NEW**: Specialized AI agents that collaborate
- **Security Agent**: Penetration testing, vulnerability scanning, exploit research
- **DevOps Agent**: Docker/Kubernetes management, deployments, monitoring
- **Research Agent**: Web search, codebase analysis, documentation lookup
- **Orchestrator**: Coordinates complex multi-step workflows
- Predefined workflows: Pentest, Infrastructure Audit, Research & Analysis

### 💻 Full PC Control
- Execute terminal commands
- Open/close applications
- File management (read, write, delete, search)
- System monitoring (CPU, memory, disk)
- Screenshot capture
- Clipboard management
- Keyboard/mouse automation

### 🌐 Web Capabilities
- Web search
- Wikipedia queries
- URL browsing
- File downloads

### 🛡️ Kali Linux Support
- Process management
- Network operations & port scanning
- Service management
- Package management (apt)
- Firewall & security tools
- System logs analysis
- User management
- Kali tools integration
- **NEW**: Autonomous pentesting workflows

### 🎤 Voice I/O
- Voice recognition (SpeechRecognition)
- Text-to-speech (pyttsx3, gTTS, espeak)
- Sound effects

### 🔒 Real-Time Threat Detection
- **NEW**: Continuous security monitoring
- Log analysis for suspicious patterns
- Process scanning for malware indicators
- Network connection monitoring
- Threat alerts and notifications
- Pattern-based detection with customizable rules

### 🆙 Self-Update & Auto-Upgrade System
- **NEW**: Check for updates from PyPI/GitHub
- **NEW**: Auto-install missing dependencies
- **NEW**: Automatic backup before updates
- **NEW**: Apply code fixes automatically
- **NEW**: Learn and improve from interactions
- **NEW**: Continuous learning engine

### 👁️ Computer Vision & Screen Understanding
- **NEW**: Screen capture with multiple backends (MSS, PIL)
- **NEW**: OCR text detection (Tesseract)
- **NEW**: Visual element detection (buttons, text fields)
- **NEW**: Window management
- Screenshot capture and analysis

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/tradler-az/kareem_bot.git
cd kareem_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Bosco

```bash
# Using the clean runner (recommended - suppresses ALSA/JACK warnings)
./run_bosco_clean.py

# Or directly
python3 main.py
```

## 📋 Requirements

```
speech_recognition>=3.8.0
pyttsx3>=2.90
pyaudio>=0.2.13
gtts>=2.2.0
numpy>=1.20.0
requests>=2.25.0
beautifulsoup4>=4.9.0
selenium>=3.141.0
pyautogui>=0.9.53
pyperclip>=1.8.0
pillow>=8.0.0
```

## 🎮 Commands

### General
| Command | Description |
|---------|-------------|
| `search [query]` | Search the web |
| `wikipedia [topic]` | Get Wikipedia info |
| `weather` | Check weather |
| `news` | Latest news |
| `joke` | Tell a joke |

### Terminal
| Command | Description |
|---------|-------------|
| `run [command]` | Execute terminal command |
| `open terminal` | Open terminal app |

### Files
| Command | Description |
|---------|-------------|
| `list files [path]` | List directory |
| `find file [name]` | Search for files |
| `read file [path]` | Read file content |
| `create file [name] with [content]` | Create file |
| `delete file [path]` | Delete file |

### Apps
| Command | Description |
|---------|-------------|
| `open [app]` | Open application |
| `close [app]` | Close application |

### System
| Command | Description |
|---------|-------------|
| `system info` | Full system information |
| `processes` | Running processes |
| `screenshot` | Take screenshot |
| `cpu` / `memory` / `disk` | Quick stats |
| `install [package]` | Install package |
| `update` | Update system |
| `git clone [url]` | Clone repository |
| `download [url]` | Download file |

### Input Automation
| Command | Description |
|---------|-------------|
| `type [text]` | Type text |
| `press [key]` | Press a key |
| `click` | Mouse click |

### Clipboard
| Command | Description |
|---------|-------------|
| `clipboard` | Show clipboard |
| `copy [text]` | Copy to clipboard |

### Kali Linux
| Command | Description |
|---------|-------------|
| `list processes` | Show top processes |
| `network status` | Network configuration |
| `listening ports` | Open ports |
| `nmap scan [target]` | Run nmap scan |
| `list services` | Running services |
| `check root` | Check root access |
| `check iptables` | Firewall rules |
| `system logs` | System logs |

## 📁 Project Structure

```
bosco-core/
├── bosco.py                 # Main entry point wrapper
├── main.py                  # Core CLI application
├── run_bosco_clean.py       # Clean runner (recommended)
├── run_bosco.sh            # Shell wrapper
├── config.json             # Configuration
├── requirements.txt        # Dependencies
│
├── bosco_os/               # Core package
│   ├── brain/             # AI & processing
│   │   ├── neural_brain.py    # ML neural network
│   │   ├── llm_client.py      # LLM integration
│   │   ├── personality.py    # Personality module
│   │   ├── kali_personality.py
│   │   ├── perception.py
│   │   ├── creativity.py
│   │   ├── linux_command_handler.py
│   │   └── vector_memory.py     # NEW: RAG semantic memory
│   │
│   ├── agents/            # NEW: Multi-Agent System
│   │   ├── base_agent.py      # Base agent class
│   │   ├── security_agent.py  # Security specialist
│   │   ├── security_expert.py # OWASP Top 10 vulnerability scanner
│   │   ├── devops_agent.py    # DevOps specialist
│   │   ├── research_agent.py  # Research specialist
│   │   └── orchestrator.py    # Multi-agent coordinator
│   │
│   ├── perception/       # NEW: Computer Vision
│   │   └── screen_capture.py  # Screen capture & OCR
│   │
│   ├── mcp/              # NEW: Model Context Protocol
│   │   └── server.py         # MCP server & adapters
│   │
│   ├── capabilities/      # System capabilities
│   │   ├── system/
│   │   │   ├── full_control.py    # PC control
│   │   │   ├── kali_control.py    # Kali features
│   │   │   ├── pc_control.py
│   │   │   ├── control.py
│   │   │   └── enhanced_automation.py
│   │   ├── security/
│   │   │   └── threat_detector.py  # NEW: Threat detection
│   │   ├── multi_device.py
│   │   ├── task_manager.py
│   │   ├── devops/
│   │   ├── iot/
│   │   ├── monitoring/
│   │   └── network/
│   │
│   ├── core/              # Core utilities
│   │   ├── command_executor.py
│   │   ├── config.py
│   │   ├── event_bus.py
│   │   ├── scheduler.py
│   │   ├── self_update.py       # NEW: Self-update system
│   │   ├── validator.py         # NEW: ReAct validation
│   │   └── execution_sandbox.py # NEW: Safe code execution
│   │
│   ├── security/          # Security modules
│   │   ├── auth.py
│   │   └── audit_log.py
│   │
│   └── ui/               # UI components
│
├── voice/                 # Voice I/O
│   ├── listener.py       # Speech recognition
│   ├── speaker.py        # Text-to-speech
│   ├── sound_effects.py  # Sound effects
│   ├── wake_word.py      # Wake word detection
│   └── audio_helpers.py  # Audio utilities
│
├── brain/                # Legacy brain modules
│   ├── intent_parser.py
│   ├── memory.py
│   └── personality.py
│
├── automation/           # Automation modules
│   ├── command_router.py
│   └── system_control.py
│
├── capabilities/         # Legacy capabilities
│   ├── file_manager.py
│   ├── weather.py
│   ├── news.py
│   └── reminders.py
│
├── ui/                   # UI modules
│   └── arc_reactor.py
│
├── data/                 # Data storage
│   ├── brain_models.pkl
│   ├── conversations.json
│   ├── preferences.json
│   └── vector_store/     # NEW: ChromaDB vector storage
│
├── sounds/               # Sound files
│   ├── startup.wav
│   ├── listening.wav
│   ├── processing.wav
│   └── success.wav
│
└── logs/                 # Log files
    └── history.log
```

## 🔧 New Capabilities Usage

### Multi-Agent System

```python
from bosco_os.agents import get_orchestrator, create_task, TaskPriority
import asyncio

async def main():
    # Get orchestrator
    orchestrator = get_orchestrator()
    
    # Create a task
    task = create_task(
        "Scan target for vulnerabilities",
        "vulnerability_scan",
        TaskPriority.HIGH,
        {"target": "192.168.1.1"}
    )
    
    # Execute
    result = await orchestrator.execute_task(task)
    print(result)

asyncio.run(main())
```

### Run Predefined Workflows

```python
from bosco_os.agents import get_orchestrator

async def workflows():
    orchestrator = get_orchestrator()
    
    # Pentest workflow
    result = await orchestrator.pentest_workflow("192.168.1.1")
    
    # Infrastructure audit
    result = await orchestrator.infrastructure_audit_workflow()
```

### Vector Memory (RAG)

```python
from bosco_os.brain.vector_memory import get_vector_memory

# Get semantic memory
vm = get_vector_memory()

# Add documents
vm.add("Important note about the project", metadata={"type": "fact"})
vm.add("User prefers dark mode", metadata={"type": "preference"})

# Semantic search
results = vm.search("what are user preferences", n_results=3)
```

### Threat Detection

```python
from bosco_os.capabilities.security.threat_detector import get_threat_detector

# Get threat detector
detector = get_threat_detector()

# Register alert callback
def alert_callback(event):
    print(f"ALERT: {event.description}")

detector.register_alert_callback(alert_callback)

# Start monitoring
detector.start_monitoring(interval=60)

# Get threats
events = detector.get_events(severity="high")
```

### Screen Capture & OCR

```python
from bosco_os.perception import get_screen_capture, get_visual_analyzer

# Capture screen
capture = get_screen_capture()
capture.save_screenshot()

# Analyze screen
analyzer = get_visual_analyzer()
elements = analyzer.detect_text_elements(image)
```

### MCP Server

```python
from bosco_os.mcp import get_mcp_server

# Get MCP server
server = get_mcp_server()

# Register custom tool
async def my_handler(params):
    return {"result": "Hello!"}

server.register_tool(MCPTool(
    name="my_tool",
    description="My custom tool",
    input_schema={},
    handler=my_handler
))

# Start server
await server.start()
```

### Self-Update & Auto-Upgrade System

```python
from bosco_os.core.self_update import get_update_manager, get_learning_engine

# Get update manager
update_mgr = get_update_manager()

# Check for updates
update_info = update_mgr.check_for_updates()
print(f"Update available: {update_info.get('available')}")

# Auto-install missing dependencies
result = update_mgr.install_missing_dependencies()

# Enable auto-update
update_mgr.enable_auto_update(True)

# Get learning engine for continuous improvement
learning = get_learning_engine()

# Record interaction for learning
learning.record_interaction(
    user_input="your query",
    response="bot response",
    success=True
)
```

## ⚙️ Configuration

Edit `config.json`:

```json
{
  "ai_name": "Bosco",
  "version": "3.0.0",
  "voice": {
    "energy_threshold": 300,
    "pause_threshold": 0.8,
    "listen_timeout": 5.0,
    "phrase_time_limit": 10.0
  },
  "neural_brain": {
    "learning_enabled": true,
    "prediction_enabled": true
  },
  "system_control": {
    "allow_execution": true,
    "allow_file_operations": true
  }
}
```

## 🎤 Voice Commands

Bosco supports voice input and output:

```python
# Listen for command
cmd = listen()  # Uses speech_recognition

# Speak response
speak("Hello!")  # Uses pyttsx3 or espeak
```

## 🔧 Audio Troubleshooting

If you see ALSA/JACK warnings, use the clean runner:

```bash
./run_bosco_clean.py
```

This suppresses:
- ALSA `Unknown PCM` warnings
- JACK server connection errors
- `JackShmReadWritePtr` errors

These warnings are harmless and appear because ALSA probes for multichannel audio devices that don't exist on modern laptops.

## 🧪 Testing

### Run All Tests

```bash
# Run the comprehensive test suite (project + system diagnostics)
python test_all.py
```

The test suite checks:

#### Project Tests
- Core module imports
- Neural brain functionality
- Online services (weather, search, Wikipedia)
- System info (CPU, memory, storage)
- Advanced features (Vector Memory, Multi-Agent, MCP Server, etc.)
- Kali Linux integration

#### System Diagnostics (NEW)
- **Audio System**: ALSA, PulseAudio, audio devices
- **Network Connectivity**: Internet connection, DNS
- **Dependencies**: Required and optional packages
- **File System**: Critical directories, permissions
- **Running Services**: Bosco processes
- **Display/Graphics**: DISPLAY variable, X11
- **Python Environment**: Version, pip, module imports
- **Log Files**: Size and permissions

The test provides a **System Health Score** and suggests fixes for any issues found.

## 🤖 Neural Brain

The neural brain provides:

1. **Intent Recognition** - Understands what the user wants
2. **Learning** - Improves from conversations
3. **Prediction** - Anticipates user needs
4. **Memory** - Remembers context

### Training

```python
from bosco_os.brain.neural_brain import get_brain

brain = get_brain()
brain.learn("search python", "search")
brain.learn("find information about python", "search")
```

## 🛡️ Kali Integration

Bosco detects if running on Kali Linux and enables:

- Nmap integration
- Network scanning tools
- Security auditing commands
- Root privilege checks
- Service management
- Log analysis

## 📝 License

MIT License

## 👤 Author

Created by [Your Name]

## 🙏 Acknowledgments

- SpeechRecognition library
- pyttsx3 for TTS
- Neural network concepts from various ML resources
- JARVIS from Iron Man (inspiration)

