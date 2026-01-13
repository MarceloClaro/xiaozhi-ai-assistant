#!/usr/bin/env python3
"""
Inicializando dispositivo、configuração、OTAconfiguraçãode ativaçãousuário.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict

from src.constants.system import InitializationStage
from src.core.ota import Ota
from src.utils.config_manager import ConfigManager
from src.utils.device_fingerprint import DeviceFingerprint
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class SystemInitializer:
    """sistemaInicializandoDispositivo - """

    def __init__(self):
        self.device_fingerprint = None
        self.config_manager = None
        self.ota = None
        self.current_stage = None
        self.activation_data = None
        self.activation_status = {
            "local_activated": False,  # Estado
            "server_activated": False,  # DispositivoEstado
            "status_consistent": True,  # Estado
        }

    async def run_initialization(self) -> Dict:
        """deInicializando.

        Returns:
            Dict: Inicializando，ativaçãoestadoeativação
        """
        logger.info("ComeçarInicializando")

        try:
            # ：Dispositivo
            await self.stage_1_device_fingerprint()

            # ：Inicializando
            await self.stage_2_config_management()

            # ：OTA
            await self.stage_3_ota_config()

            # Versão
            activation_version = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.ACTIVATION_VERSION", "v1"
            )

            logger.info(f"Versão: {activation_version}")

            # Versão
            if activation_version == "v1":
                # v1：ConcluídoRetornoSucesso
                logger.info("v1：Concluído，")
                return {
                    "success": True,
                    "local_activated": True,
                    "server_activated": True,
                    "status_consistent": True,
                    "need_activation_ui": False,
                    "status_message": "v1Inicialização concluída",
                    "activation_version": activation_version,
                }
            else:
                # v2：Estado
                logger.info("v2：Estado")
                activation_result = self.analyze_activation_status()
                activation_result["activation_version"] = activation_version

                # 
                if activation_result["need_activation_ui"]:
                    logger.info("")
                else:
                    logger.info("，DispositivoJá")

                return activation_result

        except Exception as e:
            logger.error(f"InicializandoFalha: {e}")
            return {"success": False, "error": str(e), "need_activation_ui": False}

    async def stage_1_device_fingerprint(self):
        """
        ：dispositivo.
        """
        self.current_stage = InitializationStage.DEVICE_FINGERPRINT
        logger.info(f"Começar{self.current_stage.value}")

        # InicializandoDispositivo
        self.device_fingerprint = DeviceFingerprint.get_instance()

        # DispositivoInformação
        (
            serial_number,
            hmac_key,
            is_activated,
        ) = self.device_fingerprint.ensure_device_identity()

        # Estado
        self.activation_status["local_activated"] = is_activated

        # MACFormato
        mac_address = self.device_fingerprint.get_mac_address_from_efuse()

        logger.info(f"Dispositivo: {serial_number}")
        logger.info(f"MAC: {mac_address}")
        logger.info(f"HMAC: {hmac_key[:8] if hmac_key else None}...")
        logger.info(f"Estado: {'Já' if is_activated else 'Não'}")

        # Validandoefuse.jsonArquivo
        efuse_file = Path("config/efuse.json")
        if efuse_file.exists():
            logger.info(f"efuse.jsonArquivoPosição: {efuse_file.absolute()}")
            with open(efuse_file, "r", encoding="utf-8") as f:
                efuse_data = json.load(f)
            logger.debug(
                f"efuse.json: "
                f"{json.dumps(efuse_data, indent=2, ensure_ascii=False)}")
        else:
            logger.warning("efuse.jsonArquivoNãoExiste")

        logger.info(f"Concluído{self.current_stage.value}")

    async def stage_2_config_management(self):
        """
        ：configuraçãoInicializando.
        """
        self.current_stage = InitializationStage.CONFIG_MANAGEMENT
        logger.info(f"Começar{self.current_stage.value}")

        # InicializandoDispositivo
        self.config_manager = ConfigManager.get_instance()

        # CLIENT_IDExiste
        self.config_manager.initialize_client_id()

        # deDispositivoInicializandoDEVICE_ID
        self.config_manager.initialize_device_id_from_fingerprint(
            self.device_fingerprint
        )

        # Validando
        client_id = self.config_manager.get_config("SYSTEM_OPTIONS.CLIENT_ID")
        device_id = self.config_manager.get_config("SYSTEM_OPTIONS.DEVICE_ID")

        logger.info(f"ID: {client_id}")
        logger.info(f"DispositivoID: {device_id}")

        logger.info(f"Concluído{self.current_stage.value}")

    async def stage_3_ota_config(self):
        """
        ：OTAconfiguração.
        """
        self.current_stage = InitializationStage.OTA_CONFIG
        logger.info(f"Começar{self.current_stage.value}")

        # InicializandoOTA
        self.ota = await Ota.get_instance()

        # 
        try:
            config_result = await self.ota.fetch_and_update_config()

            logger.info("OTA:")
            mqtt_status = "Já" if config_result["mqtt_config"] else "Não"
            logger.info(f"- MQTT: {mqtt_status}")

            ws_status = "Já" if config_result["websocket_config"] else "Não"
            logger.info(f"- WebSocket: {ws_status}")

            # paradeInformação
            response_data = config_result["response_data"]
            # Informação  EmDebugModo
            logger.debug(
                f"OTADados: {json.dumps(response_data, indent=2, ensure_ascii=False)}"
)
            if "websocket" in response_data:
                ws_info = response_data["websocket"]
                logger.info(f"WebSocket URL: {ws_info.get('url', 'N/A')}")

            # PesquisarInformação
            if "activation" in response_data:
                logger.info("paraInformação，Dispositivo")
                self.activation_data = response_data["activation"]
                # DispositivoparaDispositivoNão
                self.activation_status["server_activated"] = False
            else:
                logger.info("NãoparaInformação，DispositivoJá")
                self.activation_data = None
                # DispositivoparaDispositivoJá
                self.activation_status["server_activated"] = True

        except Exception as e:
            logger.error(f"OTAFalha: {e}")
            raise

        logger.info(f"Concluído{self.current_stage.value}")

    def analyze_activation_status(self) -> Dict:
        """ativaçãoestado，.

        Returns:
            Dict: ，ativaçãoAguardarInformação
        """
        local_activated = self.activation_status["local_activated"]
        server_activated = self.activation_status["server_activated"]

        # PesquisarEstado
        status_consistent = local_activated == server_activated
        self.activation_status["status_consistent"] = status_consistent

        result = {
            "success": True,
            "local_activated": local_activated,
            "server_activated": server_activated,
            "status_consistent": status_consistent,
            "need_activation_ui": False,
            "status_message": "",
        }

        # 1: Não，DispositivoRetornoDados - 
        if not local_activated and not server_activated:
            result["need_activation_ui"] = True
            result["status_message"] = "Dispositivo"

        # 2: Já，DispositivoDados - JáEstado
        elif local_activated and server_activated:
            result["need_activation_ui"] = False
            result["status_message"] = "DispositivoJá"

        # 3: Não，DispositivoDados - EstadoNão，Automático
        elif not local_activated and server_activated:
            logger.warning("EstadoNão: Não，DispositivoparaJá，AutomáticoEstado")
            # AutomáticoEstadoparaJá
            self.device_fingerprint.set_activation_status(True)
            result["need_activation_ui"] = False
            result["status_message"] = "JáAutomáticoEstado"
            result["local_activated"] = True  # EmdeEstado

        # 4: Já，DispositivoRetornoDados - EstadoNão，TentativaAutomático
        elif local_activated and not server_activated:
            logger.warning("EstadoNão: Já，DispositivoparaNão，TentativaAutomático")

            # PesquisarDados
            if self.activation_data and isinstance(self.activation_data, dict):
                # Se，entãoNovamente
                if "code" in self.activation_data:
                    logger.info("DispositivoRetorno，Novamente")
                    result["need_activation_ui"] = True
                    result["status_message"] = "EstadoNão，Novamente"
                else:
                    # Nenhum，DispositivoEstadoNão，TentativaContinuarUsando
                    logger.info("DispositivoNãoRetorno，Estado")
                    result["need_activation_ui"] = False
                    result["status_message"] = "Estado"
            else:
                # NenhumDados，，Estado
                logger.info("NãoparaDados，Estado")
                result["need_activation_ui"] = False
                result["status_message"] = "Estado"
                # ForçarEstado，
                result["status_consistent"] = True
                self.activation_status["status_consistent"] = True
                self.activation_status["server_activated"] = True

        return result

    def get_activation_data(self):
        """
        ativaçãodados（ativaçãoUsando）
        """
        return getattr(self, "activation_data", None)

    def get_device_fingerprint(self):
        """
        dispositivo.
        """
        return self.device_fingerprint

    def get_config_manager(self):
        """
        configuraçãoDispositivo.
        """
        return self.config_manager

    def get_activation_status(self) -> Dict:
        """
        ativaçãoestadoInformação.
        """
        return self.activation_status

    async def handle_activation_process(self, mode: str = "gui") -> Dict:
        """Processandoativação，Criandoativação.

        Args:
            mode: modo，"gui"ou"cli"

        Returns:
            Dict: ativação
        """
        # Inicializando
        init_result = await self.run_initialization()

        # SeNão，Retorno
        if not init_result.get("need_activation_ui", False):
            return {
                "is_activated": True,
                "device_fingerprint": self.device_fingerprint,
                "config_manager": self.config_manager,
            }

        # ，Modo
        if mode == "gui":
            return await self._run_gui_activation()
        else:
            return await self._run_cli_activation()

    async def _run_gui_activation(self) -> Dict:
        """GUIativação.

        Returns:
            Dict: ativação
        """
        try:
            from src.views.activation.activation_window import ActivationWindow

            # Janela
            activation_window = ActivationWindow(self)

            # Future  AguardandoConcluído
            activation_future = asyncio.Future()

            # ConfigurandoConcluído
            def on_activation_completed(success: bool):
                if not activation_future.done():
                    activation_future.set_result(success)

            # ConfigurandoJanelaFechando
            def on_window_closed():
                if not activation_future.done():
                    activation_future.set_result(False)

            # Conexão
            activation_window.activation_completed.connect(on_activation_completed)
            activation_window.window_closed.connect(on_window_closed)

            # Janela
            activation_window.show()

            # AguardandoConcluído
            activation_success = await activation_future

            # FechandoJanela
            activation_window.close()

            return {
                "is_activated": activation_success,
                "device_fingerprint": self.device_fingerprint,
                "config_manager": self.config_manager,
            }

        except Exception as e:
            logger.error(f"GUIExceção: {e}", exc_info=True)
            return {"is_activated": False, "error": str(e)}

    async def _run_cli_activation(self) -> Dict:
        """CLIativação.

        Returns:
            Dict: ativação
        """
        try:
            from src.views.activation.cli_activation import CLIActivation

            # CLIProcessandoDispositivo
            cli_activation = CLIActivation(self)

            # 
            activation_success = await cli_activation.run_activation_process()

            return {
                "is_activated": activation_success,
                "device_fingerprint": self.device_fingerprint,
                "config_manager": self.config_manager,
            }

        except Exception as e:
            logger.error(f"CLIExceção: {e}", exc_info=True)
            return {"is_activated": False, "error": str(e)}
