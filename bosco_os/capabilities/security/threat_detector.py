"""
Bosco Core - Real-time Threat Detector
Monitors system logs and network activity for suspicious patterns
"""

import os
import re
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import hashlib

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ThreatPattern:
    """Represents a detection pattern for threats"""
    
    def __init__(
        self,
        name: str,
        pattern: str,
        severity: str,
        description: str,
        regex: bool = True
    ):
        self.name = name
        self.pattern = pattern
        self.severity = severity  # critical, high, medium, low
        self.description = description
        self.regex = regex
        
        if regex:
            try:
                self.compiled = re.compile(pattern, re.IGNORECASE)
            except:
                self.compiled = None
        else:
            self.compiled = None
    
    def match(self, text: str) -> bool:
        """Check if text matches this pattern"""
        if self.regex and self.compiled:
            return bool(self.compiled.search(text))
        else:
            return self.pattern.lower() in text.lower()


class ThreatEvent:
    """Represents a detected threat event"""
    
    def __init__(
        self,
        pattern_name: str,
        severity: str,
        description: str,
        source: str,
        details: Dict = None
    ):
        self.id = f"threat_{int(time.time() * 1000)}"
        self.pattern_name = pattern_name
        self.severity = severity
        self.description = description
        self.source = source
        self.details = details or {}
        self.timestamp = datetime.now()
        self.acknowledged = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "pattern_name": self.pattern_name,
            "severity": self.severity,
            "description": self.description,
            "source": self.source,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged
        }


class ThreatDetector:
    """
    Real-time threat detection system
    Monitors logs, processes, and network for suspicious activity
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Detection patterns
        self.patterns: List[ThreatPattern] = []
        
        # Detected events
        self.events: List[ThreatEvent] = []
        self.max_events = 1000
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Callbacks for notifications
        self.alert_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            "total_scans": 0,
            "threats_detected": 0,
            "start_time": None
        }
        
        # Initialize default patterns
        self._init_default_patterns()
    
    def _init_default_patterns(self):
        """Initialize default threat detection patterns"""
        
        # Authentication threats
        self.add_pattern(ThreatPattern(
            name="failed_login",
            pattern=r"failed login|failed password|authentication failure|invalid user",
            severity="medium",
            description="Failed login attempt"
        ))
        
        self.add_pattern(ThreatPattern(
            name="brute_force",
            pattern=r"(\b\d{5,}\b.*failed)",  # Many failed attempts
            severity="high",
            description="Potential brute force attack"
        ))
        
        self.add_pattern(ThreatPattern(
            name="sudo_failure",
            pattern=r"failed.*sudo|password.*failure.*sudo",
            severity="medium",
            description="Failed sudo attempt"
        ))
        
        # Network threats
        self.add_pattern(ThreatPattern(
            name="port_scan",
            pattern=r"port scan|SYN scan|TCP scan",
            severity="medium",
            description="Port scan detected"
        ))
        
        self.add_pattern(ThreatPattern(
            name="suspicious_connection",
            pattern=r"suspicious connection|unusual traffic|dark corner",
            severity="high",
            description="Suspicious network connection"
        ))
        
        # Malware indicators
        self.add_pattern(ThreatPattern(
            name="malware_signature",
            pattern=r"malware|ransomware|trojan|backdoor|keylogger",
            severity="critical",
            description="Malware indicator detected"
        ))
        
        self.add_pattern(ThreatPattern(
            name="suspicious_process",
            pattern=r"nc -l|netcat.*listen|python.*reverse|msfconsole|metasploit",
            severity="high",
            description="Suspicious process detected"
        ))
        
        # File system threats
        self.add_pattern(ThreatPattern(
            name="unauthorized_access",
            pattern=r"permission denied|access denied|denied",
            severity="low",
            description="Access denied"
        ))
        
        self.add_pattern(ThreatPattern(
            name="file_modification",
            pattern=r"modified.*system|changed.*config|rootkit",
            severity="critical",
            description="Unauthorized file modification"
        ))
        
        # Service threats
        self.add_pattern(ThreatPattern(
            name="service_failure",
            pattern=r"service.*failed|systemd.*fail|crashed",
            severity="medium",
            description="Service failure detected"
        ))
        
        print(f"[ThreatDetector] Initialized with {len(self.patterns)} patterns")
    
    def add_pattern(self, pattern: ThreatPattern):
        """Add a detection pattern"""
        self.patterns.append(pattern)
    
    def remove_pattern(self, name: str):
        """Remove a detection pattern"""
        self.patterns = [p for p in self.patterns if p.name != name]
    
    def detect_in_text(self, text: str, source: str = "unknown") -> List[ThreatEvent]:
        """Detect threats in text"""
        events = []
        
        for pattern in self.patterns:
            if pattern.match(text):
                event = ThreatEvent(
                    pattern_name=pattern.name,
                    severity=pattern.severity,
                    description=pattern.description,
                    source=source,
                    details={"matched_text": text[:200]}
                )
                events.append(event)
                self._handle_threat_event(event)
        
        return events
    
    def detect_in_log(self, log_path: str, lines: int = 100) -> List[ThreatEvent]:
        """Scan a log file for threats"""
        events = []
        
        if not os.path.exists(log_path):
            return events
        
        try:
            with open(log_path, 'r') as f:
                # Read last N lines
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in recent_lines:
                    line_events = self.detect_in_text(line, source=log_path)
                    events.extend(line_events)
        
        except PermissionError:
            print(f"[ThreatDetector] Permission denied: {log_path}")
        except Exception as e:
            print(f"[ThreatDetector] Error reading {log_path}: {e}")
        
        return events
    
    def detect_in_processes(self) -> List[ThreatEvent]:
        """Scan running processes for suspicious activity"""
        events = []
        
        if not PSUTIL_AVAILABLE:
            return events
        
        try:
            # Suspicious process names
            suspicious_names = [
                "nc", "netcat", "ncat",
                "msfconsole", "msfvenom",
                "hydra", "john", "hashcat",
                "aircrack", "reaver",
                "wireshark", "tcpdump"
            ]
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                    
                    for sus_name in suspicious_names:
                        if sus_name in proc_name or sus_name in cmdline:
                            event = ThreatEvent(
                                pattern_name="suspicious_process",
                                severity="high",
                                description=f"Suspicious process: {proc.info['name']}",
                                source="process_scan",
                                details={
                                    "pid": proc.info['pid'],
                                    "name": proc.info['name'],
                                    "cmdline": proc.info['cmdline']
                                }
                            )
                            events.append(event)
                            self._handle_threat_event(event)
                            break
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        except Exception as e:
            print(f"[ThreatDetector] Process scan error: {e}")
        
        return events
    
    def detect_in_network(self) -> List[ThreatEvent]:
        """Scan network connections for suspicious activity"""
        events = []
        
        if not PSUTIL_AVAILABLE:
            return events
        
        try:
            suspicious_ports = [31337, 1337, 4444, 5555, 6666, 8080, 3128]
            suspicious_ips = []  # Could integrate with threat intelligence
            
            for conn in psutil.net_connections(kind='inet'):
                try:
                    # Check suspicious ports
                    if conn.raddr:
                        port = conn.raddr.port
                        if port in suspicious_ports:
                            event = ThreatEvent(
                                pattern_name="suspicious_connection",
                                severity="high",
                                description=f"Connection to suspicious port: {port}",
                                source="network_scan",
                                details={
                                    "local_addr": conn.laddr,
                                    "remote_addr": conn.raddr,
                                    "status": conn.status
                                }
                            )
                            events.append(event)
                            self._handle_threat_event(event)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        except Exception as e:
            print(f"[ThreatDetector] Network scan error: {e}")
        
        return events
    
    def detect_in_auth_logs(self) -> List[ThreatEvent]:
        """Analyze authentication logs"""
        events = []
        
        log_paths = [
            "/var/log/auth.log",
            "/var/log/secure",
            "/var/log/syslog"
        ]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                log_events = self.detect_in_log(log_path, lines=50)
                events.extend(log_events)
        
        return events
    
    def _handle_threat_event(self, event: ThreatEvent):
        """Handle a detected threat event"""
        # Store event
        self.events.append(event)
        
        # Limit stored events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Update stats
        self.stats["threats_detected"] += 1
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[ThreatDetector] Callback error: {e}")
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous threat monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.stats["start_time"] = datetime.now()
        
        def monitor_loop():
            while self.is_monitoring:
                self.stats["total_scans"] += 1
                
                # Scan auth logs
                self.detect_in_auth_logs()
                
                # Scan processes
                self.detect_in_processes()
                
                # Scan network
                self.detect_in_network()
                
                # Sleep
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("[ThreatDetector] Monitoring started")
    
    def stop_monitoring(self):
        """Stop threat monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("[ThreatDetector] Monitoring stopped")
    
    def register_alert_callback(self, callback: Callable):
        """Register a callback for threat alerts"""
        self.alert_callbacks.append(callback)
    
    def get_events(
        self,
        severity: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ThreatEvent]:
        """Get threat events with optional filtering"""
        events = self.events
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        return events[-limit:]
    
    def get_threat_summary(self) -> Dict:
        """Get summary of detected threats"""
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for event in self.events:
            if event.severity in severity_counts:
                severity_counts[event.severity] += 1
        
        return {
            "total_threats": len(self.events),
            "severity_counts": severity_counts,
            "is_monitoring": self.is_monitoring,
            "stats": self.stats,
            "patterns_loaded": len(self.patterns)
        }
    
    def acknowledge_threat(self, event_id: str):
        """Acknowledge a threat event"""
        for event in self.events:
            if event.id == event_id:
                event.acknowledged = True
                break
    
    def clear_events(self):
        """Clear all threat events"""
        self.events.clear()
        print("[ThreatDetector] Events cleared")
    
    def export_report(self, filepath: str) -> bool:
        """Export threat report to JSON"""
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": self.get_threat_summary(),
                "events": [e.to_dict() for e in self.events]
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[ThreatDetector] Export error: {e}")
            return False


# Global instance
_threat_detector: Optional[ThreatDetector] = None


def get_threat_detector(config: Dict = None) -> ThreatDetector:
    """Get the global threat detector instance"""
    global _threat_detector
    if _threat_detector is None:
        _threat_detector = ThreatDetector(config)
    return _threat_detector


# Example callback for voice alerts
def voice_alert_callback(event: ThreatEvent):
    """Example callback that could trigger voice alert"""
    severity_emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "⚡",
        "low": "ℹ️"
    }
    
    emoji = severity_emoji.get(event.severity, "❓")
    message = f"{emoji} Security Alert: {event.description}"
    
    print(f"[ALERT] {message}")
    # Could integrate with voice.speak(message) here


if __name__ == "__main__":
    print("=== Testing Threat Detector ===\n")
    
    # Create detector
    detector = ThreatDetector()
    
    # Register alert callback
    detector.register_alert_callback(voice_alert_callback)
    
    # Test detection in text
    print("Testing text detection...")
    test_text = """
    Failed login attempt for user admin from IP 192.168.1.100
    Multiple authentication failures detected
    """
    events = detector.detect_in_text(test_text, source="test")
    print(f"  Detected {len(events)} threats")
    
    # Test process detection
    print("\nTesting process detection...")
    events = detector.detect_in_processes()
    print(f"  Detected {len(events)} threats")
    
    # Test network detection
    print("\nTesting network detection...")
    events = detector.detect_in_network()
    print(f"  Detected {len(events)} threats")
    
    # Get summary
    print("\nThreat Summary:")
    summary = detector.get_threat_summary()
    print(f"  Total: {summary['total_threats']}")
    print(f"  By severity: {summary['severity_counts']}")

