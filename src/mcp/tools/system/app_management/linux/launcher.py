"""LinuxsistemaaplicaçãoprogramaIniciandoDispositivo.

LinuxdeaplicaçãoprogramaIniciando
"""

import os
import subprocess

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def launch_application(app_name: str) -> bool:
    """EmLinux  Inicia a aplicação.

    Args:
        app_name: aplicaçãoprogramaNome

    Returns:
        bool: Iniciandosucesso
    """
    try:
        logger.info(f"[LinuxLauncher] IniciandoAplicação: {app_name}")

        # 1: UsandoAplicaçãoNome
        try:
            subprocess.Popen([app_name])
            logger.info(f"[LinuxLauncher] IniciandoSucesso: {app_name}")
            return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[LinuxLauncher] IniciandoFalha: {app_name}")

        # 2: UsandowhichPesquisarAplicaçãoCaminho
        try:
            result = subprocess.run(["which", app_name], capture_output=True, text=True)
            if result.returncode == 0:
                app_path = result.stdout.strip()
                subprocess.Popen([app_path])
                logger.info(f"[LinuxLauncher] Através dewhichIniciandoSucesso: {app_name}")
                return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[LinuxLauncher] whichIniciandoFalha: {app_name}")

        # 3: Usandoxdg-open（）
        try:
            subprocess.Popen(["xdg-open", app_name])
            logger.info(f"[LinuxLauncher] Usandoxdg-openIniciandoSucesso: {app_name}")
            return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[LinuxLauncher] xdg-openIniciandoFalha: {app_name}")

        # 4: TentativadeAplicaçãoCaminho
        common_paths = [
            f"/usr/bin/{app_name}",
            f"/usr/local/bin/{app_name}",
            f"/opt/{app_name}/{app_name}",
            f"/snap/bin/{app_name}",
        ]

        for path in common_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                logger.info(
                    f"[LinuxLauncher] Através deCaminhoIniciandoSucesso: {app_name} ({path})")
                return True

        # 5: Tentativa.desktopArquivoIniciando
        desktop_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications"),
        ]

        for desktop_dir in desktop_dirs:
            desktop_file = os.path.join(desktop_dir, f"{app_name}.desktop")
            if os.path.exists(desktop_file):
                subprocess.Popen(["gtk-launch", f"{app_name}.desktop"])
                logger.info(f"[LinuxLauncher] Através dedesktopArquivoIniciandoSucesso: {app_name}")
                return True

        logger.warning(f"[LinuxLauncher] LinuxIniciandoFalha: {app_name}")
        return False

    except Exception as e:
        logger.error(f"[LinuxLauncher] LinuxIniciandoFalha: {e}")
        return False
