"""
Normal camera implementation using remote API.
"""

import cv2
import requests

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

from .base_camera import BaseCamera

logger = get_logger(__name__)


class NormalCamera(BaseCamera):
    """
    ，UsandoAPI.
    """

    _instance = None

    def __init__(self):
        """
        Inicializando.
        """
        super().__init__()
        self.explain_url = ""
        self.explain_token = ""

    @classmethod
    def get_instance(cls):
        """
        .
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def set_explain_url(self, url: str):
        """
        ConfigurandodeURL.
        """
        self.explain_url = url
        logger.info(f"Vision service URL set to: {url}")

    def set_explain_token(self, token: str):
        """
        Configurandodetoken.
        """
        self.explain_token = token
        if token:
            logger.info("Vision service token has been set")

    def capture(self) -> bool:
        """
        Capturandoimagem.
        """
        try:
            logger.info("Accessing camera...")

            # TentativaAbrindo
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                logger.error(f"Cannot open camera at index {self.camera_index}")
                return False

            # ConfigurandoParâmetro
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

            #
            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.error("Failed to capture image")
                return False

            # Original
            height, width = frame.shape[:2]

            # ，para320
            max_dim = max(height, width)
            scale = 320 / max_dim if max_dim > 320 else 1.0

            # Aguardar
            if scale < 1.0:
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(
                    frame, (new_width, new_height), interpolation=cv2.INTER_AREA
                )

            # CodificaçãoparaJPEGBytes
            success, jpeg_data = cv2.imencode(".jpg", frame)

            if not success:
                logger.error("Failed to encode image to JPEG")
                return False

            # BytesDados
            self.set_jpeg_data(jpeg_data.tobytes())
            logger.info(
                f"Image captured successfully (size: {self.jpeg_data['len']} bytes)"
            )
            return True

        except Exception as e:
            logger.error(f"Exception during capture: {e}")
            return False

    def analyze(self, question: str, context: str = "") -> str:
        """
        imagem.
        """
        if not self.explain_url:
            return '{"success": false, "message": "Image explain URL is not set"}'

        if not self.jpeg_data["buf"]:
            return '{"success": false, "message": "Camera buffer is empty"}'

        #
        headers = {
            "Device-Id": ConfigManager.get_instance().get_config(
                "SYSTEM_OPTIONS.DEVICE_ID"
            ),
            "Client-Id": ConfigManager.get_instance().get_config(
                "SYSTEM_OPTIONS.CLIENT_ID"
            ),
        }

        if self.explain_token:
            headers["Authorization"] = f"Bearer {self.explain_token}"

        # ArquivoDados com contexto opcional
        files = {
            "question": (None, question),
            "file": ("camera.jpg", self.jpeg_data["buf"], "image/jpeg"),
        }
        
        # Adicionar contexto/prompt se fornecido
        if context:
            files["context"] = (None, context)
            logger.info(f"Sending image with context: {context[:50]}...")

        try:
            # Enviando
            response = requests.post(
                self.explain_url, headers=headers, files=files, timeout=10
            )

            # PesquisarEstado
            if response.status_code != 200:
                error_msg = (
                    f"Failed to upload photo, status code: {response.status_code}"
                )
                logger.error(error_msg)
                return f'{{"success": false, "message": "{error_msg}"}}'

            #
            logger.info(
                f"Explain image size={self.jpeg_data['len']}, "
                f"question={question}\n{response.text}"
            )
            return response.text

        except requests.RequestException as e:
            error_msg = f"Failed to connect to explain URL: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "message": "{error_msg}"}}'
