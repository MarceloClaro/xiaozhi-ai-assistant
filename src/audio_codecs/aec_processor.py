import platform
from collections import deque
from typing import Any, Dict, Optional

import numpy as np
import sounddevice as sd

from src.constants.constants import AudioConfig
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AECProcessor:
    """
    áudioProcessandoDispositivo Processando（DispositivoSaída）eEntradadeAEC.
    """

    def __init__(self):
        # Informação
        self._platform = platform.system().lower()
        self._is_macos = self._platform == "darwin"
        self._is_linux = self._platform == "linux"
        self._is_windows = self._platform == "windows"

        # WebRTC APM （ macOS Usando）
        self.apm = None
        self.apm_config = None
        self.capture_config = None
        self.render_config = None

        # （ macOS Usando）
        self.reference_stream = None
        self.reference_device_id = None
        self.reference_sample_rate = None

        # Dispositivo（ macOS Usando）
        self.reference_resampler = None
        self._resample_reference_buffer = deque()

        # 
        self._reference_buffer = deque()
        self._webrtc_frame_size = 160  # WebRTC：16kHz, 10ms = 160 samples
        self._system_frame_size = (
            AudioConfig.INPUT_FRAME_SIZE
        )  # deQuadrosTamanho

        # Estado
        self._is_initialized = False
        self._is_closing = False

    async def initialize(self):
        """
        InicializandoAECProcessandoDispositivo.
        """
        try:
            if self._is_windows or self._is_linux:
                # Windows e Linux UsandoAEC，Processando
                logger.info(
                    f"{self._platform.capitalize()} Usando，AECProcessando Dispositivo Já"
                )
                self._is_initialized = True
                return
            elif self._is_macos:
                # macOS Usando WebRTC + BlackHole
                await self._initialize_apm()
                await self._initialize_reference_capture()
            else:
                logger.warning(f" {self._platform} NãoSuportadoAEC")
                self._is_initialized = True
                return

            self._is_initialized = True
            logger.info("AECProcessando Dispositivo Inicialização concluída")

        except Exception as e:
            logger.error(f"AECProcessando Dispositivo InicializandoFalha: {e}")
            await self.close()
            raise

    async def _initialize_apm(self):
        """
        InicializandoWebRTCáudioProcessando（macOS）
        """
        if not self._is_macos:
            logger.warning("macOS_initialize_apm，Não")
            return

        try:
            # ，EmmacOSBanco de dados
            from libs.webrtc_apm import WebRTCAudioProcessing, create_default_config

            self.apm = WebRTCAudioProcessing()

            # 
            self.apm_config = create_default_config()

            # 
            self.apm_config.echo.enabled = True
            self.apm_config.echo.mobile_mode = False
            self.apm_config.echo.enforce_high_pass_filtering = True

            # 
            self.apm_config.noise_suppress.enabled = True
            self.apm_config.noise_suppress.noise_level = 2  # HIGH

            # Dispositivo
            self.apm_config.high_pass.enabled = True
            self.apm_config.high_pass.apply_in_full_band = True

            # App
            result = self.apm.apply_config(self.apm_config)
            if result != 0:
                raise RuntimeError(f"WebRTC APMFalha，Erro: {result}")

            # 
            sample_rate = AudioConfig.INPUT_SAMPLE_RATE  # 16kHz
            channels = AudioConfig.CHANNELS  # 1

            self.capture_config = self.apm.create_stream_config(sample_rate, channels)
            self.render_config = self.apm.create_stream_config(sample_rate, channels)

            # Configurando
            self.apm.set_stream_delay_ms(40)  # 50ms

            logger.info("WebRTC APMInicialização concluída")

        except Exception as e:
            logger.error(f"WebRTC APMInicializandoFalha: {e}")
            raise

    async def _initialize_reference_capture(self):
        """
        InicializandoCapturando（macOS）
        """
        if not self._is_macos:
            return

        try:
            # PesquisarBlackHole 2chDispositivo
            reference_device = self._find_blackhole_device()
            if reference_device is None:
                logger.warning(
                    "NãoEncontradoBlackHole 2chDispositivo，CapturandoNão"
                )
                return

            self.reference_device_id = reference_device["id"]
            self.reference_sample_rate = int(reference_device["default_samplerate"])

            # Dispositivo（）
            if self.reference_sample_rate != AudioConfig.INPUT_SAMPLE_RATE:
                import soxr

                self.reference_resampler = soxr.ResampleStream(
                    self.reference_sample_rate,
                    AudioConfig.INPUT_SAMPLE_RATE,
                    num_channels=1,
                    dtype="int16",
                    quality="QQ",  # Qualidade rápida, consistente com AudioCodec
                )
                logger.info(
                    f"Reamostragem de sinal de referência: {self.reference_sample_rate}Hz → {AudioConfig.INPUT_SAMPLE_RATE}Hz (Usando soxr)"
                )

            # Criar fluxo de Entrada de sinal de referência (fixo Usando 10ms Quadros, Correspondência ao padrão WebRTC)
            webrtc_frame_duration = 0.01  # 10ms, padrão WebRTC Comprimento de Quadros
            reference_frame_size = int(
                self.reference_sample_rate * webrtc_frame_duration
            )

            self.reference_stream = sd.InputStream(
                device=self.reference_device_id,
                samplerate=self.reference_sample_rate,
                channels=AudioConfig.CHANNELS,
                dtype=np.int16,
                blocksize=reference_frame_size,
                callback=self._reference_callback,
                finished_callback=self._reference_finished_callback,
                latency="low",
            )

            self.reference_stream.start()

            logger.info(
                f"Captura de sinal de referência Já Iniciada: [{self.reference_device_id}] {reference_device['name']}"
            )

        except Exception as e:
            logger.error(f"Falha ao Inicializar Captura de sinal de referência: {e}")
            # Não lançar Exceção, permitir AEC trabalhar sem sinal de referência

    def _find_blackhole_device(self) -> Optional[Dict[str, Any]]:
        """
        Procurar dispositivo virtual BlackHole 2ch.
        """
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                device_name = device["name"].lower()
                # PesquisarBlackHole 2chDispositivo
                if "blackhole" in device_name and "2ch" in device_name:
                    # EntradaDispositivo
                    if device["max_input_channels"] >= 1:
                        device_info = dict(device)
                        device_info["id"] = i
                        logger.info(
                            f"EncontradoBlackHoleDispositivo: [{i}] {device['name']}"
                        )
                        return device_info

            # Se  EncontradodeBlackHole 2ch，TentativaPesquisarBlackHoleDispositivo
            for i, device in enumerate(devices):
                device_name = device["name"].lower()
                if "blackhole" in device_name and device["max_input_channels"] >= 1:
                    device_info = dict(device)
                    device_info["id"] = i
                    logger.info(
                        f"EncontradoBlackHoleDispositivo: [{i}] {device['name']}"
                    )
                    return device_info

            return None

        except Exception as e:
            logger.error(f"PesquisarBlackHoleDispositivoFalha: {e}")
            return None

    def _reference_callback(self, indata, frames, time_info, status):
        """
        .
        """
        # frames, time_infosounddevice，NãoUsando
        _ = frames, time_info

        if status and "overflow" not in str(status).lower():
            logger.warning(f"Estado: {status}")

        if self._is_closing:
            return

        try:
            audio_data = indata.copy().flatten()

            # Usandosoxr
            if self.reference_resampler:
                # para16kHz
                resampled_data = self.reference_resampler.resample_chunk(
                    audio_data, last=False
                )
                if len(resampled_data) > 0:
                    self._resample_reference_buffer.extend(
                        resampled_data.astype(np.int16)
                    )

                # deWebRTCQuadros
                while len(self._resample_reference_buffer) >= self._webrtc_frame_size:
                    for _ in range(self._webrtc_frame_size):
                        self._reference_buffer.append(
                            self._resample_reference_buffer.popleft()
                        )
            else:
                # ，Usando
                self._reference_buffer.extend(audio_data)

            # Tamanho
            max_buffer_size = self._webrtc_frame_size * 20  # 200msdeDados
            while len(self._reference_buffer) > max_buffer_size:
                self._reference_buffer.popleft()

        except Exception as e:
            logger.error(f"Erro: {e}")

    def _reference_finished_callback(self):
        """
        Final.
        """
        logger.info("JáFinal")

    def process_audio(self, capture_audio: np.ndarray) -> np.ndarray:
        """ProcessandoáudioQuadros，aplicaçãoAEC Suportado10ms/20ms/40ms/60msAguardarNão  QuadrosComprimento，Através deProcessando.

        Args:
            capture_audio: deáudiodados (16kHz, int16)

        Returns:
            Processando  deáudiodados
        """
        if not self._is_initialized:
            return capture_audio

        # Windows e Linux RetornoOriginalÁudio（Processando）
        if self._is_windows or self._is_linux:
            return capture_audio

        # macOS Usando WebRTC AEC Processando
        if not self._is_macos or self.apm is None:
            return capture_audio

        try:
            # PesquisarEntradaQuadrosTamanhoparaWebRTCQuadrosTamanhode
            if len(capture_audio) % self._webrtc_frame_size != 0:
                logger.warning(
                    f"ÁudioQuadrosTamanhoNão  WebRTCQuadrosde: {len(capture_audio)}, WebRTCQuadros: {self._webrtc_frame_size}"
                )
                return capture_audio

            # de
            num_chunks = len(capture_audio) // self._webrtc_frame_size

            if num_chunks == 1:
                # 10msQuadros，Processando
                return self._process_single_aec_frame(capture_audio)
            else:
                # 20ms/40ms/60msQuadros，Processando
                return self._process_chunked_aec_frames(capture_audio, num_chunks)

        except Exception as e:
            logger.error(f"AECProcessandoFalha: {e}")
            return capture_audio

    def _process_single_aec_frame(self, capture_audio: np.ndarray) -> np.ndarray:
        """
        Processando10ms WebRTCQuadros（macOS）
        """
        if not self._is_macos:
            return capture_audio

        try:
            # EmmacOSctypes
            import ctypes

            # 
            reference_audio = self._get_reference_frame(self._webrtc_frame_size)

            # ctypes
            capture_buffer = (ctypes.c_short * self._webrtc_frame_size)(*capture_audio)
            reference_buffer = (ctypes.c_short * self._webrtc_frame_size)(
                *reference_audio
            )

            processed_capture = (ctypes.c_short * self._webrtc_frame_size)()
            processed_reference = (ctypes.c_short * self._webrtc_frame_size)()

            # Processando（render stream）
            render_result = self.apm.process_reverse_stream(
                reference_buffer,
                self.render_config,
                self.render_config,
                processed_reference,
            )

            if render_result != 0:
                logger.warning(f"ProcessandoFalha，Erro: {render_result}")

            # Processando（capture stream）
            capture_result = self.apm.process_stream(
                capture_buffer,
                self.capture_config,
                self.capture_config,
                processed_capture,
            )

            if capture_result != 0:
                logger.warning(f"ProcessandoFalha，Erro: {capture_result}")
                return capture_audio

            # numpy
            return np.array(processed_capture, dtype=np.int16)

        except Exception as e:
            logger.error(f"AECQuadrosProcessandoFalha: {e}")
            return capture_audio

    def _process_chunked_aec_frames(
        self, capture_audio: np.ndarray, num_chunks: int
    ) -> np.ndarray:
        """
        Processando  Quadros（20ms/40ms/60msAguardar）
        """
        processed_chunks = []

        for i in range(num_chunks):
            # 10ms
            start_idx = i * self._webrtc_frame_size
            end_idx = (i + 1) * self._webrtc_frame_size
            chunk = capture_audio[start_idx:end_idx]

            # Processando10ms
            processed_chunk = self._process_single_aec_frame(chunk)
            processed_chunks.append(processed_chunk)

        # Processando  de  Novamente
        return np.concatenate(processed_chunks)

    def _get_reference_frame(self, frame_size: int) -> np.ndarray:
        """
        TamanhodeQuadros.
        """
        # SeNenhumouNão，Retorno
        if len(self._reference_buffer) < frame_size:
            return np.zeros(frame_size, dtype=np.int16)

        # deQuadros
        frame_data = []
        for _ in range(frame_size):
            frame_data.append(self._reference_buffer.popleft())

        return np.array(frame_data, dtype=np.int16)

    async def close(self):
        """
        FechandoAECProcessandoDispositivo.
        """
        if self._is_closing:
            return

        self._is_closing = True
        logger.info("ComeçarFechandoAECProcessandoDispositivo...")

        try:
            # Em macOS  WebRTC Fonte
            if self._is_macos:
                # Parar
                if self.reference_stream:
                    try:
                        self.reference_stream.stop()
                        self.reference_stream.close()
                    except Exception as e:
                        logger.warning(f"FechandoFalha: {e}")
                    finally:
                        self.reference_stream = None

                # Dispositivo
                if self.reference_resampler:
                    try:
                        # Dispositivo
                        empty_array = np.array([], dtype=np.int16)
                        self.reference_resampler.resample_chunk(empty_array, last=True)
                    except Exception as e:
                        logger.debug(f"DispositivoFalha: {e}")
                    finally:
                        self.reference_resampler = None

                # WebRTC APM
                if self.apm:
                    try:
                        if self.capture_config:
                            self.apm.destroy_stream_config(self.capture_config)
                        if self.render_config:
                            self.apm.destroy_stream_config(self.render_config)
                    except Exception as e:
                        logger.warning(f"APMFalha: {e}")
                    finally:
                        self.capture_config = None
                        self.render_config = None
                        self.apm = None

            # 
            self._reference_buffer.clear()
            self._resample_reference_buffer.clear()

            self._is_initialized = False
            logger.info("AECProcessando Dispositivo JáFechando")

        except Exception as e:
            logger.error(f"FechandoAECProcessandoDispositivoErro: {e}")
