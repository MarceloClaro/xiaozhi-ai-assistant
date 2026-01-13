import asyncio
import json
import ssl
import time

import websockets

from src.constants.constants import AudioConfig
from src.protocols.protocol import Protocol
from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

ssl_context = ssl._create_unverified_context()

logger = get_logger(__name__)


class WebsocketProtocol(Protocol):
    def __init__(self):
        super().__init__()
        # Dispositivo
        self.config = ConfigManager.get_instance()
        self.websocket = None
        self.connected = False
        self.hello_received = None  # Inicializandopara None
        # MensagemProcessando，EmFechando
        self._message_task = None

        # ConexãoEstado
        self._last_ping_time = None
        self._last_pong_time = None
        self._ping_interval = 30.0  # （Segundos）
        self._ping_timeout = 10.0  # pingTimeoutTempo（Segundos）
        self._heartbeat_task = None
        self._connection_monitor_task = None

        # ConexãoEstado
        self._is_closing = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 0  # NãoReconexão
        self._auto_reconnect_enabled = False  # FechandoAutomáticoReconexão

        self.WEBSOCKET_URL = self.config.get_config(
            "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_URL"
        )
        access_token = self.config.get_config(
            "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_ACCESS_TOKEN"
        )
        device_id = self.config.get_config("SYSTEM_OPTIONS.DEVICE_ID")
        client_id = self.config.get_config("SYSTEM_OPTIONS.CLIENT_ID")

        self.HEADERS = {
            "Authorization": f"Bearer {access_token}",
            "Protocol-Version": "1",
            "Device-Id": device_id,  # DispositivoMAC
            "Client-Id": client_id,
        }

    async def connect(self) -> bool:
        """
        ConectandoparaWebSocketservidor.
        """
        if self._is_closing:
            logger.warning("Conexão Está fechandoEm，deConexãoTentativa")
            return False

        try:
            # EmConexão Event，EmdeEm
            self.hello_received = asyncio.Event()

            # Usando SSL
            current_ssl_context = None
            if self.WEBSOCKET_URL.startswith("wss://"):
                current_ssl_context = ssl_context

            # WebSocketConexão (Não  PythonVersãode)
            try:
                # de (EmPython 3.11+VersãoEm)
                self.websocket = await websockets.connect(
                    uri=self.WEBSOCKET_URL,
                    ssl=current_ssl_context,
                    additional_headers=self.HEADERS,
                    ping_interval=20,  # Usandowebsocketsde，20Segundos
                    ping_timeout=20,  # pingTimeout20Segundos
                    close_timeout=10,  # FechandoTimeout10Segundos
                    max_size=10 * 1024 * 1024,  # MáximoMensagem10MB
                    compression=None,  # 
                )
            except TypeError:
                # de (EmdePythonVersãoEm)
                self.websocket = await websockets.connect(
                    self.WEBSOCKET_URL,
                    ssl=current_ssl_context,
                    extra_headers=self.HEADERS,
                    ping_interval=20,  # Usandowebsocketsde
                    ping_timeout=20,  # pingTimeout20Segundos
                    close_timeout=10,  # FechandoTimeout10Segundos
                    max_size=10 * 1024 * 1024,  # MáximoMensagem10MB
                    compression=None,  # 
                )

            # IniciandoMensagemProcessando（，Fechando）
            self._message_task = asyncio.create_task(self._message_handler())

            # ，Usandowebsocketsde
            # self._start_heartbeat()

            # IniciandoConexão
            self._start_connection_monitor()

            # EnviandohelloMensagem
            hello_message = {
                "type": "hello",
                "version": 1,
                "features": {
                    "mcp": True,
                },
                "transport": "websocket",
                "audio_params": {
                    "format": "opus",
                    "sample_rate": AudioConfig.INPUT_SAMPLE_RATE,
                    "channels": AudioConfig.CHANNELS,
                    "frame_duration": AudioConfig.FRAME_DURATION,
                },
            }
            await self.send_text(json.dumps(hello_message))

            # AguardandoDispositivohello
            try:
                await asyncio.wait_for(self.hello_received.wait(), timeout=10.0)
                self.connected = True
                self._reconnect_attempts = 0  # Reconexão
                logger.info("JáConexãoparaWebSocketDispositivo")

                # NotificandoConexãoEstadoConversão
                if self._on_connection_state_changed:
                    self._on_connection_state_changed(True, "ConexãoSucesso")

                return True
            except asyncio.TimeoutError:
                logger.error("AguardandoDispositivohelloTimeout")
                await self._cleanup_connection()
                if self._on_network_error:
                    self._on_network_error("AguardandoTimeout")
                return False

        except Exception as e:
            logger.error(f"WebSocketConexão falhou: {e}")
            await self._cleanup_connection()
            if self._on_network_error:
                self._on_network_error(f"Incapaz deConexão: {str(e)}")
            return False

    def _start_heartbeat(self):
        """
        Iniciando.
        """
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def _start_connection_monitor(self):
        """
        IniciandoConectando.
        """
        if (
            self._connection_monitor_task is None
            or self._connection_monitor_task.done()
        ):
            self._connection_monitor_task = asyncio.create_task(
                self._connection_monitor()
            )

    async def _heartbeat_loop(self):
        """
        .
        """
        try:
            while self.websocket and not self._is_closing:
                await asyncio.sleep(self._ping_interval)

                if self.websocket and not self._is_closing:
                    try:
                        self._last_ping_time = time.time()
                        # Enviandoping  Aguardandopong
                        pong_waiter = await self.websocket.ping()
                        logger.debug("Enviandoping")

                        # Aguardandopong
                        try:
                            await asyncio.wait_for(
                                pong_waiter, timeout=self._ping_timeout
                            )
                            self._last_pong_time = time.time()
                            logger.debug("parapong")
                        except asyncio.TimeoutError:
                            logger.warning("pongTimeout")
                            await self._handle_connection_loss("pongTimeout")
                            break

                    except Exception as e:
                        logger.error(f"EnviandoFalha: {e}")
                        await self._handle_connection_loss("EnviandoFalha")
                        break
        except asyncio.CancelledError:
            logger.debug("")
        except Exception as e:
            logger.error(f"Exceção: {e}")

    async def _connection_monitor(self):
        """
        Conectandoestado.
        """
        try:
            while self.websocket and not self._is_closing:
                await asyncio.sleep(5)  # 5SegundosPesquisarVezes

                # PesquisarConexãoEstado
                if self.websocket:
                    if self.websocket.close_code is not None:
                        logger.warning("paraWebSocketConexãoJáFechando")
                        await self._handle_connection_loss("ConexãoJáFechando")
                        break

        except asyncio.CancelledError:
            logger.debug("Conexão")
        except Exception as e:
            logger.error(f"ConexãoExceção: {e}")

    async def _handle_connection_loss(self, reason: str):
        """
        ProcessandoConectando.
        """
        logger.warning(f"Conexão: {reason}")

        # ConexãoEstado
        was_connected = self.connected
        self.connected = False

        # NotificandoConexãoEstadoConversão
        if self._on_connection_state_changed and was_connected:
            try:
                self._on_connection_state_changed(False, reason)
            except Exception as e:
                logger.error(f"ConexãoEstadoConversãoFalha: {e}")

        # Conexão
        await self._cleanup_connection()

        # NotificandoÁudioFechando
        if self._on_audio_channel_closed:
            try:
                await self._on_audio_channel_closed()
            except Exception as e:
                logger.error(f"ÁudioFechandoFalha: {e}")

        # EmAutomáticoReconexão  NãoFechandoTentativaReconexão
        if (
            not self._is_closing
            and self._auto_reconnect_enabled
            and self._reconnect_attempts < self._max_reconnect_attempts
        ):
            await self._attempt_reconnect(reason)
        else:
            # NotificandoErro
            if self._on_network_error:
                if (
                    self._auto_reconnect_enabled
                    and self._reconnect_attempts >= self._max_reconnect_attempts
                ):
                    self._on_network_error(f"ConexãoReconexãoFalha: {reason}")
                else:
                    self._on_network_error(f"Conexão: {reason}")

    async def _attempt_reconnect(self, original_reason: str):
        """
        Tentando reconexão automática.
        """
        self._reconnect_attempts += 1

        # Notificação Começar Reconexão
        if self._on_reconnecting:
            try:
                self._on_reconnecting(
                    self._reconnect_attempts, self._max_reconnect_attempts
                )
            except Exception as e:
                logger.error(f"Falha ao chamar callback de Reconexão: {e}")

        logger.info(
            f"Tentando reconexão automática ({self._reconnect_attempts}/{self._max_reconnect_attempts})"
        )

        # Aguardando um tempo antes de Reconectar
        await asyncio.sleep(
            min(self._reconnect_attempts * 2, 30)
        )  # Backoff exponencial, máximo 30 segundos

        try:
            success = await self.connect()
            if success:
                logger.info("Reconexão Automática bem-sucedida")
                # Notificação Alteração Estado Conexão
                if self._on_connection_state_changed:
                    self._on_connection_state_changed(True, "Reconexão bem-sucedida")
            else:
                logger.warning(
                    f"Reconexão Automática Falhou ({self._reconnect_attempts}/{self._max_reconnect_attempts})"
                )
                # Se ainda pode Tentar novamente, não erro imediatamente
                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    if self._on_network_error:
                        self._on_network_error(
                            f"Reconexão Falhou, Já atingiu máximo de tentativas de Reconexão: {original_reason}"
                        )
        except Exception as e:
            logger.error(f"Erro durante processo de Reconexão: {e}")
            if self._reconnect_attempts >= self._max_reconnect_attempts:
                if self._on_network_error:
                    self._on_network_error(f"Exceção de Reconexão: {str(e)}")

    def enable_auto_reconnect(self, enabled: bool = True, max_attempts: int = 5):
        """Ativar ou desativar funcionalidade de Reconexão automática.

        Args:
            enabled: AutomáticoReconexão
            max_attempts: MáximoReconexãoTentativaVezes
        """
        self._auto_reconnect_enabled = enabled
        if enabled:
            self._max_reconnect_attempts = max_attempts
            logger.info(f"AutomáticoReconexão，MáximoTentativaVezes: {max_attempts}")
        else:
            self._max_reconnect_attempts = 0
            logger.info("AutomáticoReconexão")

    def get_connection_info(self) -> dict:
        """ConectandoInformação.

        Returns:
            dict: Conectandoestado、ReconexãoVezes  AguardarInformaçãode
        """
        return {
            "connected": self.connected,
            "websocket_closed": (
                self.websocket.close_code is not None if self.websocket else True
            ),
            "is_closing": self._is_closing,
            "auto_reconnect_enabled": self._auto_reconnect_enabled,
            "reconnect_attempts": self._reconnect_attempts,
            "max_reconnect_attempts": self._max_reconnect_attempts,
            "last_ping_time": self._last_ping_time,
            "last_pong_time": self._last_pong_time,
            "websocket_url": self.WEBSOCKET_URL,
        }

    async def _message_handler(self):
        """
        ProcessandoRecebendoparadeWebSocketmensagem.
        """
        try:
            async for message in self.websocket:
                if self._is_closing:
                    break

                try:
                    if isinstance(message, str):
                        try:
                            data = json.loads(message)
                            msg_type = data.get("type")
                            if msg_type == "hello":
                                # ProcessandoDispositivo hello Mensagem
                                await self._handle_server_hello(data)
                            else:
                                if self._on_incoming_json:
                                    self._on_incoming_json(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"deJSONMensagem: {message}, Erro: {e}")
                    elif isinstance(message, bytes):
                        # Mensagem，Áudio
                        if self._on_incoming_audio:
                            self._on_incoming_audio(message)
                except Exception as e:
                    # Processando  MensagemdeErro，ContinuarProcessandoMensagem
                    logger.error(f"ProcessandoMensagem: {e}", exc_info=True)
                    continue

        except asyncio.CancelledError:
            logger.debug("MensagemProcessando")
            return
        except websockets.ConnectionClosed as e:
            if not self._is_closing:
                logger.info(f"WebSocketConexãoJáFechando: {e}")
                await self._handle_connection_loss(
                    f"ConexãoFechando: {e.code} {e.reason}"
                )
        except websockets.ConnectionClosedError as e:
            if not self._is_closing:
                logger.info(f"WebSocketConexãoErroFechando: {e}")
                await self._handle_connection_loss(f"ConexãoErro: {e.code} {e.reason}")
        except websockets.InvalidState as e:
            logger.error(f"WebSocketEstado: {e}")
            await self._handle_connection_loss("ConexãoEstadoExceção")
        except ConnectionResetError:
            logger.warning("Conexão")
            await self._handle_connection_loss("Conexão")
        except OSError as e:
            logger.error(f"I/OErro: {e}")
            await self._handle_connection_loss("I/OErro")
        except Exception as e:
            logger.error(f"MensagemProcessandoExceção: {e}", exc_info=True)
            await self._handle_connection_loss(f"MensagemProcessandoExceção: {str(e)}")

    async def send_audio(self, data: bytes):
        """
        Enviandoáudiodados.
        """
        if not self.is_audio_channel_opened():
            return

        try:
            await self.websocket.send(data)
        except websockets.ConnectionClosed as e:
            logger.warning(f"EnviandoÁudio  ConexãoJáFechando: {e}")
            await self._handle_connection_loss(
                f"EnviandoÁudioFalha: {e.code} {e.reason}"
            )
        except websockets.ConnectionClosedError as e:
            logger.warning(f"EnviandoÁudio  ConexãoErro: {e}")
            await self._handle_connection_loss(f"EnviandoÁudioErro: {e.code} {e.reason}")
        except Exception as e:
            logger.error(f"EnviandoÁudioDadosFalha: {e}")
            # Não  EmErro，ConexãoProcessando Dispositivo Processando
            await self._handle_connection_loss(f"EnviandoÁudioExceção: {str(e)}")

    async def send_text(self, message: str):
        """
        Enviandomensagem.
        """
        if not self.websocket or self._is_closing:
            logger.warning("WebSocketNãoConexãoou Está fechando，Incapaz deEnviandoMensagem")
            return

        try:
            await self.websocket.send(message)
        except websockets.ConnectionClosed as e:
            logger.warning(f"EnviandoConexãoJáFechando: {e}")
            await self._handle_connection_loss(
                f"EnviandoFalha: {e.code} {e.reason}"
            )
        except websockets.ConnectionClosedError as e:
            logger.warning(f"EnviandoConexãoErro: {e}")
            await self._handle_connection_loss(f"EnviandoErro: {e.code} {e.reason}")
        except Exception as e:
            logger.error(f"EnviandoMensagemFalha: {e}")
            await self._handle_connection_loss(f"EnviandoExceção: {str(e)}")

    def is_audio_channel_opened(self) -> bool:
        """PesquisaráudioAbrindo.

        PesquisarConectandoestado，WebSocketdeestado
        """
        if not self.websocket or not self.connected or self._is_closing:
            return False

        # PesquisarWebSocketdeEstado
        try:
            return self.websocket.close_code is None
        except Exception:
            return False

    async def open_audio_channel(self) -> bool:
        """ WebSocket Conectando.

        Se  NãoConectando,entãoCriando  de WebSocket Conectando
        Returns:
            bool: Conectandosucesso
        """
        if not self.is_audio_channel_opened():
            return await self.connect()
        return True

    async def _handle_server_hello(self, data: dict):
        """
        Processandoservidorde hello mensagem.
        """
        try:
            # Validar
            transport = data.get("transport")
            if not transport or transport != "websocket":
                logger.error(f"NãoSuportadode: {transport}")
                return

            # Configurando hello Recebendo
            self.hello_received.set()

            # NotificandoÁudioJáAbrindo
            if self._on_audio_channel_opened:
                await self._on_audio_channel_opened()

            logger.info("SucessoProcessandoDispositivo hello Mensagem")

        except Exception as e:
            logger.error(f"ProcessandoDispositivo hello Mensagem: {e}")
            if self._on_network_error:
                self._on_network_error(f"ProcessandoDispositivoFalha: {str(e)}")

    async def _cleanup_connection(self):
        """
        ConectandoFonte.
        """
        self.connected = False

        # MensagemProcessando，Aguardando
        if self._message_task and not self._message_task.done():
            self._message_task.cancel()
            try:
                await self._message_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.debug(f"AguardandoMensagemExceção: {e}")
        self._message_task = None

        # 
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Conexão
        if self._connection_monitor_task and not self._connection_monitor_task.done():
            self._connection_monitor_task.cancel()
            try:
                await self._connection_monitor_task
            except asyncio.CancelledError:
                pass

        # FechandoWebSocketConexão
        if self.websocket and self.websocket.close_code is None:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"FechandoWebSocketConexão: {e}")

        self.websocket = None
        self._last_ping_time = None
        self._last_pong_time = None

    async def close_audio_channel(self):
        """
        Fechandoáudio.
        """
        self._is_closing = True

        try:
            await self._cleanup_connection()

            if self._on_audio_channel_closed:
                await self._on_audio_channel_closed()

        except Exception as e:
            logger.error(f"FechandoÁudioFalha: {e}")
        finally:
            self._is_closing = False
