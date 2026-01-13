"""aplicaçãoprograma.

deaplicaçãoprograma、IniciandoeFechando
"""

from .scanner import list_running_applications, scan_installed_applications
from .utils import AppMatcher, find_best_matching_app, get_cached_applications

__all__ = [
    "scan_installed_applications",
    "list_running_applications",
    "AppMatcher",
    "find_best_matching_app",
    "get_cached_applications",
]
