import asyncio
import json
import socket
import ssl

import aiohttp

from src.constants.system import SystemConstants
from src.utils.config_manager import ConfigManager
from src.utils.device_fingerprint import DeviceFingerprint
from src.utils.logging_config import get_logger


class Ota:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager.get_instance()
        self.device_fingerprint = DeviceFingerprint.get_instance()
        self.mac_addr = None
        self.ota_version_url = None
        self.local_ip = None
        self.system_info = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    instance = cls()
                    await instance.init()
                    cls._instance = instance
        return cls._instance

    async def init(self):
        """
        InicializandoOTA.
        """
        self.local_ip = await self.get_local_ip()
        # deEmDispositivoID（MAC）
        self.mac_addr = self.config.get_config("SYSTEM_OPTIONS.DEVICE_ID")
        # OTA URL
        self.ota_version_url = self.config.get_config(
            "SYSTEM_OPTIONS.NETWORK.OTA_VERSION_URL"
        )

    async def get_local_ip(self):
        """
        IP.
        """
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._sync_get_ip)
        except Exception as e:
            self.logger.error(f" IP Falha：{e}")
            return "127.0.0.1"

    def _sync_get_ip(self):
        """
        IP.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

    def build_payload(self):
        """
        OTAdepayload.
        """
        # deefuse.jsonhmac_key  paraelf_sha256
        hmac_key = self.device_fingerprint.get_hmac_key()
        elf_sha256 = hmac_key if hmac_key else "unknown"

        return {
            "application": {
                "version": SystemConstants.APP_VERSION,
                "elf_sha256": elf_sha256,
            },
            "board": {
                "type": SystemConstants.BOARD_TYPE,
                "name": SystemConstants.APP_NAME,
                "ip": self.local_ip,
                "mac": self.mac_addr,
            },
        }

    def build_headers(self):
        """
        OTAdeheaders.
        """
        app_version = SystemConstants.APP_VERSION
        board_type = SystemConstants.BOARD_TYPE
        app_name = SystemConstants.APP_NAME

        #
        headers = {
            "Device-Id": self.mac_addr,
            "Client-Id": self.config.get_config("SYSTEM_OPTIONS.CLIENT_ID"),
            "Content-Type": "application/json",
            "User-Agent": f"{board_type}/{app_name}-{app_version}",
            "Accept-Language": "zh-CN",
        }

        # VersãoActivation-Version
        activation_version = self.config.get_config(
            "SYSTEM_OPTIONS.NETWORK.ACTIVATION_VERSION", "v1"
        )

        # v2Activation-Version
        if activation_version == "v2":
            headers["Activation-Version"] = app_version
            self.logger.debug(f"v2：Activation-Version: {app_version}")
        else:
            self.logger.debug("v1：NãoActivation-Version")

        return headers

    async def get_ota_config(self):
        """
        OTAservidordeconfiguraçãoInformação（MQTT、WebSocketAguardar）
        """
        if not self.mac_addr:
            self.logger.error("DispositivoID(MAC)Não")
            raise ValueError("dispositivoIDNãoconfiguração")

        if not self.ota_version_url:
            self.logger.error("OTA URLNão")
            raise ValueError("OTA URLNãoconfiguração")

        headers = self.build_headers()
        payload = self.build_payload()

        try:
            # SSLValidando  Suportado
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # UsandoaiohttpEnviando
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(
                timeout=timeout, connector=connector
            ) as session:
                async with session.post(
                    self.ota_version_url, headers=headers, json=payload
                ) as response:
                    # PesquisarHTTPEstado
                    if response.status != 200:
                        self.logger.error(f"OTADispositivoErro: HTTP {response.status}")
                        raise ValueError(
                            f"OTADispositivoRetornoErroEstado: {response.status}"
                        )

                    # AnalisandoJSONDados
                    response_data = await response.json()

                    # DebugInformação：deOTA
                    self.logger.debug(
                        "OTADispositivoRetornoDados: %s",
                        json.dumps(response_data, indent=4, ensure_ascii=False),
                    )

                    return response_data

        except asyncio.TimeoutError:
            self.logger.error("OTATimeout，PesquisarouDispositivoEstado")
            raise ValueError("OTATimeout！Tentar novamente。")

        except aiohttp.ClientError as e:
            self.logger.error(f"OTAFalha: {e}")
            raise ValueError(
                "Incapaz deConectandoparaOTAservidor，PesquisarredeConectando！"
            )

    async def update_mqtt_config(self, response_data):
        """
        MQTTconfiguraçãoInformação.
        """
        if "mqtt" in response_data:
            self.logger.info("MQTTInformação")
            mqtt_info = response_data["mqtt"]
            if mqtt_info:
                #
                success = self.config.update_config(
                    "SYSTEM_OPTIONS.NETWORK.MQTT_INFO", mqtt_info
                )
                if success:
                    self.logger.info("MQTTJá")
                    return mqtt_info
                else:
                    self.logger.error("MQTTFalha")
            else:
                self.logger.warning("MQTTpara")
        else:
            self.logger.info("NãoMQTTInformação")

        return None

    async def update_websocket_config(self, response_data):
        """
        WebSocketconfiguraçãoInformação.
        """
        if "websocket" in response_data:
            self.logger.info("WebSocketInformação")
            websocket_info = response_data["websocket"]

            # WebSocket URL
            if "url" in websocket_info:
                self.config.update_config(
                    "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_URL", websocket_info["url"]
                )
                self.logger.info(f"WebSocket URLJá: {websocket_info['url']}")

            # WebSocket Token
            token_value = websocket_info.get("token", "test-token") or "test-token"
            self.config.update_config(
                "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_ACCESS_TOKEN", token_value
            )
            self.logger.info("WebSocket TokenJá")

            return websocket_info
        else:
            self.logger.info("NãoWebSocketInformação")

        return None

    async def fetch_and_update_config(self):
        """
        configuraçãoInformação.
        """
        try:
            # OTA
            response_data = await self.get_ota_config()

            # MQTT
            mqtt_config = await self.update_mqtt_config(response_data)

            # WebSocket
            websocket_config = await self.update_websocket_config(response_data)

            # RetornodeDados，Usando
            return {
                "response_data": response_data,
                "mqtt_config": mqtt_config,
                "websocket_config": websocket_config,
            }

        except Exception as e:
            self.logger.error(f"Falha: {e}")
            raise
