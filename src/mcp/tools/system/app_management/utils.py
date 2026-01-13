"""aplicaçãoprograma.

deaplicaçãoprogramaCorrespondência、Pesquisare
"""

import platform
import re
import time
from typing import Any, Dict, List, Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# App
_cached_applications: Optional[List[Dict[str, Any]]] = None
_cache_timestamp: float = 0
_cache_duration = 300  # 5


class AppMatcher:
    """
    deaplicaçãoprogramaCorrespondênciaDispositivo.
    """

    # AppNome - Comprimento，NomeCorrespondência
    SPECIAL_MAPPINGS = {
        "qqMúsica": ["qqmusic", "qqMúsica", "qq music"],
        "qqmusic": ["qqmusic", "qqMúsica", "qq music"],
        "qq music": ["qqmusic", "qqMúsica", "qq music"],
        "tencent meeting": ["tencent meeting", "", "voovmeeting"],
        "": ["tencent meeting", "", "voovmeeting"],
        "google chrome": ["chrome", "googlechrome", "google chrome"],
        "microsoft edge": ["msedge", "edge", "microsoft edge"],
        "microsoft office": [
            "microsoft office",
            "office",
            "word",
            "excel",
            "powerpoint",
        ],
        "microsoft word": ["microsoft word", "word"],
        "microsoft excel": ["microsoft excel", "excel"],
        "microsoft powerpoint": ["microsoft powerpoint", "powerpoint"],
        "visual studio code": ["code", "vscode", "visual studio code"],
        "wps office": ["wps", "wps office"],
        "qq": ["qq", "qqnt", "tencentqq"],
        "wechat": ["wechat", "weixin", ""],
        "dingtalk": ["dingtalk", "", "ding"],
        "": ["dingtalk", "", "ding"],
        "chrome": ["chrome", "googlechrome", "google chrome"],
        "firefox": ["firefox", "mozilla"],
        "edge": ["msedge", "edge", "microsoft edge"],
        "safari": ["safari"],
        "notepad": ["notepad", "notepad++"],
        "calculator": ["calc", "calculator", "calculatorapp"],
        "calc": ["calc", "calculator", "calculatorapp"],
        "feishu": ["feishu", "", "lark"],
        "vscode": ["code", "vscode", "visual studio code"],
        "pycharm": ["pycharm", "pycharm64"],
        "cursor": ["cursor"],
        "typora": ["typora"],
        "wps": ["wps", "wps office"],
        "office": ["microsoft office", "office", "word", "excel", "powerpoint"],
        "word": ["microsoft word", "word"],
        "excel": ["microsoft excel", "excel"],
        "powerpoint": ["microsoft powerpoint", "powerpoint"],
        "finder": ["finder"],
        "terminal": ["terminal", "iterm"],
        "iterm": ["iterm", "iterm2"],
    }

    # Processo（Fechando）
    PROCESS_GROUPS = {
        "chrome": "chrome",
        "googlechrome": "chrome",
        "firefox": "firefox",
        "edge": "edge",
        "msedge": "edge",
        "safari": "safari",
        "qq": "qq",
        "qqnt": "qq",
        "tencentqq": "qq",
        "qqmusic": "qqmusic",
        "QQMUSIC": "QQMUSIC",
        "QQMúsica": "QQMúsica",
        "wechat": "wechat",
        "weixin": "wechat",
        "dingtalk": "dingtalk",
        "": "dingtalk",
        "feishu": "feishu",
        "": "feishu",
        "lark": "feishu",
        "vscode": "vscode",
        "code": "vscode",
        "cursor": "cursor",
        "pycharm": "pycharm",
        "pycharm64": "pycharm",
        "typora": "typora",
        "calculatorapp": "calculator",
        "calc": "calculator",
        "calculator": "calculator",
        "tencent meeting": "tencent_meeting",
        "": "tencent_meeting",
        "voovmeeting": "tencent_meeting",
        "wps": "wps",
        "word": "word",
        "excel": "excel",
        "powerpoint": "powerpoint",
        "finder": "finder",
        "terminal": "terminal",
        "iterm": "iterm",
        "iterm2": "iterm",
    }

    @classmethod
    def normalize_name(cls, name: str) -> str:
        """
        ConversãoaplicaçãoprogramaNome.
        """
        if not name:
            return ""

        # .exe
        name = name.lower().replace(".exe", "")

        # Versão  eCaracteres
        name = re.sub(r"\s+v?\d+[\.\d]*", "", name)
        name = re.sub(r"\s*\(\d+\)", "", name)
        name = re.sub(r"\s*\[.*?\]", "", name)
        name = " ".join(name.split())

        return name.strip()

    @classmethod
    def get_process_group(cls, process_name: str) -> str:
        """
        Processode.
        """
        normalized = cls.normalize_name(process_name)

        # Pesquisar
        if normalized in cls.PROCESS_GROUPS:
            return cls.PROCESS_GROUPS[normalized]

        # Pesquisar
        for key, group in cls.PROCESS_GROUPS.items():
            if key in normalized or normalized in key:
                return group

        return normalized

    @classmethod
    def match_application(cls, target_name: str, app_info: Dict[str, Any]) -> int:
        """Correspondênciaaplicaçãoprograma，RetornoCorrespondência  Pontuação.

        Args:
            target_name: AlvoaplicaçãoNome
            app_info: aplicaçãoprogramaInformação

        Returns:
            int: Correspondência  Pontuação (0-100)，0NãoCorrespondência
        """
        if not target_name or not app_info:
            return 0

        target_lower = target_name.lower()
        app_name = app_info.get("name", "").lower()
        display_name = app_info.get("display_name", "").lower()
        window_title = app_info.get("window_title", "").lower()
        exe_path = app_info.get("command", "").lower()

        # 1. Correspondência (100)
        if target_lower == app_name or target_lower == display_name:
            return 100

        # 2. Correspondência (95-98) - Correspondênciade
        best_special_score = 0

        for key in cls.SPECIAL_MAPPINGS:
            if key in target_lower or target_lower == key:
                # PesquisarCorrespondênciade
                for alias in cls.SPECIAL_MAPPINGS[key]:
                    if alias.lower() in app_name or alias.lower() in display_name:
                        # Correspondência：deCorrespondência
                        if target_lower == key:
                            score = 98  # Correspondência
                        elif len(key) > len(target_lower) * 0.8:
                            score = 97  # ComprimentodeCorrespondência
                        else:
                            score = 95  # Correspondência

                        if score > best_special_score:
                            best_special_score = score

        if best_special_score > 0:
            return best_special_score

        # 3. ConversãoNomeCorrespondência (90)
        normalized_target = cls.normalize_name(target_name)
        normalized_app = cls.normalize_name(app_info.get("name", ""))
        normalized_display = cls.normalize_name(app_info.get("display_name", ""))

        if (
            normalized_target == normalized_app
            or normalized_target == normalized_display
        ):
            return 90

        # 4. Correspondência (70-80)
        if target_lower in app_name:
            return 80
        if target_lower in display_name:
            return 75
        if app_name and app_name in target_lower:
            # Nome  Correspondência  Nome
            if len(app_name) < len(target_lower) * 0.5:
                return 50  # Pontuação
            return 70

        # 5. JanelaCorrespondência (60)
        if window_title and target_lower in window_title:
            return 60

        # 6. CaminhoCorrespondência (50)
        if exe_path and target_lower in exe_path:
            return 50

        # 7. Correspondência (30)
        if cls._fuzzy_match(target_lower, app_name) or cls._fuzzy_match(
            target_lower, display_name
        ):
            return 30

        return 0

    @classmethod
    def _fuzzy_match(cls, target: str, candidate: str) -> bool:
        """
        Correspondência.
        """
        if not target or not candidate:
            return False

        # Caracteres
        target_clean = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]", "", target)
        candidate_clean = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]", "", candidate)

        return target_clean in candidate_clean or candidate_clean in target_clean


async def get_cached_applications(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """deaplicaçãoprograma.

    Args:
        force_refresh: Forçar

    Returns:
        aplicaçãoprograma
    """
    global _cached_applications, _cache_timestamp

    current_time = time.time()

    # Pesquisar
    if (
        not force_refresh
        and _cached_applications is not None
        and (current_time - _cache_timestamp) < _cache_duration
    ):
        logger.debug(
            f"[AppUtils] UsandodeAplicação，Tempo: {int(current_time - _cache_timestamp)}Segundos")
        return _cached_applications

    # NovamenteAplicação
    try:
        import json

        from .scanner import scan_installed_applications

        logger.info("[AppUtils] Aplicação")
        result_json = await scan_installed_applications(
            {"force_refresh": force_refresh}
        )
        result = json.loads(result_json)

        if result.get("success", False):
            _cached_applications = result.get("applications", [])
            _cache_timestamp = current_time
            logger.info(
                f"[AppUtils] AplicaçãoJá，Encontrado {len(_cached_applications)} App")
            return _cached_applications
        else:
            logger.warning(
                f"[AppUtils] AplicaçãoFalha: {result.get('message', 'Não  Erro')}")
            return _cached_applications or []

    except Exception as e:
        logger.error(f"[AppUtils] AplicaçãoFalha: {e}")
        return _cached_applications or []


async def find_best_matching_app(
    app_name: str, app_type: str = "any"
) -> Optional[Dict[str, Any]]:
    """PesquisarCorrespondênciadeaplicaçãoprograma.

    Args:
        app_name: aplicaçãoprogramaNome
        app_type: aplicaçãoprogramaTipo ("installed", "running", "any")

    Returns:
        CorrespondênciadeaplicaçãoprogramaInformação
    """
    try:
        if app_type == "running":
            # EmdeAplicação
            import json

            from .scanner import list_running_applications

            result_json = await list_running_applications({})
            result = json.loads(result_json)

            if not result.get("success", False):
                return None

            applications = result.get("applications", [])
        else:
            # JádeAplicação
            applications = await get_cached_applications()

        if not applications:
            return None

        # AppdeCorrespondência
        matches = []
        for app in applications:
            score = AppMatcher.match_application(app_name, app)
            if score > 0:
                matches.append((score, app))

        if not matches:
            return None

        # Pontuação，RetornoCorrespondência
        matches.sort(key=lambda x: x[0], reverse=True)
        best_score, best_app = matches[0]

        logger.info(
            f"[AppUtils] EncontradoCorrespondência: {best_app.get('display_name', best_app.get('name', ''))} (Pontuação: {best_score})")
        return best_app

    except Exception as e:
        logger.error(f"[AppUtils] PesquisarCorrespondênciaAppFalha: {e}")
        return None


def clear_app_cache():
    """
    Limpandoaplicaçãoprograma.
    """
    global _cached_applications, _cache_timestamp

    _cached_applications = None
    _cache_timestamp = 0
    logger.info("[AppUtils] AplicaçãoJáLimpando")


def get_cache_info() -> Dict[str, Any]:
    """
    Informação.
    """

    current_time = time.time()
    cache_age = current_time - _cache_timestamp if _cache_timestamp > 0 else -1

    return {
        "cached": _cached_applications is not None,
        "count": len(_cached_applications) if _cached_applications else 0,
        "age_seconds": int(cache_age) if cache_age >= 0 else None,
        "valid": cache_age >= 0 and cache_age < _cache_duration,
        "cache_duration": _cache_duration,
    }


def get_system_scanner():
    """sistemadeDispositivo.

    Returns:
        sistemadeDispositivo
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        from .mac import scanner

        return scanner
    elif system == "Windows":  # Windows
        from .windows import scanner

        return scanner
    elif system == "Linux":  # Linux
        from .linux import scanner

        return scanner
    else:
        logger.warning(f"[AppUtils] NãoSuportadode: {system}")
        return None
