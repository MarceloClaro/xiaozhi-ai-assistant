# 
from enum import Enum


class InitializationStage(Enum):
    """
    Inicializando.
    """

    DEVICE_FINGERPRINT = "：Dispositivo"
    CONFIG_MANAGEMENT = "：Inicializando"
    OTA_CONFIG = "：OTA"
    ACTIVATION = "："


class SystemConstants:
    """
    sistema.
    """

    # AppInformação
    APP_NAME = "py-xiaozhi"
    APP_VERSION = "2.0.0"
    BOARD_TYPE = "bread-compact-wifi"

    # TimeoutConfigurando
    DEFAULT_TIMEOUT = 10
    ACTIVATION_MAX_RETRIES = 60
    ACTIVATION_RETRY_INTERVAL = 5

    # Arquivo
    CONFIG_FILE = "config.json"
    EFUSE_FILE = "efuse.json"
