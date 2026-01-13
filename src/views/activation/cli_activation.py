# -*- coding: utf-8 -*-
"""
CLImododispositivoativação comGUIativaçãoJanelade，UsandoSaída.
"""

from datetime import datetime
from typing import Optional

from src.core.system_initializer import SystemInitializer
from src.utils.device_activator import DeviceActivator
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class CLIActivation:
    """
    CLImododispositivoativaçãoProcessandoDispositivo.
    """

    def __init__(self, system_initializer: Optional[SystemInitializer] = None):
        # 
        self.system_initializer = system_initializer
        self.device_activator: Optional[DeviceActivator] = None

        # Estado
        self.current_stage = None
        self.activation_data = None
        self.is_activated = False

        self.logger = logger

    async def run_activation_process(self) -> bool:
        """deCLIativação.

        Returns:
            bool: Se a ativação foi bem-sucedida
        """
        try:
            self._print_header()

            # SeJáSystemInitializer，Usando
            if self.system_initializer:
                self._log_and_print("UsandoInicializandode")
                self._update_device_info()
                return await self._start_activation_process()
            else:
                # entãodeInicializando
                self._log_and_print("ComeçarInicializando")
                self.system_initializer = SystemInitializer()

                # Inicializando
                init_result = await self.system_initializer.run_initialization()

                if init_result.get("success", False):
                    self._update_device_info()

                    # EstadoMensagem
                    status_message = init_result.get("status_message", "")
                    if status_message:
                        self._log_and_print(status_message)

                    # Pesquisar
                    if init_result.get("need_activation_ui", True):
                        return await self._start_activation_process()
                    else:
                        # ，Concluído
                        self.is_activated = True
                        self._log_and_print("DispositivoJá，Operação")
                        return True
                else:
                    error_msg = init_result.get("error", "InicializandoFalha")
                    self._log_and_print(f"Erro: {error_msg}")
                    return False

        except KeyboardInterrupt:
            self._log_and_print("\nEm")
            return False
        except Exception as e:
            self.logger.error(f"CLIExceção: {e}", exc_info=True)
            self._log_and_print(f"Exceção: {e}")
            return False

    def _print_header(self):
        """
        CLIativaçãoInformação.
        """
        print("\n" + "=" * 60)
        print("AI - Dispositivo")
        print("=" * 60)
        print("EmInicializandoDispositivo，...")
        print()

    def _update_device_info(self):
        """
        dispositivoInformação.
        """
        if (
            not self.system_initializer
            or not self.system_initializer.device_fingerprint
        ):
            return

        device_fp = self.system_initializer.device_fingerprint

        # DispositivoInformação
        serial_number = device_fp.get_serial_number()
        mac_address = device_fp.get_mac_address_from_efuse()

        # Estado
        activation_status = self.system_initializer.get_activation_status()
        local_activated = activation_status.get("local_activated", False)
        server_activated = activation_status.get("server_activated", False)
        status_consistent = activation_status.get("status_consistent", True)

        # Estado
        self.is_activated = local_activated

        # DispositivoInformação
        print("📱 DispositivoInformação:")
        print(f"   : {serial_number if serial_number else '--'}")
        print(f"   MAC: {mac_address if mac_address else '--'}")

        # Estado
        if not status_consistent:
            if local_activated and not server_activated:
                status_text = "EstadoNão(Novamente)"
            else:
                status_text = "EstadoNão(JáAutomático)"
        else:
            status_text = "Já" if local_activated else "Não"

        print(f"   Estado: {status_text}")

    async def _start_activation_process(self) -> bool:
        """
        Iniciandoativação.
        """
        try:
            # Dados
            activation_data = self.system_initializer.get_activation_data()

            if not activation_data:
                self._log_and_print("\nNãoparaDados")
                print("Erro: NãoparaDados，PesquisarConexão")
                return False

            self.activation_data = activation_data

            # Informação
            self._show_activation_info(activation_data)

            # InicializandoDispositivoDispositivo
            config_manager = self.system_initializer.get_config_manager()
            self.device_activator = DeviceActivator(config_manager)

            # Começar
            self._log_and_print("\nComeçarDispositivo...")
            print("EmConexãoDispositivo，Conexão...")

            activation_success = await self.device_activator.process_activation(
                activation_data
            )

            if activation_success:
                self._log_and_print("\nDispositivoSucesso！")
                self._print_activation_success()
                return True
            else:
                self._log_and_print("\nDispositivoFalha")
                self._print_activation_failure()
                return False

        except Exception as e:
            self.logger.error(f"Exceção: {e}", exc_info=True)
            self._log_and_print(f"\nExceção: {e}")
            return False

    def _show_activation_info(self, activation_data: dict):
        """
        ativaçãoInformação.
        """
        code = activation_data.get("code", "------")
        message = activation_data.get("message", "xiaozhi.meEntradaValidando")

        print("\n" + "=" * 60)
        print("DispositivoInformação")
        print("=" * 60)
        print(f"Validando: {code}")
        print(f": {message}")
        print("=" * 60)

        # FormatoConversãoValidando（Caracteres）
        formatted_code = " ".join(code)
        print(f"\nValidando（EmEntrada）: {formatted_code}")
        print("\nConcluído:")
        print("1. AbrindoDispositivo xiaozhi.me")
        print("2. de")
        print("3. SelecionandoDispositivo")
        print(f"4. EntradaValidando: {formatted_code}")
        print("5. Dispositivo")
        print("\nAguardandoEm，EmConcluídoOperação...")

        self._log_and_print(f"Validando: {code}")
        self._log_and_print(f": {message}")

    def _print_activation_success(self):
        """
        ativaçãosucessoInformação.
        """
        print("\n" + "=" * 60)
        print("DispositivoSucesso！")
        print("=" * 60)
        print("DispositivoJáSucessopara  de")
        print("ConfiguraçãoJáAutomático")
        print("IniciandoAI...")
        print("=" * 60)

    def _print_activation_failure(self):
        """
        ativaçãofalhouInformação.
        """
        print("\n" + "=" * 60)
        print("DispositivoFalha")
        print("=" * 60)
        print("deMotivo:")
        print("• ConexãoNão")
        print("• ValidandoEntradaErroouJá")
        print("• DispositivoNão")
        print("\n:")
        print("• PesquisarConexão")
        print("• NovamenteValidando")
        print("• EmEntradaValidando")
        print("=" * 60)

    def _log_and_print(self, message: str):
        """
        Logepara.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.logger.info(message)

    def get_activation_result(self) -> dict:
        """
        ativação.
        """
        device_fingerprint = None
        config_manager = None

        if self.system_initializer:
            device_fingerprint = self.system_initializer.device_fingerprint
            config_manager = self.system_initializer.config_manager

        return {
            "is_activated": self.is_activated,
            "device_fingerprint": device_fingerprint,
            "config_manager": config_manager,
        }
