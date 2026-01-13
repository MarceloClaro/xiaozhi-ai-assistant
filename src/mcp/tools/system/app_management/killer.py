"""deaplicaçãoprogramaFechandoDispositivo.

sistemaAutomáticoSelecionandodeFechandoDispositivo
"""

import asyncio
import json
import platform
from typing import Any, Dict, List

from src.utils.logging_config import get_logger

from .utils import AppMatcher

logger = get_logger(__name__)


async def kill_application(args: Dict[str, Any]) -> bool:
    """Fechandoaplicaçãoprograma.

    Args:
        args: aplicaçãoprogramaNomedeParâmetro
            - app_name: aplicaçãoprogramaNome
            - force: ForçarFechando（，False）

    Returns:
        bool: Fechandosucesso
    """
    try:
        app_name = args["app_name"]
        force = args.get("force", False)
        logger.info(f"[AppKiller] TentativaFechandoAplicação: {app_name}, ForçarFechando: {force}")

        # TentativaAtravés deEncontrado  EmdeAplicação
        running_apps = await _find_running_applications(app_name)

        if not running_apps:
            logger.warning(f"[AppKiller] NãoEncontrado  EmdeAplicação: {app_name}")
            return False

        # SelecionandoFechando
        system = platform.system()
        if system == "Windows":
            # WindowsUsandodeFechando
            success = await asyncio.to_thread(
                _kill_windows_app_group, running_apps, app_name, force
            )
        else:
            # macOSeLinuxUsandode  Fechando
            success_count = 0
            for app in running_apps:
                success = await asyncio.to_thread(_kill_app_sync, app, force, system)
                if success:
                    success_count += 1
                    logger.info(
                        f"[AppKiller] SucessoFechandoAplicacao: {app['name']} (PID: {app.get('pid', 'N/A')})"
                    )
                else:
                    logger.warning(
                        f"[AppKiller] FechandoAplicacaoFalha: {app['name']} (PID: {app.get('pid', 'N/A')})"
                    )

            success = success_count > 0
            logger.info(
                f"[AppKiller] FechandoOperacaoConcluido,"
                f"SucessoFechando {success_count}/{len(running_apps)} Processos"
            )
        return success

    except Exception as e:
        logger.error(f"[AppKiller] FechandoAplicação: {e}", exc_info=True)
        return False


async def list_running_applications(args: Dict[str, Any]) -> str:
    """Emdeaplicaçãoprograma.

    Args:
        args: Parâmetrode
            - filter_name: aplicaçãoprogramaNome（）

    Returns:
        str: JSONFormatodeEmaplicaçãoprograma
    """
    try:
        filter_name = args.get("filter_name", "")
        logger.info(f"[AppKiller] ComeçarEmdeAplicação，: {filter_name}")

        # Usando，
        apps = await asyncio.to_thread(_list_running_apps_sync, filter_name)

        result = {
            "success": True,
            "total_count": len(apps),
            "applications": apps,
            "message": f"Encontrado {len(apps)} EmdeAplicação",
        }

        logger.info(f"[AppKiller] Concluído，Encontrado {len(apps)} EmdeAplicação")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"EmAplicaçãoFalha: {str(e)}"
        logger.error(f"[AppKiller] {error_msg}", exc_info=True)
        return json.dumps(
            {
                "success": False,
                "total_count": 0,
                "applications": [],
                "message": error_msg,
            },
            ensure_ascii=False,
        )


async def _find_running_applications(app_name: str) -> List[Dict[str, Any]]:
    """PesquisarEmdeCorrespondênciaaplicaçãoprograma.

    Args:
        app_name: PesquisardeaplicaçãoprogramaNome

    Returns:
        Correspondênciade  Emaplicaçãoprograma
    """
    try:
        # EmdeAplicação
        all_apps = await asyncio.to_thread(_list_running_apps_sync, "")

        # UsandoCorrespondência Dispositivo EncontradoCorrespondência
        matched_apps = []

        for app in all_apps:
            score = AppMatcher.match_application(app_name, app)
            if score >= 50:  # Correspondência  Limiar
                matched_apps.append(app)

        # Correspondência
        matched_apps.sort(
            key=lambda x: AppMatcher.match_application(app_name, x), reverse=True
        )

        logger.info(f"[AppKiller] Encontrado {len(matched_apps)} CorrespondênciadeApp")
        return matched_apps

    except Exception as e:
        logger.warning(f"[AppKiller] PesquisarEmAplicação: {e}")
        return []


def _list_running_apps_sync(filter_name: str = "") -> List[Dict[str, Any]]:
    """Emdeaplicaçãoprograma.

    Args:
        filter_name: aplicaçãoprogramaNome

    Returns:
        Emdeaplicaçãoprograma
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        from .mac.killer import list_running_applications

        return list_running_applications(filter_name)
    elif system == "Windows":  # Windows
        from .windows.killer import list_running_applications

        return list_running_applications(filter_name)
    elif system == "Linux":  # Linux
        from .linux.killer import list_running_applications

        return list_running_applications(filter_name)
    else:
        logger.warning(f"[AppKiller] NãoSuportadodeOperação: {system}")
        return []


def _kill_app_sync(app: Dict[str, Any], force: bool, system: str) -> bool:
    """Fechandoaplicaçãoprograma.

    Args:
        app: aplicaçãoprogramaInformação
        force: ForçarFechando
        system: OperaçãosistemaTipo

    Returns:
        bool: Fechandosucesso
    """
    try:
        pid = app.get("pid")
        if not pid:
            return False

        if system == "Windows":
            from .windows.killer import kill_application

            return kill_application(pid, force)
        elif system == "Darwin":  # macOS
            from .mac.killer import kill_application

            return kill_application(pid, force)
        elif system == "Linux":  # Linux
            from .linux.killer import kill_application

            return kill_application(pid, force)
        else:
            logger.error(f"[AppKiller] NãoSuportadodeOperação: {system}")
            return False

    except Exception as e:
        logger.error(f"[AppKiller] FechandoAplicaçãoFalha: {e}")
        return False


def _kill_windows_app_group(
    apps: List[Dict[str, Any]], app_name: str, force: bool
) -> bool:
    """WindowssistemadeFechando.

    Args:
        apps: CorrespondênciadeaplicaçãoprogramaProcesso
        app_name: aplicaçãoprogramaNome
        force: ForçarFechando

    Returns:
        bool: Fechandosucesso
    """
    try:
        from .windows.killer import kill_application_group

        return kill_application_group(apps, app_name, force)
    except Exception as e:
        logger.error(f"[AppKiller] WindowsFechandoFalha: {e}")
        return False


def get_system_killer():
    """sistemadeFechandoDispositivo.

    Returns:
        sistemadeFechandoDispositivo
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        from .mac import killer

        return killer
    elif system == "Windows":  # Windows
        from .windows import killer

        return killer
    elif system == "Linux":  # Linux
        from .linux import killer

        return killer
    else:
        logger.warning(f"[AppKiller] NãoSuportadode: {system}")
        return None
