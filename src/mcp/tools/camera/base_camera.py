"""
Base camera implementation.
"""

import threading
from abc import ABC, abstractmethod
from typing import Dict

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class BaseCamera(ABC):
    """
    ，.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        """
        Inicializando.
        """
        self.jpeg_data = {
            "buf": b"",
            "len": 0,
        }  # deJPEGBytesDados  # BytesDadosComprimento

        # Carregando configuração de câmera
        config = ConfigManager.get_instance()
        self.camera_index = config.get_config("CAMERA_OPTIONS.INDEX", 0)
        self.frame_width = config.get_config("CAMERA_OPTIONS.FRAME_WIDTH", 640)
        self.frame_height = config.get_config("CAMERA_OPTIONS.FRAME_HEIGHT", 480)
        self.fps = config.get_config("CAMERA_OPTIONS.FPS", 30)
        
        logger.info(f"Camera configuration: index={self.camera_index}, {self.frame_width}x{self.frame_height}, {self.fps}fps")
        
        # Configurações de visão
        self.explain_url = ""
        self.explain_token = ""

    def set_explain_url(self, url: str):
        """
        Configurando URL do serviço de visão.
        """
        self.explain_url = url
        logger.info(f"Vision service URL set to: {url}")

    def set_explain_token(self, token: str):
        """
        Configurando token do serviço de visão.
        """
        self.explain_token = token
        if token:
            logger.info("Vision service token has been set")

    @abstractmethod
    def capture(self) -> bool:
        """
        Capturandoimagem.
        """

    @abstractmethod
    def analyze(self, question: str, context: str = "") -> str:
        """
        imagem.
        """

    def get_jpeg_data(self) -> Dict[str, any]:
        """
        JPEGdados.
        """
        return self.jpeg_data

    def set_jpeg_data(self, data_bytes: bytes):
        """
        ConfigurandoJPEGdados.
        """
        self.jpeg_data["buf"] = data_bytes
        self.jpeg_data["len"] = len(data_bytes)
