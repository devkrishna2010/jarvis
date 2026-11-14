"""
J.A.R.V.I.S. Skills Package
"""

from skills.memory import JarvisMemory, get_memory, handle_store, handle_recall
from skills.system_control import launch_application, adjust_volume, lock_system, capture_screenshot, handle_app_launch, handle_system_action
from skills.web_search import search_web, check_internet_connection, handle_search
from skills.scheduler import JarvisScheduler, get_scheduler, handle_reminder, handle_briefing
from skills.weather import get_current_weather, handle_weather_query
from skills.system_diagnostics import get_system_telemetry, format_diagnostic_report, handle_diagnostics
from skills.protocols import ProtocolEngine, get_protocol_engine, handle_protocol

__all__ = [
    "JarvisMemory",
    "get_memory",
    "handle_store",
    "handle_recall",
    "launch_application",
    "adjust_volume",
    "lock_system",
    "capture_screenshot",
    "handle_app_launch",
    "handle_system_action",
    "search_web",
    "check_internet_connection",
    "handle_search",
    "JarvisScheduler",
    "get_scheduler",
    "handle_reminder",
    "handle_briefing",
    "get_current_weather",
    "handle_weather_query",
    "get_system_telemetry",
    "format_diagnostic_report",
    "handle_diagnostics",
    "ProtocolEngine",
    "get_protocol_engine",
    "handle_protocol",
]
