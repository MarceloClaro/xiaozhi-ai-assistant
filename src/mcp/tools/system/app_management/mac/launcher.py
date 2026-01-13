"""macOSsistemaaplicaçãoprogramaIniciandoDispositivo.

macOSdeaplicaçãoprogramaIniciando
"""

import os
import subprocess

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def launch_application(app_name: str) -> bool:
    """EmmacOS  Inicia a aplicação.

    Args:
        app_name: aplicaçãoprogramaNome

    Returns:
        bool: Iniciandosucesso
    """
    try:
        logger.info(f"[MacLauncher] IniciandoAplicação: {app_name}")

        # 1: Usandoopen -aComando
        try:
            subprocess.Popen(["open", "-a", app_name])
            logger.info(f"[MacLauncher] Usandoopen -aSucessoIniciando: {app_name}")
            return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[MacLauncher] open -aIniciandoFalha: {app_name}")

        # 2: UsandoAplicaçãoNome
        try:
            subprocess.Popen([app_name])
            logger.info(f"[MacLauncher] IniciandoSucesso: {app_name}")
            return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[MacLauncher] IniciandoFalha: {app_name}")

        # 3: TentativaApplicationsDiretório
        app_path = f"/Applications/{app_name}.app"
        if os.path.exists(app_path):
            subprocess.Popen(["open", app_path])
            logger.info(f"[MacLauncher] Através deApplicationsDiretórioIniciandoSucesso: {app_name}")
            return True

        # 4: UsandoosascriptIniciando
        script = f'tell application "{app_name}" to activate'
        subprocess.Popen(["osascript", "-e", script])
        logger.info(f"[MacLauncher] UsandoosascriptIniciandoSucesso: {app_name}")
        return True

    except Exception as e:
        logger.error(f"[MacLauncher] macOSIniciandoFalha: {e}")
        return False
