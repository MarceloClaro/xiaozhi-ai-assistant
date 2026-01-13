"""deaplicaçãoprogramaDispositivo.

sistemaAutomáticoSelecionandodeDispositivo
"""

import asyncio
import json
from typing import Any, Dict

from src.utils.logging_config import get_logger

from .utils import get_system_scanner

logger = get_logger(__name__)


async def scan_installed_applications(args: Dict[str, Any]) -> str:
    """sistemaEmJádeaplicaçãoprograma.

    Args:
        args: Parâmetrode
            - force_refresh: ForçarNovamente（，False）

    Returns:
        str: JSONFormatodeaplicaçãoprograma
    """
    try:
        force_refresh = args.get("force_refresh", False)
        logger.info(f"[AppScanner] ComeçarJáAplicação，Forçar: {force_refresh}")

        # deDispositivo
        scanner = get_system_scanner()
        if not scanner:
            error_msg = "NãoSuportadodeOperação"
            logger.error(f"[AppScanner] {error_msg}")
            return json.dumps(
                {
                    "success": False,
                    "total_count": 0,
                    "applications": [],
                    "message": error_msg,
                },
                ensure_ascii=False,
            )

        # Usando，
        apps = await asyncio.to_thread(scanner.scan_installed_applications)

        result = {
            "success": True,
            "total_count": len(apps),
            "applications": apps,
            "message": f"Sucessopara {len(apps)} JáAplicação",
        }

        logger.info(f"[AppScanner] Concluído，Encontrado {len(apps)} Aplicação")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"AplicaçãoFalha: {str(e)}"
        logger.error(f"[AppScanner] {error_msg}", exc_info=True)
        return json.dumps(
            {
                "success": False,
                "total_count": 0,
                "applications": [],
                "message": error_msg,
            },
            ensure_ascii=False,
        )


async def list_running_applications(args: Dict[str, Any]) -> str:
    """sistemaEm  Emdeaplicaçãoprograma.

    Args:
        args: Parâmetrode
            - filter_name: aplicaçãoNome（）

    Returns:
        str: JSONFormatodeaplicaçãoprograma
    """
    try:
        filter_name = args.get("filter_name", "")
        logger.info(f"[AppScanner] ComeçarEmdeAplicação，: {filter_name}")

        # deDispositivo
        scanner = get_system_scanner()
        if not scanner:
            error_msg = "NãoSuportadodeOperação"
            logger.error(f"[AppScanner] {error_msg}")
            return json.dumps(
                {
                    "success": False,
                    "total_count": 0,
                    "applications": [],
                    "message": error_msg,
                },
                ensure_ascii=False,
            )

        # Usando，
        apps = await asyncio.to_thread(scanner.scan_running_applications)

        # App
        if filter_name:
            filter_lower = filter_name.lower()
            filtered_apps = []
            for app in apps:
                if (
                    filter_lower in app.get("name", "").lower()
                    or filter_lower in app.get("display_name", "").lower()
                    or filter_lower in app.get("command", "").lower()
                ):
                    filtered_apps.append(app)
            apps = filtered_apps

        result = {
            "success": True,
            "total_count": len(apps),
            "applications": apps,
            "message": f"Encontrado {len(apps)} EmdeAplicação",
        }

        logger.info(f"[AppScanner] Concluído，Encontrado {len(apps)} EmdeAplicação")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"AplicaçãoFalha: {str(e)}"
        logger.error(f"[AppScanner] {error_msg}", exc_info=True)
        return json.dumps(
            {
                "success": False,
                "total_count": 0,
                "applications": [],
                "message": error_msg,
            },
            ensure_ascii=False,
        )
