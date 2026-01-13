import asyncio
import platform
import re
from typing import Any, Dict, List, Optional

import numpy as np
import sounddevice as sd

# ：/Dispositivo（Não）
_VIRTUAL_PATTERNS = [
    r"blackhole",
    r"aggregate",
    r"multi[-\s]?output",  # macOS
    r"monitor",
    r"echo[-\s]?cancel",  # Linux Pulse/PipeWire
    r"vb[-\s]?cable",
    r"voicemeeter",
    r"cable (input|output)",  # Windows
    r"loopback",
]


def _is_virtual(name: str) -> bool:
    n = name.casefold()
    return any(re.search(pat, n) for pat in _VIRTUAL_PATTERNS)


def downmix_to_mono(
    pcm: np.ndarray | bytes,
    *,
    keepdims: bool = True,
    dtype: np.dtype | str = np.int16,
    in_channels: int | None = None,
) -> np.ndarray | bytes:
    """Formatodeáudiopara  Canais.

    SuportadoEntrada:
    1. np.ndarray:  (N,) ou (N, C) de PCM 
    2. bytes: PCM Bytes ( dtype e in_channels)

    Args:
        pcm: Entradaáudiodados (ndarray ou bytes)
        keepdims: True Retorno (N,1)，False Retorno (N,) ( ndarray Entrada)
        dtype: PCM dadosTipo ( bytes EntradaUsando)
        in_channels: EntradaCanais ( bytes Entrada)

    Returns:
        Canaisáudiodados (comEntradaTipo)

    Examples:
        >>> # ndarray Entrada
        >>> stereo = np.random.randint(-32768, 32767, (1000, 2), dtype=np.int16)
        >>> mono = downmix_to_mono(stereo, keepdims=False)  # shape: (1000,)

        >>> # bytes Entrada
        >>> stereo_bytes = b'...'  #  PCM dados
        >>> mono_bytes = downmix_to_mono(stereo_bytes, dtype=np.int16, in_channels=2)
    """
    # bytes Entrada:  -> Processando ->  bytes
    if isinstance(pcm, bytes):
        if in_channels is None:
            raise ValueError("bytes Entrada in_channels Parâmetro")
        arr = np.frombuffer(pcm, dtype=dtype).reshape(-1, in_channels)
        mono_arr = downmix_to_mono(arr, keepdims=False)  # bytes SaídaNão keepdims
        return mono_arr.tobytes()

    # ndarray Entrada: Processando
    x = np.asarray(pcm)
    if x.ndim == 1:
        return x[:, None] if keepdims else x

    # JáCanais
    if x.shape[1] == 1:
        return x if keepdims else x[:, 0]

    # Canais
    if np.issubdtype(x.dtype, np.integer):
        # ，Tipo，
        y = np.rint(x.astype(np.float32).mean(axis=1))
        info = np.iinfo(x.dtype)
        y = np.clip(y, info.min, info.max).astype(x.dtype)
    else:
        # ： dtype（ float32），para float64
        y = x.mean(axis=1, dtype=x.dtype)

    return y[:, None] if keepdims else y


def safe_queue_put(
    queue: asyncio.Queue, item: Any, replace_oldest: bool = True
) -> bool:
    """Fila，FilaSelecionandodados.

    Args:
        queue: asyncio.Queue 
        item: dedados
        replace_oldest: True=Filadadosdados, False=dados

    Returns:
        True=sucesso, False=FilaNão
    """
    try:
        queue.put_nowait(item)
        return True
    except asyncio.QueueFull:
        if replace_oldest:
            try:
                queue.get_nowait()  # de
                queue.put_nowait(item)  # Dados
                return True
            except asyncio.QueueEmpty:
                # Não,
                queue.put_nowait(item)
                return True
        return False


def upmix_mono_to_channels(mono_data: np.ndarray, num_channels: int) -> np.ndarray:
    """Canaisáudiopara  Canais（paraCanais）

    Args:
        mono_data: Canaisáudiodados， (N,)
        num_channels: AlvoCanais

    Returns:
        Canaisáudiodados， (N, num_channels)
    """
    if num_channels == 1:
        return mono_data.reshape(-1, 1)

    # CanaisparaCanais
    return np.tile(mono_data.reshape(-1, 1), (1, num_channels))


def _valid(devs: List[dict], idx: int, kind: str, include_virtual: bool) -> bool:
    if not isinstance(idx, int) or idx < 0 or idx >= len(devs):
        return False
    d = devs[idx]
    key = "max_input_channels" if kind == "input" else "max_output_channels"
    if int(d.get(key, 0)) <= 0:
        return False
    if not include_virtual and _is_virtual(d.get("name", "")):
        return False
    return True


def select_audio_device(
    kind: str,
    *,
    include_virtual: bool = False,
    allow_name_hints: Optional[bool] = None,  # None=Linux ；True/False Forçar
) -> Optional[Dict[str, Any]]:
    """
    Selecionandoáudiodispositivo：HostAPI  →（：dispositivo hints， Linux）→ sounddevice sistema →  Retorno：{index, name,
    sample_rate, channels} ou None.
    """
    assert kind in ("input", "output")
    system = platform.system().lower()

    # HostAPI 
    if system == "windows":
        host_order = ["wasapi", "wdm-ks", "directsound", "mme"]
    elif system == "darwin":
        host_order = ["core audio"]
    else:
        host_order = ["alsa", "jack", "oss"]  #  Linux de PortAudio  ALSA

    # Linux  name hints；Fechando（Através deParâmetroAbrindo）
    if allow_name_hints is None:
        allow_name_hints = system == "linux"

    DEVICE_NAME_HINTS = {
        "input": ["default", "sysdefault", "pulse", "pipewire"],
        "output": ["default", "sysdefault", "dmix", "pulse", "pipewire"],
    }

    # 
    try:
        hostapis = list(sd.query_hostapis())
        devices = list(sd.query_devices())
    except Exception:
        hostapis, devices = [], []

    key_host_default = (
        "default_input_device" if kind == "input" else "default_output_device"
    )
    key_channels = "max_input_channels" if kind == "input" else "max_output_channels"

    def pack(idx: int, base: Optional[dict] = None) -> Optional[Dict[str, Any]]:
        if base is None:
            if not _valid(devices, idx, kind, include_virtual):
                return None
            d = devices[idx]
        else:
            d = base
            if not include_virtual and _is_virtual(d.get("name", "")):
                return None
        sr = d.get("default_samplerate", None)
        return {
            "index": int(d.get("index", idx)),
            "name": d.get("name", "Unknown"),
            "sample_rate": int(sr) if isinstance(sr, (int, float)) else None,
            "channels": int(d.get(key_channels, 0)),
        }

    # 1)  HostAPI NomeCorrespondência（、Tamanho）→  HostAPI de“Dispositivo”
    for token in host_order:
        t = token.casefold()
        for ha in hostapis:
            if t in str(ha.get("name", "")).casefold():
                idx = ha.get(key_host_default, -1)
                info = pack(idx)
                if info:
                    return info

    # 1.5) （）Dispositivo hints， allow_name_hints=True （ Linux）
    if allow_name_hints and devices:
        hints = [h.casefold() for h in DEVICE_NAME_HINTS[kind]]
        cands: List[int] = []
        for i, d in enumerate(devices):
            if not _valid(devices, i, kind, include_virtual):
                continue
            name_low = str(d.get("name", "")).casefold()
            if any(h in name_low for h in hints):
                cands.append(i)
        if cands:
            cands.sort()  # ：
            info = pack(cands[0])
            if info:
                return info

    # 2) sounddevice de（Já）
    try:
        info = sd.query_devices(
            kind=kind
        )  # dict， index / default_samplerate / max_*_channels
        packed = pack(int(info.get("index")), base=info)
        if packed:
            return packed
    except Exception:
        pass

    # 3) ：（，）
    for i, d in enumerate(devices):
        if _valid(devices, i, kind, include_virtual):
            return pack(i)

    return None
