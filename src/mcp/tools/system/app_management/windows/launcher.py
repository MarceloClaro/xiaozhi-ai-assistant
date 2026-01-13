"""WindowssistemaaplicaçãoprogramaIniciandoDispositivo.

WindowsdeaplicaçãoprogramaIniciando
"""

import os
import subprocess
from typing import Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def launch_application(app_name: str) -> bool:
    """EmWindows  Inicia a aplicação.

    Args:
        app_name: aplicaçãoprogramaNome

    Returns:
        bool: Iniciandosucesso
    """
    try:
        logger.info(f"[WindowsLauncher] IniciandoAplicação: {app_name}")

        # TentativaNão  deIniciando
        launch_methods = [
            ("PowerShell Start-Process", _try_powershell_start),
            ("startComando", _try_start_command),
            ("os.startfile", _try_os_startfile),
            ("Pesquisar", _try_registry_launch),
            ("Caminho", _try_common_paths),
            ("whereComando", _try_where_command),
            ("UWPApp", _try_uwp_launch),
        ]

        for method_name, method_func in launch_methods:
            try:
                if method_func(app_name):
                    logger.info(f"[WindowsLauncher] {method_name}SucessoIniciando: {app_name}")
                    return True
                else:
                    logger.debug(f"[WindowsLauncher] {method_name}IniciandoFalha: {app_name}")
            except Exception as e:
                logger.debug(f"[WindowsLauncher] {method_name}Exceção: {e}")

        logger.warning(f"[WindowsLauncher] WindowsIniciandoFalha: {app_name}")
        return False

    except Exception as e:
        logger.error(f"[WindowsLauncher] WindowsIniciandoExceção: {e}", exc_info=True)
        return False


def launch_uwp_app_by_path(uwp_path: str) -> bool:
    """Através deUWPCaminhoInicia a aplicação.

    Args:
        uwp_path: UWPaplicaçãoprogramaCaminho（shell:AppsFolder\\...Formato）

    Returns:
        bool: Iniciandosucesso
    """
    try:
        if uwp_path.startswith("shell:AppsFolder\\"):
            # UsandoexplorerIniciandoUWPApp
            subprocess.Popen(["explorer.exe", uwp_path])
            logger.info(f"[WindowsLauncher] UWPAppIniciandoSucesso: {uwp_path}")
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"[WindowsLauncher] UWPAppIniciandoFalha: {e}")
        return False


def launch_shortcut(shortcut_path: str) -> bool:
    """IniciandoAtalhoarquivo.

    Args:
        shortcut_path: AtalhoarquivoCaminho

    Returns:
        bool: Iniciandosucesso
    """
    try:
        os.startfile(shortcut_path)
        logger.info(f"[WindowsLauncher] AtalhoIniciandoSucesso: {shortcut_path}")
        return True
    except Exception as e:
        logger.error(f"[WindowsLauncher] AtalhoIniciandoFalha: {e}")
        return False


def _try_powershell_start(app_name: str) -> bool:
    """
    TentativaUsandoPowerShell Start-ProcessInicia a aplicação.
    """
    try:
        escaped_name = app_name.replace('"', '""').replace("'", "''")
        powershell_cmd = f"powershell -Command \"Start-Process '{escaped_name}'\""
        result = subprocess.run(
            powershell_cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def _try_start_command(app_name: str) -> bool:
    """
    TentativaUsandostartComandoInicia a aplicação.
    """
    try:
        start_cmd = f'start "" "{app_name}"'
        result = subprocess.run(
            start_cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def _try_os_startfile(app_name: str) -> bool:
    """
    TentativaUsandoos.startfileInicia a aplicação.
    """
    try:
        os.startfile(app_name)
        return True
    except OSError:
        return False


def _try_registry_launch(app_name: str) -> bool:
    """
    TentativaAtravés dePesquisarInicia a aplicação.
    """
    try:
        executable_path = _find_executable_in_registry(app_name)
        if executable_path:
            subprocess.Popen([executable_path])
            return True
    except Exception:
        pass
    return False


def _try_common_paths(app_name: str) -> bool:
    """
    TentativadeaplicaçãoprogramaCaminho.
    """
    common_paths = [
        f"C:\\Program Files\\{app_name}\\{app_name}.exe",
        f"C:\\Program Files (x86)\\{app_name}\\{app_name}.exe",
        f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\{app_name}\\{app_name}.exe",
        f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\{app_name}\\{app_name}.exe",
        f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Roaming\\{app_name}\\{app_name}.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path])
                return True
            except Exception:
                continue
    return False


def _try_where_command(app_name: str) -> bool:
    """
    TentativaUsandowhereComandoPesquisarInicia a aplicação.
    """
    try:
        result = subprocess.run(
            f"where {app_name}", shell=True, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            exe_path = result.stdout.strip().split("\n")[0]  # 
            if exe_path and os.path.exists(exe_path):
                subprocess.Popen([exe_path])
                return True
    except Exception:
        pass
    return False


def _try_uwp_launch(app_name: str) -> bool:
    """
    TentativaIniciandoUWPaplicaçãoprograma.
    """
    try:
        return _launch_uwp_app(app_name)
    except Exception:
        return False


def _find_executable_in_registry(app_name: str) -> Optional[str]:
    """Através dePesquisaraplicaçãoprogramadearquivoCaminho.

    Args:
        app_name: aplicaçãoprogramaNome

    Returns:
        aplicaçãoprogramaCaminho，Se  EncontradoentãoRetornoNone
    """
    try:
        import winreg

        # PesquisarEmdeInformação
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]

        for registry_path in registry_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(
                                        subkey, "DisplayName"
                                    )[0]
                                    if app_name.lower() in display_name.lower():
                                        try:
                                            install_location = winreg.QueryValueEx(
                                                subkey, "InstallLocation"
                                            )[0]
                                            if install_location and os.path.exists(
                                                install_location
                                            ):
                                                # PesquisarArquivo
                                                for root, dirs, files in os.walk(
                                                    install_location
                                                ):
                                                    for file in files:
                                                        if (
                                                            file.lower().endswith(
                                                                ".exe"
                                                            )
                                                            and app_name.lower()
                                                            in file.lower()
                                                        ):
                                                            return os.path.join(
                                                                root, file
                                                            )
                                        except FileNotFoundError:
                                            pass

                                        try:
                                            display_icon = winreg.QueryValueEx(
                                                subkey, "DisplayIcon"
                                            )[0]
                                            if (
                                                display_icon
                                                and display_icon.endswith(".exe")
                                                and os.path.exists(display_icon)
                                            ):
                                                return display_icon
                                        except FileNotFoundError:
                                            pass

                                except FileNotFoundError:
                                    continue
                        except Exception:
                            continue
            except Exception:
                continue

        return None

    except ImportError:
        logger.debug("[WindowsLauncher] winregNão，Pesquisar")
        return None
    except Exception as e:
        logger.debug(f"[WindowsLauncher] PesquisarFalha: {e}")
        return None


def _launch_uwp_app(app_name: str) -> bool:
    """TentativaIniciandoUWP（Windows Store）aplicaçãoprograma.

    Args:
        app_name: aplicaçãoprogramaNome

    Returns:
        bool: Iniciandosucesso
    """
    try:
        # UsandoPowerShellPesquisareIniciandoUWPApp
        powershell_script = f"""")
        $app = Get-AppxPackage | Where-Object {{$_.Name -like "*{app_name}*" -or $_.PackageFullName -like "*{app_name}*"}} | Select-Object -First 1
        if ($app) {{
            $manifest = Get-AppxPackageManifest $app.PackageFullName
            $appId = $manifest.Package.Applications.Application.Id
            if ($appId) {{
                Start-Process "shell:AppsFolder\\$($app.PackageFullName)!$appId"
                Write-Output "Success"
            }}
        }}
        """

        result = subprocess.run(
            ["powershell", "-Command", powershell_script],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0 and "Success" in result.stdout:
            return True

    except Exception as e:
        logger.debug(f"[WindowsLauncher] UWPIniciandoExceção: {e}")

    return False
