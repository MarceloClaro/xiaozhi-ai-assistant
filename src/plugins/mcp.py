from typing import Any, Optional

from src.mcp.mcp_server import McpServer
from src.plugins.base import Plugin
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class McpPlugin(Plugin):
    name = "mcp"
    priority = 20  # ，Inicializando

    def __init__(self) -> None:
        super().__init__()
        self.app: Any = None
        self._server: Optional[McpServer] = None

    async def setup(self, app: Any) -> None:
        self.app = app
        self._server = McpServer.get_instance()

        # Através deAppEnviandoMCP
        async def _send(msg: str):
            try:
                if not self.app or not getattr(self.app, "protocol", None):
                    return
                await self.app.protocol.send_mcp_message(msg)
            except Exception:
                pass

        try:
            self._server.set_send_callback(_send)
            # （ calendar ）。de CalendarPlugin 
            self._server.add_common_tools()
            tools_count = len(self._server.tools)
            logger.info(f"[MCP] Ferramentas registradas: {tools_count}")
            camera_available = any(
                t.name == "take_photo" for t in self._server.tools
            )
            cam_status = "DISPONIVEL" if camera_available else "FALTA"
            logger.info(f"[MCP] Camera tool: {cam_status}")
        except Exception as e:
            logger.error(f"[MCP] Erro ao registrar ferramentas: {e}")
            import traceback
            traceback.print_exc()

    async def on_incoming_json(self, message: Any) -> None:
        if not isinstance(message, dict):
            return
        try:
            # Processando MCP Mensagem
            if message.get("type") == "mcp":
                payload = message.get("payload")
                if not payload:
                    return
                if self._server is None:
                    self._server = McpServer.get_instance()
                await self._server.parse_message(payload)
        except Exception:
            pass

    async def shutdown(self) -> None:
        # ：，GC
        try:
            if self._server:
                self._server.set_send_callback(None)  # type: ignore[arg-type]
        except Exception:
            pass
