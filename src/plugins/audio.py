import asyncio
import os
from typing import Any

from src.audio_codecs.audio_codec import AudioCodec
from src.plugins.base import Plugin
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# 常量配置
MAX_CONCURRENT_AUDIO_SENDS = 4


class AudioPlugin(Plugin):
    name = "audio"
    priority = 10  # 最高优先级，其他插件依赖 audio_codec

    def __init__(self) -> None:
        super().__init__()
        self.app = None
        self.codec: AudioCodec | None = None
        self._main_loop = None
        self._send_sem = asyncio.Semaphore(MAX_CONCURRENT_AUDIO_SENDS)
        self._in_silence_period = False  # 静默期标志，用于防止TTS尾音被Capturando

    async def setup(self, app: Any) -> None:
        self.app = app
        self._main_loop = app._main_loop

        if os.getenv("XIAOZHI_DISABLE_AUDIO") == "1":
            return

        try:
            self.codec = AudioCodec()
            await self.codec.initialize()

            # ConfigurandoCodificaçãoÁudio回调：直接Enviando，Não 走 Fila
            self.codec.set_encoded_callback(self._on_encoded_audio)

            # Expor para App, facilitar plugin de palavra-chave Usar
            self.app.audio_codec = self.codec
        except Exception as e:
            logger.error(f"Falha ao Inicializar plugin de Áudio: {e}", exc_info=True)
            self.codec = None

    async def on_device_state_changed(self, state):
        """Quando estado do dispositivo muda Limpando fila de áudio.

        Especialmente Processando: ao entrar estado LISTENING, Aguardando saída de áudio do hardware ficar completamente Parado, evitando que cauda TTS seja Capturado por microfone levando a ativação falsa.
        """
        if not self.codec:
            return

        from src.constants.constants import DeviceState

        # Se进入监听Estado，LimpandoFila 并 Aguardando硬件输出完全Parar
        if state == DeviceState.LISTENING:
            # Configurando静默期标志，阻止麦克风ÁudioEnviando
            self._in_silence_period = True
            try:
                # Aguardando硬件 DAC 输出Concluído（50-100ms）+ 声波传播（20ms）+ 安全余量
                await asyncio.sleep(0.2)
            finally:
                # LimpandoeAguardandoConcluído后，解除静默期
                self._in_silence_period = False

    async def on_incoming_json(self, message: Any) -> None:
        """Processando TTS 事件，控制MúsicaReprodução.

        Args:
            message: JSONmensagem，包含 type e state 字段
        """
        if not isinstance(message, dict):
            return

        try:
            # 监听 TTS Estado变化，控制MúsicaReprodução
            if message.get("type") == "tts":
                state = message.get("state")
                if state == "start":
                    # TTS Começar：先LimpandoÁudioFila，再PausadoMúsica
                    await self._pause_music_for_tts()
                elif state == "stop":
                    # TTS Final: Restaurando Reprodução de Música
                    await self._resume_music_after_tts()
                    await self.codec.clear_audio_queue()
        except Exception as e:
            logger.error(f"Falha ao processar evento TTS: {e}", exc_info=True)

    async def on_incoming_audio(self, data: bytes) -> None:
        """Recebendo retorno de dados de áudio do servidor e Reprodução.

        Args:
            data: 服务端RetornodeOpusCodificaçãoáudiodados
        """
        if self.codec:
            try:
                await self.codec.write_audio(data)
            except Exception as e:
                logger.debug(f"写入ÁudioDadosFalha: {e}")

    async def _pause_music_for_tts(self):
        """
        TTS Iniciando时：先LimpandoáudioFila，再PausadoMúsica.
        """
        try:
            if self.codec:
                await self.codec.clear_audio_queue()
                logger.debug("TTS Começar，JáLimpandoÁudioFila")

            try:
                from src.mcp.tools.music.music_player import get_music_player_instance

                music_player = get_music_player_instance()

                # SeMúsica 正 EmReprodução 且 NãoPausado，entãoPausado
                if music_player.is_playing and not music_player.paused:
                    logger.info("TTS Começar，PausadoMúsicaReprodução")
                    result = await music_player.pause(source="tts")
                    if result.get("status") != "success":
                        logger.warning(f"PausadoMúsicaRetornoExceção: {result}")
            except Exception as e:
                logger.warning(f"PausadoMúsicaFalha: {e}")

        except Exception as e:
            logger.error(f"TTS ComeçarProcessandoFalha: {e}", exc_info=True)

    async def _resume_music_after_tts(self):
        """
        TTS Final后：RestaurandoMúsicaReproduçãoouIniciando延迟Reprodução.
        """
        try:
            from src.mcp.tools.music.music_player import get_music_player_instance

            music_player = get_music_player_instance()

            if music_player._deferred_start_path:
                logger.info("TTS ReproduçãoConcluído，Iniciando延迟ReproduçãodeMúsica")
                # 直接调用内部方法，跳过TTS检查
                file_path = music_player._deferred_start_path
                start_pos = music_player._deferred_start_position
                music_player._deferred_start_path = None
                music_player._deferred_start_position = 0.0

                # NovamenteIniciandoReprodução（此时TTSJáFinal，Não会再延迟）
                await music_player._start_playback(file_path, start_pos)
                return

            if music_player.is_playing and music_player.paused:
                if music_player._pause_source == "tts":
                    logger.info("TTS ReproduçãoConcluído，RestaurandoMúsicaReprodução")
                    await music_player.resume()
                else:
                    logger.debug(
                        f"MúsicaPausadoOrigem: {music_player._pause_source}，Não自动Restaurando")
            else:
                logger.debug(
                    f"MúsicaEstado: is_playing={music_player.is_playing}, "
                    f"paused={music_player.paused}, 无需Restaurando")
        except Exception as e:
            logger.error(f"RestaurandoMúsicaReproduçãoFalha: {e}", exc_info=True)

    async def shutdown(self) -> None:
        """
        完全Fechando并释放áudio 资 Fonte.
        """
        # PararÁudio消费者任务
        if self._audio_consumer_task and not self._audio_consumer_task.done():
            self._audio_consumer_task.cancel()
            try:
                await self._audio_consumer_task
            except asyncio.CancelledError:
                pass

        if self.codec:
            try:
                await self.codec.close()
            except Exception as e:
                logger.error(f"FechandoÁudio编解码器Falha: {e}", exc_info=True)
            finally:
                self.codec = None

        # LimpandoApp引用
        if self.app:
            self.app.audio_codec = None

    # -------------------------
    # Interno: Enviar diretamente áudio de gravação (Não vai para Fila)
    # -------------------------
    def _on_encoded_audio(self, encoded_data: bytes) -> None:
        """
        Callback de thread de áudio: mudar para loop principal e enviar diretamente (referência versão antiga)
        """
        try:
            if not self.app or not self._main_loop or not self.app.running:
                return
            if self._main_loop.is_closed():
                return
            self._main_loop.call_soon_threadsafe(
                self._schedule_send_audio, encoded_data
            )
        except Exception:
            pass

    def _schedule_send_audio(self, encoded_data: bytes) -> None:
        """
        Em主事件循环Em调度Enviando任务.
        """
        if not self.app or not self.app.running or not self.app.protocol:
            return

        async def _send():
            async with self._send_sem:
                try:
                    if not (
                        self.app.protocol
                        and self.app.protocol.is_audio_channel_opened()
                    ):
                        return
                    if self._should_send_microphone_audio():
                        await self.app.protocol.send_audio(encoded_data)
                except Exception:
                    pass

        # 创建任务但NãoAguardando，实现"发完即忘"
        self.app.spawn(_send(), name="audio:send")

    def _should_send_microphone_audio(self) -> bool:
        """
        委托paraaplicaçãode统一estado机规então，并检查静默期标志.
        """
        try:
            # 静默期内禁止EnviandoÁudio（防止TTS尾音被Capturando）
            if self._in_silence_period:
                return False
            return self.app and self.app.should_capture_audio()
        except Exception:
            return False
