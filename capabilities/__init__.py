"""
Bosco Core - Capabilities Package
"""

from .weather import get_weather, format_weather_response
from .news import get_top_headlines, search_news, format_headlines
from .web_search import search, format_results
from .file_manager import list_files, search_files, open_file, format_list_response
from .reminders import add_reminder, get_pending, complete_reminder, delete_reminder

__all__ = [
    "get_weather", "format_weather_response",
    "get_top_headlines", "search_news", "format_headlines",
    "search", "format_results",
    "list_files", "search_files", "open_file", "format_list_response",
    "add_reminder", "get_pending", "complete_reminder", "delete_reminder"
]

