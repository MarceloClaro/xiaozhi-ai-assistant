"""WindowsaplicaçãoprogramaDispositivo.

Windowssistemadeaplicaçãoprogramae
"""

import json
import os
import platform
import subprocess
from typing import Dict, List, Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def scan_installed_applications() -> List[Dict[str, str]]:
    """WindowssistemaEmJádeaplicaçãoprograma.

    Returns:
        List[Dict[str, str]]: aplicaçãoprograma
    """
    if platform.system() != "Windows":
        return []

    apps = []

    # 1. ComeçarEmdeAplicação（de）
    try:
        logger.info("[WindowsScanner] ComeçarComeçarApp")
        start_menu_apps = _scan_main_start_menu_apps()
        apps.extend(start_menu_apps)
        logger.info(
            f"[WindowsScanner] deComeçarpara {len(start_menu_apps)} App")
    except Exception as e:
        logger.warning(f"[WindowsScanner] ComeçarFalha: {e}")

    # 2. EmdeApp（）
    try:
        logger.info("[WindowsScanner] ComeçarJádeAplicação")
        registry_apps = _scan_main_registry_apps()
        # ：ComeçarEmdeApp
        existing_names = {app["display_name"].lower() for app in apps}
        for app in registry_apps:
            if app["display_name"].lower() not in existing_names:
                apps.append(app)
        logger.info(
            f"[WindowsScanner] depara {len([a for a in registry_apps if a['display_name'].lower() not in existing_names])} deApp")
    except Exception as e:
        logger.warning(f"[WindowsScanner] Falha: {e}")

    # 3. deApp（de）
    system_apps = [
        {
            "name": "Calculator",
            "display_name": "Dispositivo",
            "path": "calc",
            "type": "system",
        },
        {
            "name": "Notepad",
            "display_name": "",
            "path": "notepad",
            "type": "system",
        },
        {"name": "Paint", "display_name": "", "path": "mspaint", "type": "system"},
        {
            "name": "File Explorer",
            "display_name": "Arquivo  FonteDispositivo",
            "path": "explorer",
            "type": "system",
        },
        {
            "name": "Task Manager",
            "display_name": "Dispositivo",
            "path": "taskmgr",
            "type": "system",
        },
        {
            "name": "Control Panel",
            "display_name": "",
            "path": "control",
            "type": "system",
        },
        {
            "name": "Settings",
            "display_name": "Configurando",
            "path": "ms-settings:",
            "type": "system",
        },
    ]
    apps.extend(system_apps)

    logger.info(
        f"[WindowsScanner] WindowsAppConcluído，Encontrado {len(apps)} Aplicação")
    return apps


def scan_running_applications() -> List[Dict[str, str]]:
    """WindowssistemaEm  Emdeaplicaçãoprograma.

    Returns:
        List[Dict[str, str]]: Emdeaplicaçãoprograma
    """
    if platform.system() != "Windows":
        return []

    apps = []

    try:
        # UsandotasklistComandoProcessoInformação
        result = subprocess.run(
            ["tasklist", "/fo", "csv", "/v"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]  # 

            for line in lines:
                try:
                    # AnalisandoCSVFormato
                    parts = [part.strip('"') for part in line.split('","')]
                    if len(parts) >= 8:
                        image_name = parts[0].strip('"')
                        pid = parts[1]
                        window_title = parts[8] if len(parts) > 8 else ""

                        # NãodeProcesso
                        if _should_include_process(image_name, window_title):
                            display_name = _extract_app_name(image_name, window_title)
                            clean_name = _clean_app_name(display_name)

                            apps.append(
                                {
                                    "pid": int(pid),
                                    "name": clean_name,
                                    "display_name": display_name,
                                    "command": image_name,
                                    "window_title": window_title,
                                    "type": "application",
                                }
                            )
                except (ValueError, IndexError):
                    continue

        logger.info(f"[WindowsScanner] Encontrado {len(apps)} EmdeAplicação")
        return apps

    except Exception as e:
        logger.error(f"[WindowsScanner] AppFalha: {e}")
        return []


def _scan_main_start_menu_apps() -> List[Dict[str, str]]:
    """
    IniciandoEmdeaplicaçãoprograma（sistemae）.
    """
    apps = []

    # ComeçarDiretório
    start_menu_paths = [
        os.path.join(
            os.environ.get("PROGRAMDATA", ""),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
        ),
        os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
        ),
    ]

    for start_path in start_menu_paths:
        if os.path.exists(start_path):
            try:
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if file.lower().endswith(".lnk"):
                            try:
                                shortcut_path = os.path.join(root, file)
                                display_name = file[:-4]  # .lnk

                                # NãodeAplicação
                                if _should_include_app(display_name):
                                    clean_name = _clean_app_name(display_name)
                                    target_path = _resolve_shortcut_target(
                                        shortcut_path
                                    )

                                    apps.append(
                                        {
                                            "name": clean_name,
                                            "display_name": display_name,
                                            "path": target_path or shortcut_path,
                                            "type": "shortcut",
                                        }
                                    )

                            except Exception as e:
                                logger.debug(
                                    f"[WindowsScanner] ProcessandoAtalhoFalha {file}: {e}"
)
            except Exception as e:
                logger.debug(f"[WindowsScanner] ComeçarFalha {start_path}: {e}")

    return apps


def _scan_main_registry_apps() -> List[Dict[str, str]]:
    """
    Emdeaplicaçãoprograma（sistema）.
    """
    apps = []

    try:
        powershell_cmd = [
            "powershell",
            "-Command",
            "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
            "Select-Object DisplayName, InstallLocation, Publisher | "
            "Where-Object {$_.DisplayName -ne $null} | "
            "ConvertTo-Json",
        ]

        result = subprocess.run(
            powershell_cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout:
            try:
                installed_apps = json.loads(result.stdout)
                if isinstance(installed_apps, dict):
                    installed_apps = [installed_apps]

                for app in installed_apps:
                    display_name = app.get("DisplayName", "")
                    publisher = app.get("Publisher", "")

                    if display_name and _should_include_app(display_name, publisher):
                        clean_name = _clean_app_name(display_name)
                        apps.append(
                            {
                                "name": clean_name,
                                "display_name": display_name,
                                "path": app.get("InstallLocation", ""),
                                "type": "installed",
                            }
                        )

            except json.JSONDecodeError:
                logger.warning("[WindowsScanner] Incapaz deAnalisandoPowerShellSaída")

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.warning(f"[WindowsScanner] PowerShellFalha: {e}")

    return apps


def _should_include_app(display_name: str, publisher: str = "") -> bool:
    """aplicaçãoprograma.

    Args:
        display_name: aplicaçãoprogramaNome
        publisher: （）

    Returns:
        bool: 
    """
    name_lower = display_name.lower()

    # deeBanco de dados
    exclude_keywords = [
        # Microsoft
        "microsoft visual c++",
        "microsoft .net",
        "microsoft office",
        "microsoft edge webview",
        "microsoft visual studio",
        "microsoft redistributable",
        "microsoft windows sdk",
        # e
        "uninstall",
        "",
        "readme",
        "help",
        "",
        "documentation",
        "",
        "driver",
        "",
        "update",
        "",
        "hotfix",
        "patch",
        "",
        # 
        "development",
        "sdk",
        "runtime",
        "redistributable",
        "framework",
        "python documentation",
        "python test suite",
        "python executables",
        "java update",
        "java development kit",
        # 
        "service pack",
        "security update",
        "language pack",
        # deAtalho
        "website",
        "web site",
        "",
        "online",
        "Em",
        "report",
        "",
        "feedback",
        "",
    ]

    # Pesquisar
    for keyword in exclude_keywords:
        if keyword in name_lower:
            return False

    # deAplicação
    include_keywords = [
        # Dispositivo
        "chrome",
        "firefox",
        "edge",
        "safari",
        "opera",
        "brave",
        # 
        "office",
        "word",
        "excel",
        "powerpoint",
        "outlook",
        "onenote",
        "wps",
        "typora",
        "notion",
        "obsidian",
        # 
        "visual studio code",
        "vscode",
        "pycharm",
        "idea",
        "eclipse",
        "git",
        "docker",
        "nodejs",
        "android studio",
        # 
        "qq",
        "",
        "wechat",
        "skype",
        "zoom",
        "teams",
        "",
        "feishu",
        "discord",
        "slack",
        "telegram",
        # 
        "vlc",
        "potplayer",
        "Música",
        "spotify",
        "itunes",
        "photoshop",
        "premiere",
        "after effects",
        "illustrator",
        # 
        "steam",
        "epic",
        "origin",
        "uplay",
        "battlenet",
        # 
        "7-zip",
        "winrar",
        "bandizip",
        "everything",
        "listary",
        "notepad++",
        "sublime",
        "atom",
    ]

    # Pesquisarde
    for keyword in include_keywords:
        if keyword in name_lower:
            return True

    # SeInformação，Microsoftde
    if publisher:
        publisher_lower = publisher.lower()
        if "microsoft corporation" in publisher_lower and any(
            x in name_lower
            for x in [
                "visual c++",
                ".net",
                "redistributable",
                "runtime",
                "framework",
                "update",
            ]
        ):
            return False

    # Aplicação（de）
    # de
    system_indicators = ["(x64)", "(x86)", "redistributable", "runtime", "framework"]
    if any(indicator in name_lower for indicator in system_indicators):
        return False

    return True


def _should_include_process(image_name: str, window_title: str) -> bool:
    """Processo.

    Args:
        image_name: ProcessoNome
        window_title: Janela

    Returns:
        bool: 
    """
    # Processo
    system_processes = {
        "dwm.exe",
        "winlogon.exe",
        "csrss.exe",
        "smss.exe",
        "lsass.exe",
        "services.exe",
        "svchost.exe",
        "explorer.exe",
        "taskhostw.exe",
        "conhost.exe",
        "dllhost.exe",
        "rundll32.exe",
        "msiexec.exe",
        "wininit.exe",
        "lsm.exe",
        "spoolsv.exe",
        "audiodg.exe",
    }

    image_lower = image_name.lower()

    # Processo
    if image_lower in system_processes:
        return False

    # JaneladeProcesso（）
    if not window_title or window_title == "N/A":
        return False

    # deJanela
    if len(window_title.strip()) < 3:
        return False

    return True


def _extract_app_name(image_name: str, window_title: str) -> str:
    """deProcessoInformaçãoEmaplicaçãoprogramaNome.

    Args:
        image_name: ProcessoNome
        window_title: Janela

    Returns:
        str: aplicaçãoprogramaNome
    """
    # UsandoJanela
    if window_title and window_title != "N/A" and len(window_title.strip()) > 0:
        return window_title.strip()

    # UsandoProcessoNome（.exe）
    if image_name.lower().endswith(".exe"):
        return image_name[:-4]

    return image_name


def _resolve_shortcut_target(shortcut_path: str) -> Optional[str]:
    """AnalisandoWindowsAtalhodeAlvoCaminho.

    Args:
        shortcut_path: AtalhoarquivoCaminho

    Returns:
        AlvoCaminho，SeAnalisandofalhouentãoRetornoNone
    """
    try:
        import win32com.client

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        target_path = shortcut.Targetpath

        if target_path and os.path.exists(target_path):
            return target_path

    except ImportError:
        logger.debug("[WindowsScanner] win32comNão，Incapaz deAnalisandoAtalho")
    except Exception as e:
        logger.debug(f"[WindowsScanner] AnalisandoAtalhoFalha: {e}")

    return None


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
