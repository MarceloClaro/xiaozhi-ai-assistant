"""macOSaplicaçãoprogramaDispositivo.

macOSsistemadeaplicaçãoprogramae
"""

import platform
import subprocess
from pathlib import Path
from typing import Dict, List

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def scan_installed_applications() -> List[Dict[str, str]]:
    """macOSsistemaEmJádeaplicaçãoprograma.

    Returns:
        List[Dict[str, str]]: aplicaçãoprograma
    """
    if platform.system() != "Darwin":
        return []

    apps = []

    #  /Applications Diretório
    applications_dir = Path("/Applications")
    if applications_dir.exists():
        for app_path in applications_dir.glob("*.app"):
            app_name = app_path.stem
            clean_name = _clean_app_name(app_name)
            apps.append(
                {
                    "name": clean_name,
                    "display_name": app_name,
                    "path": str(app_path),
                    "type": "application",
                }
            )

    # AplicaçãoDiretório
    user_apps_dir = Path.home() / "Applications"
    if user_apps_dir.exists():
        for app_path in user_apps_dir.glob("*.app"):
            app_name = app_path.stem
            clean_name = _clean_app_name(app_name)
            apps.append(
                {
                    "name": clean_name,
                    "display_name": app_name,
                    "path": str(app_path),
                    "type": "user_application",
                }
            )

    # App
    system_apps = [
        {
            "name": "Calculator",
            "display_name": "Dispositivo",
            "path": "Calculator",
            "type": "system",
        },
        {
            "name": "TextEdit",
            "display_name": "",
            "path": "TextEdit",
            "type": "system",
        },
        {
            "name": "Preview",
            "display_name": "",
            "path": "Preview",
            "type": "system",
        },
        {
            "name": "Safari",
            "display_name": "SafariDispositivo",
            "path": "Safari",
            "type": "system",
        },
        {"name": "Finder", "display_name": "", "path": "Finder", "type": "system"},
        {
            "name": "Terminal",
            "display_name": "",
            "path": "Terminal",
            "type": "system",
        },
        {
            "name": "System Preferences",
            "display_name": "Configurando",
            "path": "System Preferences",
            "type": "system",
        },
    ]
    apps.extend(system_apps)

    logger.info(f"[MacScanner] Concluído，Encontrado {len(apps)} Aplicação")
    return apps


def scan_running_applications() -> List[Dict[str, str]]:
    """macOSsistemaEm  Emdeaplicaçãoprograma.

    Returns:
        List[Dict[str, str]]: Emdeaplicaçãoprograma
    """
    if platform.system() != "Darwin":
        return []

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

                    # NãodeProcesso
                    if _should_include_process(comm, command):
                        display_name = _extract_app_name(comm, command)
                        clean_name = _clean_app_name(display_name)

                        apps.append(
                            {
                                "pid": int(pid),
                                "ppid": int(ppid),
                                "name": clean_name,
                                "display_name": display_name,
                                "command": command,
                                "type": "application",
                            }
                        )

        logger.info(f"[MacScanner] Encontrado {len(apps)} EmdeAplicação")
        return apps

    except Exception as e:
        logger.error(f"[MacScanner] AppFalha: {e}")
        return []


def _should_include_process(comm: str, command: str) -> bool:
    """Processo.

    Args:
        comm: ProcessoNome
        command: Comando

    Returns:
        bool: 
    """
    # Processoe
    system_processes = {
        # Processo
        "kernel_task",
        "launchd",
        "kextd",
        "UserEventAgent",
        "cfprefsd",
        "loginwindow",
        "WindowServer",
        "SystemUIServer",
        "Dock",
        "Finder",
        "ControlCenter",
        "NotificationCenter",
        "WallpaperAgent",
        "Spotlight",
        "WiFiAgent",
        "CoreLocationAgent",
        "bluetoothd",
        "wirelessproxd",
        # 
        "com.apple.",
        "suhelperd",
        "softwareupdated",
        "cloudphotod",
        "identityservicesd",
        "imagent",
        "sharingd",
        "remindd",
        "contactsd",
        "accountsd",
        "CallHistorySyncHelper",
        "CallHistoryPluginHelper",
        # e
        "AppleSpell",
        "coreaudiod",
        "audio",
        "webrtc",
        "chrome_crashpad_handler",
        "crashpad_handler",
        "fsnotifier",
        "mdworker",
        "mds",
        "spotlight",
        # 
        "automountd",
        "autofsd",
        "aslmanager",
        "syslogd",
        "ntpd",
        "mDNSResponder",
        "distnoted",
        "notifyd",
        "powerd",
        "thermalmonitord",
        "watchdogd",
    }

    # PesquisarProcesso
    comm_lower = comm.lower()
    command_lower = command.lower()

    # NomeouCaminho
    if not comm or comm_lower in system_processes:
        return False

    # Caminho  deProcesso
    if any(
        path in command_lower
        for path in [
            "/system/library/",
            "/library/apple/",
            "/usr/libexec/",
            "/system/applications/utilities/",
            "/private/var/",
            "com.apple.",
            ".xpc/",
            ".framework/",
            ".appex/",
            "helper (gpu)",
            "helper (renderer)",
            "helper (plugin)",
            "crashpad_handler",
            "fsnotifier",
        ]
    ):
        return False

    # de
    if any(
        keyword in command_lower
        for keyword in [
            "xpcservice",
            "daemon",
            "agent",
            "service",
            "monitor",
            "updater",
            "sync",
            "backup",
            "cache",
            "log",
        ]
    ):
        return False

    # Aplicação
    user_app_indicators = ["/applications/", "/users/", "~/", ".app/contents/macos/"]

    return any(indicator in command_lower for indicator in user_app_indicators)


def _extract_app_name(comm: str, command: str) -> str:
    """deProcessoInformaçãoEmaplicaçãoprogramaNome.

    Args:
        comm: ProcessoNome
        command: Comando

    Returns:
        str: aplicaçãoprogramaNome
    """
    # TentativadeComandoCaminhoEm.appNome
    if ".app/Contents/MacOS/" in command:
        try:
            app_path = command.split(".app/Contents/MacOS/")[0] + ".app"
            app_name = Path(app_path).name.replace(".app", "")
            return app_name
        except (IndexError, AttributeError):
            pass

    # Tentativade/Applications/Caminho
    if "/Applications/" in command:
        try:
            parts = command.split("/Applications/")[1].split("/")[0]
            if parts.endswith(".app"):
                return parts.replace(".app", "")
        except (IndexError, AttributeError):
            pass

    # UsandoProcessoNome
    return comm if comm else "Unknown"


def _clean_app_name(name: str) -> str:
    """aplicaçãoprogramaNome，Versão  eCaracteres.

    Args:
        name: OriginalNome

    Returns:
        str: deNome
    """
    if not name:
        return ""

    # deVersãoModo
    import re

    # Versão ( "App 1.0", "App v2.1", "App (2023)")
    name = re.sub(r"\s+v?\d+[\.\d]*", "", name)
    name = re.sub(r"\s*\(\d+\)", "", name)
    name = re.sub(r"\s*\[.*?\]", "", name)

    # de
    name = " ".join(name.split())

    return name.strip()
