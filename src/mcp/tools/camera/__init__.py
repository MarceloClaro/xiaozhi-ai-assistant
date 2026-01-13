"""
Camera tool for MCP.
"""

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

from .normal_camera import NormalCamera
from .vl_camera import VLCamera

logger = get_logger(__name__)


def get_camera_instance():
    """
    configuraçãoRetornode.
    """
    config = ConfigManager.get_instance()

    # PesquisarAI
    vl_key = config.get_config("CAMERA_OPTIONS.VL_API_KEY")
    vl_url = config.get_config("CAMERA_OPTIONS.LOCAL_VL_URL")

    if vl_url:
        logger.info(f"Initializing VL Camera with URL: {vl_url}")
        camera = VLCamera.get_instance()
        camera.set_explain_url(vl_url)
        if vl_key:
            camera.set_explain_token(vl_key)
        return camera

    logger.info("VL configuration not found, using normal Camera implementation")
    camera = NormalCamera.get_instance()
    # Configurar URL padrão para câmera normal
    default_url = config.get_config("CAMERA_OPTIONS.LOCAL_VL_URL", "https://api.tenclass.net/xiaozhi/vision/explain")
    if default_url:
        camera.set_explain_url(default_url)
        logger.info(f"Normal camera configured with URL: {default_url}")
    return camera


def take_photo(arguments: dict) -> str:
    """
    de.
    """
    camera = get_camera_instance()
    logger.info(f"Using camera implementation: {camera.__class__.__name__}")

    question = arguments.get("question", "")
    context = arguments.get("context", "")
    logger.info(f"Taking photo with question: {question}, context: {context[:50] if context else 'None'}...")

    # 
    success = camera.capture()
    if not success:
        logger.error("Failed to capture photo")
        return '{"success": false, "message": "Failed to capture photo"}'

    # 
    logger.info("Photo captured, starting analysis...")
    return camera.analyze(question, context)
