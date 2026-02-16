"""
Bosco Core - Command Router
Routes commands to appropriate handlers
"""

from typing import Dict, Any
from automation.system_control import (
    check_cpu, check_memory, check_battery, check_disk,
    open_browser, open_file_manager,
    set_volume, increase_volume, decrease_volume,
    shutdown, restart, sleep, take_screenshot
)


def route_command(intent_data: Dict[str, Any]) -> str:
    """Route command to appropriate handler"""
    intent = intent_data.get("intent", "unknown")
    command = intent_data.get("original", "").lower()
    entities = intent_data.get("entities", {})
    
    # System monitoring
    if intent == "check_cpu" or "cpu" in command:
        return check_cpu()
    
    elif intent == "check_memory" or "memory" in command or "ram" in command:
        return check_memory()
    
    elif intent == "check_battery" or "battery" in command:
        return check_battery()
    
    elif intent == "check_disk" or "disk" in command or "storage" in command:
        return check_disk()
    
    # Applications
    elif intent == "open_browser" or "browser" in command:
        return open_browser()
    
    elif intent == "open_file_manager" or "file manager" in command:
        return open_file_manager()
    
    # Volume
    elif intent == "volume_control" or "volume" in command:
        if "up" in command or "increase" in command:
            return increase_volume()
        elif "down" in command or "decrease" in command:
            return decrease_volume()
        # Extract level if specified
        for word in command.split():
            if word.isdigit():
                return set_volume(int(word))
        return "Please specify volume level."
    
    # System
    elif intent == "shutdown" or "shutdown" in command:
        return "Permission required for shutdown."
    
    elif intent == "restart" or "reboot" in command:
        return "Permission required for restart."
    
    elif intent == "sleep" or "standby" in command:
        return sleep()
    
    elif "screenshot" in command:
        return take_screenshot()
    
    # Files
    elif intent == "list_files":
        from capabilities import list_files, format_list_response
        result = list_files(entities.get("path", "."))
        return format_list_response(result)
    
    # Unknown
    else:
        return "Command not recognized. Would you like me to search for information instead?"


# Quick route function
def quick_route(command: str) -> str:
    """Quick route a command string"""
    from brain.intent_parser import parse_intent
    intent_data = parse_intent(command)
    return route_command(intent_data)


if __name__ == "__main__":
    # Test routing
    test_commands = [
        "check cpu",
        "check memory",
        "open browser",
        "take a screenshot",
    ]
    
    for cmd in test_commands:
        result = quick_route(cmd)
        print(f"Command: {cmd}")
        print(f"Result: {result}")
        print()

