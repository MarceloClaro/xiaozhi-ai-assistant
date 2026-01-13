import asyncio
import sys
import threading
from pathlib import Path
from typing import Any, Awaitable

# para：Diretório sys.path（src de）
try:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except Exception:
    pass

from src.constants.constants import DeviceState, ListeningMode
from src.plugins.calendar import CalendarPlugin
from src.plugins.iot import IoTPlugin
from src.plugins.manager import PluginManager
from src.plugins.mcp import McpPlugin
from src.plugins.shortcuts import ShortcutsPlugin
from src.plugins.ui import UIPlugin
from src.plugins.wake_word import WakeWordPlugin
from src.protocols.mqtt_protocol import MqttProtocol
from src.protocols.websocket_protocol import WebsocketProtocol
from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger
from src.utils.opus_loader import setup_opus
from src.utils.enhanced_context_example import EnhancedContext

logger = get_logger(__name__)
setup_opus()


class Application:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Application()
        return cls._instance

    def __init__(self):
        if Application._instance is not None:
            logger.error("Tentativa de criar múltiplas instâncias de Application")
            raise Exception(
                "Application é uma classe singleton, use get_instance() para obter instância"
            )
        Application._instance = self

        logger.debug("Inicializando instância de Application")

        # Configuração
        self.config = ConfigManager.get_instance()

        # Sistema RAG Local + Memória Expandida
        self.context_system = EnhancedContext()
        logger.info("RAG Local inicializado com EnhancedContext")

        # Estado
        self.running = False
        self.protocol = None

        # DispositivoEstado（，）
        self.device_state = DeviceState.IDLE
        try:
            aec_enabled_cfg = bool(self.config.get_config("AEC_OPTIONS.ENABLED", True))
        except Exception:
            aec_enabled_cfg = True
        self.aec_enabled = aec_enabled_cfg
        self.listening_mode = (
            ListeningMode.REALTIME if self.aec_enabled else ListeningMode.AUTO_STOP
        )
        self.keep_listening = False

        # （ _main_tasks/_bg_tasks）
        self._tasks: set[asyncio.Task] = set()

        # 
        self._shutdown_event: asyncio.Event | None = None

        # 
        self._main_loop: asyncio.AbstractEventLoop | None = None

        # 
        self._state_lock: asyncio.Lock | None = None
        self._connect_lock: asyncio.Lock | None = None

        # 
        self.plugins = PluginManager()

    # -------------------------
    # Período
    # -------------------------
    async def run(self, *, protocol: str = "websocket", mode: str = "gui") -> int:
        logger.info("Iniciando Application, protocolo=%s", protocol)
        try:
            self.running = True
            self._main_loop = asyncio.get_running_loop()
            self._initialize_async_objects()
            self._set_protocol(protocol)
            self._setup_protocol_callbacks()
            # ：setup（AudioPlugin，setup_opusJá）
            from src.plugins.audio import AudioPlugin

            # Áudio、UI、MCP、IoT、、comAgendamento（UIderunParâmetro）
            # Automático priority ：
            # AudioPlugin(10) -> McpPlugin(20) -> WakeWordPlugin(30) -> CalendarPlugin(40)
            # -> IoTPlugin(50) -> UIPlugin(60) -> ShortcutsPlugin(70)
            self.plugins.register(
                McpPlugin(),
                IoTPlugin(),
                AudioPlugin(),
                WakeWordPlugin(),
                CalendarPlugin(),
                UIPlugin(mode=mode),
                ShortcutsPlugin(),
            )
            await self.plugins.setup_all(self)

            # Garantir que MCP foi inicializado
            try:
                mcp_plugin = self.plugins.get_plugin("mcp")
                if mcp_plugin and hasattr(mcp_plugin, "_server"):
                    tools_count = len(mcp_plugin._server.tools)
                    msg = f"[APP] MCP iniciado com {tools_count}"
                    logger.info(msg)
            except Exception as e:
                msg = f"[APP] Não foi possível verificar: {e}"
                logger.warning(msg)

            # IniciandoEstado， UI para""
            try:
                await self.plugins.notify_device_state_changed(
                    self.device_state
                )
            except Exception:
                pass
            # await self.connect_protocol()
            # ：start
            await self.plugins.start_all()
            # Aguardando
            await self._wait_shutdown()
            return 0

        except Exception as e:
            logger.error(f"Falha ao executar aplicação: {e}", exc_info=True)
            return 1
        finally:
            try:
                await self.shutdown()
            except Exception as e:
                logger.error(f"Erro ao fechar aplicação: {e}")

    async def connect_protocol(self):
        """
        protocoloAbrindoVezesprotocolo。RetornoJáAbrindo。
        """
        # JáAbrindoRetorno
        try:
            if self.is_audio_channel_opened():
                return True
            if not self._connect_lock:
                # NãoInicializando，Tentativa  Vezes
                opened = await asyncio.wait_for(
                    self.protocol.open_audio_channel(), timeout=12.0
                )
                if not opened:
                    logger.error("Conexão falhou")
                    return False
                logger.info("ConexãoJá，Ctrl+C")
                await self.plugins.notify_protocol_connected(self.protocol)
                return True

            async with self._connect_lock:
                if self.is_audio_channel_opened():
                    return True
                opened = await asyncio.wait_for(
                    self.protocol.open_audio_channel(), timeout=12.0
                )
                if not opened:
                    logger.error("Conexão falhou")
                    return False
                logger.info("ConexãoJá，Ctrl+C")
                await self.plugins.notify_protocol_connected(self.protocol)
                return True
        except asyncio.TimeoutError:
            logger.error("ConexãoTimeout")
            return False

    def _initialize_async_objects(self) -> None:
        logger.debug("Inicializando objetos assíncronos")
        self._shutdown_event = asyncio.Event()
        self._state_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()

    def _set_protocol(self, protocol_type: str) -> None:
        logger.debug("Definindo tipo de protocolo: %s", protocol_type)
        if protocol_type == "mqtt":
            self.protocol = MqttProtocol(asyncio.get_running_loop())
        else:
            self.protocol = WebsocketProtocol()

    # -------------------------
    # （）
    # -------------------------
    async def start_listening_manual(self) -> None:
        try:
            ok = await self.connect_protocol()
            if not ok:
                return
            self.keep_listening = False

            # Se está falando, enviar interrupção
            if self.device_state == DeviceState.SPEAKING:
                logger.info("Enviando interrupção durante fala")
                await self.protocol.send_abort_speaking(None)
                await self.set_device_state(DeviceState.IDLE)
            await self.protocol.send_start_listening(ListeningMode.MANUAL)
            await self.set_device_state(DeviceState.LISTENING)
        except Exception:
            pass

    async def stop_listening_manual(self) -> None:
        try:
            await self.protocol.send_stop_listening()
            await self.set_device_state(DeviceState.IDLE)
        except Exception:
            pass

    # -------------------------
    # Automático/： AEC comConfiguraçãoSelecionandoModo，
    # -------------------------
    async def start_auto_conversation(self) -> None:
        try:
            ok = await self.connect_protocol()
            if not ok:
                return

            mode = (
                ListeningMode.REALTIME if self.aec_enabled else ListeningMode.AUTO_STOP
            )
            self.listening_mode = mode
            self.keep_listening = True
            await self.protocol.send_start_listening(mode)
            await self.set_device_state(DeviceState.LISTENING)
        except Exception:
            pass

    def _setup_protocol_callbacks(self) -> None:
        self.protocol.on_network_error(self._on_network_error)
        self.protocol.on_incoming_json(self._on_incoming_json)
        self.protocol.on_incoming_audio(self._on_incoming_audio)
        self.protocol.on_audio_channel_opened(self._on_audio_channel_opened)
        self.protocol.on_audio_channel_closed(self._on_audio_channel_closed)

    async def _wait_shutdown(self) -> None:
        await self._shutdown_event.wait()

    # -------------------------
    # （）
    # -------------------------
    def spawn(self, coro: Awaitable[Any], name: str) -> asyncio.Task:
        """
        Criando，。
        """
        if not self.running or (self._shutdown_event and self._shutdown_event.is_set()):
            logger.debug(f"Pulando criação de tarefa (aplicação fechando): {name}")
            return None
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)

        def _done(t: asyncio.Task):
            self._tasks.discard(t)
            if not t.cancelled() and t.exception():
                logger.error(f" {name} ExceçãoFinal: {t.exception()}", exc_info=True)

        task.add_done_callback(_done)
        return task

    def schedule_command_nowait(self, fn, *args, **kwargs) -> None:
        if not self._main_loop or self._main_loop.is_closed():
            logger.warning("Não，")
            return

        def _runner():
            try:
                res = fn(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    self.spawn(res, name=f"call:{getattr(fn, '__name__', 'anon')}")
            except Exception as e:
                logger.error(
                    f"Falha na execução do callable agendado: {e}", exc_info=True
                )

        # Em
        self._main_loop.call_soon_threadsafe(_runner)

    # -------------------------
    # 
    # -------------------------
    def _on_network_error(self, error_message=None):
        if error_message:
            logger.error(error_message)

        self.keep_listening = False
        # Fechando
        # if self._shutdown_event and not self._shutdown_event.is_set():
        #     self._shutdown_event.set()

    def _on_incoming_audio(self, data: bytes):
        logger.debug(f"Mensagem binária recebida, comprimento: {len(data)}")
        # para
        self.spawn(self.plugins.notify_incoming_audio(data), "plugin:on_audio")

    def _on_incoming_json(self, json_data):
        try:
            msg_type = json_data.get("type") if isinstance(json_data, dict) else None
            logger.info(f"Mensagem JSON recebida: type={msg_type}")
            #  TTS start/stop paraDispositivoEstado（SuportadoAutomático/，NãoModo）
            if msg_type == "tts":
                state = json_data.get("state")
                if state == "start":
                    # Modo，TTSComeçarLISTENING；entãoSPEAKING
                    if (
                        self.keep_listening
                        and self.listening_mode == ListeningMode.REALTIME
                    ):
                        self.spawn(
                            self.set_device_state(DeviceState.LISTENING),
                            "state:tts_start_rt",
                        )
                    else:
                        self.spawn(
                            self.set_device_state(DeviceState.SPEAKING),
                            "state:tts_start_speaking",
                        )
                elif state == "stop":
                    if self.keep_listening:
                        # Continuar：Modo
                        async def _restart_listening():
                            try:
                                # ConfigurandoEstadopara LISTENING，ÁudioFilaLimpandoePararAguardando
                                await self.set_device_state(DeviceState.LISTENING)

                                # AguardandoÁudioParar，Enviando
                                # REALTIME JáEm LISTENING Enviando
                                if not (
                                    self.listening_mode == ListeningMode.REALTIME
                                    and self.device_state == DeviceState.LISTENING
                                ):
                                    await self.protocol.send_start_listening(
                                        self.listening_mode
                                    )
                            except Exception:
                                pass

                        self.spawn(_restart_listening(), "state:tts_stop_restart")
                    else:
                        self.spawn(
                            self.set_device_state(DeviceState.IDLE),
                            "state:tts_stop_idle",
                        )
            # para
            self.spawn(self.plugins.notify_incoming_json(json_data), "plugin:on_json")
        except Exception:
            logger.info("paraJSONMensagem")

    async def _on_audio_channel_opened(self):
        logger.info("JáAbrindo")
        # Abrindo LISTENING（：Conversãopara）
        await self.set_device_state(DeviceState.LISTENING)

    async def _on_audio_channel_closed(self):
        logger.info("JáFechando")
        # Fechando  para IDLE
        await self.set_device_state(DeviceState.IDLE)

    async def set_device_state(self, state: DeviceState):
        """
        programa：Configurandodispositivoestado。plugin。
        """
        # print(f"set_device_state: {state}")
        if not self._state_lock:
            self.device_state = state
            try:
                await self.plugins.notify_device_state_changed(state)
            except Exception:
                pass
            return
        async with self._state_lock:
            if self.device_state == state:
                return
            logger.info(f"Definindo estado do dispositivo: {state}")
            self.device_state = state
        # ，Emde
        try:
            await self.plugins.notify_device_state_changed(state)
            if state == DeviceState.LISTENING:
                await asyncio.sleep(0.5)
                self.aborted = False
        except Exception:
            pass

    # -------------------------
    # Dispositivo（paraUsando）
    # -------------------------
    def get_device_state(self):
        return self.device_state

    def is_idle(self) -> bool:
        return self.device_state == DeviceState.IDLE

    def is_listening(self) -> bool:
        return self.device_state == DeviceState.LISTENING

    def is_speaking(self) -> bool:
        return self.device_state == DeviceState.SPEAKING

    def get_listening_mode(self):
        return self.listening_mode

    def is_keep_listening(self) -> bool:
        return bool(self.keep_listening)

    def is_audio_channel_opened(self) -> bool:
        try:
            return bool(self.protocol and self.protocol.is_audio_channel_opened())
        except Exception:
            return False

    def should_capture_audio(self) -> bool:
        try:
            if self.device_state == DeviceState.LISTENING and not self.aborted:
                return True

            return (
                self.device_state == DeviceState.SPEAKING
                and self.aec_enabled
                and self.keep_listening
                and self.listening_mode == ListeningMode.REALTIME
            )
        except Exception:
            return False

    def get_state_snapshot(self) -> dict:
        return {
            "device_state": self.device_state,
            "listening_mode": self.listening_mode,
            "keep_listening": bool(self.keep_listening),
            "audio_opened": self.is_audio_channel_opened(),
        }

    async def abort_speaking(self, reason):
        """
        EmSaída.
        """

        if self.aborted:
            logger.debug(
                f"Já foi abortado, ignorando solicitação de aborto duplicada: {reason}"
            )
            return

        logger.info(f"Abortando saída de voz, motivo: {reason}")
        self.aborted = True
        await self.protocol.send_abort_speaking(reason)
        await self.set_device_state(DeviceState.IDLE)

    # -------------------------
    # UI ：ou
    # -------------------------
    def set_chat_message(self, role, message: str) -> None:
        """para UI Identificandode JSON mensagem（ UIPlugin de on_incoming_json）。
        role: "assistant" | "user" mensagemTipo。
        """
        try:
            msg_type = "tts" if str(role).lower() == "assistant" else "stt"
        except Exception:
            msg_type = "tts"
        payload = {"type": msg_type, "text": message}
        # Através de
        self.spawn(self.plugins.notify_incoming_json(payload), "ui:text_update")

    def set_emotion(self, emotion: str) -> None:
        """
        Configurando：Através de UIPlugin de on_incoming_json 。
        """
        payload = {"type": "llm", "emotion": emotion}
        self.spawn(self.plugins.notify_incoming_json(payload), "ui:emotion_update")

    # -------------------------
    # RAG Local + Memória Expandida
    # -------------------------
    async def process_input_with_context(
        self, user_input: str, max_context_length: int = 4000
    ) -> dict:
        """
        Processar input do usuário com contexto expandido do RAG.

        Args:
            user_input: Input do usuário
            max_context_length: Comprimento máximo do contexto

        Returns:
            Dicionário com contexto expandido e input
        """
        try:
            # Preparar contexto expandido
            context = (
                await self.context_system.prepare_context_for_query(
                    user_input, max_context_length
                )
            )

            logger.info(
                "Contexto expandido preparado: %d chars, %d chunks",
                context["context_length"],
                context["chunks_used"],
            )

            return {
                "user_input": user_input,
                "context": context["context"],
                "context_length": context["context_length"],
                "chunks_used": context["chunks_used"],
                "full_prompt": f"{context['context']}\n\n"
                f"Pergunta: {user_input}",
            }
        except Exception as e:
            logger.error(
                "Erro ao preparar contexto expandido: %s", e
            )
            return {
                "user_input": user_input,
                "context": "",
                "context_length": 0,
                "chunks_used": 0,
                "full_prompt": f"Pergunta: {user_input}",
            }

    async def register_conversation_turn(
        self,
        user_input: str,
        assistant_response: str,
        context_chunks: list[str] = None,
    ) -> None:
        """
        Registrar turno de conversa no RAG para histórico.

        Args:
            user_input: Input do usuário
            assistant_response: Resposta do assistente
            context_chunks: Chunks usados como contexto
        """
        try:
            await self.context_system.add_conversation_turn(
                user_input, assistant_response, context_chunks
            )
            logger.debug("Turno de conversa registrado no RAG")
        except Exception as e:
            logger.error("Erro ao registrar turno: %s", e)

    async def start_meeting_recording(
        self, title: str = None
    ) -> dict:
        """
        Iniciar gravação de reunião/áudio.

        Args:
            title: Título da reunião

        Returns:
            Info da gravação iniciada
        """
        try:
            return await self.context_system.start_meeting_recording(
                title
            )
        except Exception as e:
            logger.error("Erro ao iniciar gravação: %s", e)
            return {}

    async def add_meeting_transcript(
        self, text: str, speaker: str = "Falante"
    ) -> bool:
        """
        Adicionar transcrição a uma reunião em andamento.

        Args:
            text: Texto transcrito
            speaker: Nome do falante

        Returns:
            Sucesso da operação
        """
        try:
            return (
                await self.context_system.add_meeting_transcript(
                    text, speaker
                )
            )
        except Exception as e:
            logger.error("Erro ao adicionar transcrição: %s", e)
            return False

    async def stop_meeting_recording(self) -> dict:
        """
        Finalizar gravação de reunião e gerar resumo.

        Returns:
            Info da reunião criada (título, resumo, duração)
        """
        try:
            return await self.context_system.stop_meeting_recording()
        except Exception as e:
            logger.error("Erro ao finalizar gravação: %s", e)
            return {}

    def get_rag_stats(self) -> dict:
        """
        Obter estatísticas do sistema RAG.

        Returns:
            Dicionário com stats do RAG
        """
        try:
            return self.context_system.get_rag_stats()
        except Exception as e:
            logger.error("Erro ao obter stats RAG: %s", e)
            return {}

    # -------------------------
    # 
    # -------------------------
    async def shutdown(self):
        if not self.running:
            return
        logger.info("EmFechandoApplication...")
        self.running = False

        if self._shutdown_event is not None:
            self._shutdown_event.set()

        try:
            # 
            if self._tasks:
                for t in list(self._tasks):
                    if not t.done():
                        t.cancel()
                await asyncio.gather(*self._tasks, return_exceptions=True)
                self._tasks.clear()

            # Fechando（，）
            if self.protocol:
                try:
                    try:
                        self._main_loop.create_task(self.protocol.close_audio_channel())
                    except asyncio.TimeoutError:
                        logger.warning("FechandoTimeout，Aguardando")
                except Exception as e:
                    logger.error(f"Falha ao fechar protocolo: {e}")

            # ：stop/shutdown
            try:
                await self.plugins.stop_all()
            except Exception:
                pass
            try:
                await self.plugins.shutdown_all()
            except Exception:
                pass

            logger.info("Application FechandoConcluído")
        except Exception as e:
            logger.error(f"FechandoApp: {e}", exc_info=True)
