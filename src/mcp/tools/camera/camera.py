import threading
import base64
import json

import cv2

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
        Envia imagem para Vision API (DEPRECATED).
        Use take_photo() com Vision API Integration.
        """
        logger.warning(
            "Camera.explain() is deprecated. "
            "Use take_photo() for Vision API analysis."
        )
        return '{"success": false, "message": "Use take_photo() instead"}'


def take_photo(arguments: dict) -> str:
    """
    Captura foto da câmera e analisa com Vision API.
    
    Argumentos:
        question: (opcional) Pergunta sobre a imagem
        
    Retorna:
        JSON com resultado:
        {
            "success": true,
            "photo_description": "Descrição da imagem",
            "tokens_used": 256
        }
    """
    try:
        # Importar aqui para evitar dependência circular
        import asyncio
        from src.mcp.tools.providers import explain_image_via_mcp
        
        camera = Camera.get_instance()
        question = arguments.get(
            "question",
            "Descreva detalhadamente tudo que você vê nesta imagem"
        )
        
        # Capturar imagem
        logger.info("[Camera] Capturando foto...")
        success = camera.capture()
        if not success:
            return '{"success": false, "message": "Falha ao capturar foto"}'
        
        # Converter para base64
        image_base64 = base64.b64encode(
            camera.jpeg_data["buf"]
        ).decode('utf-8')
        
        logger.info(
            f"[Camera] Imagem capturada ({len(camera.jpeg_data['buf'])} bytes)"
        )
        
        # Carregar configuração da Vision API
        config_manager = ConfigManager.get_instance()
        vision_config = config_manager.get_config("VLLM", {})
        
        if not vision_config or not vision_config.get("zhipu"):
            logger.error("[Camera] Vision API não configurada")
            return (
                '{"success": false, "message": '
                '"Vision API não configurada em config.yaml"}'
            )
        
        zhipu_config = vision_config.get("zhipu", {})
        
        if not zhipu_config.get("api_key"):
            logger.error("[Camera] API Key do Zhipu não definida")
            return (
                '{"success": false, "message": '
                '"API Key do Zhipu não configurada"}'
            )
        
        # Enviar para análise (sync wrapper para função async)
        logger.info("[Camera] Enviando para Vision API...")
        
        async def analyze():
            return await explain_image_via_mcp(
                image_base64=image_base64,
                question=question,
                vision_config=zhipu_config
            )
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(analyze())
        
        # Retornar resultado
        if result.get("status") == "success":
            logger.info("[Camera] Análise concluída com sucesso")
            return (
                f'{{"success": true, '
                f'"photo_description": {json.dumps(result["analysis"])}, '
                f'"tokens_used": {result.get("tokens", 0)}}}'
            )
        else:
            logger.error(
                f"[Camera] Erro na análise: {result.get('error')}"
            )
            error_msg = result.get("error", "Erro desconhecido")
            return (
                f'{{"success": false, '
                f'"message": "Erro ao analisar imagem: {error_msg}"}}'
            )
    
    except Exception as e:
        logger.error(
            f"[Camera] Erro ao capturar/analisar foto: {str(e)}",
            exc_info=True
        )
        return (
            f'{{"success": false, '
            f'"message": "Erro: {str(e)}"}}'
        )
