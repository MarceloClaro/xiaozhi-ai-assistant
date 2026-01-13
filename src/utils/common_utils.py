"""
 、DispositivoOperação、Aguardar.
"""

import queue
import shutil
import threading
import time
import webbrowser
from typing import Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# ÁudioReproduçãoFilae
_audio_queue = queue.Queue()
_audio_lock = threading.Lock()
_audio_worker_thread = None
_audio_worker_running = False
_audio_device_warmed_up = False


def _warm_up_audio_device():
    """
    áudiodispositivo，.
    """
    global _audio_device_warmed_up
    if _audio_device_warmed_up:
        return

    try:
        import platform
        import subprocess

        system = platform.system()

        if system == "Darwin":
            subprocess.run(
                ["say", "-v", "Ting-Ting", ""],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux" and shutil.which("espeak"):
            subprocess.run(
                ["espeak", "-v", "zh", ""],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Windows":
            import win32com.client

            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak("")

        _audio_device_warmed_up = True
        logger.info("JáÁudioDispositivo")
    except Exception as e:
        logger.warning(f"ÁudioDispositivoFalha: {e}")


def _audio_queue_worker():
    """
    áudioFila，áudio  OrdemReprodução  Não  Truncado.
    """

    while _audio_worker_running:
        try:
            text = _audio_queue.get(timeout=1)
            if text is None:
                break

            with _audio_lock:
                logger.info(f"ComeçarReproduçãoÁudio: {text[:50]}...")
                success = _play_system_tts(text)

                if not success:
                    logger.warning("TTSFalha，Tentativa")
                    import os

                    if os.name == "nt":
                        _play_windows_tts(text, set_chinese_voice=False)
                    else:
                        _play_system_tts(text)

                time.sleep(0.5)  # ReproduçãoFinal  de，

            _audio_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"ÁudioFila: {e}")

    logger.info("ÁudioFilaJáParar")


def _ensure_audio_worker():
    """
    áudioEm.
    """
    global _audio_worker_thread, _audio_worker_running

    if _audio_worker_thread is None or not _audio_worker_thread.is_alive():
        _warm_up_audio_device()
        _audio_worker_running = True
        _audio_worker_thread = threading.Thread(target=_audio_queue_worker, daemon=True)
        _audio_worker_thread.start()
        logger.info("ÁudioFilaIniciando")


def open_url(url: str) -> bool:
    try:
        success = webbrowser.open(url)
        if success:
            logger.info(f"JáSucessoAbrindo: {url}")
        else:
            logger.warning(f"Incapaz deAbrindo: {url}")
        return success
    except Exception as e:
        logger.error(f"Abrindo: {e}")
        return False


def copy_to_clipboard(text: str) -> bool:
    try:
        import pyperclip

        pyperclip.copy(text)
        logger.info(f"Texto '{text}' Já copiado para a área de transferência")
        return True
    except ImportError:
        logger.warning(
            "Módulo pyperclip não instalado, não é possível copiar para a área de transferência"
        )
        return False
    except Exception as e:
        logger.error(f"para: {e}")
        return False


def _play_windows_tts(text: str, set_chinese_voice: bool = True) -> bool:
    try:
        import win32com.client

        speaker = win32com.client.Dispatch("SAPI.SpVoice")

        if set_chinese_voice:
            try:
                voices = speaker.GetVoices()
                for i in range(voices.Count):
                    if "Chinese" in voices.Item(i).GetDescription():
                        speaker.Voice = voices.Item(i)
                        break
            except Exception as e:
                logger.warning(f"ConfigurandoEm: {e}")

        try:
            speaker.Rate = -2
        except Exception:
            pass

        enhanced_text = text + "。 。 。"
        speaker.Speak(enhanced_text)
        logger.info("JáUsandoWindowsReprodução")
        time.sleep(0.5)
        return True
    except ImportError:
        logger.warning("Windows TTSNão，ÁudioReprodução")
        return False
    except Exception as e:
        logger.error(f"Windows TTSReprodução: {e}")
        return False


def _play_linux_tts(text: str) -> bool:
    import subprocess

    if shutil.which("espeak"):
        try:
            enhanced_text = text + "。 。 。"
            result = subprocess.run(
                ["espeak", "-v", "zh", "-s", "150", "-g", "10", enhanced_text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            time.sleep(0.5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.warning("espeakReproduçãoTimeout")
            return False
        except Exception as e:
            logger.error(f"espeakReprodução: {e}")
            return False
    else:
        logger.warning("espeakNão，ÁudioReprodução")
        return False


def _play_macos_tts(text: str) -> bool:
    import subprocess

    if shutil.which("say"):
        try:
            enhanced_text = text + "。 。 。"
            result = subprocess.run(
                ["say", "-r", "180", enhanced_text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            time.sleep(0.5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.warning("sayComandoReproduçãoTimeout")
            return False
        except Exception as e:
            logger.error(f"sayComandoReprodução: {e}")
            return False
    else:
        logger.warning("sayComandoNão，ÁudioReprodução")
        return False


def _play_system_tts(text: str) -> bool:
    import os
    import platform

    if os.name == "nt":
        return _play_windows_tts(text)
    else:
        system = platform.system()
        if system == "Linux":
            return _play_linux_tts(text)
        elif system == "Darwin":
            return _play_macos_tts(text)
        else:
            logger.warning(f"NãoSuportadode {system}，ÁudioReprodução")
            return False


def play_audio_nonblocking(text: str) -> None:
    try:
        _ensure_audio_worker()
        _audio_queue.put(text)
        logger.info(f"JáÁudioparaFila: {text[:50]}...")
    except Exception as e:
        logger.error(f"ÁudioparaFila: {e}")

        def audio_worker():
            try:
                _warm_up_audio_device()
                _play_system_tts(text)
            except Exception as e:
                logger.error(f"ÁudioReprodução: {e}")

        threading.Thread(target=audio_worker, daemon=True).start()


def extract_verification_code(text: str) -> Optional[str]:
    try:
        import re

        # 
        activation_keywords = [
            "",
            "",
            "",
            "Validando",
            "Dispositivo",
            "Dispositivo",
            "EntradaValidando",
            "Entrada",
            "",
            "xiaozhi.me",
            "",
        ]

        # Pesquisar
        has_activation_keyword = any(keyword in text for keyword in activation_keywords)

        if not has_activation_keyword:
            logger.debug(f"Não，Validando: {text}")
            return None

        # deValidando  CorrespondênciaModo
        # Correspondência6BitsdeValidando，
        patterns = [
            r"Validando[：:]\s*(\d{6})",  # Validando：123456
            r"EntradaValidando[：:]\s*(\d{6})",  # EntradaValidando：123456
            r"Entrada\s*(\d{6})",  # Entrada123456
            r"Validando\s*(\d{6})",  # Validando123456
            r"[：:]\s*(\d{6})",  # ：123456
            r"(\d{6})[，,。.]",  # 123456，ou123456。
            r"[，,。.]\s*(\d{6})",  # ，123456
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                code = match.group(1)
                logger.info(f"JádeEmValidando: {code}")
                return code

        # SeNenhumCorrespondênciaparaModo，TentativaOriginalModo
        # de
        match = re.search(r"((?:\d\s*){6,})", text)
        if match:
            code = "".join(match.group(1).split())
            # Validando6Bits
            if len(code) == 6 and code.isdigit():
                logger.info(f"JádeEmValidando（Modo）: {code}")
                return code

        logger.warning(f"Não  deEmEncontradoValidando: {text}")
        return None
    except Exception as e:
        logger.error(f"Validando: {e}")
        return None


def handle_verification_code(text: str) -> None:
    code = extract_verification_code(text)
    if not code:
        return

    copy_to_clipboard(code)
