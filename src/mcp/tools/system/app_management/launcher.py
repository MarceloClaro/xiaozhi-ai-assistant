"""deaplicaçãoprogramaIniciandoDispositivo.

sistemaAutomáticoSelecionandodeIniciandoDispositivo
"""

import asyncio
import platform
from typing import Any, Dict, Optional

from src.utils.logging_config import get_logger

from .utils import find_best_matching_app

logger = get_logger(__name__)


async def launch_application(args: Dict[str, Any]) -> bool:
    """Inicia a aplicação.

    Args:
        args: aplicaçãoprogramaNomedeParâmetro
            - app_name: aplicaçãoprogramaNome

    Returns:
        bool: Iniciandosucesso
    """
    try:
        app_name = args["app_name"]
        logger.info(f"[AppLauncher] TentativaIniciandoAplicação: {app_name}")

        # TentativaAtravés deEncontradoCorrespondênciadeAplicação
        matched_app = await _find_matching_application(app_name)
        if matched_app:
            logger.info(
                f"[AppLauncher] EncontradoCorrespondênciadeAplicação: {matched_app.get('display_name', matched_app.get('name', ''))}")
            # AplicaçãoTipoUsandoNão  deIniciando
            success = await _launch_matched_app(matched_app, app_name)
        else:
            # SeNenhumEncontradoCorrespondência，Usandode
            logger.info(f"[AppLauncher] NãoEncontradoCorrespondência，UsandoOriginalNome: {app_name}")
            success = await _launch_by_name(app_name)

        if success:
            logger.info(f"[AppLauncher] SucessoIniciandoAplicação: {app_name}")
        else:
            logger.warning(f"[AppLauncher] IniciandoAplicaçãoFalha: {app_name}")

        return success

    except KeyError:
        logger.error("[AppLauncher] app_nameParâmetro")
        return False
    except Exception as e:
        logger.error(f"[AppLauncher] IniciandoAplicaçãoFalha: {e}", exc_info=True)
        return False


async def _find_matching_application(app_name: str) -> Optional[Dict[str, Any]]:
    """Através deEncontradoCorrespondênciadeaplicaçãoprograma.

    Args:
        app_name: PesquisardeaplicaçãoprogramaNome

    Returns:
        CorrespondênciadeaplicaçãoprogramaInformação，Se  EncontradoentãoRetornoNone
    """
    try:
        # UsandodeCorrespondência
        matched_app = await find_best_matching_app(app_name, "installed")

        if matched_app:
            logger.info(
                f"[AppLauncher] Através deCorrespondênciaEncontradoApp: {matched_app.get('display_name', matched_app.get('name', ''))}"
)
        return matched_app

    except Exception as e:
        logger.warning(f"[AppLauncher] PesquisarCorrespondênciaAplicação: {e}")
        return None


async def _launch_matched_app(matched_app: Dict[str, Any], original_name: str) -> bool:
    """IniciandoCorrespondênciaparadeaplicaçãoprograma.

    Args:
        matched_app: CorrespondênciadeaplicaçãoprogramaInformação
        original_name: OriginalaplicaçãoprogramaNome

    Returns:
        bool: Iniciandosucesso
    """
    try:
        app_type = matched_app.get("type", "unknown")
        app_path = matched_app.get("path", matched_app.get("name", original_name))

        system = platform.system()

        if system == "Windows":
            # WindowsProcessando
            if app_type == "uwp":
                # UWPAppUsandodeIniciando
                from .windows.launcher import launch_uwp_app_by_path

                return await asyncio.to_thread(launch_uwp_app_by_path, app_path)
            elif app_type == "shortcut" and app_path.endswith(".lnk"):
                # AtalhoArquivo
                from .windows.launcher import launch_shortcut

                return await asyncio.to_thread(launch_shortcut, app_path)

        # AplicaçãoIniciando
        return await _launch_by_name(app_path)

    except Exception as e:
        logger.error(f"[AppLauncher] IniciandoCorrespondênciaAppFalha: {e}")
        return False


async def _launch_by_name(app_name: str) -> bool:
    """NomeInicia a aplicação.

    Args:
        app_name: aplicaçãoprogramaNomeouCaminho

    Returns:
        bool: Iniciandosucesso
    """
    try:
        system = platform.system()

        if system == "Windows":
            from .windows.launcher import launch_application

            return await asyncio.to_thread(launch_application, app_name)
        elif system == "Darwin":  # macOS
            from .mac.launcher import launch_application

            return await asyncio.to_thread(launch_application, app_name)
        elif system == "Linux":
            from .linux.launcher import launch_application

            return await asyncio.to_thread(launch_application, app_name)
        else:
            logger.error(f"[AppLauncher] NãoSuportadodeOperação: {system}")
            return False

    except Exception as e:
        logger.error(f"[AppLauncher] IniciandoAplicaçãoFalha: {e}")
        return False


def get_system_launcher():
    """sistemadeIniciandoDispositivo.

    Returns:
        sistemadeIniciandoDispositivo
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        from .mac import launcher

        return launcher
    elif system == "Windows":  # Windows
        from .windows import launcher

        return launcher
    elif system == "Linux":  # Linux
        from .linux import launcher

        return launcher
    else:
        logger.warning(f"[AppLauncher] NãoSuportadode: {system}")
        return None
