# Em opuslib Processando opus Banco de dados
import ctypes
import os
import platform
import shutil
import sys
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Union, cast

# LogDispositivo
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


# 
class PLATFORM(Enum):
    WINDOWS = "windows"
    MACOS = "darwin"
    LINUX = "linux"


# 
class ARCH(Enum):
    WINDOWS = {"arm": "x64", "intel": "x64"}
    MACOS = {"arm": "arm64", "intel": "x64"}
    LINUX = {"arm": "arm64", "intel": "x64"}


# Banco de dadosCaminho
class LIB_PATH(Enum):
    WINDOWS = "libs/libopus/win/x64"
    MACOS = "libs/libopus/mac/{arch}"
    LINUX = "libs/libopus/linux/{arch}"


# Banco de dadosNome
class LIB_INFO(Enum):
    WINDOWS = {"name": "opus.dll", "system_name": ["opus"]}
    MACOS = {"name": "libopus.dylib", "system_name": ["libopus.dylib"]}
    LINUX = {"name": "libopus.so", "system_name": ["libopus.so.0", "libopus.so"]}


def get_platform() -> str:
    system = platform.system().lower()
    if system == "windows" or system.startswith("win"):
        system = PLATFORM.WINDOWS
    elif system == "darwin":
        system = PLATFORM.MACOS
    else:
        system = PLATFORM.LINUX
    return system


def get_arch(system: PLATFORM) -> str:
    architecture = platform.machine().lower()
    is_arm = "arm" in architecture or "aarch64" in architecture
    if system == PLATFORM.WINDOWS:
        arch_name = ARCH.WINDOWS.value["arm" if is_arm else "intel"]
    elif system == PLATFORM.MACOS:
        arch_name = ARCH.MACOS.value["arm" if is_arm else "intel"]
    else:
        arch_name = ARCH.LINUX.value["arm" if is_arm else "intel"]
    return architecture, arch_name


def get_lib_path(system: PLATFORM, arch_name: str):
    if system == PLATFORM.WINDOWS:
        lib_name = LIB_PATH.WINDOWS.value
    elif system == PLATFORM.MACOS:
        lib_name = LIB_PATH.MACOS.value.format(arch=arch_name)
    else:
        lib_name = LIB_PATH.LINUX.value.format(arch=arch_name)
    return lib_name


def get_lib_name(system: PLATFORM, local: bool = True) -> Union[str, List[str]]:
    """Banco de dadosNome.

    Args:
        system (PLATFORM): 
        local (bool, optional): Nome(str), para True. Separa False, entãosistemaNome(List).

    Returns:
        str | List: Banco de dadosNome
    """
    key = "name" if local else "system_name"
    if system == PLATFORM.WINDOWS:
        lib_name = LIB_INFO.WINDOWS.value[key]
    elif system == PLATFORM.MACOS:
        lib_name = LIB_INFO.MACOS.value[key]
    else:
        lib_name = LIB_INFO.LINUX.value[key]
    return lib_name


def get_system_info() -> Tuple[str, str]:
    """
    sistemaInformação.
    """
    # ConversãoNome
    system = get_platform()

    # ConversãoNome
    _, arch_name = get_arch(system)
    logger.info(f"para: {system}, : {arch_name}")

    return system, arch_name


def get_search_paths(system: PLATFORM, arch_name: str) -> List[Tuple[Path, str]]:
    """
    Banco de dadosarquivoPesquisaCaminho（Usandode  FontePesquisarDispositivo）
    """
    from .resource_finder import find_libs_dir, get_project_root

    lib_name = cast(str, get_lib_name(system))

    search_paths: List[Tuple[Path, str]] = []

    # NomeparaDiretórioNome
    system_dir_map = {
        PLATFORM.WINDOWS: "win",
        PLATFORM.MACOS: "mac",
        PLATFORM.LINUX: "linux",
    }

    system_dir = system_dir_map.get(system)

    # TentativaPesquisaredelibsDiretório
    if system_dir:
        specific_libs_dir = find_libs_dir(f"libopus/{system_dir}", arch_name)
        if specific_libs_dir:
            search_paths.append((specific_libs_dir, lib_name))
            logger.debug(f"EncontradolibsDiretório: {specific_libs_dir}")

    # PesquisardelibsDiretório
    if system_dir:
        platform_libs_dir = find_libs_dir(f"libopus/{system_dir}")
        if platform_libs_dir:
            search_paths.append((platform_libs_dir, lib_name))
            logger.debug(f"EncontradolibsDiretório: {platform_libs_dir}")

    # PesquisarlibsDiretório
    general_libs_dir = find_libs_dir()
    if general_libs_dir:
        search_paths.append((general_libs_dir, lib_name))
        logger.debug(f"libsDiretório: {general_libs_dir}")

    # Diretório  parade
    project_root = get_project_root()
    search_paths.append((project_root, lib_name))

    # Imprimir todos os caminhos de pesquisa, ajudar Debug
    for dir_path, filename in search_paths:
        full_path = dir_path / filename
        logger.debug(f"Pesquisa de Caminho: {full_path} (Existe: {full_path.exists()})")
    return search_paths


def find_system_opus() -> str:
    """
    desistemaCaminhoPesquisaropusBanco de dados.
    """
    system, _ = get_system_info()
    lib_path = ""

    try:
        # opus Banco de dados deNome
        lib_names = cast(List[str], get_lib_name(system, False))

        # TentativadeNome
        for lib_name in lib_names:
            try:
                # ctypes.util  Usandofind_library
                import ctypes.util

                system_lib_path = ctypes.util.find_library(lib_name)

                if system_lib_path:
                    lib_path = system_lib_path
                    logger.info(f"EmCaminhoEmEncontradoopusBanco de dados: {lib_path}")
                    break
                else:
                    # TentativaBanco de dados
                    ctypes.cdll.LoadLibrary(lib_name)
                    lib_path = lib_name
                    logger.info(f"opusBanco de dados: {lib_name}")
                    break
            except Exception as e:
                logger.debug(f"Banco de dados {lib_name} Falha: {e}")
                continue

    except Exception as e:
        logger.error(f"Pesquisaropus Banco de dados Falha: {e}")

    return lib_path


def copy_opus_to_project(system_lib_path):
    """
    sistemaBanco de dadosparaDiretório.
    """
    from .resource_finder import get_project_root

    system, arch_name = get_system_info()

    if not system_lib_path:
        logger.error("Incapaz deopusBanco de dados：Banco de dadosCaminhopara")
        return None

    try:
        # Usandoresource_finderDiretório
        project_root = get_project_root()

        # AlvoDiretórioCaminho - UsandoDiretório
        target_path = get_lib_path(system, arch_name)
        target_dir = project_root / target_path

        # AlvoDiretório(SeNãoExiste)
        target_dir.mkdir(parents=True, exist_ok=True)

        # AlvoArquivo
        lib_name = cast(str, get_lib_name(system))
        target_file = target_dir / lib_name

        # Arquivo
        shutil.copy2(system_lib_path, target_file)
        logger.info(f"Jáopus Banco de dados de {system_lib_path} para {target_file}")

        return str(target_file)

    except Exception as e:
        logger.error(f"opus Banco de dados paraDiretórioFalha: {e}")
        return None


def setup_opus() -> bool:
    """
    ConfigurandoopusBanco de dados.
    """
    # PesquisarJáruntime_hook
    if hasattr(sys, "_opus_loaded"):
        logger.info("opus Banco de dados Já")
        return True

    # Informação
    system, arch_name = get_system_info()
    logger.info(f": {system}, : {arch_name}")

    # PesquisaCaminho
    search_paths = get_search_paths(system, arch_name)

    # PesquisarBanco de dadosArquivo
    lib_path = ""
    lib_dir = ""

    for dir_path, file_name in search_paths:
        full_path = dir_path / file_name
        if full_path.exists():
            lib_path = str(full_path)
            lib_dir = str(dir_path)
            logger.info(f"Encontradoopus Banco de dados Arquivo: {lib_path}")
            break

    # SeEncontrado，TentativadePesquisar
    if not lib_path:
        logger.warning("NãoEncontradoopus Banco de dados Arquivo，TentativadeCaminho")
        system_lib_path = find_system_opus()

        if system_lib_path:
            # VezesTentativaUsandoBanco de dados
            try:
                _ = ctypes.cdll.LoadLibrary(system_lib_path)
                logger.info(f"JádeCaminhoopusBanco de dados: {system_lib_path}")
                sys._opus_loaded = True
                return True
            except Exception as e:
                logger.warning(
                    f"opus Banco de dados Falha: {e}，TentativaparaDiretório"
                )

            # SeFalha，TentativaparaDiretório
            lib_path = copy_opus_to_project(system_lib_path)
            if lib_path:
                lib_dir = str(Path(lib_path).parent)
            else:
                logger.error("Incapaz deEncontradoouopus Banco de dados Arquivo")
                return False
        else:
            logger.error("EmEm  NãoEncontradoopus Banco de dados Arquivo")
            return False

    # WindowsProcessando
    if system == PLATFORM.WINDOWS and lib_dir:
        # DLLPesquisaCaminho
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(lib_dir)
                logger.debug(f"JáDLLPesquisaCaminho: {lib_dir}")
            except Exception as e:
                logger.warning(f"DLLPesquisaCaminhoFalha: {e}")

        # Configurando
        os.environ["PATH"] = lib_dir + os.pathsep + os.environ.get("PATH", "")

    # Banco de dadosCaminho
    _patch_find_library("opus", lib_path)

    # TentativaBanco de dados
    try:
        # DLL
        _ = ctypes.CDLL(lib_path)
        logger.info(f"SucessoopusBanco de dados: {lib_path}")
        sys._opus_loaded = True
        return True
    except Exception as e:
        logger.error(f"opus Banco de dados Falha: {e}")
        return False


def _patch_find_library(lib_name: str, lib_path: str):
    """
    ctypes.util.find_library.
    """
    import ctypes.util

    original_find_library = ctypes.util.find_library

    def patched_find_library(name):
        if name == lib_name:
            return lib_path
        return original_find_library(name)

    ctypes.util.find_library = patched_find_library
