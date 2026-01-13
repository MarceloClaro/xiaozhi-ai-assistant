import threading

import cv2
import requests

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class Camera:
    _instance = None
    _lock = threading.Lock()  # 

    def __init__(self):
        self.explain_url = ""
        self.explain_token = ""
        self.jpeg_data = {"buf": b"", "len": 0}  # deJPEGBytesDados  # BytesDadosComprimento

        # deEmParâmetro
        config = ConfigManager.get_instance()
        self.camera_index = config.get_config("CAMERA.camera_index", 0)
        self.frame_width = config.get_config("CAMERA.frame_width", 640)
        self.frame_height = config.get_config("CAMERA.frame_height", 480)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def set_explain_url(self, url):
        """
        ConfigurandodeURL.
        """
        self.explain_url = url
        logger.info(f"Vision service URL set to: {url}")

    def set_explain_token(self, token):
        """
        Configurandodetoken.
        """
        self.explain_token = token
        if token:
            logger.info("Vision service token has been set")

    def set_jpeg_data(self, data_bytes):
        """
        ConfigurandoJPEGimagemdados.
        """
        self.jpeg_data["buf"] = data_bytes
        self.jpeg_data["len"] = len(data_bytes)

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
            self.jpeg_data["buf"] = jpeg_data.tobytes()
            self.jpeg_data["len"] = len(self.jpeg_data["buf"])
            logger.info(
                f"Image captured successfully (size: {self.jpeg_data['len']} bytes)")
            return True

        except Exception as e:
            logger.error(f"Exception during capture: {e}")
            return False

    def get_device_id(self):
        """
        dispositivoID.
        """
        return ConfigManager.get_instance().get_config("SYSTEM_OPTIONS.DEVICE_ID")

    def get_client_id(self):
        """
        clienteID.
        """
        return ConfigManager.get_instance().get_config("SYSTEM_OPTIONS.CLIENT_ID")

    def explain(self, question: str) -> str:
        """
        Enviandoimagem.
        """
        if not self.explain_url:
            return '{"success": false, "message": "Image explain URL is not set"}'

        if not self.jpeg_data["buf"]:
            return '{"success": false, "message": "Camera buffer is empty"}'

        # 
        headers = {"Device-Id": self.get_device_id(), "Client-Id": self.get_client_id()}

        if self.explain_token:
            headers["Authorization"] = f"Bearer {self.explain_token}"

        # ArquivoDados
        files = {
            "question": (None, question),
            "file": ("camera.jpg", self.jpeg_data["buf"], "image/jpeg"),
        }

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
                f"question={question}\n{response.text}")
            return response.text

        except requests.RequestException as e:
            error_msg = f"Failed to connect to explain URL: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "message": "{error_msg}"}}'


def take_photo(arguments: dict) -> str:
    """
    de.
    """
    camera = Camera.get_instance()
    question = arguments.get("question", "")

    # 
    success = camera.capture()
    if not success:
        return '{"success": false, "message": "Failed to capture photo"}'

    # Enviando
    return camera.explain(question)
