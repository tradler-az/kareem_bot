"""
Bosco OS - Core Configuration Module
Handles all configuration settings
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Central configuration manager for Bosco OS"""
    
    def __init__(self, config_path: str = "bosco-os/config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config = {
            "version": "1.0.0",
            "name": "Bosco OS",
            "api_keys": {
                "groq": "",
                "openweather": "",
                "newsapi": "",
                "google_search": "",
                "huggingface": ""
            },
            "brain": {
                "model": "llama-3.1-70b-versatile",
                "temperature": 0.7,
                "max_tokens": 2048,
                "reasoning_enabled": True,
                "planner_enabled": True
            },
            "voice": {
                "wake_word": "hey bosco",
                "language": "en-US",
                "voice_rate": 170,
                "voice_volume": 1.0,
                "continuous_mode": False
            },
            "security": {
                "auth_enabled": False,
                "sandbox_mode": True,
                "audit_logging": True,
                "policy_strict": False
            },
            "capabilities": {
                "system": {
                    "allow_shutdown": False,
                    "allow_restart": True,
                    "allow_sudo": False
                },
                "network": {
                    "allow_nmap": True,
                    "allow_netcat": True
                },
                "devops": {
                    "allow_docker": True,
                    "allow_git": True
                }
            },
            "kali_linux": {
                "tools_path": "/usr/bin",
                "wordlists": "/usr/share/wordlists",
                "tools": [
                    "nmap", "hydra", "msfconsole", "sqlmap", 
                    "nikto", "gobuster", "dirb", "wpscan",
                    "aircrack-ng", "john", "hashcat", "metasploit"
                ]
            },
            "api": {
                "host": "0.0.0.0",
                "port": 5000,
                "cors_enabled": True
            }
        }
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config()
    
    def get_api_key(self, service: str) -> str:
        """Get API key for a service"""
        return self.config.get("api_keys", {}).get(service, "")
    
    def set_api_key(self, service: str, key: str):
        """Set API key for a service"""
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][service] = key
        self._save_config()
    
    def is_kali_linux(self) -> bool:
        """Check if running on Kali Linux"""
        return os.path.exists("/usr/bin/nmap") and os.path.exists("/etc/kali_security")
    
    def get_kali_tools(self) -> list:
        """Get list of available Kali tools"""
        kali_config = self.config.get("kali_linux", {})
        return kali_config.get("tools", [])
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()


# Global config instance
_config = Config()


def get_config() -> Config:
    """Get global config instance"""
    return _config


# Quick access functions
def get(key: str, default: Any = None) -> Any:
    return _config.get(key, default)


def set(key: str, value: Any):
    return _config.set(key, value)


def get_api_key(service: str) -> str:
    return _config.get_api_key(service)


if __name__ == "__main__":
    print("Bosco OS Config Test")
    print(f"Version: {get('version')}")
    print(f"Name: {get('name')}")
    print(f"Kali Linux: {_config.is_kali_linux()}")
    print(f"Kali Tools: {_config.get_kali_tools()}")

