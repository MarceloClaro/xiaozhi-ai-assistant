"""
Screenshot tool for MCP.
"""

from src.utils.logging_config import get_logger

from .screenshot_camera import ScreenshotCamera

logger = get_logger(__name__)


def get_screenshot_camera_instance():
    """
    .
    """
    return ScreenshotCamera.get_instance()


def take_screenshot(arguments: dict) -> str:
    """de.

    Args:
        arguments: question、displayAguardarParâmetrode
                  displayValor: None(Dispositivo), "main"(), "secondary"(), 1,2,3...(Dispositivo)

    Returns:
        deJSONCaracteres
    """
    camera = get_screenshot_camera_instance()
    logger.info(f"Using screenshot camera implementation: {camera.__class__.__name__}")

    question = arguments.get("question", "")
    display_id = arguments.get("display", None)

    # AnalisandodisplayParâmetro
    if display_id:
        if isinstance(display_id, str):
            if display_id.lower() in ["main", "", "Dispositivo", "", ""]:
                display_id = "main"
            elif display_id.lower() in [
                "secondary",
                "",
                "Dispositivo",
                "",
                "",
                "",
            ]:
                display_id = "secondary"
            else:
                try:
                    display_id = int(display_id)
                except ValueError:
                    logger.warning(
                        f"Invalid display parameter: {display_id}, using default"
                    )
                    display_id = None

    logger.info(f"Taking screenshot with question: {question}, display: {display_id}")

    # 
    success = camera.capture(display_id)
    if not success:
        logger.error("Failed to capture screenshot")
        return '{"success": false, "message": "Failed to capture screenshot"}'

    # 
    logger.info("Screenshot captured, starting analysis...")
    return camera.analyze(question)
