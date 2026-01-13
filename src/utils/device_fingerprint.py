import hashlib
import hmac
import json
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple

import machineid
import psutil

from src.utils.logging_config import get_logger
from src.utils.resource_finder import find_config_dir

# LogDispositivo
logger = get_logger(__name__)


class DeviceFingerprint:
    """dispositivoDispositivo - dedispositivo"""

    _instance = None

    def __new__(cls):
        """
        modo.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        InicializandodispositivoDispositivo.
        """
        if self._initialized:
            return
        self._initialized = True

        self.system = platform.system()
        self._efuse_cache: Optional[Dict] = None  # efuseDados

        # InicializandoArquivoCaminho
        self._init_file_paths()

        # efuseArquivoEmInicializandoExiste
        self._ensure_efuse_file()

    def _init_file_paths(self):
        """
        InicializandoarquivoCaminho.
        """
        config_dir = find_config_dir()
        if config_dir:
            self.efuse_file = config_dir / "efuse.json"
            logger.debug(f"UsandoDiretório: {config_dir}")
        else:
            # ：UsandoCaminhoDiretórioExiste
            config_path = Path("config")
            config_path.mkdir(parents=True, exist_ok=True)
            self.efuse_file = config_path / "efuse.json"
            logger.info(f"Diretório: {config_path.absolute()}")

    def get_hostname(self) -> str:
        """
        .
        """
        return platform.node()

    def _normalize_mac_address(self, mac_address: str) -> str:
        """ConversãoMACFormatoparaFormato.

        Args:
            mac_address: OriginalMAC，Usando  Caracteres、ou

        Returns:
            str: ConversãodeMAC，Formatopara "00:00:00:00:00:00"
        """
        if not mac_address:
            return mac_address

        # de，Caracteres
        clean_mac = "".join(c for c in mac_address if c.isalnum())

        # Comprimentopara12Caracteres（6Bytesde）
        if len(clean_mac) != 12:
            logger.warning(f"MACComprimentoNão: {mac_address} -> {clean_mac}")
            return mac_address.lower()

        # NovamenteFormato Conversão paradeFormato
        formatted_mac = ":".join(clean_mac[i : i + 2] for i in range(0, 12, 2))

        # para
        return formatted_mac.lower()

    def get_mac_address(self) -> Optional[str]:
        """
        deMAC.
        """
        try:
            # deInformação
            net_if_addrs = psutil.net_if_addrs()

            # SelecionandodeMAC
            for iface, addrs in net_if_addrs.items():
                # 
                if iface.lower().startswith(("lo", "loopback")):
                    continue

                for snic in addrs:
                    if snic.family == psutil.AF_LINK and snic.address:
                        # ConversãoMACFormato
                        normalized_mac = self._normalize_mac_address(snic.address)
                        # deMAC
                        if normalized_mac != "00:00:00:00:00:00":
                            return normalized_mac

            # SeNenhumEncontradodeMAC，RetornoNone
            logger.warning("NãoEncontradodeMAC")
            return None

        except Exception as e:
            logger.error(f"MACErro: {e}")
            return None

    def get_machine_id(self) -> Optional[str]:
        """
        dispositivo.
        """
        try:
            return machineid.id()
        except machineid.MachineIdNotFound:
            logger.warning("NãoEncontradoDispositivoID")
            return None
        except Exception as e:
            logger.error(f"DispositivoIDErro: {e}")
            return None

    def _generate_fresh_fingerprint(self) -> Dict:
        """
        dedispositivo（Nãoouarquivo）.
        """
        return {
            "system": self.system,
            "hostname": self.get_hostname(),
            "mac_address": self.get_mac_address(),
            "machine_id": self.get_machine_id(),
        }

    def generate_fingerprint(self) -> Dict:
        """
        dedispositivo（deefuse.json）.
        """
        # Tentativadeefuse.jsonDispositivo
        if self.efuse_file.exists():
            try:
                efuse_data = self._load_efuse_data()
                if efuse_data.get("device_fingerprint"):
                    logger.debug("deefuse.jsonDispositivo")
                    return efuse_data["device_fingerprint"]
            except Exception as e:
                logger.warning(f"efuse.jsonEmdeDispositivoFalha: {e}")

        # SeFalhaouNãoExiste，entãodeDispositivo
        logger.info("deDispositivo")
        return self._generate_fresh_fingerprint()

    def generate_hardware_hash(self) -> str:
        """
        InformaçãodeValor.
        """
        fingerprint = self.generate_fingerprint()

        # Nãode
        identifiers = []

        # 
        hostname = fingerprint.get("hostname")
        if hostname:
            identifiers.append(hostname)

        # MAC
        mac_address = fingerprint.get("mac_address")
        if mac_address:
            identifiers.append(mac_address)

        # DispositivoID
        machine_id = fingerprint.get("machine_id")
        if machine_id:
            identifiers.append(machine_id)

        # SeNenhum，UsandoInformação  para
        if not identifiers:
            identifiers.append(self.system)
            logger.warning("NãoEncontrado，UsandoInformação  para")

        # ConexãoValor
        fingerprint_str = "||".join(identifiers)
        return hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

    def generate_serial_number(self) -> str:
        """
        dispositivo.
        """
        fingerprint = self.generate_fingerprint()

        # UsandoMAC
        mac_address = fingerprint.get("mac_address")

        if not mac_address:
            # SeNenhumMAC，UsandoDispositivoIDou
            machine_id = fingerprint.get("machine_id")
            hostname = fingerprint.get("hostname")

            if machine_id:
                identifier = machine_id[:12]  # 12Bits
            elif hostname:
                identifier = hostname.replace("-", "").replace("_", "")[:12]
            else:
                identifier = "unknown"

            short_hash = hashlib.md5(identifier.encode()).hexdigest()[:8].upper()
            return f"SN-{short_hash}-{identifier.upper()}"

        # MACparaNenhum
        mac_clean = mac_address.lower().replace(":", "")
        short_hash = hashlib.md5(mac_clean.encode()).hexdigest()[:8].upper()
        serial_number = f"SN-{short_hash}-{mac_clean}"
        return serial_number

    def _ensure_efuse_file(self):
        """
        efusearquivoExisteInformação.
        """
        logger.info(f"PesquisarefuseArquivo: {self.efuse_file.absolute()}")

        # Dispositivo（Informação）
        fingerprint = self._generate_fresh_fingerprint()
        mac_address = fingerprint.get("mac_address")

        if not self.efuse_file.exists():
            logger.info("efuse.jsonArquivoNãoExiste，Arquivo")
            self._create_new_efuse_file(fingerprint, mac_address)
        else:
            logger.info("efuse.jsonArquivoJáExiste，Validando")
            self._validate_and_fix_efuse_file(fingerprint, mac_address)

    def _create_new_efuse_file(self, fingerprint: Dict, mac_address: Optional[str]):
        """
        Criando  deefusearquivo.
        """
        # eHMAC
        serial_number = self.generate_serial_number()
        hmac_key = self.generate_hardware_hash()

        logger.info(f": {serial_number}")
        logger.debug(f"HMAC: {hmac_key[:8]}...  # 8Bits")

        # deefuseDados
        efuse_data = {
            "mac_address": mac_address,
            "serial_number": serial_number,
            "hmac_key": hmac_key,
            "activation_status": False,
            "device_fingerprint": fingerprint,
        }

        # DiretórioExiste
        self.efuse_file.parent.mkdir(parents=True, exist_ok=True)

        # Dados
        success = self._save_efuse_data(efuse_data)
        if success:
            logger.info(f"JáefuseArquivo: {self.efuse_file}")
        else:
            logger.error("efuseArquivoFalha")

    def _validate_and_fix_efuse_file(
        self, fingerprint: Dict, mac_address: Optional[str]
    ):
        """
        Validandoefusearquivode.
        """
        try:
            efuse_data = self._load_efuse_data_from_file()

            # PesquisarExiste
            required_fields = [
                "mac_address",
                "serial_number",
                "hmac_key",
                "activation_status",
                "device_fingerprint",
            ]
            missing_fields = [
                field for field in required_fields if field not in efuse_data
            ]

            if missing_fields:
                logger.warning(f"efuseArquivo: {missing_fields}")
                self._fix_missing_fields(
                    efuse_data, missing_fields, fingerprint, mac_address
                )
            else:
                logger.debug("efuseArquivoPesquisarAtravés de")
                # 
                self._efuse_cache = efuse_data

        except Exception as e:
            logger.error(f"ValidandoefuseArquivo: {e}")
            # SeValidandoFalha，NovamenteArquivo
            logger.info("NovamenteefuseArquivo")
            self._create_new_efuse_file(fingerprint, mac_address)

    def _fix_missing_fields(
        self,
        efuse_data: Dict,
        missing_fields: list,
        fingerprint: Dict,
        mac_address: Optional[str],
    ):
        """
        de.
        """
        for field in missing_fields:
            if field == "device_fingerprint":
                efuse_data[field] = fingerprint
            elif field == "mac_address":
                efuse_data[field] = mac_address
            elif field == "serial_number":
                efuse_data[field] = self.generate_serial_number()
            elif field == "hmac_key":
                efuse_data[field] = self.generate_hardware_hash()
            elif field == "activation_status":
                efuse_data[field] = False

        # deDados
        success = self._save_efuse_data(efuse_data)
        if success:
            logger.info("JáefuseArquivo")
        else:
            logger.error("efuseArquivoFalha")

    def _load_efuse_data_from_file(self) -> Dict:
        """
        dearquivoCarregandoefusedados（NãoUsando）.
        """
        with open(self.efuse_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_efuse_data(self) -> Dict:
        """
        Carregandoefusedados（）.
        """
        # Se，Retorno
        if self._efuse_cache is not None:
            return self._efuse_cache

        try:
            data = self._load_efuse_data_from_file()
            # Dados
            self._efuse_cache = data
            return data
        except Exception as e:
            logger.error(f"efuseDadosFalha: {e}")
            # Retorno  deDados，Não
            return {
                "mac_address": None,
                "serial_number": None,
                "hmac_key": None,
                "activation_status": False,
                "device_fingerprint": {},
            }

    def _save_efuse_data(self, data: Dict) -> bool:
        """
        Salvandoefusedados.
        """
        try:
            # DiretórioExiste
            self.efuse_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.efuse_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # 
            self._efuse_cache = data
            logger.debug(f"efuseDadosJápara: {self.efuse_file}")
            return True
        except Exception as e:
            logger.error(f"efuseDadosFalha: {e}")
            return False

    def ensure_device_identity(self) -> Tuple[Optional[str], Optional[str], bool]:
        """
        dispositivoInformaçãoJáCarregando - Retorno、HMACeativaçãoestado

        Returns:
            Tuple[Optional[str], Optional[str], bool]: (, HMAC, ativaçãoestado)
        """
        # efuseDados（ArquivoJáExiste）
        efuse_data = self._load_efuse_data()

        # 、HMACeEstado
        serial_number = efuse_data.get("serial_number")
        hmac_key = efuse_data.get("hmac_key")
        is_activated = efuse_data.get("activation_status", False)

        return serial_number, hmac_key, is_activated

    def has_serial_number(self) -> bool:
        """
        Pesquisar.
        """
        efuse_data = self._load_efuse_data()
        return efuse_data.get("serial_number") is not None

    def get_serial_number(self) -> Optional[str]:
        """
        .
        """
        efuse_data = self._load_efuse_data()
        return efuse_data.get("serial_number")

    def get_hmac_key(self) -> Optional[str]:
        """
        HMAC.
        """
        efuse_data = self._load_efuse_data()
        return efuse_data.get("hmac_key")

    def get_mac_address_from_efuse(self) -> Optional[str]:
        """
        deefuse.jsonMAC.
        """
        efuse_data = self._load_efuse_data()
        return efuse_data.get("mac_address")

    def set_activation_status(self, status: bool) -> bool:
        """
        Configurandoativaçãoestado.
        """
        efuse_data = self._load_efuse_data()
        efuse_data["activation_status"] = status
        return self._save_efuse_data(efuse_data)

    def is_activated(self) -> bool:
        """
        PesquisardispositivoJáativação.
        """
        efuse_data = self._load_efuse_data()
        return efuse_data.get("activation_status", False)

    def generate_hmac(self, challenge: str) -> Optional[str]:
        """
        UsandoHMAC.
        """
        if not challenge:
            logger.error("Caracteres  Não  para")
            return None

        hmac_key = self.get_hmac_key()

        if not hmac_key:
            logger.error("NãoEncontradoHMAC，Incapaz de")
            return None

        try:
            # HMAC-SHA256
            signature = hmac.new(
                hmac_key.encode(), challenge.encode(), hashlib.sha256
            ).hexdigest()

            return signature
        except Exception as e:
            logger.error(f"HMACFalha: {e}")
            return None

    @classmethod
    def get_instance(cls) -> "DeviceFingerprint":
        """
        dispositivo.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
