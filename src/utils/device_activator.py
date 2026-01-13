import asyncio
import json
from typing import Optional

import aiohttp

from src.utils.common_utils import handle_verification_code
from src.utils.device_fingerprint import DeviceFingerprint
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DeviceActivator:
    """dispositivoativaçãoDispositivo - Versão"""

    def __init__(self, config_manager):
        """
        InicializandodispositivoativaçãoDispositivo.
        """
        self.logger = get_logger(__name__)
        self.config_manager = config_manager
        # Usandodevice_fingerprintDispositivo
        self.device_fingerprint = DeviceFingerprint.get_instance()
        # DispositivoInformaçãoJá
        self._ensure_device_identity()

        # 
        self._activation_task: Optional[asyncio.Task] = None

    def _ensure_device_identity(self):
        """
        dispositivoInformaçãoJáCriando.
        """
        (
            serial_number,
            hmac_key,
            is_activated,
        ) = self.device_fingerprint.ensure_device_identity()
        self.logger.info(
            f"Informação de Identidade do Dispositivo: Número de série: {serial_number}, Estado de Ativação: {'Já ativado' if is_activated else 'Não ativado'}"
        )

    def cancel_activation(self):
        """
        ativação.
        """
        if self._activation_task and not self._activation_task.done():
            self.logger.info("Em")
            self._activation_task.cancel()

    def has_serial_number(self) -> bool:
        """
        Pesquisar.
        """
        return self.device_fingerprint.has_serial_number()

    def get_serial_number(self) -> str:
        """
        .
        """
        return self.device_fingerprint.get_serial_number()

    def get_hmac_key(self) -> str:
        """
        HMAC.
        """
        return self.device_fingerprint.get_hmac_key()

    def set_activation_status(self, status: bool) -> bool:
        """
        Configurandoativaçãoestado.
        """
        return self.device_fingerprint.set_activation_status(status)

    def is_activated(self) -> bool:
        """
        PesquisardispositivoJáativação.
        """
        return self.device_fingerprint.is_activated()

    def generate_hmac(self, challenge: str) -> str:
        """
        UsandoHMAC.
        """
        return self.device_fingerprint.generate_hmac(challenge)

    async def process_activation(self, activation_data: dict) -> bool:
        """Processandoativação.

        Args:
            activation_data: ativaçãoInformaçãode，challengeecode

        Returns:
            bool: Se a ativação foi bem-sucedida
        """
        try:
            # 
            self._activation_task = asyncio.current_task()

            # PesquisareValidando
            if not activation_data.get("challenge"):
                self.logger.error("DadosEmchallenge")
                return False

            if not activation_data.get("code"):
                self.logger.error("DadosEmcode")
                return False

            challenge = activation_data["challenge"]
            code = activation_data["code"]
            message = activation_data.get("message", "Emxiaozhi.meEntradaValidando")

            # Pesquisar
            if not self.has_serial_number():
                self.logger.error("DispositivoNenhum，Incapaz de")

                # Usandodevice_fingerprinteHMAC
                (
                    serial_number,
                    hmac_key,
                    _,
                ) = self.device_fingerprint.ensure_device_identity()

                if serial_number and hmac_key:
                    self.logger.info("JáAutomáticoDispositivoeHMAC")
                else:
                    self.logger.error("ouHMACFalha")
                    return False

            # Informaçãopara
            self.logger.info(f": {message}")
            self.logger.info(f"Validando: {code}")

            # Validando
            text = f".paraDispositivo，EntradaValidando：{' '.join(code)}..."
            print("\n==================")
            print(text)
            print("==================\n")
            handle_verification_code(text)

            # UsandoReproduçãoValidando
            try:
                # EmdeEmReprodução
                from src.utils.common_utils import play_audio_nonblocking

                play_audio_nonblocking(text)
                self.logger.info("EmReproduçãoValidando")
            except Exception as e:
                self.logger.error(f"ReproduçãoValidandoFalha: {e}")

            # TentativaDispositivo，Validando  Informação
            return await self.activate(challenge, code)

        except asyncio.CancelledError:
            self.logger.info("")
            return False

    async def activate(self, challenge: str, code: str = None) -> bool:
        """ativação.

        Args:
            challenge: servidorEnviandodeCaracteres
            code: Validando，Tentar novamente  Reprodução

        Returns:
            bool: Se a ativação foi bem-sucedida
        """
        try:
            # Pesquisar
            serial_number = self.get_serial_number()
            if not serial_number:
                self.logger.error(
                    "DispositivoNenhum，Incapaz deConcluídoHMACValidando"
                )
                return False

            # HMAC
            hmac_signature = self.generate_hmac(challenge)
            if not hmac_signature:
                self.logger.error("Incapaz deHMAC，Falha")
                return False

            # payload，DispositivoFormato
            payload = {
                "Payload": {
                    "algorithm": "hmac-sha256",
                    "serial_number": serial_number,
                    "challenge": challenge,
                    "hmac": hmac_signature,
                }
            }

            # URL
            ota_url = self.config_manager.get_config(
                "SYSTEM_OPTIONS.NETWORK.OTA_VERSION_URL"
            )
            if not ota_url:
                self.logger.error("NãoEncontradoOTA URL")
                return False

            # URL
            if not ota_url.endswith("/"):
                ota_url += "/"

            activate_url = f"{ota_url}activate"
            self.logger.info(f"URL: {activate_url}")

            # Configurando
            headers = {
                "Activation-Version": "2",
                "Device-Id": self.config_manager.get_config("SYSTEM_OPTIONS.DEVICE_ID"),
                "Client-Id": self.config_manager.get_config("SYSTEM_OPTIONS.CLIENT_ID"),
                "Content-Type": "application/json",
            }

            # DebugInformação
            self.logger.debug(f": {headers}")
            payload_str = json.dumps(payload, indent=2, ensure_ascii=False)
            self.logger.debug(f": {payload_str}")

            # Tentar novamente
            max_retries = 60  # Aguardando5
            retry_interval = 5  # Configurando5SegundosdeTentar novamente

            error_count = 0
            last_error = None

            # aiohttp，ConfigurandodeTimeoutTempo
            timeout = aiohttp.ClientTimeout(total=10)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                for attempt in range(max_retries):
                    try:
                        self.logger.info(
                            f"Tentativa de Ativação (Tentativa {attempt + 1}/{max_retries})..."
                        )

                        # Cada vez que Tentar novamente, Validação de código (a partir da 2ª tentativa)
                        if attempt > 0 and code:
                            try:
                                from src.utils.common_utils import (
                                    play_audio_nonblocking,
                                )

                                text = f".paraDispositivo，EntradaValidando：{' '.join(code)}..."
                                play_audio_nonblocking(text)
                                self.logger.info(
                                    f"Tentar novamenteReproduçãoValidando: {code}"
                                )
                            except Exception as e:
                                self.logger.error(
                                    f"Tentar novamenteReproduçãoValidando  Falha: {e}"
                                )

                        # Enviando
                        async with session.post(
                            activate_url, headers=headers, json=payload
                        ) as response:
                            # 
                            response_text = await response.text()

                            # 
                            self.logger.warning(f"\n (HTTP {response.status}):")
                            try:
                                response_json = json.loads(response_text)
                                self.logger.warning(json.dumps(response_json, indent=2))
                            except json.JSONDecodeError:
                                self.logger.warning(response_text)

                            # PesquisarEstado
                            if response.status == 200:
                                # Sucesso
                                self.logger.info("DispositivoSucesso!")
                                self.set_activation_status(True)
                                return True

                            elif response.status == 202:
                                # AguardandoEntradaValidando
                                self.logger.info(
                                    "AguardandoEntradaValidando，ContinuarAguardando..."
                                )

                                # UsandodeAguardando
                                await asyncio.sleep(retry_interval)

                            else:
                                # ProcessandoErro  ContinuarTentar novamente
                                error_msg = "Não  Erro"
                                try:
                                    error_data = json.loads(response_text)
                                    error_msg = error_data.get(
                                        "error",
                                        f"Não  Erro (Estado: {response.status})",
                                    )
                                except json.JSONDecodeError:
                                    error_msg = f"DispositivoRetornoErro (Estado: {response.status})"

                                # Erro  Não
                                if error_msg != last_error:
                                    self.logger.warning(
                                        f"DispositivoRetorno: {error_msg}，ContinuarAguardandoValidando"
                                    )
                                    last_error = error_msg

                                # Erro
                                if "Device not found" in error_msg:
                                    error_count += 1
                                    if error_count >= 5 and error_count % 5 == 0:
                                        self.logger.warning(
                                            "\n: SeErro，EmValidando\n"
                                        )

                                # UsandodeAguardando
                                await asyncio.sleep(retry_interval)

                    except asyncio.CancelledError:
                        # 
                        self.logger.info("")
                        return False

                    except aiohttp.ClientError as e:
                        self.logger.warning(
                            f"Falha: {e}，Tentar novamenteEm..."
                        )
                        await asyncio.sleep(retry_interval)

                    except asyncio.TimeoutError as e:
                        self.logger.warning(f"Timeout: {e}，Tentar novamenteEm...")
                        await asyncio.sleep(retry_interval)

                    except Exception as e:
                        # ExceçãodeInformação
                        import traceback

                        error_detail = (
                            str(e) if str(e) else f"{type(e).__name__}: Não  Erro"
                        )
                        self.logger.warning(
                            f"Erro durante processo de Ativação: {error_detail}, Tentando novamente..."
                        )
                        # Modo Debug imprime informação de exceção completa
                        self.logger.debug(
                            f"Informação de Exceção Completa: {traceback.format_exc()}"
                        )
                        await asyncio.sleep(retry_interval)

            # Atingido máximo de tentativas
            self.logger.error(
                f"Ativação Falhou, Atingido máximo de tentativas ({max_retries}), Último erro: {last_error}"
            )
            return False

        except asyncio.CancelledError:
            self.logger.info("")
            return False
