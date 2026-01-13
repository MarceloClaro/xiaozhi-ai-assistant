import json

from src.constants.constants import AbortReason, ListeningMode
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class Protocol:
    def __init__(self):
        self.session_id = ""
        # InicializandoparaNone
        self._on_incoming_json = None
        self._on_incoming_audio = None
        self._on_audio_channel_opened = None
        self._on_audio_channel_closed = None
        self._on_network_error = None
        # ConexãoEstadoConversão
        self._on_connection_state_changed = None
        self._on_reconnecting = None

    def on_incoming_json(self, callback):
        """
        ConfigurandoJSONmensagemRecebendo.
        """
        self._on_incoming_json = callback

    def on_incoming_audio(self, callback):
        """
        ConfigurandoáudiodadosRecebendo.
        """
        self._on_incoming_audio = callback

    def on_audio_channel_opened(self, callback):
        """
        ConfigurandoáudioAbrindo.
        """
        self._on_audio_channel_opened = callback

    def on_audio_channel_closed(self, callback):
        """
        ConfigurandoáudioFechando.
        """
        self._on_audio_channel_closed = callback

    def on_network_error(self, callback):
        """
        Configurandoredeerro.
        """
        self._on_network_error = callback

    def on_connection_state_changed(self, callback):
        """ConfigurandoConectandoestadoConversão.

        Args:
            callback: ，RecebendoParâmetro (connected: bool, reason: str)
        """
        self._on_connection_state_changed = callback

    def on_reconnecting(self, callback):
        """ConfigurandoReconexãoTentativa.

        Args:
            callback: ，RecebendoParâmetro (attempt: int, max_attempts: int)
        """
        self._on_reconnecting = callback

    async def send_text(self, message):
        """
        Enviandomensagemde，EmEm.
        """
        raise NotImplementedError("send_text")

    async def send_audio(self, data: bytes):
        """
        Enviandoáudiodadosde，EmEm.
        """
        raise NotImplementedError("send_audio")

    def is_audio_channel_opened(self) -> bool:
        """
        PesquisaráudioAbrindode，EmEm.
        """
        raise NotImplementedError("is_audio_channel_opened")

    async def open_audio_channel(self) -> bool:
        """
        Abrindoáudiode，EmEm.
        """
        raise NotImplementedError("open_audio_channel")

    async def close_audio_channel(self):
        """
        Fechandoáudiode，EmEm.
        """
        raise NotImplementedError("close_audio_channel")

    async def send_abort_speaking(self, reason):
        """
        EnviandoEmdemensagem.
        """
        message = {"session_id": self.session_id, "type": "abort"}
        if reason == AbortReason.WAKE_WORD_DETECTED:
            message["reason"] = "wake_word_detected"
        await self.send_text(json.dumps(message))

    async def send_wake_word_detected(self, wake_word):
        """
        Enviandoparademensagem.
        """
        message = {
            "session_id": self.session_id,
            "type": "listen",
            "state": "detect",
            "text": wake_word,
        }
        await self.send_text(json.dumps(message))

    async def send_start_listening(self, mode):
        """
        EnviandoIniciandodemensagem.
        """
        mode_map = {
            ListeningMode.REALTIME: "realtime",
            ListeningMode.AUTO_STOP: "auto",
            ListeningMode.MANUAL: "manual",
        }
        message = {
            "session_id": self.session_id,
            "type": "listen",
            "state": "start",
            "mode": mode_map[mode],
        }
        await self.send_text(json.dumps(message))

    async def send_stop_listening(self):
        """
        EnviandoParardemensagem.
        """
        message = {"session_id": self.session_id, "type": "listen", "state": "stop"}
        await self.send_text(json.dumps(message))

    async def send_iot_descriptors(self, descriptors):
        """
        EnviandodispositivoInformação.
        """
        try:
            # AnalisandoDados
            if isinstance(descriptors, str):
                descriptors_data = json.loads(descriptors)
            else:
                descriptors_data = descriptors

            # Pesquisarpara
            if not isinstance(descriptors_data, list):
                logger.error("IoT descriptors should be an array")
                return

            # paraEnviandodeMensagem
            for i, descriptor in enumerate(descriptors_data):
                if descriptor is None:
                    logger.error(f"Failed to get IoT descriptor at index {i}")
                    continue

                message = {
                    "session_id": self.session_id,
                    "type": "iot",
                    "update": True,
                    "descriptors": [descriptor],
                }

                try:
                    await self.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(
                        f"Failed to send JSON message for IoT descriptor "
                        f"at index {i}: {e}")
                    continue

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse IoT descriptors: {e}")
            return

    async def send_iot_states(self, states):
        """
        EnviandodispositivoestadoInformação.
        """
        if isinstance(states, str):
            states_data = json.loads(states)
        else:
            states_data = states

        message = {
            "session_id": self.session_id,
            "type": "iot",
            "update": True,
            "states": states_data,
        }
        await self.send_text(json.dumps(message))

    async def send_mcp_message(self, payload):
        """
        EnviandoMCPmensagem.
        """
        if isinstance(payload, str):
            payload_data = json.loads(payload)
        else:
            payload_data = payload

        message = {
            "session_id": self.session_id,
            "type": "mcp",
            "payload": payload_data,
        }

        await self.send_text(json.dumps(message))
