from typing import Any, Optional

from src.constants.constants import AbortReason, DeviceState
from src.plugins.base import Plugin


class UIPlugin(Plugin):
    """UI plugin -  CLI/GUI """

    name = "ui"
    priority = 60  # UI EmConcluído  Inicializando

    # DispositivoEstado
    STATE_TEXT_MAP = {
        DeviceState.IDLE: "",
        DeviceState.LISTENING: "Em...",
        DeviceState.SPEAKING: "Em...",
    }

    def __init__(self, mode: Optional[str] = None) -> None:
        super().__init__()
        self.app = None
        self.mode = (mode or "cli").lower()
        self.display = None
        self._is_gui = False
        self.is_first = True

    async def setup(self, app: Any) -> None:
        """
        Inicializando UI plugin.
        """
        self.app = app

        # de display 
        self.display = self._create_display()

        # AppEntrada
        if hasattr(app, "use_console_input"):
            app.use_console_input = False

    def _create_display(self):
        """
        modoCriando display .
        """
        if self.mode == "gui":
            from src.display.gui_display import GuiDisplay

            self._is_gui = True
            return GuiDisplay()
        else:
            from src.display.cli_display import CliDisplay

            self._is_gui = False
            return CliDisplay()

    async def start(self) -> None:
        """
        Iniciando UI .
        """
        if not self.display:
            return

        # 
        await self._setup_callbacks()

        # Iniciando
        self.app.spawn(self.display.start(), name=f"ui:{self.mode}:start")

    async def _setup_callbacks(self) -> None:
        """
        Configurando display .
        """
        if self._is_gui:
            # GUI para
            callbacks = {
                "press_callback": self._wrap_callback(self._press),
                "release_callback": self._wrap_callback(self._release),
                "auto_callback": self._wrap_callback(self._auto_toggle),
                "abort_callback": self._wrap_callback(self._abort),
                "send_text_callback": self._send_text,
            }
        else:
            # CLI 
            callbacks = {
                "auto_callback": self._auto_toggle,
                "abort_callback": self._abort,
                "send_text_callback": self._send_text,
            }

        await self.display.set_callbacks(**callbacks)

    def _wrap_callback(self, coro_func):
        """
        parade lambda.
        """
        return lambda: self.app.spawn(coro_func(), name="ui:callback")

    async def on_incoming_json(self, message: Any) -> None:
        """
        Processandode JSON mensagem.
        """
        if not self.display or not isinstance(message, dict):
            return

        msg_type = message.get("type")

        # tts/stt 
        if msg_type in ("tts", "stt"):
            if text := message.get("text"):
                await self.display.update_text(text)

        # llm 
        elif msg_type == "llm":
            if emotion := message.get("emotion"):
                await self.display.update_emotion(emotion)

    async def on_device_state_changed(self, state: Any) -> None:
        """
        dispositivoestadoConversãoProcessando.
        """
        if not self.display:
            return

        # Vezes
        if self.is_first:
            self.is_first = False
            return

        # eEstado
        await self.display.update_emotion("neutral")
        if status_text := self.STATE_TEXT_MAP.get(state):
            await self.display.update_status(status_text, True)

    async def shutdown(self) -> None:
        """
         UI Fonte，FechandoJanela.
        """
        if self.display:
            await self.display.close()
            self.display = None

    # =====  =====

    async def _send_text(self, text: str):
        """
        Enviandopara.
        """
        if self.app.device_state == DeviceState.SPEAKING:
            audio_plugin = self.app.plugins.get_plugin("audio")
            if audio_plugin:
                await audio_plugin.codec.clear_audio_queue()
            await self.app.abort_speaking(None)
        if await self.app.connect_protocol():
            await self.app.protocol.send_wake_word_detected(text)

    async def _press(self):
        """
        modo：Iniciando.
        """
        await self.app.start_listening_manual()

    async def _release(self):
        """
        modo：Parar.
        """
        await self.app.stop_listening_manual()

    async def _auto_toggle(self):
        """
        Automáticomodo.
        """
        await self.app.start_auto_conversation()

    async def _abort(self):
        """
        Em.
        """
        await self.app.abort_speaking(AbortReason.USER_INTERRUPTION)
