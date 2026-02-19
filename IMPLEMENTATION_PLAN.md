# Bosco Core - Advanced Implementation Plan

## Task Analysis Summary

You want to enhance Bosco with these capabilities:
1. **Advanced Kali Linux tools** - Port scanning URLs/IPs, network analysis
2. **App listing** - List all installed applications on your PC  
3. **Conversation memory** - Remember recent discussions (RAG/infinite context)
4. **Self-update system** - "Update yourself" to add new features dynamically
5. **Online/Offline modes** - Both supported, with online as recommended

## Information Gathered

### Current Architecture:
- **main.py**: CLI entry point with neural brain, voice, Kali control integration
- **bosco_os/brain/neural_brain.py**: ML-based intent classification, personality system
- **bosco_os/capabilities/system/kali_control.py**: Advanced Kali Linux control (processes, network, services)
- **bosco_os/capabilities/network/scanner.py**: Basic nmap wrapper
- **bosco_os/core/self_update.py**: Self-update system (exists but not fully integrated)
- **bosco_os/brain/vector_memory.py**: ChromaDB-based semantic memory
- **config.json**: Configuration with features, voice, ML settings

### Existing Capabilities:
- ✅ Neural brain with intent classification
- ✅ Kali Linux detection and control
- ✅ Process management (list, find, kill)
- ✅ Network info, listening ports, connections
- ✅ Service management, package management
- ✅ System logs, disk usage
- ✅ Basic nmap scanning
- ✅ Self-update framework
- ✅ Vector memory for semantic search
- ✅ Voice input/output

### What's Missing:
- ❌ Port scanning for URLs (need to resolve URL to IP first)
- ❌ List ALL installed applications (need app discovery)
- ❌ "Recent talk" recall (need enhanced conversation memory)
- ❌ "Update yourself" command (need integration in main.py)
- ❌ Proper offline/online fallback (need LLM client enhancement)

---

## Implementation Plan

### Phase 1: Enhance Kali Linux Capabilities (Priority: HIGH)

#### 1.1 Add URL Port Scanner
**New File**: `bosco_os/capabilities/network/url_scanner.py`
- Resolve URL to IP address
- Scan common ports or custom port range
- Service detection
- Integration with existing Kali control

#### 1.2 Enhanced Network Tools
**Update**: `bosco_os/capabilities/network/scanner.py`
- Add UDP scan support
- Add OS detection
- Add script scanning (nmap -sC)
- Better output formatting

#### 1.3 Add to main.py Command Processing
- "scan [url/ip]" - Scan ports
- "check ports on [url]" - Check open ports
- "network scan" - Quick network discovery

---

### Phase 2: App Listing (Priority: HIGH)

#### 2.1 Create Application Discovery Module
**New File**: `bosco_os/capabilities/system/app_manager.py`
- List installed applications (Linux: .desktop files, snap, apt)
- List running applications
- App categories (System, Development, Games, etc.)
- Search/filter applications

#### 2.2 Add Commands to main.py
- "list apps" / "show applications"
- "running apps"
- "find app [name]"
- "open [app name]" (already exists)

---

### Phase 3: Conversation Memory Enhancement (Priority: HIGH)

#### 3.1 Enhance Vector Memory Integration
**Update**: `main.py` 
- Auto-store conversations in vector memory
- Add "remember this" command
- Add "what did we talk about" command
- Semantic search across past conversations

#### 3.2 Add Memory Commands
- "remember [something]" - Store important info
- "what did I tell you about [topic]" - Recall
- "what did we discuss" - Recent topics
- "forget [topic]" - Remove from memory

---

### Phase 4: Self-Update System Integration (Priority: HIGH)

#### 4.1 Integrate Self-Update into main.py
**Update**: `main.py`
- Add "update yourself" command
- Add "check for updates" command
- Add "add feature [description]" command
- Connect to existing self_update.py

#### 4.2 Enhanced Update Capabilities
**Update**: `bosco_os/core/self_update.py`
- Code generation/insertion capability
- Dynamic feature addition
- Safe rollback system
- Update from GitHub/PyPI

---

### Phase 5: Online/Offline Mode (Priority: HIGH)

#### 5.1 Enhance LLM Client
**Update**: `bosco_os/brain/llm_client.py`
- Online: Use Groq API (already configured)
- Offline: Use local fallback (rule-based responses)
- Seamless fallback on network error
- Mode indicator in status

#### 5.2 Add Mode Commands
- "go online/offline"
- "check mode"
- "status" - Show current mode and capabilities

---

### Phase 6: Additional Enhancements (Priority: MEDIUM)

#### 6.1 System Information Dashboard
- Quick system overview command
- Resource usage graphs (text-based)
- Top processes, network, disk in one view

#### 6.2 Enhanced Help System
- Categorized help
- Searchable commands
- Contextual help

---

## Files to Create

| File | Purpose |
|------|---------|
| `bosco_os/capabilities/network/url_scanner.py` | URL to IP + port scanning |
| `bosco_os/capabilities/system/app_manager.py` | App discovery and listing |

## Files to Update

| File | Changes |
|------|---------|
| `main.py` | Add new commands, integrate self-update, enhance memory |
| `bosco_os/capabilities/network/scanner.py` | Enhanced nmap capabilities |
| `bosco_os/brain/llm_client.py` | Online/offline mode |
| `config.json` | Add new config options |

---

## Command Summary After Implementation

### Network Scanning:
```
scan ports [url/ip]          - Scan ports on URL or IP
check open ports [url]      - Check open ports
quick scan [target]         - Quick port scan
network status              - Show network info
```

### Application Management:
```
list apps                   - List all installed apps
running apps               - List running applications
find app [name]            - Search for application
open [app]                 - Open application (exists)
```

### Memory & Conversation:
```
remember [info]            - Store important information
what did I tell you about  - Recall specific topic
what did we discuss        - Recent conversation topics
forget [topic]             - Remove from memory
```

### Updates & Mode:
```
update yourself             - Check and apply updates
add feature [description]   - Request new feature
go online                  - Switch to online mode
go offline                 - Switch to offline mode
status                     - Show system status
```

### Enhanced Kali:
```
nmap scan [target]          - Full nmap scan
check services             - List running services
system logs                - View system logs
```

---

## Implementation Order

1. **URL Scanner** - Scan ports on URLs
2. **App Manager** - List all applications  
3. **Memory Integration** - Enhanced conversation recall
4. **Self-Update Integration** - "Update yourself" command
5. **Online/Offline Mode** - Proper fallback handling
6. **Additional Commands** - Polish and expand

---

## Follow-up Steps

1. **Test after each phase** - Verify functionality incrementally
2. **Voice command testing** - Test with voice input
3. **Offline mode testing** - Disconnect network and verify fallback
4. **Memory testing** - Verify conversation recall works
5. **Update testing** - Test self-update capability

---

## Notes

- All features work BOTH online and offline (with offline having limited AI capabilities)
- Online mode uses Groq API (already configured in config.json)
- All new commands integrate with existing neural brain for intent detection
- Vector memory provides infinite context recall

