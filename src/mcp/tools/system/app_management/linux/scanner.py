"""LinuxaplicaçãoprogramaDispositivo.

Linuxsistemadeaplicaçãoprogramae
"""

import platform
import subprocess
from pathlib import Path
from typing import Dict, List

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def scan_installed_applications() -> List[Dict[str, str]]:
    """LinuxsistemaEmJádeaplicaçãoprograma.

    Returns:
        List[Dict[str, str]]: aplicaçãoprograma
    """
    if platform.system() != "Linux":
        return []

    apps = []

    #  .desktop Arquivo
    desktop_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        Path.home() / ".local/share/applications",
    ]

    for desktop_dir in desktop_dirs:
        desktop_path = Path(desktop_dir)
        if desktop_path.exists():
            for desktop_file in desktop_path.glob("*.desktop"):
                try:
                    app_info = _parse_desktop_file(desktop_file)
                    if app_info and _should_include_app(app_info["display_name"]):
                        apps.append(app_info)
                except Exception as e:
                    logger.debug(
                        f"[LinuxScanner] AnalisandodesktopArquivoFalha {desktop_file}: {e}"

    # deLinuxApp
    system_apps = [
        {
            "name": "gedit",
            "display_name": "Dispositivo",
            "path": "gedit",
            "type": "system",
        },
        {
            "name": "firefox",
            "display_name": "FirefoxDispositivo",
            "path": "firefox",
            "type": "system",
        },
        {
            "name": "gnome-calculator",
            "display_name": "Dispositivo",
            "path": "gnome-calculator",
            "type": "system",
        },
        {
            "name": "nautilus",
            "display_name": "ArquivoDispositivo",
            "path": "nautilus",
            "type": "system",
        },
        {
            "name": "gnome-terminal",
            "display_name": "",
            "path": "gnome-terminal",
            "type": "system",
        },
        {
            "name": "gnome-control-center",
            "display_name": "Configurando",
            "path": "gnome-control-center",
            "type": "system",
        },
    ]
    apps.extend(system_apps)

    logger.info(f"[LinuxScanner] Concluído，Encontrado {len(apps)} Aplicação")
    return apps


def scan_running_applications() -> List[Dict[str, str]]:
    """LinuxsistemaEm  Emdeaplicaçãoprograma.

    Returns:
        List[Dict[str, str]]: Emdeaplicaçãoprograma
    """
    if platform.system() != "Linux":
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

        logger.info(f"[LinuxScanner] Encontrado {len(apps)} EmdeAplicação")
        return apps

    except Exception as e:
        logger.error(f"[LinuxScanner] AppFalha: {e}")
        return []


def _parse_desktop_file(desktop_file: Path) -> Dict[str, str]:
    """Analisando.desktoparquivo.

    Args:
        desktop_file: .desktoparquivoCaminho

    Returns:
        Dict[str, str]: aplicaçãoprogramaInformação
    """
    try:
        with open(desktop_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Analisando .desktop Arquivo
        name = ""
        display_name = ""
        exec_cmd = ""

        for line in content.split("\n"):
            if line.startswith("Name="):
                display_name = line.split("=", 1)[1]
            elif line.startswith("Name[zh_CN]="):
                display_name = line.split("=", 1)[1]  # UsandoEm
            elif line.startswith("Exec="):
                exec_cmd = line.split("=", 1)[1].split()[0]  # Comando

        if display_name and exec_cmd:
            name = _clean_app_name(display_name)
            return {
                "name": name,
                "display_name": display_name,
                "path": exec_cmd,
                "type": "desktop",
            }

        return None

    except Exception:
        return None


def _should_include_app(display_name: str) -> bool:
    """aplicaçãoprograma.

    Args:
        display_name: aplicaçãoprogramaNome

    Returns:
        bool: 
    """
    if not display_name:
        return False

    # deAplicaçãoModo
    exclude_patterns = [
        # 
        "gnome-",
        "kde-",
        "xfce-",
        "unity-",
        # 
        "gdb",
        "valgrind",
        "strace",
        "ltrace",
        # 
        "dconf",
        "gsettings",
        "xdg-",
        "desktop-file-",
        # 
        "help",
        "about",
        "preferences",
        "settings",
    ]

    display_lower = display_name.lower()

    # PesquisarModo
    for pattern in exclude_patterns:
        if pattern in display_lower:
            return False

    return True


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
        # eProcesso
        "kthreadd",
        "ksoftirqd",
        "migration",
        "rcu_",
        "watchdog",
        "systemd",
        "init",
        "kernel",
        "kworker",
        "kcompactd",
        # 
        "dbus",
        "networkd",
        "resolved",
        "logind",
        "udevd",
        "cron",
        "rsyslog",
        "ssh",
        "avahi",
        "cups",
        # 
        "gnome-",
        "kde-",
        "xfce-",
        "unity-",
        "compiz",
        "pulseaudio",
        "pipewire",
        "wireplumber",
        # X11/Wayland
        "Xorg",
        "wayland",
        "weston",
        "mutter",
        "kwin",
    }

    # PesquisarProcesso
    comm_lower = comm.lower()
    command_lower = command.lower()

    # NomeouProcesso
    if not comm or any(proc in comm_lower for proc in system_processes):
        return False

    # Caminho  deProcesso
    if any(
        path in command_lower
        for path in [
            "/usr/libexec/",
            "/usr/lib/",
            "/lib/",
            "/sbin/",
            "/usr/sbin/",
            "/bin/systemd",
            "/usr/bin/dbus",
        ]
    ):
        return False

    # de
    if any(
        keyword in command_lower
        for keyword in ["daemon", "service", "helper", "agent", "monitor"]
    ):
        return False

    # Aplicação
    user_app_indicators = [
        "/usr/bin/",
        "/usr/local/bin/",
        "/opt/",
        "/home/",
        "/snap/",
        "/flatpak/",
    ]

    return any(indicator in command_lower for indicator in user_app_indicators)


def _extract_app_name(comm: str, command: str) -> str:
    """deProcessoInformaçãoEmaplicaçãoprogramaNome.

    Args:
        comm: ProcessoNome
        command: Comando

    Returns:
        str: aplicaçãoprogramaNome
    """
    # TentativadeComandoCaminhoEmAppNome
    if "/" in command:
        try:
            # Arquivo
            exec_path = command.split()[0]
            app_name = Path(exec_path).name

            # 
            if app_name.endswith(".py"):
                app_name = app_name[:-3]
            elif app_name.endswith(".sh"):
                app_name = app_name[:-3]

            return app_name
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
