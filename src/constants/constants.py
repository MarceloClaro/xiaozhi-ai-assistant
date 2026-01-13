import platform

from src.utils.config_manager import ConfigManager

config = ConfigManager.get_instance()


class ListeningMode:
    """
    modo.
    """

    REALTIME = "realtime"
    AUTO_STOP = "auto_stop"
    MANUAL = "manual"


class AbortReason:
    """
    Em  Motivo.
    """

    NONE = "none"
    WAKE_WORD_DETECTED = "wake_word_detected"
    USER_INTERRUPTION = "user_interruption"


class DeviceState:
    """
    dispositivoestado.
    """

    IDLE = "idle"
    CONNECTING = "connecting"
    LISTENING = "listening"
    SPEAKING = "speaking"


class EventType:
    """
    Tipo.
    """

    SCHEDULE_EVENT = "schedule_event"
    AUDIO_INPUT_READY_EVENT = "audio_input_ready_event"
    AUDIO_OUTPUT_READY_EVENT = "audio_output_ready_event"


def is_official_server(ws_addr: str) -> bool:
    """paradeservidor.

    Args:
        ws_addr (str): WebSocket 

    Returns:
        bool: paradeservidor
    """
    return "api.tenclass.net" in ws_addr


def get_frame_duration() -> int:
    """dispositivodeQuadrosComprimento.

    Retorno:
        int: QuadrosComprimento(Milissegundos)
    """
    try:
        # PesquisarparaDispositivo
        ota_url = config.get_config("SYSTEM_OPTIONS.NETWORK.OTA_VERSION_URL")
        if not is_official_server(ota_url):
            return 60

        # ARMDispositivo（）
        machine = platform.machine().lower()
        arm_archs = ["arm", "aarch64", "armv7l", "armv6l"]
        is_arm_device = any(arch in machine for arch in arm_archs)

        if is_arm_device:
            # ARMDispositivo（）UsandoQuadrosCPU
            return 60
        else:
            # Dispositivo（Windows/macOS/Linux x86），Usando
            return 20

    except Exception:
        # SeFalha，RetornoValor20ms（Dispositivo）
        return 20


class AudioConfig:
    """
    áudioconfiguração.
    """

    # 
    INPUT_SAMPLE_RATE = 16000  # EntradaTaxa de amostragem16kHz
    # SaídaTaxa de amostragem：DispositivoUsando24kHz，Usando16kHz
    _ota_url = config.get_config("SYSTEM_OPTIONS.NETWORK.OTA_VERSION_URL")
    OUTPUT_SAMPLE_RATE = 24000 if is_official_server(_ota_url) else 16000
    CHANNELS = 1  # ：Canais

    # DispositivoCanaisLimitado a（CanaisDispositivo）
    MAX_INPUT_CHANNELS = 2  # Usando2EntradaCanais（）
    MAX_OUTPUT_CHANNELS = 2  # Usando2SaídaCanais（）

    # QuadrosComprimento
    FRAME_DURATION = get_frame_duration()

    # Não  Taxa de amostragemQuadrosTamanho
    INPUT_FRAME_SIZE = int(INPUT_SAMPLE_RATE * (FRAME_DURATION / 1000))
    # LinuxUsandoQuadrosTamanhoPCM，
    OUTPUT_FRAME_SIZE = int(OUTPUT_SAMPLE_RATE * (FRAME_DURATION / 1000))
