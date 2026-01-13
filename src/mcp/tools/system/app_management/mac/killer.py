"""macOSsistemaaplicaçãoprogramaFechandoDispositivo.

macOSdeaplicaçãoprogramaFechando
"""

import json
import subprocess
from typing import Any, Dict, List

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def list_running_applications(filter_name: str = "") -> List[Dict[str, Any]]:
    """macOSEmde、usuáriodeaplicaçãoprograma.

    UsandoAppleScript (JXA) deaplicação.
    """
    apps = []
    script = """
    ObjC.import('AppKit');

    function run() {
        let procs = $.NSWorkspace.sharedWorkspace.runningApplications;
        let apps = [];
        for (let i = 0; i < procs.count; i++) {
            let app = procs.objectAtIndex(i);
            // NSApplicationActivationPolicyRegular are regular apps that appear in the Dock.
            if (app.activationPolicy === $.NSApplicationActivationPolicyRegular) {
                apps.push({
                    'name': app.localizedName.js,
                    'pid': app.processIdentifier,
                    'path': app.bundleURL ? app.bundleURL.path.js : ""
                });
            }
        }
        return JSON.stringify(apps);
    }
    """
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )

        running_apps = json.loads(result.stdout)

        for app_info in running_apps:
            app_name = app_info.get("name", "")
            if not filter_name or filter_name.lower() in app_name.lower():
                apps.append(
                    {
                        "pid": app_info.get("pid"),
                        "ppid": -1,  # Not available via this method
                        "name": app_name,
                        "display_name": app_name,
                        "command": app_info.get("path", ""),
                        "type": "application",
                    }
                )

        logger.info(f"[MacKiller] UsandoJXAEncontrado {len(apps)} Emdeaplicaçãoprograma")
        return apps

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
        subprocess.CalledProcessError,
    ) as e:
        logger.warning(f"[MacKiller] JXAProcessofalhou ({e})，parapsComando")
        return _list_running_applications_ps(filter_name)
    except json.JSONDecodeError as e:
        logger.error(f"[MacKiller] AnalisandoJXASaídafalhou ({e})，parapsComando")
        return _list_running_applications_ps(filter_name)


def _list_running_applications_ps(filter_name: str = "") -> List[Dict[str, Any]]:
    """
    macOSEmdeAplicação (psComando).
    """
    apps = []

    try:
        # UsandopsComandoProcessoInformação
        result = subprocess.run(
            ["ps", "-eo", "pid,ppid,comm,command"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]  # 

            for line in lines:
                parts = line.strip().split(None, 3)
                if len(parts) >= 4:
                    pid, ppid, comm, command = parts

                    # aplicaçãoprograma
                    is_app = (
                        ".app" in command
                        or not command.startswith("/")
                        or any(
                            name in command.lower()
                            for name in ["chrome", "firefox", "qq", "wechat", "music"]
                        )
                    )

                    if is_app:
                        app_name = comm.split("/")[-1]

                        # aplicação
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
        logger.warning(f"[MacKiller] macOSProcessofalhou (ps): {e}")

    return apps


def kill_application(pid: int, force: bool) -> bool:
    """
    EmmacOS  FechandoAplicação.
    """
    try:
        logger.info(f"[MacKiller] TentativaFechandomacOSAplicação，PID: {pid}, ForçarFechando: {force}")

        if force:
            # ForçarFechando (SIGKILL)
            result = subprocess.run(
                ["kill", "-9", str(pid)], capture_output=True, text=True, timeout=5
            )
        else:
            # Fechando (SIGTERM)
            result = subprocess.run(
                ["kill", "-15", str(pid)], capture_output=True, text=True, timeout=5
            )

        success = result.returncode == 0

        if success:
            logger.info(f"[MacKiller] SucessoFechandoAplicação，PID: {pid}")
        else:
            logger.warning(f"[MacKiller] FechandoAplicaçãoFalha，PID: {pid}")

        return success

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.error(f"[MacKiller] macOSFechandoAplicaçãoFalha: {e}")
        return False
