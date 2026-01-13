"""sistemaDispositivo.

sistemadeInicializando、configuraçãoeMCP
"""

from typing import Any, Dict

from src.utils.logging_config import get_logger

from .app_management.killer import kill_application, list_running_applications
from .app_management.launcher import launch_application
from .app_management.scanner import scan_installed_applications
from .tools import get_volume, set_volume

logger = get_logger(__name__)


class SystemToolsManager:
    """
    sistemaDispositivo.
    """

    def __init__(self):
        """
        InicializandosistemaDispositivo.
        """
        self._initialized = False
        logger.info("[SystemManager] DispositivoInicializando")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        Inicializandosistema.
        """
        try:
            logger.info("[SystemManager] Começar")

            # 
            self._register_volume_control_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # 
            self._register_volume_get_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # AplicaçãoIniciando
            self._register_app_launcher_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # Aplicação
            self._register_app_scanner_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # AplicaçãoFechando
            self._register_app_killer_tools(
                add_tool, PropertyList, Property, PropertyType
            )

            self._initialized = True
            logger.info("[SystemManager] Concluído")

        except Exception as e:
            logger.error(f"[SystemManager] Falha: {e}", exc_info=True)
            raise

    def _register_volume_control_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        .
        """
        volume_props = PropertyList(
            [Property("volume", PropertyType.INTEGER, min_value=0, max_value=100)]
        )
        add_tool(
            (
                "self.audio_speaker.set_volume",
                "Set the system speaker volume to an absolute value (0-100).\n"
                "Use when user mentions: volume, sound, louder, quieter, mute, unmute, adjust volume.\n"
                "Examples: 'set volume to 50', 'turn volume up', 'make it louder', 'mute', "
                "'para50', '', '', ''.\n"
                "Parameter:\n"
                "- volume: Integer (0-100) representing the target volume level. Set to 0 for mute.",
                volume_props,
                set_volume,
            )
        )
        logger.debug("[SystemManager] Sucesso")

    def _register_volume_get_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        .
        """
        get_volume_props = PropertyList([])
        add_tool(
            (
                "self.audio_speaker.get_volume",
                "Get the current system speaker volume level.\n"
                "Use when user asks about: current volume, volume level, how loud, what's the volume.\n"
                "Examples: 'what is the current volume?', 'how loud is it?', 'check volume level', "
                "'Agora?', 'Pesquisar', ''.\n"
                "Returns:\n"
                "- Integer (0-100) representing the current volume level.",
                get_volume_props,
                get_volume,
            )
        )
        logger.debug("[SystemManager] Sucesso")

    def _register_app_launcher_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        aplicaçãoprogramaIniciando.
        """
        app_props = PropertyList([Property("app_name", PropertyType.STRING)])
        add_tool(
            (
                "self.application.launch",
                "Launch desktop applications and software programs by name. This tool "
                "opens applications installed on the user's computer across Windows, "
                "macOS, and Linux platforms. It automatically detects the operating "
                "system and uses appropriate launch methods.\n"
                "Use this tool when the user wants to:\n"
                "1. Open specific software applications (e.g., 'QQ', 'QQMúsica', 'WeChat', '')\n"
                "2. Launch system utilities (e.g., 'Calculator', 'Dispositivo', 'Notepad', '')\n"
                "3. Start browsers (e.g., 'Chrome', 'Firefox', 'Safari')\n"
                "4. Open media players (e.g., 'VLC', 'Windows Media Player')\n"
                "5. Launch development tools (e.g., 'VS Code', 'PyCharm')\n"
                "6. Start games or other installed programs\n\n"
                "Examples of valid app names:\n"
                "- Chinese: 'QQMúsica', '', 'Dispositivo', '', 'Dispositivo'\n"
                "- English: 'QQ', 'WeChat', 'Calculator', 'Notepad', 'Chrome'\n"
                "- Mixed: 'QQ Music', 'Microsoft Word', 'Adobe Photoshop'\n\n"
                "The system will try multiple launch strategies including direct execution, "
                "system commands, and path searching to find and start the application.",
                app_props,
                launch_application,
            )
        )
        logger.debug("[SystemManager] AplicaçãoIniciandoSucesso")

    def _register_app_scanner_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        aplicaçãoprograma.
        """
        scanner_props = PropertyList(
            [Property("force_refresh", PropertyType.BOOLEAN, default_value=False)]
        )
        add_tool(
            (
                "self.application.scan_installed",
                "Scan and list all installed applications on the system. This tool "
                "provides a comprehensive list of available applications that can be "
                "launched using the launch tool. It scans system directories, registry "
                "(Windows), and application folders to find installed software.\n"
                "Use this tool when:\n"
                "1. User asks what applications are available on the system\n"
                "2. You need to find the correct application name before launching\n"
                "3. User wants to see all installed software\n"
                "4. Application launch fails and you need to check available apps\n\n"
                "The scan results include both system applications (Calculator, Notepad) "
                "and user-installed software (QQ, WeChat, Chrome, etc.). Each application "
                "entry contains the clean name for launching and display name for reference.\n\n"
                "After scanning, use the 'name' field from results with self.application.launch "
                "to start applications. For example, if scan shows {name: 'QQ', display_name: 'QQMúsica'}, "
                "use self.application.launch with app_name='QQ' to launch it.",
                scanner_props,
                scan_installed_applications,
            )
        )
        logger.debug("[SystemManager] AplicaçãoSucesso")

    def _register_app_killer_tools(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        aplicaçãoprogramaFechando.
        """
        # AplicaçãoFechando
        killer_props = PropertyList(
            [
                Property("app_name", PropertyType.STRING),
                Property("force", PropertyType.BOOLEAN, default_value=False),
            ]
        )
        add_tool(
            (
                "self.application.kill",
                "Close or terminate running applications by name. This tool can gracefully "
                "close applications or force-kill them if needed. It automatically finds "
                "running processes matching the application name and terminates them.\n"
                "Use this tool when:\n"
                "1. User asks to close, quit, or exit an application\n"
                "2. User wants to stop or terminate a running program\n"
                "3. Application is unresponsive and needs to be force-closed\n"
                "4. User says 'close QQ', 'quit Chrome', 'stop music player', etc.\n\n"
                "Parameters:\n"
                "- app_name: Name of the application to close (e.g., 'QQ', 'Chrome', 'Calculator')\n"
                "- force: Set to true for force-kill unresponsive applications (default: false)\n\n"
                "The tool will find all running processes matching the application name and "
                "attempt to close them gracefully. If force=true, it will use system kill "
                "commands to immediately terminate the processes.",
                killer_props,
                kill_application,
            )
        )

        # EmAplicação
        list_props = PropertyList(
            [Property("filter_name", PropertyType.STRING, default_value="")]
        )
        add_tool(
            (
                "self.application.list_running",
                "List all currently running applications and processes. This tool provides "
                "real-time information about active applications on the system, including "
                "process IDs, names, and commands.\n"
                "Use this tool when:\n"
                "1. User asks what applications are currently running\n"
                "2. You need to check if a specific application is running before closing it\n"
                "3. User wants to see active processes or programs\n"
                "4. Troubleshooting application issues\n\n"
                "Parameters:\n"
                "- filter_name: Optional filter to show only applications containing this name\n\n"
                "Returns detailed information about running applications including process IDs "
                "which can be useful for targeted application management.",
                list_props,
                list_running_applications,
            )
        )
        logger.debug("[SystemManager] AplicaçãoFechandoSucesso")

    def is_initialized(self) -> bool:
        """
        PesquisarDispositivoInicializando.
        """
        return self._initialized

    def get_status(self) -> Dict[str, Any]:
        """
        Dispositivoestado.
        """
        available_tools = [
            "set_volume",
            "get_volume",
            "launch_application",
            "scan_installed_applications",
            "kill_application",
            "list_running_applications",
        ]
        return {
            "initialized": self._initialized,
            "tools_count": len(available_tools),
            "available_tools": available_tools,
        }


# Dispositivo
_system_tools_manager = None


def get_system_tools_manager() -> SystemToolsManager:
    """
    sistemaDispositivo.
    """
    global _system_tools_manager
    if _system_tools_manager is None:
        _system_tools_manager = SystemToolsManager()
        logger.debug("[SystemManager] Dispositivo")
    return _system_tools_manager
