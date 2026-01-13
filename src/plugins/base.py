import asyncio
from typing import Any


class Plugin:
    """
    Mínimoplugin：Período。。
    """

    name: str = "plugin"
    priority: int = 50  # ，Valor（: 1-100）

    def __init__(self) -> None:
        self._started = False

    async def setup(self, app: Any) -> None:
        """
        plugin（Emaplicação run ）。
        """
        await asyncio.sleep(0)

    async def start(self) -> None:
        """
        pluginIniciando（EmprotocoloConectando）。
        """
        self._started = True
        await asyncio.sleep(0)

    async def on_protocol_connected(self, protocol: Any) -> None:
        """
        protocolodeNotificando。
        """
        await asyncio.sleep(0)

    async def on_incoming_json(self, message: Any) -> None:
        """
        Mensagem JSON recebida  deNotificando。
        """
        await asyncio.sleep(0)

    async def on_incoming_audio(self, data: bytes) -> None:
        """
        paraáudiodados  deNotificando。
        """
        await asyncio.sleep(0)

    async def on_device_state_changed(self, state: Any) -> None:
        """
        dispositivoestadoNotificando（aplicação）。
        """
        await asyncio.sleep(0)

    async def stop(self) -> None:
        """
        pluginParar（Emaplicação shutdown ）。
        """
        self._started = False
        await asyncio.sleep(0)

    async def shutdown(self) -> None:
        """
        plugin（Emaplicação shutdown Em）。
        """
        await asyncio.sleep(0)
