"""DispositivoMCP.

paraMCPservidorde
"""

import json
from typing import Any, Dict

from src.utils.logging_config import get_logger

from .timer_service import get_timer_service

logger = get_logger(__name__)


async def start_countdown_timer(args: Dict[str, Any]) -> str:
    """Iniciando.

    Args:
        args: Parâmetrode
            - command: deMCP (JSONFormatoCaracteres，nameearguments)
            - delay: Tempo（Segundos），，para5Segundos
            - description: ，

    Returns:
        str: JSONFormatodeCaracteres
    """
    try:
        command = args["command"]
        delay = args.get("delay")
        description = args.get("description", "")

        logger.info(f"[TimerTools] Iniciando - Comando: {command}, : {delay}Segundos")

        timer_service = get_timer_service()
        result = await timer_service.start_countdown(
            command=command, delay=delay, description=description
        )

        logger.info(f"[TimerTools] Iniciando: {result['success']}")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except KeyError as e:
        error_msg = f"Parâmetro: {e}"
        logger.error(f"[TimerTools] {error_msg}")
        return json.dumps({"success": False, "message": error_msg}, ensure_ascii=False)
    except Exception as e:
        error_msg = f"IniciandoFalha: {str(e)}"
        logger.error(f"[TimerTools] {error_msg}", exc_info=True)
        return json.dumps({"success": False, "message": error_msg}, ensure_ascii=False)


async def cancel_countdown_timer(args: Dict[str, Any]) -> str:
    """de.

    Args:
        args: Parâmetrode
            - timer_id: deDispositivoID

    Returns:
        str: JSONFormatodeCaracteres
    """
    try:
        timer_id = args["timer_id"]

        logger.info(f"[TimerTools]  {timer_id}")

        timer_service = get_timer_service()
        result = await timer_service.cancel_countdown(timer_id)

        logger.info(f"[TimerTools] : {result['success']}")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except KeyError as e:
        error_msg = f"Parâmetro: {e}"
        logger.error(f"[TimerTools] {error_msg}")
        return json.dumps({"success": False, "message": error_msg}, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Falha: {str(e)}"
        logger.error(f"[TimerTools] {error_msg}", exc_info=True)
        return json.dumps({"success": False, "message": error_msg}, ensure_ascii=False)


async def get_active_countdown_timers(args: Dict[str, Any]) -> str:
    """deestado.

    Args:
        args: （Parâmetro）

    Returns:
        str: JSONFormatodeDispositivo
    """
    try:
        logger.info("[TimerTools] ")

        timer_service = get_timer_service()
        result = await timer_service.get_active_timers()

        logger.info(f"[TimerTools] : {result['total_active_timers']}")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Falha: {str(e)}"
        logger.error(f"[TimerTools] {error_msg}", exc_info=True)
        return json.dumps({"success": False, "message": error_msg}, ensure_ascii=False)
