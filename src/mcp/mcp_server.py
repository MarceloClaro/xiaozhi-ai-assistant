"""
MCP Server Implementation for Python
Reference: https://modelcontextprotocol.io/specification/2024-11-05
"""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from src.constants.system import SystemConstants
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# RetornoValorTipo
ReturnValue = Union[bool, int, str]


class PropertyType(Enum):
    """
    Tipo.
    """

    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"


@dataclass
class Property:
    """
    MCP.
    """

    name: str
    type: PropertyType
    default_value: Optional[Any] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    @property
    def has_default_value(self) -> bool:
        return self.default_value is not None

    @property
    def has_range(self) -> bool:
        return self.min_value is not None and self.max_value is not None

    def value(self, value: Any) -> Any:
        """
        Validando  RetornoValor.
        """
        if self.type == PropertyType.INTEGER and self.has_range:
            if value < self.min_value:
                raise ValueError(
                    f"Value {value} is below minimum allowed: " f"{self.min_value}"
                )
            if value > self.max_value:
                raise ValueError(
                    f"Value {value} exceeds maximum allowed: " f"{self.max_value}"
                )
        return value

    def to_json(self) -> Dict[str, Any]:
        """
        paraJSONFormato.
        """
        result = {"type": self.type.value}

        if self.has_default_value:
            result["default"] = self.default_value

        if self.type == PropertyType.INTEGER:
            if self.min_value is not None:
                result["minimum"] = self.min_value
            if self.max_value is not None:
                result["maximum"] = self.max_value

        return result


@dataclass
class PropertyList:
    """
    .
    """

    properties: List[Property] = field(default_factory=list)

    def __init__(self, properties: Optional[List[Property]] = None):
        """
        Inicializando.
        """
        self.properties = properties or []

    def add_property(self, prop: Property):
        self.properties.append(prop)

    def __getitem__(self, name: str) -> Property:
        for prop in self.properties:
            if prop.name == name:
                return prop
        raise KeyError(f"Property not found: {name}")

    def get_required(self) -> List[str]:
        """
        deNome.
        """
        return [p.name for p in self.properties if not p.has_default_value]

    def to_json(self) -> Dict[str, Any]:
        """
        paraJSONFormato.
        """
        return {prop.name: prop.to_json() for prop in self.properties}

    def parse_arguments(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisando  ValidandoParâmetro.
        """
        result = {}

        for prop in self.properties:
            if arguments and prop.name in arguments:
                value = arguments[prop.name]
                # TipoPesquisar
                if prop.type == PropertyType.BOOLEAN and isinstance(value, bool):
                    result[prop.name] = value
                elif prop.type == PropertyType.INTEGER and isinstance(
                    value, (int, float)
                ):
                    result[prop.name] = prop.value(int(value))
                elif prop.type == PropertyType.STRING and isinstance(value, str):
                    result[prop.name] = value
                else:
                    raise ValueError(f"Invalid type for property {prop.name}")
            elif prop.has_default_value:
                result[prop.name] = prop.default_value
            else:
                raise ValueError(f"Missing required argument: {prop.name}")

        return result


@dataclass
class McpTool:
    """
    MCP.
    """

    name: str
    description: str
    properties: PropertyList
    callback: Callable[[Dict[str, Any]], ReturnValue]

    def to_json(self) -> Dict[str, Any]:
        """
        paraJSONFormato.
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.properties.to_json(),
                "required": self.properties.get_required(),
            },
        }

    async def call(self, arguments: Dict[str, Any]) -> str:
        """
        .
        """
        try:
            # AnalisandoParâmetro
            parsed_args = self.properties.parse_arguments(arguments)

            # 
            if asyncio.iscoroutinefunction(self.callback):
                result = await self.callback(parsed_args)
            else:
                result = self.callback(parsed_args)

            # Formato Conversão RetornoValor
            if isinstance(result, bool):
                text = "true" if result else "false"
            elif isinstance(result, int):
                text = str(result)
            else:
                text = str(result)

            return json.dumps(
                {"content": [{"type": "text", "text": text}], "isError": False}
            )

        except Exception as e:
            logger.error(f"Error calling tool {self.name}: {e}", exc_info=True)
            return json.dumps(
                {"content": [{"type": "text", "text": str(e)}], "isError": True}
            )


class McpServer:
    """
    MCPservidor.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        """
        .
        """
        if cls._instance is None:
            cls._instance = McpServer()
        return cls._instance

    def __init__(self):
        self.tools: List[McpTool] = []
        self._send_callback: Optional[Callable] = None
        self._camera = None

    def set_send_callback(self, callback: Callable):
        """
        ConfigurandoEnviandomensagemde.
        """
        self._send_callback = callback

    def add_tool(self, tool: Union[McpTool, Tuple[str, str, PropertyList, Callable]]):
        """
        .
        """
        if isinstance(tool, tuple):
            # deParâmetroMcpTool
            name, description, properties, callback = tool
            tool = McpTool(name, description, properties, callback)

        # PesquisarJáExiste
        if any(t.name == tool.name for t in self.tools):
            logger.warning(f"Tool {tool.name} already added")
            return

        logger.info(f"Add tool: {tool.name}")
        self.tools.append(tool)

    def add_common_tools(self):
        """
        .
        """
        # 
        original_tools = self.tools.copy()
        self.tools.clear()

        # 
        from src.mcp.tools.system import get_system_tools_manager

        system_manager = get_system_tools_manager()
        system_manager.init_tools(self.add_tool, PropertyList, Property, PropertyType)

        # Agendamento
        from src.mcp.tools.calendar import get_calendar_manager

        calendar_manager = get_calendar_manager()
        calendar_manager.init_tools(self.add_tool, PropertyList, Property, PropertyType)

        # Dispositivo
        from src.mcp.tools.timer import get_timer_manager

        timer_manager = get_timer_manager()
        timer_manager.init_tools(self.add_tool, PropertyList, Property, PropertyType)

        # MúsicaReproduçãoDispositivo
        from src.mcp.tools.music import get_music_tools_manager

        music_manager = get_music_tools_manager()
        music_manager.init_tools(self.add_tool, PropertyList, Property, PropertyType)

        # 
        from src.mcp.tools.camera import take_photo

        # take_photo
        properties = PropertyList([
            Property("question", PropertyType.STRING),
            Property("context", PropertyType.STRING, default_value="")
        ])
        VISION_DESC = (
            "【】para：、、、、、、、Identificando、"
            "、、、、 。\n"
            "：，de。\n"
            "Usando：\n"
            "1.  (: '', '', '')\n"
            "2. /Identificando ('', '', 'Identificando')\n"
            "3. TextoIdentificandoOCR ('de', 'Texto', 'de')\n"
            "4.  ('', '', '')\n\n"
            "Parâmetro：\n"
            "- question: Caracteres  Tipo，dede\n"
            "- context: Contexto adicional/prompt para análise (opcional)\n\n"
            "Usando：''、''、''Aguardar，UsandoIdentificando。\n"
            "English: Take a photo and explain it. Use this tool after the user asks you to see something.\n"
            "Args: `question` - The question that you want to ask about the photo.\n"
            "      `context` - Additional context or instructions for the analysis (optional).\n"
            "Return: A JSON object that provides the photo information.\n"
            "Examples: '', '', '', 'take a photo', 'what is this'."
        )

        self.add_tool(
            McpTool(
                "take_photo",  # 
                VISION_DESC,
                properties,
                take_photo,
            )
        )

        # 
        from src.mcp.tools.screenshot import take_screenshot

        # take_screenshot
        screenshot_properties = PropertyList(
            [
                Property("question", PropertyType.STRING),
                Property("display", PropertyType.STRING, default_value=None),
            ]
        )
        SCREENSHOT_DESC = (
            "【/】para：、、、、、"
            "、Pesquisar、、、OCR 。"
            "：①；②Identificandocom；③OCRTexto；④；"
            "⑤AplicaçãoIdentificando；⑥ErroInformação；⑦EstadoPesquisar；⑧。"
            "Parâmetro：{ question: 'de/de', display: 'DispositivoSelecionando()' }；"
            "displayValor：'main'/''/''(Dispositivo), 'secondary'/''/''(Dispositivo), ou(Dispositivo)；"
            "：、、、AppEstadoPesquisar、ErroAguardar。"
            "：，Operação。"
            "English: Desktop screenshot/screen analysis tool. Use when user mentions: screenshot, screen capture, "
            "desktop analysis, screen content, current interface, screen OCR, etc. "
            "Functions: ①Full desktop capture; ②Screen content recognition; ③Screen OCR; ④Interface analysis; "
            "⑤Application identification; ⑥Error screenshot analysis; ⑦Desktop status check. "
            "Parameters: { question: 'Question about desktop/screen', display: 'Display selection (optional)' }; "
            "Display options: 'main'(primary), 'secondary'(external), or empty(all displays). "
            "Examples: '', 'Pesquisar', '', 'deTexto'。"
        )

        self.add_tool(
            McpTool(
                "take_screenshot",
                SCREENSHOT_DESC,
                screenshot_properties,
                take_screenshot,
            )
        )

        # 
        from src.mcp.tools.bazi import get_bazi_manager

        bazi_manager = get_bazi_manager()
        bazi_manager.init_tools(self.add_tool, PropertyList, Property, PropertyType)

        # Restaurando
        self.tools.extend(original_tools)

    async def parse_message(self, message: Union[str, Dict[str, Any]]):
        """
        AnalisandoMCPmensagem.
        """
        try:
            if isinstance(message, str):
                data = json.loads(message)
            else:
                data = message

            logger.info(
                f"[MCP] Analisando mensagem: {json.dumps(data, ensure_ascii=False, indent=2)}"
            )

            # PesquisarJSONRPCVersão
            if data.get("jsonrpc") != "2.0":
                logger.error(f"Invalid JSONRPC version: {data.get('jsonrpc')}")
                return

            method = data.get("method")
            if not method:
                logger.error("Missing method")
                return

            # Notificando
            if method.startswith("notifications"):
                logger.info(f"[MCP] NotificandoMensagem: {method}")
                return

            params = data.get("params", {})
            id = data.get("id")

            if id is None:
                logger.error(f"Invalid id for method: {method}")
                return

            logger.info(f"[MCP] Processando: {method}, ID: {id}, Parâmetro: {params}")

            # ProcessandoNão  de
            if method == "initialize":
                await self._handle_initialize(id, params)
            elif method == "tools/list":
                await self._handle_tools_list(id, params)
            elif method == "tools/call":
                await self._handle_tool_call(id, params)
            else:
                logger.error(f"Method not implemented: {method}")
                await self._reply_error(id, f"Method not implemented: {method}")

        except Exception as e:
            logger.error(f"Error parsing MCP message: {e}", exc_info=True)
            if "id" in locals():
                await self._reply_error(id, str(e))

    async def _handle_initialize(self, id: int, params: Dict[str, Any]):
        """
        ProcessandoInicializando.
        """
        # Analisandocapabilities
        capabilities = params.get("capabilities", {})
        await self._parse_capabilities(capabilities)

        # RetornoDispositivoInformação
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": SystemConstants.APP_NAME,
                "version": SystemConstants.APP_VERSION,
            },
        }

        await self._reply_result(id, result)

    async def _handle_tools_list(self, id: int, params: Dict[str, Any]):
        """
        Processando.
        """
        cursor = params.get("cursor", "")
        max_payload_size = 8000

        tools_json = []
        total_size = 0
        found_cursor = not cursor
        next_cursor = ""

        for tool in self.tools:
            # SeAinda  EncontradoPosição，ContinuarPesquisa
            if not found_cursor:
                if tool.name == cursor:
                    found_cursor = True
                else:
                    continue

            # PesquisarTamanho
            tool_json = tool.to_json()
            tool_size = len(json.dumps(tool_json))

            if total_size + tool_size + 100 > max_payload_size:
                next_cursor = tool.name
                break

            tools_json.append(tool_json)
            total_size += tool_size

        result = {"tools": tools_json}
        if next_cursor:
            result["nextCursor"] = next_cursor

        await self._reply_result(id, result)

    async def _handle_tool_call(self, id: int, params: Dict[str, Any]):
        """
        Processando.
        """
        logger.info(f"[MCP] para! ID={id}, Parâmetro={params}")

        tool_name = params.get("name")
        if not tool_name:
            await self._reply_error(id, "Missing tool name")
            return

        logger.info(f"[MCP] Tentativa: {tool_name}")

        # Pesquisar
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break

        if not tool:
            await self._reply_error(id, f"Unknown tool: {tool_name}")
            return

        # Parâmetro
        arguments = params.get("arguments", {})

        logger.info(f"[MCP] Começar {tool_name}, Parâmetro: {arguments}")

        # 
        try:
            result = await tool.call(arguments)
            logger.info(f"[MCP]  {tool_name} Sucesso，: {result}")
            await self._reply_result(id, json.loads(result))
        except Exception as e:
            logger.error(f"[MCP]  {tool_name} Falha: {e}", exc_info=True)
            await self._reply_error(id, str(e))

    async def _parse_capabilities(self, capabilities):
        """
        Analisandocapabilities.
        """
        vision = capabilities.get("vision", {})
        if vision and isinstance(vision, dict):
            url = vision.get("url")
            token = vision.get("token")
            if url:
                from src.mcp.tools.camera import get_camera_instance

                camera = get_camera_instance()
                if hasattr(camera, "set_explain_url"):
                    camera.set_explain_url(url)
                if token and hasattr(camera, "set_explain_token"):
                    camera.set_explain_token(token)
                logger.info(f"Vision service configured with URL: {url}")

    async def _reply_result(self, id: int, result: Any):
        """
        Enviandosucesso.
        """
        payload = {"jsonrpc": "2.0", "id": id, "result": result}

        result_len = len(json.dumps(result))
        logger.info(f"[MCP] EnviandoSucesso: ID={id}, Comprimento={result_len}")

        if self._send_callback:
            await self._send_callback(json.dumps(payload))
        else:
            logger.error("[MCP] EnviandoNãoConfigurando!")

    async def _reply_error(self, id: int, message: str):
        """
        Enviandoerro.
        """
        payload = {"jsonrpc": "2.0", "id": id, "error": {"message": message}}

        logger.error(f"[MCP] EnviandoErro: ID={id}, Erro={message}")

        if self._send_callback:
            await self._send_callback(json.dumps(payload))
