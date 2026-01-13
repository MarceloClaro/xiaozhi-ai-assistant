"""LinuxsistemaaplicaçãoprogramaFechandoDispositivo.

LinuxdeaplicaçãoprogramaFechando
"""

import subprocess
from typing import Any, Dict, List

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def list_running_applications(filter_name: str = "") -> List[Dict[str, Any]]:
    """
    LinuxEmdeaplicaçãoprograma.
    """
    apps = []

    try:
        # UsandopsComandoProcessoInformação
        result = subprocess.run(
            ["ps", "-eo", "pid,ppid,comm,command", "--no-headers"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")

            for line in lines:
                parts = line.strip().split(None, 3)
                if len(parts) >= 4:
                    pid, ppid, comm, command = parts

                    # GUIAplicação
                    is_gui_app = (
                        not command.startswith("/usr/bin/")
                        and not command.startswith("/bin/")
                        and not command.startswith("[")  # 
                        and len(comm) > 2
                    )

                    if is_gui_app:
                        app_name = comm

                        # App
                        if not filter_name or filter_name.lower() in app_name.lower():
                            apps.append(
                                {
                                    "pid": int(pid),
                                    "ppid": int(ppid),
                                    "name": app_name,
                                    "display_name": app_name,
                                    "command": command,
                                    "type": "application",
                                }
                            )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.warning(f"[LinuxKiller] LinuxProcessoFalha: {e}")

    return apps


def kill_application(pid: int, force: bool) -> bool:
    """
    EmLinux  Fechandoaplicaçãoprograma.
    """
    try:
        logger.info(
            f"[LinuxKiller] TentativaFechandoLinuxAplicação，PID: {pid}, ForçarFechando: {force}"
)
        if force:
            # ForçarFechando (SIGKILL)
            result = subprocess.run(
                ["kill", "-9", str(pid)], capture_output=True, timeout=5
            )
        else:
            # Fechando (SIGTERM)
            result = subprocess.run(
                ["kill", "-15", str(pid)], capture_output=True, timeout=5
            )

        success = result.returncode == 0

        if success:
            logger.info(f"[LinuxKiller] SucessoFechandoAplicação，PID: {pid}")
        else:
            logger.warning(f"[LinuxKiller] FechandoAplicaçãoFalha，PID: {pid}")

        return success

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.error(f"[LinuxKiller] LinuxFechandoAplicaçãoFalha: {e}")
        return False
