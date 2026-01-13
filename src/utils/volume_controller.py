import platform
import re
import shutil
import subprocess
from functools import wraps
from typing import Any, Callable, List, Optional

from src.utils.logging_config import get_logger


class VolumeController:
    """
    Dispositivo.
    """

    # 
    DEFAULT_VOLUME = 70

    # de
    PLATFORM_INIT = {
        "Windows": "_init_windows",
        "Darwin": "_init_macos",
        "Linux": "_init_linux",
    }

    VOLUME_METHODS = {
        "Windows": ("_get_windows_volume", "_set_windows_volume"),
        "Darwin": ("_get_macos_volume", "_set_macos_volume"),
        "Linux": ("_get_linux_volume", "_set_linux_volume"),
    }

    LINUX_VOLUME_METHODS = {
        "pactl": ("_get_pactl_volume", "_set_pactl_volume"),
        "wpctl": ("_get_wpctl_volume", "_set_wpctl_volume"),
        "amixer": ("_get_amixer_volume", "_set_amixer_volume"),
    }

    # de
    PLATFORM_MODULES = {
        "Windows": {
            "pycaw": "pycaw.pycaw",
            "comtypes": "comtypes",
            "ctypes": "ctypes",
        },
        "Darwin": {
            "applescript": "applescript",
        },
        "Linux": {},
    }

    def __init__(self):
        """
        InicializandoDispositivo.
        """
        self.logger = get_logger("VolumeController")
        self.system = platform.system()
        self.is_arm = platform.machine().startswith(("arm", "aarch"))
        self.linux_tool = None
        self._module_cache = {}  # 

        # InicializandodeDispositivo
        init_method_name = self.PLATFORM_INIT.get(self.system)
        if init_method_name:
            init_method = getattr(self, init_method_name)
            init_method()
        else:
            self.logger.warning(f"NãoSuportadodeOperação: {self.system}")
            raise NotImplementedError(f"NãoSuportadodeOperação: {self.system}")

    def _lazy_import(self, module_name: str, attr: str = None) -> Any:
        """Carregando，Suportadoe.

        Args:
            module_name: Nome
            attr: ，Emde

        Returns:
            deou
        """
        if module_name in self._module_cache:
            module = self._module_cache[module_name]
        else:
            try:
                module = __import__(
                    module_name, fromlist=["*"] if "." in module_name else []
                )
                self._module_cache[module_name] = module
            except ImportError as e:
                self.logger.warning(f" {module_name} Falha: {e}")
                raise

        if attr:
            return getattr(module, attr)
        return module

    def _safe_execute(self, func_name: str, default_return: Any = None) -> Callable:
        """
        deDispositivo.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.logger.warning(f"{func_name}Falha: {e}")
                    return default_return

            return wrapper

        return decorator

    def _run_command(
        self, cmd: List[str], check: bool = False
    ) -> Optional[subprocess.CompletedProcess]:
        """
        Comando.
        """
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=check)
        except Exception as e:
            self.logger.debug(f"ComandoFalha {' '.join(cmd)}: {e}")
            return None

    def _init_windows(self) -> None:
        """
        InicializandoWindows.
        """
        try:
            # Usando
            POINTER = self._lazy_import("ctypes", "POINTER")
            cast = self._lazy_import("ctypes", "cast")
            CLSCTX_ALL = self._lazy_import("comtypes", "CLSCTX_ALL")
            AudioUtilities = self._lazy_import("pycaw.pycaw", "AudioUtilities")
            IAudioEndpointVolume = self._lazy_import(
                "pycaw.pycaw", "IAudioEndpointVolume"
            )

            self.devices = AudioUtilities.GetSpeakers()
            interface = self.devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            self.volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            self.logger.debug("WindowsInicializandoSucesso")
        except Exception as e:
            self.logger.error(f"WindowsInicializandoFalha: {e}")
            raise

    def _init_macos(self) -> None:
        """
        InicializandomacOS.
        """
        try:
            applescript = self._lazy_import("applescript")

            # 
            result = applescript.run("get volume settings")
            if not result or result.code != 0:
                raise Exception("Incapaz demacOS")
            self.logger.debug("macOSInicializandoSucesso")
        except Exception as e:
            self.logger.error(f"macOSInicializandoFalha: {e}")
            raise

    def _init_linux(self) -> None:
        """
        InicializandoLinux.
        """
        # Pesquisar
        linux_tools = ["pactl", "wpctl", "amixer"]
        for tool in linux_tools:
            if shutil.which(tool):
                self.linux_tool = tool
                break

        if not self.linux_tool:
            self.logger.error(
                "Nenhuma ferramenta de controle de volume Linux disponível (pactl/wpctl/amixer)"
            )
            raise Exception("Nenhuma ferramenta de controle de volume Linux disponível")

        self.logger.debug(
            f"Inicialização de controle de volume Linux bem-sucedida, Usando: {self.linux_tool}"
        )

    def get_volume(self) -> int:
        """
         (0-100)
        """
        get_method_name, _ = self.VOLUME_METHODS.get(self.system, (None, None))
        if not get_method_name:
            return self.DEFAULT_VOLUME

        get_method = getattr(self, get_method_name)
        return get_method()

    def set_volume(self, volume: int) -> None:
        """
        Configurando (0-100)
        """
        # Em
        volume = max(0, min(100, volume))

        _, set_method_name = self.VOLUME_METHODS.get(self.system, (None, None))
        if set_method_name:
            set_method = getattr(self, set_method_name)
            set_method(volume)

    @property
    def _get_windows_volume(self) -> Callable[[], int]:
        @self._safe_execute("Windows", self.DEFAULT_VOLUME)
        def get_volume():
            volume_scalar = self.volume_control.GetMasterVolumeLevelScalar()
            return int(volume_scalar * 100)

        return get_volume

    @property
    def _set_windows_volume(self) -> Callable[[int], None]:
        @self._safe_execute("ConfigurandoWindows")
        def set_volume(volume):
            self.volume_control.SetMasterVolumeLevelScalar(volume / 100.0, None)

        return set_volume

    @property
    def _get_macos_volume(self) -> Callable[[], int]:
        @self._safe_execute("macOS", self.DEFAULT_VOLUME)
        def get_volume():
            applescript = self._lazy_import("applescript")
            result = applescript.run("output volume of (get volume settings)")
            if result and result.out:
                return int(result.out.strip())
            return self.DEFAULT_VOLUME

        return get_volume

    @property
    def _set_macos_volume(self) -> Callable[[int], None]:
        @self._safe_execute("ConfigurandomacOS")
        def set_volume(volume):
            applescript = self._lazy_import("applescript")
            applescript.run(f"set volume output volume {volume}")

        return set_volume

    def _get_linux_volume(self) -> int:
        """
        Linux.
        """
        get_method_name, _ = self.LINUX_VOLUME_METHODS.get(
            self.linux_tool, (None, None)
        )
        if not get_method_name:
            return self.DEFAULT_VOLUME

        get_method = getattr(self, get_method_name)
        return get_method()

    def _set_linux_volume(self, volume: int) -> None:
        """
        ConfigurandoLinux.
        """
        _, set_method_name = self.LINUX_VOLUME_METHODS.get(
            self.linux_tool, (None, None)
        )
        if set_method_name:
            set_method = getattr(self, set_method_name)
            set_method(volume)

    @property
    def _get_pactl_volume(self) -> Callable[[], int]:
        @self._safe_execute("Através depactl", self.DEFAULT_VOLUME)
        def get_volume():
            result = self._run_command(["pactl", "list", "sinks"])
            if result and result.returncode == 0:
                # SuportadoFormato:
                # 1. Volume: front-left: 65535 / 65% / -10.77 dB
                # 2. Volume: 65%
                # UsandodeCorrespondência  então
                for line in result.stdout.split("\n"):
                    if "Volume:" in line:
                        # ，
                        match = re.search(r"(\d+)%", line)
                        if match:
                            volume = int(match.group(1))
                            self.logger.debug(f"pactlSucesso: {volume}%")
                            return volume
                self.logger.warning("pactlSaídaEmNãoEncontradoInformação")
            else:
                self.logger.warning(
                    f"pactlComandoFalha: {result.returncode if result else 'None'}"
                )
            return self.DEFAULT_VOLUME

        return get_volume

    @property
    def _set_pactl_volume(self) -> Callable[[int], None]:
        @self._safe_execute("Através depactlConfigurando")
        def set_volume(volume):
            result = self._run_command(
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume}%"]
            )
            if result and result.returncode == 0:
                self.logger.debug(f"pactl Configurando volume Sucesso: {volume}%")
            else:
                self.logger.warning(
                    f"pactl Configurando volume Falha: {result.returncode if result else 'None'}"
                )

        return set_volume

    @property
    def _get_wpctl_volume(self) -> Callable[[], int]:
        @self._safe_execute("Através dewpctl", self.DEFAULT_VOLUME)
        def get_volume():
            result = self._run_command(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
            if result and result.returncode == 0:
                # SuportadoSaídaFormato: "Volume: 0.65", "0.65", "Volume: 0.65 [MUTED]"
                match = re.search(r"(\d+\.?\d*)", result.stdout)
                if match:
                    volume = int(float(match.group(1)) * 100)
                    self.logger.debug(f"wpctlSucesso: {volume}%")
                    return volume
                else:
                    self.logger.warning(
                        f"wpctlSaídaFormatoIncapaz deAnalisando: {result.stdout}"
                    )
            else:
                self.logger.warning(
                    f"wpctlComandoFalha: {result.returncode if result else 'None'}"
                )
            return self.DEFAULT_VOLUME

        return get_volume

    @property
    def _set_wpctl_volume(self) -> Callable[[int], None]:
        @self._safe_execute("Através dewpctlConfigurando")
        def set_volume(volume):
            result = self._run_command(
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{volume / 100.0:.2f}"]
            )
            if result and result.returncode == 0:
                self.logger.debug(f"wpctl Configurando volume Sucesso: {volume}%")
            else:
                self.logger.warning(
                    f"wpctl Configurando volume Falha: {result.returncode if result else 'None'}"
                )

        return set_volume

    @property
    def _get_amixer_volume(self) -> Callable[[], int]:
        @self._safe_execute("Obtendo volume através de amixer", self.DEFAULT_VOLUME)
        def get_volume():
            result = self._run_command(["amixer", "get", "Master"])
            if result and result.returncode == 0:
                # SuportadoFormato:
                # 1. Mono: Playback 65 [65%] [-10.77dB] [on]
                # 2. Front Left: Playback 65 [65%] [-10.77dB] [on]
                # Valor
                match = re.search(r"\[(\d+)%\]", result.stdout)
                if match:
                    volume = int(match.group(1))
                    self.logger.debug(f"amixerSucesso: {volume}%")
                    return volume
                else:
                    self.logger.warning(
                        f"amixerSaídaFormatoIncapaz deAnalisando: {result.stdout}"
                    )
            else:
                self.logger.warning(
                    f"amixerComandoFalha: {result.returncode if result else 'None'}"
                )
            return self.DEFAULT_VOLUME

        return get_volume

    @property
    def _set_amixer_volume(self) -> Callable[[int], None]:
        @self._safe_execute("Através deamixerConfigurando")
        def set_volume(volume):
            result = self._run_command(["amixer", "sset", "Master", f"{volume}%"])
            if result and result.returncode == 0:
                self.logger.debug(f"amixerConfigurandoSucesso: {volume}%")
            else:
                self.logger.warning(
                    f"amixer Configurando volume Falha: {result.returncode if result else 'None'}"
                )

        return set_volume

    @staticmethod
    def check_dependencies() -> bool:
        """
        Verificar e reportar dependências ausentes.
        """
        system = platform.system()
        missing = []

        # PesquisarPython
        VolumeController._check_python_modules(system, missing)

        # PesquisarLinux
        if system == "Linux":
            VolumeController._check_linux_tools(missing)

        # de
        return VolumeController._report_missing_dependencies(system, missing)

    @staticmethod
    def _check_python_modules(system: str, missing: List[str]) -> None:
        """
        PesquisarPython.
        """
        if system == "Windows":
            for module in ["pycaw", "comtypes"]:
                try:
                    __import__(module)
                except ImportError:
                    missing.append(module)
        elif system == "Darwin":  # macOS
            try:
                __import__("applescript")
            except ImportError:
                missing.append("applescript")

    @staticmethod
    def _check_linux_tools(missing: List[str]) -> None:
        """
        PesquisarLinux.
        """
        tools = ["pactl", "wpctl", "amixer"]
        found = any(shutil.which(tool) for tool in tools)
        if not found:
            missing.append("pulseaudio-utils、wireplumber ou alsa-utils")

    @staticmethod
    def _report_missing_dependencies(system: str, missing: List[str]) -> bool:
        """
        de.
        """
        if missing:
            print(f"Aviso: ，NãoEncontrado: {', '.join(missing)}")
            print("UsandoComandode:")
            if system in ["Windows", "Darwin"]:
                print("pip install " + " ".join(missing))
            elif system == "Linux":
                print("sudo apt-get install " + " ".join(missing))
            return False
        return True
