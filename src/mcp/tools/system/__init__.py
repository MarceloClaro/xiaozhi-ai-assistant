"""sistema.

desistema，dispositivoestadoPesquisar、áudioAguardarOperação。
"""

from .manager import SystemToolsManager, get_system_tools_manager
from .tools import get_volume, set_volume

__all__ = [
    "SystemToolsManager",
    "get_system_tools_manager",
    "set_volume",
    "get_volume",
]
