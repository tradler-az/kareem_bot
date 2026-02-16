"""
Bosco Core - File Manager Capability
Browse and manage files on the system
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional


class FileManager:
    """File management operations"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~"))
        self.current_dir = self.base_dir
    
    def list_files(self, path: str = None, show_hidden: bool = False) -> Dict:
        """List files in a directory"""
        try:
            target = Path(path) if path else self.current_dir
            
            if not target.exists():
                return {"success": False, "error": "Directory does not exist"}
            
            if not target.is_dir():
                return {"success": False, "error": "Not a directory"}
            
            items = []
            for item in target.iterdir():
                if not show_hidden and item.name.startswith("."):
                    continue
                
                items.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "path": str(item)
                })
            
            items.sort(key=lambda x: (x["type"], x["name"].lower()))
            return {"success": True, "path": str(target), "items": items}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_files(self, query: str, path: str = None, max_results: int = 10) -> Dict:
        """Search for files"""
        try:
            search_path = Path(path) if path else self.base_dir
            results = []
            
            for item in search_path.rglob(f"*{query}*"):
                if len(results) >= max_results:
                    break
                if item.is_file():
                    results.append({
                        "name": item.name,
                        "path": str(item),
                        "size": item.stat().st_size
                    })
            
            return {"success": True, "results": results, "query": query}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_file_info(self, path: str) -> Dict:
        """Get file information"""
        try:
            target = Path(path)
            
            if not target.exists():
                return {"success": False, "error": "File does not exist"}
            
            info = {
                "name": target.name,
                "path": str(target),
                "type": "dir" if target.is_dir() else "file",
                "size": target.stat().st_size if target.is_file() else 0,
                "exists": True
            }
            
            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_file(self, path: str) -> Dict:
        """Open a file with default application"""
        try:
            target = Path(path)
            
            if not target.exists():
                return {"success": False, "error": "File does not exist"}
            
            # Use platform-appropriate command
            import subprocess
            system = platform.system()
            if system == "Linux":
                subprocess.Popen(["xdg-open", str(target)])
            elif system == "Darwin":
                subprocess.Popen(["open", str(target)])
            elif system == "Windows":
                subprocess.Popen(["start", "", str(target)], shell=True)
            
            return {"success": True, "message": f"Opening {target.name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def format_list_response(self, data: Dict) -> str:
        """Format file list as speech"""
        if not data.get("success"):
            return f"Error: {data.get('error', 'Unknown')}"
        
        items = data.get("items", [])
        path = data.get("path", "")
        
        if not items:
            return f"The directory {path} is empty."
        
        dirs = [i["name"] for i in items if i["type"] == "dir"]
        files = [i["name"] for i in items if i["type"] == "file"]
        
        response = f"In {path}: "
        
        if dirs:
            response += f"{len(dirs)} folders: {', '.join(dirs[:5])}"
            if len(dirs) > 5:
                response += f" and {len(dirs) - 5} more"
        
        if files:
            if dirs:
                response += ". "
            response += f"{len(files)} files: {', '.join(files[:5])}"
            if len(files) > 5:
                response += f" and {len(files) - 5} more"
        
        return response


_file_manager = FileManager()


def list_files(path: str = None, show_hidden: bool = False) -> Dict:
    return _file_manager.list_files(path, show_hidden)


def search_files(query: str, path: str = None, max_results: int = 10) -> Dict:
    return _file_manager.search_files(query, path, max_results)


def open_file(path: str) -> Dict:
    return _file_manager.open_file(path)


def format_list_response(data: Dict) -> str:
    return _file_manager.format_list_response(data)


if __name__ == "__main__":
    print("Testing File Manager...")
    result = list_files(".")
    print(format_list_response(result))

