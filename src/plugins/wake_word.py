from typing import Any

from src.constants.constants import AbortReason
from src.plugins.base import Plugin
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class WakeWordPlugin(Plugin):
    name = "wake_word"
    priority = 30  #  AudioPlugin

    def __init__(self) -> None:
        super().__init__()
        self.app = None
        self.detector = None

    async def setup(self, app: Any) -> None:
        self.app = app
        try:
            from src.audio_processing.wake_word_detect import WakeWordDetector

            self.detector = WakeWordDetector()
            if not getattr(self.detector, "enabled", False):
                self.detector = None
                return

            # 
            self.detector.on_detected(self._on_detected)
            self.detector.on_error = self._on_error
        except ImportError as e:
            logger.error(f"Falha ao importar detector de palavra-chave de ativação: {e}")
            self.detector = None
        except Exception as e:
            logger.error(f"InicializandoFalha: {e}", exc_info=True)
            self.detector = None

    async def start(self) -> None:
        if not self.detector:
            return
        try:
            # ÁudioCodificaçãoDispositivoOriginalPCMDados
            audio_codec = getattr(self.app, "audio_codec", None)
            if audio_codec is None:
                logger.warning("NãoEncontradoaudio_codec，Incapaz deIniciando")
                return
            await self.detector.start(audio_codec)
        except Exception as e:
            logger.error(f"IniciandoDispositivoFalha: {e}", exc_info=True)

    async def stop(self) -> None:
        if self.detector:
            try:
                await self.detector.stop()
            except Exception as e:
                logger.warning(f"PararDispositivoFalha: {e}")

    async def shutdown(self) -> None:
        if self.detector:
            try:
                await self.detector.stop()
            except Exception as e:
                logger.warning(f"FechandoDispositivoFalha: {e}")

    async def _on_detected(self, wake_word, full_text):
        # para：paraAutomático（ AEC AutomáticoSelecionando/Automático）
        try:
            # Em，paraAppde/Estado  Processando
            if hasattr(self.app, "device_state") and hasattr(
                self.app, "start_auto_conversation"
            ):
                if self.app.is_speaking():
                    await self.app.abort_speaking(AbortReason.WAKE_WORD_DETECTED)
                    audio_plugin = self.app.plugins.get_plugin("audio")
                    if audio_plugin and audio_plugin.codec:
                        await audio_plugin.codec.clear_audio_queue()
                else:
                    await self.app.start_auto_conversation()
        except Exception as e:
            logger.error(f"ProcessandoFalha: {e}", exc_info=True)

    def _on_error(self, error):
        try:
            logger.error(f"Erro: {error}")
            if hasattr(self.app, "set_chat_message"):
                self.app.set_chat_message("assistant", f"[Erro] {error}")
        except Exception as e:
            logger.error(f"ProcessandoErroFalha: {e}")
