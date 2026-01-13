"""
VL camera implementation using Zhipu AI.
"""

import base64

import cv2
from openai import OpenAI

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

from .base_camera import BaseCamera

logger = get_logger(__name__)


class VLCamera(BaseCamera):
    """
    AI.
    """

    _instance = None

    def __init__(self):
        """
        InicializandoAI.
        """
        super().__init__()
        config = ConfigManager.get_instance()

        # InicializandoOpenAI
        api_key = config.get_config("CAMERA_OPTIONS.VL_API_KEY", "")
        base_url = config.get_config(
            "CAMERA_OPTIONS.LOCAL_VL_URL",
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        )
        
        self.client = OpenAI(
            api_key=api_key if api_key else "sk-default-key",
            base_url=base_url,
        )
        self.model = config.get_config("CAMERA_OPTIONS.MODELS", "glm-4v-plus")
        logger.info(f"VL Camera initialized with model: {self.model}, URL: {base_url}")

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
        UsandoAIimagem.
        """
        try:
            if not self.jpeg_data["buf"]:
                return '{"success": false, "message": "Camera buffer is empty"}'

            # paraBase64
            image_base64 = base64.b64encode(self.jpeg_data["buf"]).decode("utf-8")

            # Construir prompt com contexto
            full_prompt = question if question else "O que você vê？"
            if context:
                full_prompt = f"{full_prompt}\n\nContexto adicional: {context}"
                logger.info(f"Sending image with context: {context[:50]}...")

            # Mensagem
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                        {
                            "type": "text",
                            "text": full_prompt,
                        },
                    ],
                },
            ]

            # Enviando
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                modalities=["text"],
                stream=True,
                stream_options={"include_usage": True},
            )

            #
            result = ""
            for chunk in completion:
                if chunk.choices:
                    result += chunk.choices[0].delta.content or ""

            #
            logger.info(f"VL analysis completed, question={question}")
            return f'{{"success": true, "text": "{result}"}}'

        except Exception as e:
            error_msg = f"Failed to analyze image with VL: {str(e)}"
            logger.error(error_msg)
            return f'{{"success": false, "message": "{error_msg}"}}'
