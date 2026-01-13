import json
import uuid
from typing import Any, Dict

from src.utils.logging_config import get_logger
from src.utils.resource_finder import resource_finder

logger = get_logger(__name__)


class ConfigManager:
    """configuraçãoDispositivo - modo"""

    _instance = None

    # 
    DEFAULT_CONFIG = {
        "SYSTEM_OPTIONS": {
            "CLIENT_ID": None,
            "DEVICE_ID": None,
            "NETWORK": {
                "OTA_VERSION_URL": "https://api.tenclass.net/xiaozhi/ota/",
                "WEBSOCKET_URL": None,
                "WEBSOCKET_ACCESS_TOKEN": None,
                "MQTT_INFO": None,
                "ACTIVATION_VERSION": "v2",  # Valor: v1, v2
                "AUTHORIZATION_URL": "https://xiaozhi.me/",
            },
        },
        "WAKE_WORD_OPTIONS": {
            "USE_WAKE_WORD": True,
            "MODEL_PATH": "models",
            "NUM_THREADS": 4,
            "PROVIDER": "cpu",
            "MAX_ACTIVE_PATHS": 2,
            "KEYWORDS_SCORE": 1.8,
            "KEYWORDS_THRESHOLD": 0.2,
            "NUM_TRAILING_BLANKS": 1,
        },
        "CAMERA": {
            "camera_index": 0,
            "frame_width": 640,
            "frame_height": 480,
            "fps": 30,
            "Local_VL_url": "https://open.bigmodel.cn/api/paas/v4/",
            "VLapi_key": "",
            "models": "glm-4v-plus",
        },
        "SHORTCUTS": {
            "ENABLED": True,
            "MANUAL_PRESS": {"modifier": "ctrl", "key": "j", "description": ""},
            "AUTO_TOGGLE": {"modifier": "ctrl", "key": "k", "description": "Automático"},
            "ABORT": {"modifier": "ctrl", "key": "q", "description": "Em"},
            "MODE_TOGGLE": {"modifier": "ctrl", "key": "m", "description": "Modo"},
            "WINDOW_TOGGLE": {
                "modifier": "ctrl",
                "key": "w",
                "description": "/Janela",
            },
        },
        "AEC_OPTIONS": {
            "ENABLED": False,
            "BUFFER_MAX_LENGTH": 200,
            "FRAME_DELAY": 3,
            "FILTER_LENGTH_RATIO": 0.4,
            "ENABLE_PREPROCESS": True,
        },
        "AUDIO_DEVICES": {
            "input_device_id": None,
            "input_device_name": None,
            "output_device_id": None,
            "output_device_name": None,
            "input_sample_rate": None,
            "output_sample_rate": None,
            "input_channels": None,
            "output_channels": None,
        },
    }

    def __new__(cls):
        """
        modo.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        InicializandoconfiguraçãoDispositivo.
        """
        if self._initialized:
            return
        self._initialized = True

        # InicializandoArquivoCaminho
        self._init_config_paths()

        # deDiretórioExiste
        self._ensure_required_directories()

        # 
        self._config = self._load_config()

    def _init_config_paths(self):
        """
        InicializandoconfiguraçãoarquivoCaminho.
        """
        # Usandoresource_finderPesquisarouDiretório
        self.config_dir = resource_finder.find_config_dir()
        if not self.config_dir:
            # Se  NãoparaDiretório，EmDiretório
            project_root = resource_finder.get_project_root()
            self.config_dir = project_root / "config"
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório: {self.config_dir.absolute()}")

        self.config_file = self.config_dir / "config.json"

        # ArquivoCaminho
        logger.info(f"Diretório: {self.config_dir.absolute()}")
        logger.info(f"Arquivo: {self.config_file.absolute()}")

    def _ensure_required_directories(self):
        """
        deDiretórioExiste.
        """
        project_root = resource_finder.get_project_root()

        #  models Diretório
        models_dir = project_root / "models"
        if not models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"ModeloDiretório: {models_dir.absolute()}")

        #  cache Diretório
        cache_dir = project_root / "cache"
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório: {cache_dir.absolute()}")

    def _load_config(self) -> Dict[str, Any]:
        """
        Carregandoconfiguraçãoarquivo，SeNãoExisteentãoCriando.
        """
        try:
            # TentativaUsandoresource_finderPesquisarArquivo
            config_file_path = resource_finder.find_file("config/config.json")

            if config_file_path:
                logger.debug(f"Usandoresource_finderEncontradoArquivo: {config_file_path}")
                config = json.loads(config_file_path.read_text(encoding="utf-8"))
                return self._merge_configs(self.DEFAULT_CONFIG, config)

            # Seresource_finder  Encontrado，TentativaUsandoEmdeCaminho
            if self.config_file.exists():
                logger.debug(f"UsandoCaminhoEncontradoArquivo: {self.config_file}")
                config = json.loads(self.config_file.read_text(encoding="utf-8"))
                return self._merge_configs(self.DEFAULT_CONFIG, config)
            else:
                # Arquivo
                logger.info("ArquivoNãoExiste，")
                self._save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG.copy()

        except Exception as e:
            logger.error(f"Erro: {e}")
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: dict) -> bool:
        """
        Salvandoconfiguraçãoparaarquivo.
        """
        try:
            # DiretórioExiste
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Arquivo
            self.config_file.write_text(
                json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.debug(f"Jápara: {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"Erro: {e}")
            return False

    @staticmethod
    def _merge_configs(default: dict, custom: dict) -> dict:
        """
        configuração.
        """
        result = default.copy()
        for key, value in custom.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get_config(self, path: str, default: Any = None) -> Any:
        """
        Através deCaminhoconfiguraçãoValor
        path: deconfiguraçãoCaminho， "SYSTEM_OPTIONS.NETWORK.MQTT_INFO"
        """
        try:
            value = self._config
            for key in path.split("."):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def update_config(self, path: str, value: Any) -> bool:
        """
        configuração
        path: deconfiguraçãoCaminho， "SYSTEM_OPTIONS.NETWORK.MQTT_INFO"
        """
        try:
            current = self._config
            *parts, last = path.split(".")
            for part in parts:
                current = current.setdefault(part, {})
            current[last] = value
            return self._save_config(self._config)
        except Exception as e:
            logger.error(f"Erro {path}: {e}")
            return False

    def reload_config(self) -> bool:
        """
        NovamenteCarregandoconfiguraçãoarquivo.
        """
        try:
            self._config = self._load_config()
            logger.info("ArquivoJáNovamente")
            return True
        except Exception as e:
            logger.error(f"NovamenteFalha: {e}")
            return False

    def generate_uuid(self) -> str:
        """
         UUID v4.
        """
        return str(uuid.uuid4())

    def initialize_client_id(self):
        """
        SalvandoEmclienteID.
        """
        if not self.get_config("SYSTEM_OPTIONS.CLIENT_ID"):
            client_id = self.generate_uuid()
            success = self.update_config("SYSTEM_OPTIONS.CLIENT_ID", client_id)
            if success:
                logger.info(f"JádeID: {client_id}")
            else:
                logger.error("deIDFalha")

    def initialize_device_id_from_fingerprint(self, device_fingerprint):
        """
        dedispositivoInicializandodispositivoID.
        """
        if not self.get_config("SYSTEM_OPTIONS.DEVICE_ID"):
            try:
                # deefuse.jsonMACparaDEVICE_ID
                mac_address = device_fingerprint.get_mac_address_from_efuse()
                if mac_address:
                    success = self.update_config(
                        "SYSTEM_OPTIONS.DEVICE_ID", mac_address
                    )
                    if success:
                        logger.info(f"deefuse.jsonDEVICE_ID: {mac_address}")
                    else:
                        logger.error("DEVICE_IDFalha")
                else:
                    logger.error("Incapaz dedeefuse.jsonMAC")
                    # ：deDispositivo
                    fingerprint = device_fingerprint.generate_fingerprint()
                    mac_from_fingerprint = fingerprint.get("mac_address")
                    if mac_from_fingerprint:
                        success = self.update_config(
                            "SYSTEM_OPTIONS.DEVICE_ID", mac_from_fingerprint
                        )
                        if success:
                            logger.info(
                                f"Usando endereço MAC do fingerprint como DEVICE_ID: "
                                f"{mac_from_fingerprint}"
                            )
                        else:
                            logger.error("DEVICE_IDFalha")
            except Exception as e:
                logger.error(f"InicializandoDEVICE_ID: {e}")

    @classmethod
    def get_instance(cls):
        """
        configuraçãoDispositivo.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
