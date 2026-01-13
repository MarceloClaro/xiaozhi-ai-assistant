"""DispositivoDispositivo.

DispositivodeInicializando、configuraçãoeMCP
"""

from typing import Any, Dict

from src.utils.logging_config import get_logger

from .tools import (
    cancel_countdown_timer,
    get_active_countdown_timers,
    start_countdown_timer,
)

logger = get_logger(__name__)


class TimerToolsManager:
    """
    DispositivoDispositivo.
    """

    def __init__(self):
        """
        InicializandoDispositivoDispositivo.
        """
        self._initialized = False
        logger.info("[TimerManager] DispositivoDispositivoInicializando")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        InicializandoDispositivo.
        """
        try:
            logger.info("[TimerManager] ComeçarDispositivo")

            # Iniciando
            self._register_start_countdown_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # 
            self._register_cancel_countdown_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # 
            self._register_get_active_timers_tool(add_tool, PropertyList)

            self._initialized = True
            logger.info("[TimerManager] DispositivoConcluído")

        except Exception as e:
            logger.error(f"[TimerManager] DispositivoFalha: {e}", exc_info=True)
            raise

    def _register_start_countdown_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        Iniciando.
        """
        timer_props = PropertyList(
            [
                Property(
                    "command",
                    PropertyType.STRING,
                ),
                Property(
                    "delay",
                    PropertyType.INTEGER,
                    default_value=5,
                    min_value=1,
                    max_value=3600,  # Máximo1
                ),
                Property(
                    "description",
                    PropertyType.STRING,
                    default_value="",
                ),
            ]
        )

        add_tool(
            (
                "timer.start_countdown",
                "Start a countdown timer that will execute an MCP tool after a specified delay. "
                "The command should be a JSON string containing MCP tool name and arguments. "
                'For example: \'{"name": "self.audio_speaker.set_volume", "arguments": {"volume": 50}}\' '
                "Use this when the user wants to: \n"
                "1. Set a timer to control system settings (volume, device status, etc.) \n"
                "2. Schedule delayed MCP tool executions \n"
                "3. Create reminders with automatic tool calls \n"
                "The timer will return a timer_id that can be used to cancel it later.",
                timer_props,
                start_countdown_timer,
            )
        )
        logger.debug("[TimerManager] IniciandoSucesso")

    def _register_cancel_countdown_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """
        .
        """
        cancel_props = PropertyList(
            [
                Property(
                    "timer_id",
                    PropertyType.INTEGER,
                )
            ]
        )

        add_tool(
            (
                "timer.cancel_countdown",
                "Cancel an active countdown timer by its ID. "
                "Use this when the user wants to: \n"
                "1. Cancel a previously set timer \n"
                "2. Stop a scheduled action before it executes \n"
                "You need the timer_id which is returned when starting a countdown.",
                cancel_props,
                cancel_countdown_timer,
            )
        )
        logger.debug("[TimerManager] Sucesso")

    def _register_get_active_timers_tool(self, add_tool, PropertyList):
        """
        .
        """
        add_tool(
            (
                "timer.get_active_timers",
                "Get information about all currently active countdown timers. "
                "Returns details including timer IDs, remaining time, commands to execute, "
                "and progress for each active timer. "
                "Use this when the user wants to: \n"
                "1. Check what timers are currently running \n"
                "2. See remaining time for active timers \n"
                "3. Get timer IDs for cancellation \n"
                "4. Monitor timer progress and status",
                PropertyList(),
                get_active_countdown_timers,
            )
        )
        logger.debug("[TimerManager] Sucesso")

    def is_initialized(self) -> bool:
        """
        PesquisarDispositivoInicializando.
        """
        return self._initialized

    def get_status(self) -> Dict[str, Any]:
        """
        Dispositivoestado.
        """
        return {
            "initialized": self._initialized,
            "tools_count": 3,  # de
            "available_tools": [
                "start_countdown",
                "cancel_countdown",
                "get_active_timers",
            ],
        }


# Dispositivo
_timer_tools_manager = None


def get_timer_manager() -> TimerToolsManager:
    """
    DispositivoDispositivo.
    """
    global _timer_tools_manager
    if _timer_tools_manager is None:
        _timer_tools_manager = TimerToolsManager()
        logger.debug("[TimerManager] DispositivoDispositivo")
    return _timer_tools_manager
