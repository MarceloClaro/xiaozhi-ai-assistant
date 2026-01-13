"""WindowssistemaaplicaçãoprogramaFechandoDispositivo.

WindowsdeaplicaçãoprogramaFechando
"""

import json
import subprocess
from typing import Any, Dict, List

from src.utils.logging_config import get_logger

from ..utils import AppMatcher

logger = get_logger(__name__)


def list_running_applications(filter_name: str = "") -> List[Dict[str, Any]]:
    """
    WindowsEmdeaplicaçãoprograma.
    """
    apps = []

    # 1: UsandoConversãodePowerShell（Selecionando，）
    try:
        logger.debug("[WindowsKiller] UsandoConversãodePowerShellProcesso")
        # dePowerShell
        powershell_script = """
        Get-Process | Where-Object {
            $_.ProcessName -notmatch '^(dwm|winlogon|csrss|smss|wininit|services|lsass|svchost|spoolsv|taskhostw|explorer|fontdrvhost|dllhost|conhost|sihost|runtimebroker)$' -and
            ($_.MainWindowTitle -or $_.ProcessName -match '(chrome|firefox|edge|qq|wechat|notepad|calc|typora|vscode|pycharm|feishu|qqmusic)')
        } | Select-Object Id, ProcessName, MainWindowTitle, Path | ConvertTo-Json
        """

        result = subprocess.run(
            ["powershell", "-Command", powershell_script],
            capture_output=True,
            text=True,
            timeout=8,
        )

        if result.returncode == 0 and result.stdout.strip():
            try:
                process_data = json.loads(result.stdout)
                if isinstance(process_data, dict):
                    process_data = [process_data]

                for proc in process_data:
                    proc_name = proc.get("ProcessName", "")
                    pid = proc.get("Id", 0)
                    window_title = proc.get("MainWindowTitle", "")
                    exe_path = proc.get("Path", "")

                    if proc_name and pid:
                        # aplicação
                        if not filter_name or _matches_process_name(
                            filter_name, proc_name, window_title, exe_path
                        ):
                            apps.append(
                                {
                                    "pid": int(pid),
                                    "name": proc_name,
                                    "display_name": f"{proc_name}.exe",
                                    "command": exe_path or f"{proc_name}.exe",
                                    "window_title": window_title,
                                    "type": "application",
                                }
                            )

                if apps:
                    logger.info(
                        f"[WindowsKiller] PowerShellsucesso，Encontrado {len(apps)} Processos")
                    return _deduplicate_and_sort_apps(apps)

            except json.JSONDecodeError as e:
                logger.debug(f"[WindowsKiller] PowerShell JSONAnalisandofalhou: {e}")

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.warning(f"[WindowsKiller] PowerShellProcessofalhou: {e}")

    # 2: UsandoConversãodetasklistComando（）
    if not apps:
        try:
            logger.debug("[WindowsKiller] UsandoConversãotasklistComando")
            result = subprocess.run(
                ["tasklist", "/fo", "csv"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding="gbk",
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # 

                for line in lines:
                    try:
                        # AnalisandoCSVFormato
                        parts = [p.strip('"') for p in line.split('","')]
                        if len(parts) >= 2:
                            image_name = parts[0]
                            pid = parts[1]

                            # 
                            if not image_name.lower().endswith(".exe"):
                                continue

                            app_name = image_name.replace(".exe", "")

                            # sistemaProcesso
                            if _is_system_process(app_name):
                                continue

                            # aplicação
                            if not filter_name or _matches_process_name(
                                filter_name, app_name, "", image_name
                            ):
                                apps.append(
                                    {
                                        "pid": int(pid),
                                        "name": app_name,
                                        "display_name": image_name,
                                        "command": image_name,
                                        "type": "application",
                                    }
                                )
                    except (ValueError, IndexError):
                        continue

            if apps:
                logger.info(
                    f"[WindowsKiller] tasklistsucesso，Encontrado {len(apps)} Processos")
                return _deduplicate_and_sort_apps(apps)

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"[WindowsKiller] tasklistComandofalhou: {e}")

    # 3: Usandowmic  para
    if not apps:
        try:
            logger.debug("[WindowsKiller] UsandowmicComando")
            result = subprocess.run(
                [
                    "wmic",
                    "process",
                    "get",
                    "ProcessId,Name,ExecutablePath",
                    "/format:csv",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # 

                for line in lines:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        try:
                            exe_path = parts[1].strip() if len(parts) > 1 else ""
                            name = parts[2].strip() if len(parts) > 2 else ""
                            pid = parts[3].strip() if len(parts) > 3 else ""

                            if name.lower().endswith(".exe") and pid.isdigit():
                                app_name = name.replace(".exe", "")

                                if _is_system_process(app_name):
                                    continue

                                # aplicação
                                if not filter_name or _matches_process_name(
                                    filter_name, app_name, "", exe_path
                                ):
                                    apps.append(
                                        {
                                            "pid": int(pid),
                                            "name": app_name,
                                            "display_name": name,
                                            "command": exe_path or name,
                                            "type": "application",
                                        }
                                    )
                        except (ValueError, IndexError):
                            continue

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"[WindowsKiller] wmicProcessofalhou: {e}")

    return _deduplicate_and_sort_apps(apps)


def kill_application_group(
    apps: List[Dict[str, Any]], app_name: str, force: bool
) -> bool:
    """FechandoWindowsAplicação.

    Args:
        apps: CorrespondênciadeAplicaçãoProcesso
        app_name: AplicaçãoNome
        force: ForçarFechando

    Returns:
        bool: FechandoSucesso
    """
    try:
        logger.info(
            f"[WindowsKiller] IniciandoFechandoWindowsaplicação: {app_name}, Encontrado {len(apps)} Processo"

        # 1. Tentativa  aplicaçãoNomeFechando（）
        success = _kill_by_image_name(apps, force)
        if success:
            logger.info(f"[WindowsKiller] sucessoAtravés deaplicaçãoNomeFechando: {app_name}")
            return True

        # 2. SeFechandofalhou，TentativaFechando
        success = _kill_by_process_groups(apps, force)
        if success:
            logger.info(f"[WindowsKiller] sucessoAtravés deProcessoFechando: {app_name}")
            return True

        # 3. Tentativa  Fechando（）
        success = _kill_individual_processes(apps, force)
        logger.info(f"[WindowsKiller] Através de  Fechandoconcluído: {app_name}, sucesso: {success}")
        return success

    except Exception as e:
        logger.error(f"[WindowsKiller] WindowsFechandofalhou: {e}")
        return False


def kill_application(pid: int, force: bool) -> bool:
    """
    EmWindows  Fechando  Aplicação.
    """
    try:
        logger.info(
            f"[WindowsKiller] TentativaFechandoWindowsaplicaçãoprograma，PID: {pid}, ForçarFechando: {force}"
)
        if force:
            # ForçarFechando
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        else:
            # Fechando
            result = subprocess.run(
                ["taskkill", "/PID", str(pid)],
                capture_output=True,
                text=True,
                timeout=10,
            )

        success = result.returncode == 0

        if success:
            logger.info(f"[WindowsKiller] sucessoFechandoaplicaçãoprograma，PID: {pid}")
        else:
            logger.warning(
                f"[WindowsKiller] Fechandoaplicaçãoprogramafalhou，PID: {pid}, erroInformação: {result.stderr}"
)
        return success

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        logger.error(f"[WindowsKiller] WindowsFechandoaplicaçãoprogramaexceção，PID: {pid}, erro: {e}")
        return False


def _matches_process_name(
    filter_name: str, proc_name: str, window_title: str = "", exe_path: str = ""
) -> bool:
    """
    CorrespondênciaProcessoNome.
    """
    try:
        # aplicaçãoInformação
        app_info = {
            "name": proc_name,
            "display_name": proc_name,
            "window_title": window_title,
            "command": exe_path,
        }

        # UsandoCorrespondênciaDispositivo，Correspondência30paraCorrespondência
        score = AppMatcher.match_application(filter_name, app_info)
        return score >= 30

    except Exception:
        # Conversão
        filter_lower = filter_name.lower()
        proc_lower = proc_name.lower()

        return (
            filter_lower == proc_lower
            or filter_lower in proc_lower
            or (window_title and filter_lower in window_title.lower())
        )


def _is_system_process(proc_name: str) -> bool:
    """
    paraProcesso.
    """
    system_processes = {
        "dwm",
        "winlogon",
        "csrss",
        "smss",
        "wininit",
        "services",
        "lsass",
        "svchost",
        "spoolsv",
        "explorer",
        "taskhostw",
        "fontdrvhost",
        "dllhost",
        "ctfmon",
        "audiodg",
        "conhost",
        "sihost",
        "shellexperiencehost",
        "startmenuexperiencehost",
        "runtimebroker",
        "applicationframehost",
        "searchui",
        "cortana",
        "useroobebroker",
        "lockapp",
    }

    return proc_name.lower() in system_processes


def _deduplicate_and_sort_apps(apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aplicação.
    """
    # PID
    seen_pids = set()
    unique_apps = []
    for app in apps:
        if app["pid"] not in seen_pids:
            seen_pids.add(app["pid"])
            unique_apps.append(app)

    # Nome
    unique_apps.sort(key=lambda x: x["name"].lower())

    logger.info(
        f"[WindowsKiller] Processoconcluído，Encontrado {len(unique_apps)} aplicaçãoprograma")
    return unique_apps


def _kill_by_image_name(apps: List[Dict[str, Any]], force: bool) -> bool:
    """
    Através deImagemNomeFechandoAplicação.
    """
    try:
        # deProcessoNome
        image_names = set()
        for app in apps:
            name = app.get("name", "")
            if name:
                # .exe
                if not name.lower().endswith(".exe"):
                    name += ".exe"
                image_names.add(name)

        if not image_names:
            return False

        logger.info(f"[WindowsKiller] TentativaAtravés deImagemNomeFechando: {list(image_names)}")

        # ImagemNomeFechando
        success_count = 0
        for image_name in image_names:
            try:
                if force:
                    cmd = ["taskkill", "/IM", image_name, "/F", "/T"]  # /TFechando  Processo
                else:
                    cmd = ["taskkill", "/IM", image_name, "/T"]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    success_count += 1
                    logger.info(f"[WindowsKiller] sucessoFechandoImagem: {image_name}")
                else:
                    logger.debug(
                        f"[WindowsKiller] FechandoImagemfalhou: {image_name}, erro: {result.stderr}"
)
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                logger.debug(f"[WindowsKiller] FechandoImagemexceção: {image_name}, erro: {e}")

        return success_count > 0

    except Exception as e:
        logger.debug(f"[WindowsKiller] ImagemNomeFechandoexceção: {e}")
        return False


def _kill_by_process_groups(apps: List[Dict[str, Any]], force: bool) -> bool:
    """
    Grupo de processosFechandoAplicação.
    """
    try:
        # ProcessoNome
        process_groups = {}
        for app in apps:
            name = app.get("name", "")
            if name:
                base_name = _get_base_process_name(name)
                if base_name not in process_groups:
                    process_groups[base_name] = []
                process_groups[base_name].append(app)

        logger.info(
            f"[WindowsKiller] Identificando {len(process_groups)} Grupo de processos: {list(process_groups.keys())}"

        # paraIdentificando  Processo  Fechando
        success_count = 0
        for group_name, group_apps in process_groups.items():
            try:
                # Encontrado  Processo（PPIDMínimodeouJanelade）
                main_process = _find_main_process(group_apps)

                if main_process:
                    # Fechando  Processo（Processo）
                    pid = main_process.get("pid")
                    if pid:
                        success = kill_application(pid, force)
                        if success:
                            success_count += 1
                            logger.info(
                                f"[WindowsKiller] sucessoFechandoGrupo de processos {group_name} de  Processo (PID: {pid})"
                        else:
                            # Se  ProcessoFechandofalhou，TentativaFechandoProcesso
                            for app in group_apps:
                                if kill_application(app.get("pid"), force):
                                    success_count += 1

            except Exception as e:
                logger.debug(f"[WindowsKiller] FechandoGrupo de processosfalhou: {group_name}, erro: {e}")

        return success_count > 0

    except Exception as e:
        logger.debug(f"[WindowsKiller] Grupo de processosFechandoexceção: {e}")
        return False


def _kill_individual_processes(apps: List[Dict[str, Any]], force: bool) -> bool:
    """
    FechandoProcesso（）.
    """
    try:
        logger.info(f"[WindowsKiller] Iniciando  Fechando {len(apps)} Processos")

        success_count = 0
        for app in apps:
            pid = app.get("pid")
            if pid:
                success = kill_application(pid, force)
                if success:
                    success_count += 1
                    logger.debug(
                        f"[WindowsKiller] sucessoFechandoProcesso: {app.get('name')} (PID: {pid})"

        logger.info(
            f"[WindowsKiller] Fechandoconcluído，sucessoFechando {success_count}/{len(apps)} Processos")
        return success_count > 0

    except Exception as e:
        logger.error(f"[WindowsKiller] Fechandoexceção: {e}")
        return False


def _get_base_process_name(process_name: str) -> str:
    """
    ProcessoNome（）.
    """
    try:
        return AppMatcher.get_process_group(process_name)
    except Exception:
        # 
        name = process_name.lower().replace(".exe", "")
        if "chrome" in name:
            return "chrome"
        elif "qq" in name and "music" not in name:
            return "qq"
        return name


def _find_main_process(processes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    EmGrupo de processosEmEncontrado  Processo.
    """
    if not processes:
        return {}

    # 1: JaneladeProcessoProcesso
    for proc in processes:
        window_title = proc.get("window_title", "")
        if window_title and window_title.strip():
            return proc

    # 2: PPIDMínimodeProcesso（Processo）
    try:
        main_proc = min(processes, key=lambda p: p.get("ppid", p.get("pid", 999999)))
        return main_proc
    except (ValueError, TypeError):
        pass

    # 3: PIDMínimodeProcesso
    try:
        main_proc = min(processes, key=lambda p: p.get("pid", 999999))
        return main_proc
    except (ValueError, TypeError):
        pass

    # ：RetornoProcessos
    return processes[0]
