import asyncio
import json
import socket
import threading
import time

import paho.mqtt.client as mqtt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from src.constants.constants import AudioConfig
from src.protocols.protocol import Protocol
from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

# Log
logger = get_logger(__name__)


class MqttProtocol(Protocol):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.config = ConfigManager.get_instance()
        self.mqtt_client = None
        self.udp_socket = None
        self.udp_thread = None
        self.udp_running = False
        self.connected = False

        # ConexãoEstado
        self._is_closing = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 0  # NãoReconexão
        self._auto_reconnect_enabled = False  # FechandoAutomáticoReconexão
        self._connection_monitor_task = None
        self._last_activity_time = None
        self._keep_alive_interval = 60  # MQTT（Segundos）
        self._connection_timeout = 120  # ConexãoTimeout（Segundos）

        # MQTT
        self.endpoint = None
        self.client_id = None
        self.username = None
        self.password = None
        self.publish_topic = None
        self.subscribe_topic = None

        # UDP
        self.udp_server = ""
        self.udp_port = 0
        self.aes_key = None
        self.aes_nonce = None
        self.local_sequence = 0
        self.remote_sequence = 0

        # 
        self.server_hello_event = asyncio.Event()

    def _parse_endpoint(self, endpoint: str) -> tuple[str, int]:
        """AnalisandoendpointCaracteres，e.

        Args:
            endpoint: endpointCaracteres，Formato:
                     - "hostname" (Usando8883)
                     - "hostname:port" (Usando)

        Returns:
            tuple: (host, port) e
        """
        if not endpoint:
            raise ValueError("endpointNão  para")

        # Pesquisar
        if ":" in endpoint:
            host, port_str = endpoint.rsplit(":", 1)
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    raise ValueError(f"Em1-65535: {port}")
            except ValueError as e:
                raise ValueError(f"de: {port_str}") from e
        else:
            # Nenhum，Usando8883
            host = endpoint
            port = 8883

        return host, port

    async def connect(self):
        """
        ConectandoparaMQTTservidor.
        """
        if self._is_closing:
            logger.warning("Conexão Está fechandoEm，deConexãoTentativa")
            return False

        # hello
        self.server_hello_event = asyncio.Event()

        # TentativaMQTT
        try:
            # TentativadeOTADispositivoMQTT
            mqtt_config = self.config.get_config("SYSTEM_OPTIONS.NETWORK.MQTT_INFO")

            print(mqtt_config)

            # MQTT
            self.endpoint = mqtt_config.get("endpoint")
            self.client_id = mqtt_config.get("client_id")
            self.username = mqtt_config.get("username")
            self.password = mqtt_config.get("password")
            self.publish_topic = mqtt_config.get("publish_topic")
            self.subscribe_topic = mqtt_config.get("subscribe_topic")

            logger.info(f"JádeOTADispositivoMQTT: {self.endpoint}")
        except Exception as e:
            logger.warning(f"deOTADispositivoMQTTFalha: {e}")

        # ValidandoMQTT
        if (
            not self.endpoint
            or not self.username
            or not self.password
            or not self.publish_topic
        ):
            logger.error("MQTTNão")
            if self._on_network_error:
                await self._on_network_error("MQTTNão")
            return False

        # subscribe_topic para "null" Caracteres，Processando
        if self.subscribe_topic == "null":
            self.subscribe_topic = None
            logger.info("paranull，Não")

        # SeJáMQTT，DesconectadoConexão
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except Exception as e:
                logger.warning(f"DesconectadoMQTTConexão: {e}")

        # Analisandoendpoint，e
        try:
            host, port = self._parse_endpoint(self.endpoint)
            use_tls = port == 8883  # Usando8883UsandoTLS

            logger.info(
                f"Analisandoendpoint: {self.endpoint} -> : {host}, : {port}, UsandoTLS: {use_tls}"
            )
        except ValueError as e:
            logger.error(f"AnalisandoendpointFalha: {e}")
            if self._on_network_error:
                await self._on_network_error(f"AnalisandoendpointFalha: {e}")
            return False

        # deMQTT
        self.mqtt_client = mqtt.Client(client_id=self.client_id)
        self.mqtt_client.username_pw_set(self.username, self.password)

        # TLSConexão
        if use_tls:
            try:
                self.mqtt_client.tls_set(
                    ca_certs=None,
                    certfile=None,
                    keyfile=None,
                    cert_reqs=mqtt.ssl.CERT_REQUIRED,
                    tls_version=mqtt.ssl.PROTOCOL_TLS,
                )
                logger.info("JáTLSConexão")
            except Exception as e:
                logger.error(f"TLSFalha，Incapaz deConexãoparaMQTTDispositivo: {e}")
                if self._on_network_error:
                    await self._on_network_error(f"TLSFalha: {str(e)}")
                return False
        else:
            logger.info("Usando  TLSConexão")

        # ConexãoFuture
        connect_future = self.loop.create_future()

        def on_connect_callback(client, userdata, flags, rc, properties=None):
            if rc == 0:
                logger.info("JáConexãoparaMQTTDispositivo")
                self._last_activity_time = time.time()
                self.loop.call_soon_threadsafe(lambda: connect_future.set_result(True))
            else:
                logger.error(f"ConexãoMQTTDispositivoFalha，Retorno: {rc}")
                self.loop.call_soon_threadsafe(
                    lambda: connect_future.set_exception(
                        Exception(f"ConexãoMQTTDispositivoFalha，Retorno: {rc}")
                    )
                )

        def on_message_callback(client, userdata, msg):
            try:
                self._last_activity_time = time.time()  # Tempo
                payload = msg.payload.decode("utf-8")
                self._handle_mqtt_message(payload)
            except Exception as e:
                logger.error(f"ProcessandoMQTTMensagem: {e}")

        def on_disconnect_callback(client, userdata, rc):
            """MQTTDesconectadoConectando.

            Args:
                client: MQTTcliente
                userdata: usuáriodados
                rc: Retorno (0=Desconectado, >0=exceçãoDesconectado)
            """
            try:
                if rc == 0:
                    logger.info("MQTTConexãoDesconectado")
                else:
                    logger.warning(f"MQTTConexãoExceçãoDesconectado，Retorno: {rc}")

                was_connected = self.connected
                self.connected = False

                # NotificandoConexãoEstadoConversão
                if self._on_connection_state_changed and was_connected:
                    reason = "Desconectado" if rc == 0 else f"ExceçãoDesconectado(rc={rc})"
                    self.loop.call_soon_threadsafe(
                        lambda: self._on_connection_state_changed(False, reason)
                    )

                # PararUDPRecebendo
                self._stop_udp_receiver()

                # EmExceçãoDesconectadoAutomáticoReconexãoTentativaReconexão
                if (
                    rc != 0
                    and not self._is_closing
                    and self._auto_reconnect_enabled
                    and self._reconnect_attempts < self._max_reconnect_attempts
                ):
                    # EmEmReconexão
                    self.loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(
                            self._attempt_reconnect(f"MQTTDesconectado(rc={rc})")
                        )
                    )
                else:
                    # NotificandoÁudioFechando
                    if self._on_audio_channel_closed:
                        asyncio.run_coroutine_threadsafe(
                            self._on_audio_channel_closed(), self.loop
                        )

                    # NotificandoErro
                    if rc != 0 and self._on_network_error:
                        error_msg = f"MQTTConexãoDesconectado: {rc}"
                        if (
                            self._auto_reconnect_enabled
                            and self._reconnect_attempts >= self._max_reconnect_attempts
                        ):
                            error_msg += " (ReconexãoFalha)"
                        self.loop.call_soon_threadsafe(
                            lambda: self._on_network_error(error_msg)
                        )

            except Exception as e:
                logger.error(f"ProcessandoMQTTDesconectadoConexão falhou: {e}")

        def on_publish_callback(client, userdata, mid):
            """
            MQTTmensagem.
            """
            self._last_activity_time = time.time()  # Tempo

        def on_subscribe_callback(client, userdata, mid, granted_qos):
            """
            MQTT.
            """
            logger.info(f"Sucesso，: {self.subscribe_topic}")
            self._last_activity_time = time.time()  # Tempo

        # Configurando
        self.mqtt_client.on_connect = on_connect_callback
        self.mqtt_client.on_message = on_message_callback
        self.mqtt_client.on_disconnect = on_disconnect_callback
        self.mqtt_client.on_publish = on_publish_callback
        self.mqtt_client.on_subscribe = on_subscribe_callback

        try:
            # ConexãoMQTTDispositivo，
            logger.info(f"EmConexãoMQTTDispositivo: {host}:{port}")
            self.mqtt_client.connect_async(
                host, port, keepalive=self._keep_alive_interval
            )
            self.mqtt_client.loop_start()

            # AguardandoConexãoConcluído
            await asyncio.wait_for(connect_future, timeout=10.0)

            # 
            if self.subscribe_topic:
                self.mqtt_client.subscribe(self.subscribe_topic, qos=1)

            # IniciandoConexão
            self._start_connection_monitor()

            # EnviandohelloMensagem
            hello_message = {
                "type": "hello",
                "version": 3,
                "features": {
                    "mcp": True,
                },
                "transport": "udp",
                "audio_params": {
                    "format": "opus",
                    "sample_rate": AudioConfig.OUTPUT_SAMPLE_RATE,
                    "channels": AudioConfig.CHANNELS,
                    "frame_duration": AudioConfig.FRAME_DURATION,
                },
            }

            # EnviandoMensagem  Aguardando
            if not await self.send_text(json.dumps(hello_message)):
                logger.error("EnviandohelloMensagemFalha")
                return False

            try:
                await asyncio.wait_for(self.server_hello_event.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.error("AguardandoDispositivohelloMensagemTimeout")
                if self._on_network_error:
                    await self._on_network_error("AguardandoTimeout")
                return False

            # UDP
            try:
                if self.udp_socket:
                    self.udp_socket.close()

                self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.udp_socket.settimeout(0.5)

                # IniciandoUDPRecebendo
                if self.udp_thread and self.udp_thread.is_alive():
                    self.udp_running = False
                    self.udp_thread.join(1.0)

                self.udp_running = True
                self.udp_thread = threading.Thread(target=self._udp_receive_thread)
                self.udp_thread.daemon = True
                self.udp_thread.start()

                self.connected = True
                self._reconnect_attempts = 0  # Reconexão

                # NotificandoConexãoEstadoConversão
                if self._on_connection_state_changed:
                    self._on_connection_state_changed(True, "ConexãoSucesso")

                return True
            except Exception as e:
                logger.error(f"UDPFalha: {e}")
                if self._on_network_error:
                    await self._on_network_error(f"UDPConexão falhou: {e}")
                return False

        except Exception as e:
            logger.error(f"ConexãoMQTTDispositivoFalha: {e}")
            if self._on_network_error:
                await self._on_network_error(f"ConexãoMQTTDispositivoFalha: {e}")
            return False

    def _handle_mqtt_message(self, payload):
        """
        ProcessandoMQTTmensagem.
        """
        try:
            data = json.loads(payload)
            msg_type = data.get("type")

            if msg_type == "goodbye":
                # ProcessandogoodbyeMensagem
                session_id = data.get("session_id")
                if not session_id or session_id == self.session_id:
                    # EmEm
                    asyncio.run_coroutine_threadsafe(self._handle_goodbye(), self.loop)
                return

            elif msg_type == "hello":
                print("RetornoInicializando", data)
                # ProcessandoDispositivohello
                transport = data.get("transport")
                if transport != "udp":
                    logger.error(f"NãoSuportadode: {transport}")
                    return

                # ID
                self.session_id = data.get("session_id", "")

                # UDP
                udp = data.get("udp")
                if not udp:
                    logger.error("UDP")
                    return

                self.udp_server = udp.get("server")
                self.udp_port = udp.get("port")
                self.aes_key = udp.get("key")
                self.aes_nonce = udp.get("nonce")

                # 
                self.local_sequence = 0
                self.remote_sequence = 0

                logger.info(
                    f"Resposta hello recebida do servidor, servidor UDP: {self.udp_server}:{self.udp_port}"
                )

                # Configurandohello
                self.loop.call_soon_threadsafe(self.server_hello_event.set)

                # ÁudioAbrindo
                if self._on_audio_channel_opened:
                    self.loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(self._on_audio_channel_opened())
                    )

            else:
                # ProcessandoJSONMensagem
                if self._on_incoming_json:

                    def process_json(json_data=data):
                        if asyncio.iscoroutinefunction(self._on_incoming_json):
                            coro = self._on_incoming_json(json_data)
                            if coro is not None:
                                asyncio.create_task(coro)
                        else:
                            self._on_incoming_json(json_data)

                    self.loop.call_soon_threadsafe(process_json)
        except json.JSONDecodeError:
            logger.error(f"deJSONDados: {payload}")
        except Exception as e:
            logger.error(f"ProcessandoMQTTMensagem: {e}")

    def _udp_receive_thread(self):
        """UDPRecebendo.

         audio_player.py de
        """
        logger.info(
            f"Thread de recepção UDP iniciada, escutando dados de {self.udp_server}:{self.udp_port}"
        )

        self.udp_running = True
        debug_counter = 0

        while self.udp_running:
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                debug_counter += 1

                try:
                    # ValidandoDados
                    if len(data) < 16:  # 16Bytesdenonce
                        logger.error(f"deÁudioDados  Tamanho: {len(data)}")
                        continue

                    # nonceeDados
                    received_nonce = data[:16]
                    encrypted_audio = data[16:]

                    # UsandoAES-CTR
                    decrypted = self.aes_ctr_decrypt(
                        bytes.fromhex(self.aes_key), received_nonce, encrypted_audio
                    )

                    # DebugInformação
                    if debug_counter % 100 == 0:
                        logger.debug(
                            f"Pacote de áudio descriptografado #{debug_counter}, tamanho: {len(decrypted)} bytes"
                        )

                    # Processar dados de áudio descriptografados
                    if self._on_incoming_audio:

                        def process_audio(audio_data=decrypted):
                            if asyncio.iscoroutinefunction(self._on_incoming_audio):
                                coro = self._on_incoming_audio(audio_data)
                                if coro is not None:
                                    asyncio.create_task(coro)
                            else:
                                self._on_incoming_audio(audio_data)

                        self.loop.call_soon_threadsafe(process_audio)

                except Exception as e:
                    logger.error(f"ProcessandoÁudioDados  Erro: {e}")
                    continue

            except socket.timeout:
                # Timeoutde，Continuar
                pass
            except Exception as e:
                logger.error(f"UDPRecebendoErro: {e}")
                if not self.udp_running:
                    break
                time.sleep(0.1)  # EmErroCPU

        logger.info("UDPRecebendoJáParar")

    async def send_text(self, message):
        """
        Enviandomensagem.
        """
        if not self.mqtt_client:
            logger.error("MQTTNãoInicializando")
            return False

        try:
            result = self.mqtt_client.publish(self.publish_topic, message)
            result.wait_for_publish()
            return True
        except Exception as e:
            logger.error(f"EnviandoMQTTMensagemFalha: {e}")
            if self._on_network_error:
                await self._on_network_error(f"EnviandoMQTTMensagemFalha: {e}")
            return False

    async def send_audio(self, audio_data):
        """Enviandoáudiodados.

         audio_sender.py de
        """
        if not self.udp_socket or not self.udp_server or not self.udp_port:
            logger.error("UDPNãoInicializando")
            return False

        try:
            # denonce ( audio_sender.py Emde)
            # Formato: 0x01 (1Bytes) + 0x00 (3Bytes) + Comprimento (2Bytes) + Originalnonce (8Bytes) +  (8Bytes)
            self.local_sequence = (self.local_sequence + 1) & 0xFFFFFFFF
            new_nonce = (
                self.aes_nonce[:4]  # 
                + format(len(audio_data), "04x")  # DadosComprimento
                + self.aes_nonce[8:24]  # Originalnonce
                + format(self.local_sequence, "08x")  # 
            )

            encrypt_encoded_data = self.aes_ctr_encrypt(
                bytes.fromhex(self.aes_key), bytes.fromhex(new_nonce), bytes(audio_data)
            )

            # noncee
            packet = bytes.fromhex(new_nonce) + encrypt_encoded_data

            # EnviandoDados
            self.udp_socket.sendto(packet, (self.udp_server, self.udp_port))

            # A cada 10 pacotes enviados, imprimir um log
            if self.local_sequence % 10 == 0:
                logger.info(
                    f"Pacote de áudio enviado, número de sequência: {self.local_sequence}, destino: "
                    f"{self.udp_server}:{self.udp_port}"
                )

            self.local_sequence += 1
            return True
        except Exception as e:
            logger.error(f"EnviandoÁudioDadosFalha: {e}")
            if self._on_network_error:
                asyncio.create_task(self._on_network_error(f"EnviandoÁudioDadosFalha: {e}"))
            return False

    async def open_audio_channel(self):
        """
        Abrindoáudio.
        """
        if not self.connected:
            return await self.connect()
        return True

    async def close_audio_channel(self):
        """
        Fechandoáudio.
        """
        self._is_closing = True

        try:
            # SeID，EnviandogoodbyeMensagem
            if self.session_id:
                goodbye_msg = {"type": "goodbye", "session_id": self.session_id}
                await self.send_text(json.dumps(goodbye_msg))

            # Processandogoodbye
            await self._handle_goodbye()

        except Exception as e:
            logger.error(f"FechandoÁudio: {e}")
            # 
            if self._on_audio_channel_closed:
                await self._on_audio_channel_closed()
        finally:
            self._is_closing = False

    def is_audio_channel_opened(self) -> bool:
        """PesquisaráudioJáAbrindo.

        PesquisarConectandoestado，MQTTeUDPdeestado
        """
        if not self.connected or self._is_closing:
            return False

        # PesquisarMQTTConexãoEstado
        if not self.mqtt_client or not self.mqtt_client.is_connected():
            return False

        # PesquisarUDPConexãoEstado
        return self.udp_socket is not None and self.udp_running

    def aes_ctr_encrypt(self, key, nonce, plaintext):
        """AES-CTRmodo
        Args:
            key: bytesFormatode
            nonce: bytesFormatode
            plaintext: deOriginaldados
        Returns:
            bytesFormatodedados
        """
        cipher = Cipher(
            algorithms.AES(key), modes.CTR(nonce), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        return encryptor.update(plaintext) + encryptor.finalize()

    def aes_ctr_decrypt(self, key, nonce, ciphertext):
        """AES-CTRmodo
        Args:
            key: bytesFormatode
            nonce: bytesFormatode（comUsandode）
            ciphertext: bytesFormatodedados
        Returns:
            bytesFormatodedeOriginaldados
        """
        cipher = Cipher(
            algorithms.AES(key), modes.CTR(nonce), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext

    async def _handle_goodbye(self):
        """
        Processandogoodbyemensagem.
        """
        try:
            # PararUDPRecebendo
            if self.udp_thread and self.udp_thread.is_alive():
                self.udp_running = False
                self.udp_thread.join(1.0)
                self.udp_thread = None
            logger.info("UDPRecebendoJáParar")

            # FechandoUDP
            if self.udp_socket:
                try:
                    self.udp_socket.close()
                except Exception as e:
                    logger.error(f"FechandoUDPFalha: {e}")
                self.udp_socket = None

            # PararMQTT
            if self.mqtt_client:
                try:
                    self.mqtt_client.loop_stop()
                    self.mqtt_client.disconnect()
                    self.mqtt_client.loop_forever()  # DesconectadoConexãoConcluído
                except Exception as e:
                    logger.error(f"DesconectadoMQTTConexão falhou: {e}")
                self.mqtt_client = None

            # Estado
            self.connected = False
            self.session_id = None
            self.local_sequence = 0
            self.remote_sequence = 0
            self.udp_server = ""
            self.udp_port = 0
            self.aes_key = None
            self.aes_nonce = None

            # ÁudioFechando
            if self._on_audio_channel_closed:
                await self._on_audio_channel_closed()

        except Exception as e:
            logger.error(f"ProcessandogoodbyeMensagem: {e}")

    def _stop_udp_receiver(self):
        """
        PararUDPRecebendoeFechandoUDP.
        """
        # FechandoUDPRecebendo
        if (
            hasattr(self, "udp_thread")
            and self.udp_thread
            and self.udp_thread.is_alive()
        ):
            self.udp_running = False
            try:
                self.udp_thread.join(1.0)
            except RuntimeError:
                pass  # ProcessandoJáde

        # FechandoUDP
        if hasattr(self, "udp_socket") and self.udp_socket:
            try:
                self.udp_socket.close()
            except Exception as e:
                logger.error(f"FechandoUDPFalha: {e}")

    def __del__(self):
        """
        ，Fonte.
        """
        # PararUDPRecebendoFonte
        self._stop_udp_receiver()

        # FechandoMQTT
        if hasattr(self, "mqtt_client") and self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                self.mqtt_client.loop_forever()  # DesconectadoConexãoConcluído
            except Exception as e:
                logger.error(f"DesconectadoMQTTConexão falhou: {e}")

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

    async def _connection_monitor(self):
        """
        Conectandoestado.
        """
        try:
            while self.connected and not self._is_closing:
                await asyncio.sleep(30)  # 30SegundosPesquisarVezes

                # PesquisarMQTTConexãoEstado
                if self.mqtt_client and not self.mqtt_client.is_connected():
                    logger.warning("paraMQTTConexãoJáDesconectado")
                    await self._handle_connection_loss("MQTTConexãoFalha")
                    break

                # PesquisarTempo（Timeout）
                if self._last_activity_time:
                    time_since_activity = time.time() - self._last_activity_time
                    if time_since_activity > self._connection_timeout:
                        logger.warning(
                            f"ConexãoTimeout，Tempo: {time_since_activity:.1f}Segundos"
                        )
                        await self._handle_connection_loss("ConexãoTimeout")
                        break

        except asyncio.CancelledError:
            logger.debug("MQTTConexão")
        except Exception as e:
            logger.error(f"MQTTConexãoExceção: {e}")

    async def _handle_connection_loss(self, reason: str):
        """
        ProcessandoConectando.
        """
        logger.warning(f"MQTTConexão: {reason}")

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
                    await self._on_network_error(f"MQTTConexãoReconexãoFalha: {reason}")
                else:
                    await self._on_network_error(f"MQTTConexão: {reason}")

    async def _attempt_reconnect(self, original_reason: str):
        """
        Tentando reconexão automática.
        """
        self._reconnect_attempts += 1

        # NotificandoComeçarReconexão
        if self._on_reconnecting:
            try:
                self._on_reconnecting(
                    self._reconnect_attempts, self._max_reconnect_attempts
                )
            except Exception as e:
                logger.error(f"ReconexãoFalha: {e}")

        logger.info(
            f"Tentando reconexão automática MQTT ({self._reconnect_attempts}/{self._max_reconnect_attempts})"
        )

        # Aguardar um tempo antes de reconectar (backoff exponencial)
        await asyncio.sleep(min(self._reconnect_attempts * 2, 30))

        try:
            success = await self.connect()
            if success:
                logger.info("MQTTAutomáticoReconexãoSucesso")
                # NotificandoConexãoEstadoConversão
                if self._on_connection_state_changed:
                    self._on_connection_state_changed(True, "ReconexãoSucesso")
            else:
                logger.warning(
                    f"Falha na reconexão automática MQTT ({self._reconnect_attempts}/{self._max_reconnect_attempts})"
                )
                # Se ainda puder repetir, não reportar erro imediatamente
                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    if self._on_network_error:
                        await self._on_network_error(
                            f"MQTTReconexãoFalha，JáAtingidoMáximoReconexãoVezes: {original_reason}"
                        )
        except Exception as e:
            logger.error(f"MQTTReconexãoEm: {e}")
            if self._reconnect_attempts >= self._max_reconnect_attempts:
                if self._on_network_error:
                    await self._on_network_error(f"MQTTReconexãoExceção: {str(e)}")

    def enable_auto_reconnect(self, enabled: bool = True, max_attempts: int = 5):
        """ouAutomáticoReconexão.

        Args:
            enabled: AutomáticoReconexão
            max_attempts: MáximoReconexãoTentativaVezes
        """
        self._auto_reconnect_enabled = enabled
        if enabled:
            self._max_reconnect_attempts = max_attempts
            logger.info(f"MQTTAutomáticoReconexão，MáximoTentativaVezes: {max_attempts}")
        else:
            self._max_reconnect_attempts = 0
            logger.info("MQTTAutomáticoReconexão")

    def get_connection_info(self) -> dict:
        """ConectandoInformação.

        Returns:
            dict: Conectandoestado、ReconexãoVezes  AguardarInformaçãode
        """
        return {
            "connected": self.connected,
            "mqtt_connected": (
                self.mqtt_client.is_connected() if self.mqtt_client else False
            ),
            "is_closing": self._is_closing,
            "auto_reconnect_enabled": self._auto_reconnect_enabled,
            "reconnect_attempts": self._reconnect_attempts,
            "max_reconnect_attempts": self._max_reconnect_attempts,
            "last_activity_time": self._last_activity_time,
            "keep_alive_interval": self._keep_alive_interval,
            "connection_timeout": self._connection_timeout,
            "mqtt_endpoint": self.endpoint,
            "udp_server": (
                f"{self.udp_server}:{self.udp_port}" if self.udp_server else None
            ),
            "session_id": self.session_id,
        }

    async def _cleanup_connection(self):
        """
        ConectandoFonte.
        """
        self.connected = False

        # Conexão
        if self._connection_monitor_task and not self._connection_monitor_task.done():
            self._connection_monitor_task.cancel()
            try:
                await self._connection_monitor_task
            except asyncio.CancelledError:
                pass

        # PararUDPRecebendo
        self._stop_udp_receiver()

        # PararMQTT
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except Exception as e:
                logger.error(f"DesconectadoMQTTConexão: {e}")

        # Tempo
        self._last_activity_time = None
