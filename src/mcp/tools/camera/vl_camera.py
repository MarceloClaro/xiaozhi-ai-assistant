"""
VL camera implementation using Zhipu AI with Vision API fallback.
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
        Analisar imagem usando AI com fallback para Gemini.
        """
        try:
            if not self.jpeg_data["buf"]:
                msg = '{"success": false, "message": "Camera buffer is empty"}'
                return msg

            # Converter para Base64
            img_b64 = base64.b64encode(
                self.jpeg_data["buf"]
            ).decode("utf-8")

            # Construir prompt com contexto
            full_prompt = question if question else "O que você vê？"
            if context:
                full_prompt = f"{full_prompt}\n\nContexto: {context}"
                logger.info(f"Sending image with context: {context[:50]}")

            # Tentar com Zhipu/OpenAI primeiro
            logger.info("Tentando análise de imagem com Zhipu...")
            try:
                return self._analyze_with_openai(img_b64, full_prompt)
            except Exception as zhipu_error:
                logger.warning(
                    f"Zhipu falhou: {str(zhipu_error)}, "
                    "tentando Gemini..."
                )

            # Fallback para Gemini Vision API
            logger.info("Usando fallback: Gemini Vision API...")
            return self._analyze_with_gemini(img_b64, full_prompt)

        except Exception as e:
            error_msg = f"Failed to analyze image: {str(e)}"
            logger.error(error_msg)
            msg = f'{{"success": false, "message": "{error_msg}"}}'
            return msg

    def _analyze_with_openai(self, image_b64: str,
                             prompt: str) -> str:
        """Analisar imagem usando OpenAI-compatible API."""
        messages = [
            {"role": "system",
             "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            },
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            modalities=["text"],
            stream=True,
            stream_options={"include_usage": True},
        )

        result = ""
        for chunk in completion:
            if chunk.choices:
                result += chunk.choices[0].delta.content or ""

        logger.info("Análise Zhipu concluída com sucesso")
        return f'{{"success": true, "text": "{result}"}}'

    def _analyze_with_gemini(self, image_b64: str,
                             prompt: str) -> str:
        """Analisar imagem usando Ollama localmente (minicpm-v)."""
        try:
            import requests
            from requests.exceptions import Timeout, ConnectionError

            ollama_url = "http://localhost:11434/api/generate"
            logger.info("Analisando com Ollama (minicpm-v) fallback...")
            
            full_prompt = (
                f"{prompt}\n\nDescreva a imagem de forma concisa."
            )
            
            payload = {
                "model": "minicpm-v",
                "prompt": full_prompt,
                "images": [image_b64],
                "stream": False,
                "temperature": 0.7
            }
            
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    msg = f"Tentativa {attempt + 1}/{max_retries}"
                    logger.info(msg)
                    
                    response = requests.post(
                        ollama_url,
                        json=payload,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        resp_json = response.json()
                        description = resp_json.get(
                            "response", ""
                        ).strip()
                        
                        if description:
                            description = " ".join(
                                description.split()
                            )
                            logger.info(
                                "Análise Ollama concluída - "
                                f"Descrição: {description[:60]}..."
                            )
                            result_text = (
                                '{{"success": true, "text": '
                                '"{0}"}}'.format(description)
                            )
                            return result_text
                        else:
                            error_msg = (
                                "Ollama retornou resposta vazia"
                            )
                            logger.warning(error_msg)
                            if attempt < max_retries - 1:
                                continue
                            result_text = (
                                '{{"success": false, '
                                '"message": "{0}"}}'.format(
                                    error_msg
                                )
                            )
                            return result_text
                    else:
                        error_msg = (
                            f"Status HTTP {response.status_code}"
                        )
                        logger.warning(f"Ollama: {error_msg}")
                        if attempt < max_retries - 1:
                            continue
                        result_text = (
                            '{{"success": false, '
                            '"message": "Ollama: {0}"}}'.format(
                                error_msg
                            )
                        )
                        return result_text
                
                except Timeout:
                    msg_log = (
                        f"Timeout tentativa {attempt + 1}"
                    )
                    logger.warning(msg_log)
                    if attempt < max_retries - 1:
                        logger.info("Retentando...")
                        continue
                    error_msg = (
                        "Ollama timeout - modelo carregando. "
                        "Aguarde e tente novamente."
                    )
                    logger.error(error_msg)
                    result_text = (
                        '{{"success": false, '
                        '"message": "{0}"}}'.format(error_msg)
                    )
                    return result_text
                
                except ConnectionError:
                    msg_log = (
                        f"Falha conexão tentativa {attempt + 1}"
                    )
                    logger.warning(msg_log)
                    if attempt < max_retries - 1:
                        logger.info("Retentando...")
                        continue
                    error_msg = (
                        "Ollama não está em localhost:11434. "
                        "Execute: ollama serve"
                    )
                    logger.error(error_msg)
                    result_text = (
                        '{{"success": false, '
                        '"message": "{0}"}}'.format(error_msg)
                    )
                    return result_text

        except Exception as e:
            error_msg = f"Erro Ollama: {str(e)}"
            logger.error(error_msg)
            result_text = (
                '{{"success": false, "message": "{0}"}}'.format(
                    error_msg
                )
            )
            return result_text

