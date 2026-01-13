"""sistema.

desistema
"""

import asyncio
from typing import Any, Dict

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


async def set_volume(args: Dict[str, Any]) -> bool:
    """
    Configurando.
    """
    try:
        volume = args["volume"]
        logger.info(f"[SystemTools] Configurandopara {volume}")

        # Validando
        if not (0 <= volume <= 100):
            logger.warning(f"[SystemTools] Valor: {volume}")
            return False

        # UsandoVolumeControllerConfigurando
        from src.utils.volume_controller import VolumeController

        # PesquisarDispositivo
        if not VolumeController.check_dependencies():
            logger.warning("[SystemTools] Não，Incapaz deConfigurando")
            return False

        volume_controller = VolumeController()
        await asyncio.to_thread(volume_controller.set_volume, volume)
        logger.info(f"[SystemTools] ConfigurandoSucesso: {volume}")
        return True

    except KeyError:
        logger.error("[SystemTools] volumeParâmetro")
        return False
    except Exception as e:
        logger.error(f"[SystemTools] ConfigurandoFalha: {e}", exc_info=True)
        return False


async def get_volume(args: Dict[str, Any]) -> int:
    """
    .
    """
    try:
        logger.info("[SystemTools] ")

        # UsandoVolumeController
        from src.utils.volume_controller import VolumeController

        # PesquisarDispositivo
        if not VolumeController.check_dependencies():
            logger.warning("[SystemTools] Não，Retorno")
            return VolumeController.DEFAULT_VOLUME

        volume_controller = VolumeController()
        current_volume = await asyncio.to_thread(volume_controller.get_volume)
        logger.info(f"[SystemTools] : {current_volume}")
        return current_volume

    except Exception as e:
        logger.error(f"[SystemTools] Falha: {e}", exc_info=True)
        from src.utils.volume_controller import VolumeController

        return VolumeController.DEFAULT_VOLUME


async def _get_audio_status() -> Dict[str, Any]:
    """
    áudioestado.
    """
    try:
        from src.utils.volume_controller import VolumeController

        if VolumeController.check_dependencies():
            volume_controller = VolumeController()
            # Usando，
            current_volume = await asyncio.to_thread(volume_controller.get_volume)
            return {
                "volume": current_volume,
                "muted": current_volume == 0,
                "available": True,
            }
        else:
            return {
                "volume": 50,
                "muted": False,
                "available": False,
                "reason": "Dependencies not available",
            }

    except Exception as e:
        logger.warning(f"[SystemTools] ÁudioEstadoFalha: {e}")
        return {"volume": 50, "muted": False, "available": False, "error": str(e)}


def _get_application_status() -> Dict[str, Any]:
    """
    aplicaçãoestadoInformação.
    """
    try:
        from src.application import Application
        from src.iot.thing_manager import ThingManager

        app = Application.get_instance()
        thing_manager = ThingManager.get_instance()

        # DeviceStatedeValorCaracteres，Não.name
        device_state = str(app.get_device_state())
        iot_count = len(thing_manager.things) if thing_manager else 0

        return {
            "device_state": device_state,
            "iot_devices": iot_count,
        }

    except Exception as e:
        logger.warning(f"[SystemTools] AppEstadoFalha: {e}")
        return {"device_state": "unknown", "iot_devices": 0, "error": str(e)}
