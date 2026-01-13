import asyncio
import gc
from collections import deque
from typing import Callable, List, Optional, Protocol

import numpy as np
import opuslib
import sounddevice as sd
import soxr

from src.audio_codecs.aec_processor import AECProcessor
from src.constants.constants import AudioConfig
from src.utils.audio_utils import (
    downmix_to_mono,
    safe_queue_put,
    select_audio_device,
    upmix_mono_to_channels,
)
from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AudioListener(Protocol):
    """
    áudioDispositivoprotocolo（Aguardar）
    """

    def on_audio_data(self, audio_data: np.ndarray) -> None:
        """
        Recebendoáudiodadosde.
        """
        ...


class AudioCodec:
    """
    áudioDispositivo - áudioFormatoDispositivo + 

    ：
    1. dispositivo：dispositivoSelecionando、Criando、erroRestaurando
    2. Formato：Taxa de amostragem、Canais、Quadros
    3. ：PCM ↔ Opus
    4. ：、

    então：
    - dispositivo：dispositivoCriando（Taxa de amostragem、Canais）
    - ：AutomáticodispositivoFormatocomprotocolo
    - então：Através deemodo

    ：
    - Entrada：dispositivo → +Reamostragem → 16kHz  Canais → OpusCodificação → Enviando
    - Saída：RecebendoOpus → 24kHz  Canais → Reamostragem+ → dispositivoReprodução
    """

    def __init__(self, audio_processor: Optional[AECProcessor] = None):
        """InicializandoáudioDispositivo.

        Args:
            audio_processor: deáudioProcessandoDispositivo（AECAguardar），Através de
        """
        # Dispositivo
        self.config = ConfigManager.get_instance()

        # OpusDispositivo
        self.opus_encoder = None
        self.opus_decoder = None

        # DispositivoInformação
        self.device_input_sample_rate = None
        self.device_output_sample_rate = None
        self.input_channels = None
        self.output_channels = None
        self.mic_device_id = None
        self.speaker_device_id = None

        # Dispositivo（）
        self.input_resampler = None
        self.output_resampler = None

        # 
        self._resample_input_buffer = deque()
        self._resample_output_buffer = deque()

        # 
        self._need_input_downmix = False
        self._need_output_upmix = False

        # DispositivoQuadrosTamanho
        self._device_input_frame_size = None
        self._device_output_frame_size = None

        # Áudio
        self.input_stream = None
        self.output_stream = None

        # ReproduçãoFila
        self._output_buffer = asyncio.Queue(maxsize=500)

        # eDispositivo（）
        self._encoded_callback: Optional[Callable] = None
        self._audio_listeners: List[AudioListener] = []

        # ÁudioProcessandoDispositivo（）
        self.audio_processor = audio_processor
        self._aec_enabled = False

        # Estado
        self._is_closing = False

    async def initialize(self):
        """InicializandoáudiodispositivoeDispositivo.

        ：
        1. Vezes：AutomáticoSelecionandodispositivo，Salvandoconfiguração
        2. ：deconfiguraçãoCarregandodispositivoInformação
        3. dispositivoCriando（Taxa de amostragem、Canais）
        4. AutomáticoCriandoDispositivo（Taxa de amostragem、Canais）
        """
        try:
            # ouInicializandoDispositivo
            await self._load_device_config()

            # OpusDispositivo
            await self._create_opus_codecs()

            # Dispositivoe
            await self._create_resamplers()

            # Áudio（UsandoDispositivoFormato）
            await self._create_streams()

            # InicializandoAECProcessandoDispositivo（Se）
            if self.audio_processor:
                try:
                    await self.audio_processor.initialize()
                    self._aec_enabled = self.audio_processor._is_initialized
                    logger.info(
                        f"AECProcessando Dispositivo Inicializando: {'' if self._aec_enabled else ''}"
                    )
                except Exception as e:
                    logger.warning(f"AECProcessando Dispositivo InicializandoFalha: {e}")
                    self._aec_enabled = False

            logger.info("AudioCodec Inicialização concluída")

        except Exception as e:
            logger.error(f"InicializandoÁudioDispositivoFalha: {e}")
            await self.close()
            raise

    async def _load_device_config(self):
        """
        CarregandoouInicializandodispositivoconfiguração.
        """
        audio_config = self.config.get_config("AUDIO_DEVICES", {}) or {}

        input_device_id = audio_config.get("input_device_id")
        output_device_id = audio_config.get("output_device_id")

        # Vezes：AutomáticoSelecionandoDispositivo
        if input_device_id is None or output_device_id is None:
            logger.info("Vezes，AutomáticoSelecionandoÁudioDispositivo...")
            await self._auto_detect_devices()
            return

        # de
        self.mic_device_id = input_device_id
        self.speaker_device_id = output_device_id
        self.device_input_sample_rate = audio_config.get(
            "input_sample_rate", AudioConfig.INPUT_SAMPLE_RATE
        )
        self.device_output_sample_rate = audio_config.get(
            "output_sample_rate", AudioConfig.OUTPUT_SAMPLE_RATE
        )
        self.input_channels = audio_config.get("input_channels", 1)
        self.output_channels = audio_config.get("output_channels", 1)

        # DispositivoQuadrosTamanho
        self._device_input_frame_size = int(
            self.device_input_sample_rate * (AudioConfig.FRAME_DURATION / 1000)
        )
        self._device_output_frame_size = int(
            self.device_output_sample_rate * (AudioConfig.FRAME_DURATION / 1000)
        )

        logger.info(
            f"Carregando Configuração de Dispositivo | Entrada: {self.device_input_sample_rate}Hz {self.input_channels}ch | "
            f"Saída: {self.device_output_sample_rate}Hz {self.output_channels}ch"
        )

    async def _auto_detect_devices(self):
        """
        Detectar automaticamente e Selecionar melhor dispositivo.
        """
        # Usar Seleção inteligente de Dispositivo
        in_info = select_audio_device("input", include_virtual=False)
        out_info = select_audio_device("output", include_virtual=False)

        if not in_info or not out_info:
            raise RuntimeError(
                "Não é possível encontrar dispositivo de áudio disponível"
            )

        # Limitado aCanais（100+CanaisDispositivo）
        raw_input_channels = in_info["channels"]
        raw_output_channels = out_info["channels"]

        self.input_channels = min(raw_input_channels, AudioConfig.MAX_INPUT_CHANNELS)
        self.output_channels = min(raw_output_channels, AudioConfig.MAX_OUTPUT_CHANNELS)

        # DispositivoInformação
        self.mic_device_id = in_info["index"]
        self.speaker_device_id = out_info["index"]
        self.device_input_sample_rate = in_info["sample_rate"]
        self.device_output_sample_rate = out_info["sample_rate"]

        # QuadrosTamanho
        self._device_input_frame_size = int(
            self.device_input_sample_rate * (AudioConfig.FRAME_DURATION / 1000)
        )
        self._device_output_frame_size = int(
            self.device_output_sample_rate * (AudioConfig.FRAME_DURATION / 1000)
        )

        # LogSaída
        if raw_input_channels > AudioConfig.MAX_INPUT_CHANNELS:
            logger.info(
                f"Dispositivo de Entrada Suportado {raw_input_channels} Canais, Limitado a Usar anterior {self.input_channels} Canais"
            )
        if raw_output_channels > AudioConfig.MAX_OUTPUT_CHANNELS:
            logger.info(
                f"Dispositivo de Saída Suportado {raw_output_channels} Canais, Limitado a Usar anterior {self.output_channels} Canais"
            )

        logger.info(
            f"Selecionando Dispositivo de Entrada: {in_info['name']} ({self.device_input_sample_rate}Hz, {self.input_channels}ch)"
        )
        logger.info(
            f"Selecionando Dispositivo de Saída: {out_info['name']} ({self.device_output_sample_rate}Hz, {self.output_channels}ch)"
        )

        # （Vezes）
        self.config.update_config("AUDIO_DEVICES.input_device_id", self.mic_device_id)
        self.config.update_config("AUDIO_DEVICES.input_device_name", in_info["name"])
        self.config.update_config(
            "AUDIO_DEVICES.input_sample_rate", self.device_input_sample_rate
        )
        self.config.update_config("AUDIO_DEVICES.input_channels", self.input_channels)

        self.config.update_config(
            "AUDIO_DEVICES.output_device_id", self.speaker_device_id
        )
        self.config.update_config("AUDIO_DEVICES.output_device_name", out_info["name"])
        self.config.update_config(
            "AUDIO_DEVICES.output_sample_rate", self.device_output_sample_rate
        )
        self.config.update_config("AUDIO_DEVICES.output_channels", self.output_channels)

    async def _create_opus_codecs(self):
        """
        CriandoOpusDispositivo.
        """
        try:
            # EntradaCodificaçãoDispositivo：16kHz  Canais
            self.opus_encoder = opuslib.Encoder(
                AudioConfig.INPUT_SAMPLE_RATE,
                AudioConfig.CHANNELS,
                opuslib.APPLICATION_VOIP,
            )

            # SaídaDispositivo：24kHz  Canais
            self.opus_decoder = opuslib.Decoder(
                AudioConfig.OUTPUT_SAMPLE_RATE, AudioConfig.CHANNELS
            )

            logger.info("Sucesso do dispositivo Opus")
        except Exception as e:
            logger.error(f"OpusDispositivoFalha: {e}")
            raise

    async def _create_resamplers(self):
        """
        dispositivocomde，CriandoDispositivoe.
        """
        # EntradaDispositivoConfiguração
        # 1. Canais
        self._need_input_downmix = self.input_channels > 1
        if self._need_input_downmix:
            logger.info(f"Mistura descendente de canais de entrada: {self.input_channels}ch → 1ch")

        # 2. Taxa de amostragemDispositivo
        if self.device_input_sample_rate != AudioConfig.INPUT_SAMPLE_RATE:
            self.input_resampler = soxr.ResampleStream(
                self.device_input_sample_rate,
                AudioConfig.INPUT_SAMPLE_RATE,
                num_channels=1,  # DispositivoProcessando  Canais（）
                dtype="float32",
                quality="QQ",  # （）
            )
            logger.info(
                f"Reamostragem de entrada: {self.device_input_sample_rate}Hz → 16kHz"
            )

        # SaídaDispositivoConfiguração
        # 1. Taxa de amostragemDispositivo
        if self.device_output_sample_rate != AudioConfig.OUTPUT_SAMPLE_RATE:
            self.output_resampler = soxr.ResampleStream(
                AudioConfig.OUTPUT_SAMPLE_RATE,
                self.device_output_sample_rate,
                num_channels=1,  # Reamostragem Processando um único Canal (antes da mistura)
                dtype="float32",
                quality="QQ",
            )
            logger.info(
                f"Saída Reamostragem: {AudioConfig.OUTPUT_SAMPLE_RATE}Hz → "
                f"{self.device_output_sample_rate}Hz"
            )

        # 2. Canais Mistura ascendente marcação
        self._need_output_upmix = self.output_channels > 1
        if self._need_output_upmix:
            logger.info(
                f"Mistura de canais de saída ascendente: 1ch → {self.output_channels}ch"
            )

    async def _create_streams(self):
        """
        Criandoáudio（UsandodispositivoFormato）
        """
        try:
            # Entrada：UsandoDispositivoTaxa de amostragemeCanais
            self.input_stream = sd.InputStream(
                device=self.mic_device_id,
                samplerate=self.device_input_sample_rate,  # DispositivoTaxa de amostragem
                channels=self.input_channels,  # DispositivoCanais
                dtype=np.float32,
                blocksize=self._device_input_frame_size,  # DispositivoQuadrosTamanho
                callback=self._input_callback,
                finished_callback=self._input_finished_callback,
                latency="low",
            )

            # Saída：UsandoDispositivoTaxa de amostragemeCanais
            self.output_stream = sd.OutputStream(
                device=self.speaker_device_id,
                samplerate=self.device_output_sample_rate,  # DispositivoTaxa de amostragem
                channels=self.output_channels,  # DispositivoCanais
                dtype=np.float32,
                blocksize=self._device_output_frame_size,  # DispositivoQuadrosTamanho
                callback=self._output_callback,
                finished_callback=self._output_finished_callback,
                latency="low",
            )

            self.input_stream.start()
            self.output_stream.start()

            logger.info(
                f"Áudio stream Iniciado | Entrada: {self.device_input_sample_rate}Hz {self.input_channels}ch | "
                f"Saída: {self.device_output_sample_rate}Hz {self.output_channels}ch"
            )

        except Exception as e:
            logger.error(f"Falha ao criar Áudio stream: {e}")
            raise

    def _input_callback(self, indata, frames, time_info, status):
        """
        Callback de Entrada: conversão de Formato nativo do dispositivo → Formato do protocolo do servidor: múltiplos Canais/taxa de amostragem alta → mistura descendente + Reamostragem → 16kHz um único Canal → Codificação Opus.
        """
        if status and "overflow" not in str(status).lower():
            logger.warning(f"EntradaEstado: {status}")

        if self._is_closing:
            return

        try:
            # 1: Canais（/Canais → Canais）
            if self._need_input_downmix:
                # indata shape: (frames, channels)
                audio_data = downmix_to_mono(indata, keepdims=False)
            else:
                audio_data = indata.flatten()  # JáCanais

            # 2: Taxa de amostragem（DispositivoTaxa de amostragem → 16kHz）
            if self.input_resampler is not None:
                audio_data = self._process_input_resampling(audio_data)
                if audio_data is None:  # DadosNão，AguardandoQuadros
                    return

            # 3: ValidandoQuadrosTamanho
            if len(audio_data) != AudioConfig.INPUT_FRAME_SIZE:
                return

            # 4: para int16  Opus Codificaçãoe AEC Processando
            audio_data_int16 = (audio_data * 32768.0).astype(np.int16)

            # 5: AECProcessando（Se）
            if self._aec_enabled and self.audio_processor._is_macos:
                try:
                    audio_data_int16 = self.audio_processor.process_audio(
                        audio_data_int16
                    )
                except Exception as e:
                    logger.warning(f"AECProcessandoFalha，UsandoOriginalÁudio: {e}")

            # 6: OpusCodificaçãoEnviando
            if self._encoded_callback:
                try:
                    pcm_data = audio_data_int16.tobytes()
                    encoded_data = self.opus_encoder.encode(
                        pcm_data, AudioConfig.INPUT_FRAME_SIZE
                    )
                    if encoded_data:
                        self._encoded_callback(encoded_data)
                except Exception as e:
                    logger.warning(f"CodificaçãoFalha: {e}")

            # 7: NotificandoÁudioDispositivo（）
            for listener in self._audio_listeners:
                try:
                    listener.on_audio_data(audio_data_int16.copy())
                except Exception as e:
                    logger.warning(f"ÁudioDispositivoProcessandoFalha: {e}")

        except Exception as e:
            logger.error(f"EntradaErro: {e}")

    def _process_input_resampling(self, audio_data):
        """
        Reamostragem de entradaProcessando：dispositivoTaxa de amostragem → 16kHz Usandodados，Quadros  Retorno.
        """
        try:
            resampled_data = self.input_resampler.resample_chunk(audio_data, last=False)
            if len(resampled_data) > 0:
                self._resample_input_buffer.extend(resampled_data)

            # paraAlvoQuadrosTamanho
            expected_frame_size = AudioConfig.INPUT_FRAME_SIZE
            if len(self._resample_input_buffer) < expected_frame_size:
                return None

            # Quadros
            frame_data = []
            for _ in range(expected_frame_size):
                frame_data.append(self._resample_input_buffer.popleft())

            return np.array(frame_data, dtype=np.float32)

        except Exception as e:
            logger.error(f"Reamostragem de entradaFalha: {e}")
            return None

    def _output_callback(self, outdata, frames, time_info, status):
        """
        Saída：protocoloFormato → dispositivoFormato ：24kHz  Canais → Reamostragem+ → Canais/Taxa de amostragem.
        """
        if status:
            if "underflow" not in str(status).lower():
                logger.warning(f"SaídaEstado: {status}")

        try:
            # de24kHz  CanaisDados
            if self.output_resampler is not None:
                # ：24kHz → DispositivoTaxa de amostragem
                self._output_callback_with_resample(outdata, frames)
            else:
                # Reprodução：24kHz
                self._output_callback_direct(outdata, frames)

        except Exception as e:
            logger.error(f"SaídaErro: {e}")
            outdata.fill(0)

    def _output_callback_direct(self, outdata, frames):
        """Reprodução（dispositivoSuportado24kHz）

        Processando:
        1. deFilaCanaisdados (OUTPUT_FRAME_SIZE)
        2. ouparaQuadros
        3.  int16 → float32
        4. ,para  Canais;entãoSaída
        """
        try:
            # deReproduçãoFilaÁudioDados（Canais int16 Dados）
            audio_data = self._output_buffer.get_nowait()

            # audio_data CanaisDados,Comprimento = OUTPUT_FRAME_SIZE
            # ouparaQuadros
            if len(audio_data) >= frames:
                mono_samples = audio_data[:frames]
            else:
                # DadosNão,
                mono_samples = np.zeros(frames, dtype=np.int16)
                mono_samples[: len(audio_data)] = audio_data

            # para float32 Reprodução
            mono_samples_float = mono_samples.astype(np.float32) / 32768.0

            # CanaisProcessando
            if self._need_output_upmix:
                # Canais → Canais（paraCanais）
                multi_channel = upmix_mono_to_channels(
                    mono_samples_float, self.output_channels
                )
                outdata[:] = multi_channel
            else:
                # CanaisSaída
                outdata[:, 0] = mono_samples_float

        except asyncio.QueueEmpty:
            # DadosSaída
            outdata.fill(0)

    def _output_callback_with_resample(self, outdata, frames):
        """Reprodução（24kHz → dispositivoTaxa de amostragem）

        Processando:
        1. deFila24kHz  Canais int16 dados
        2. para float32 paradispositivoTaxa de amostragem（para  Canais）
        3. para,Quadros
        4. ,para  Canais;entãoSaída
        """
        try:
            # Processando24kHz  CanaisDados
            # : deCanaisDados, frames  frames*channels
            while len(self._resample_output_buffer) < frames:
                try:
                    audio_data = self._output_buffer.get_nowait()
                    #  int16 → float32
                    audio_data_float = audio_data.astype(np.float32) / 32768.0
                    # 24kHz  Canais → DispositivoTaxa de amostragem  Canais
                    resampled_data = self.output_resampler.resample_chunk(
                        audio_data_float, last=False
                    )
                    if len(resampled_data) > 0:
                        self._resample_output_buffer.extend(resampled_data)
                except asyncio.QueueEmpty:
                    break

            # Quadros  de  CanaisDados
            if len(self._resample_output_buffer) >= frames:
                frame_data = []
                for _ in range(frames):
                    frame_data.append(self._resample_output_buffer.popleft())
                mono_data = np.array(frame_data, dtype=np.float32)

                # CanaisProcessando
                if self._need_output_upmix:
                    # Canais → Canais（paraCanais）
                    multi_channel = upmix_mono_to_channels(
                        mono_data, self.output_channels
                    )
                    outdata[:] = multi_channel
                else:
                    # CanaisSaída
                    outdata[:, 0] = mono_data
            else:
                # DadosNãoSaída
                outdata.fill(0)

        except Exception as e:
            logger.warning(f"ReamostragemSaídaFalha: {e}")
            outdata.fill(0)

    def _input_finished_callback(self):
        """
        EntradaFinal.
        """
        logger.info("EntradaJáFinal")

    def _output_finished_callback(self):
        """
        SaídaFinal.
        """
        logger.info("SaídaJáFinal")

    # =============  =============

    def set_encoded_callback(self, callback: Callable[[bytes], None]):
        """ConfigurandoCodificaçãoáudio（rede）

        Args:
            callback: Codificação  dadosde，Recebendo bytes Tipode Opus dados

        :
            def network_send(opus_data: bytes):
                await websocket.send(opus_data)

            audio_codec.set_encoded_callback(network_send)
        """
        self._encoded_callback = callback

        if callback:
            logger.info("Já configurando codificação de áudio")
        else:
            logger.info("JáCodificaçãoÁudio")

    def add_audio_listener(self, listener: AudioListener):
        """áudioDispositivo（Aguardar）

        Args:
            listener:  AudioListener protocolodeDispositivo

        :
            wake_word_detector = WakeWordDetector()  #  on_audio_data 
            audio_codec.add_audio_listener(wake_word_detector)
        """
        if listener not in self._audio_listeners:
            self._audio_listeners.append(listener)
            logger.info(f"JáÁudioDispositivo: {listener.__class__.__name__}")

    def remove_audio_listener(self, listener: AudioListener):
        """áudioDispositivo.

        Args:
            listener: deDispositivo
        """
        if listener in self._audio_listeners:
            self._audio_listeners.remove(listener)
            logger.info(f"JáÁudioDispositivo: {listener.__class__.__name__}")

    async def write_audio(self, opus_data: bytes):
        """Reproduçãoáudio（ Opus dados → Dispositivo）

        Args:
            opus_data: Retornode Opus Codificaçãodados

        :
            Opus → 24kHz  CanaisPCM → ReproduçãoFila → SaídaProcessando
        """
        try:
            # Opuspara24kHz PCMDados
            pcm_data = self.opus_decoder.decode(
                opus_data, AudioConfig.OUTPUT_FRAME_SIZE
            )

            audio_array = np.frombuffer(pcm_data, dtype=np.int16)

            expected_length = AudioConfig.OUTPUT_FRAME_SIZE * AudioConfig.CHANNELS
            if len(audio_array) != expected_length:
                logger.warning(
                    f"ÁudioComprimentoExceção: {len(audio_array)}, : {expected_length}"
                )
                return

            # ReproduçãoFila（Usando）
            if not safe_queue_put(
                self._output_buffer, audio_array, replace_oldest=True
            ):
                logger.warning("ReproduçãoFilaJá，ÁudioQuadros")

        except opuslib.OpusError as e:
            logger.warning(f"OpusFalha，Quadros: {e}")
        except Exception as e:
            logger.warning(f"ÁudioFalha，Quadros: {e}")

    async def write_pcm_direct(self, pcm_data: np.ndarray):
        """ PCM dadosparaReproduçãoFila（ MusicPlayer Usando）

        Args:
            pcm_data: 24kHz Canais PCM dados (np.int16)

        :
             Opus ， PCM dadosReproduçãoFila。
            MúsicaReprodução，dadosJá FFmpeg paraAlvoFormato。
        """
        try:
            # ValidandoDadosFormato
            expected_length = AudioConfig.OUTPUT_FRAME_SIZE * AudioConfig.CHANNELS

            # SeDadosComprimentoNãoCorrespondência，ouTruncado
            if len(pcm_data) != expected_length:
                if len(pcm_data) < expected_length:
                    # 
                    padded = np.zeros(expected_length, dtype=np.int16)
                    padded[: len(pcm_data)] = pcm_data
                    pcm_data = padded
                    logger.debug(
                        f"Dados PCM Insuficientes, preenchendo silêncio: {len(pcm_data)} → {expected_length}"
                    )
                else:
                    # Truncado dados excedentes
                    pcm_data = pcm_data[:expected_length]
                    logger.debug(
                        f"Dados PCM Muito longo, Truncado: {len(pcm_data)} → {expected_length}"
                    )

            # Colocar em Fila de Reprodução (Não substitui dados antigos, bloqueia Aguardando)
            if not safe_queue_put(self._output_buffer, pcm_data, replace_oldest=False):
                # Quando fila está cheia bloqueia Aguardando
                await asyncio.wait_for(self._output_buffer.put(pcm_data), timeout=2.0)

        except asyncio.TimeoutError:
            logger.warning(
                "Fila de Reprodução bloqueada Timeout, descartando Quadros PCM"
            )
        except Exception as e:
            logger.warning(f" PCM DadosFalha: {e}")

    async def reinitialize_stream(self, is_input: bool = True):
        """áudio（Processandodispositivoerro/Desconectado）

        Args:
            is_input: True=Entrada, False=Saída

        Usando:
            - dispositivo
            - erroRestaurando
            - sistema
        """
        if self._is_closing:
            return False if is_input else None

        try:
            if is_input:
                if self.input_stream:
                    self.input_stream.stop()
                    self.input_stream.close()

                self.input_stream = sd.InputStream(
                    device=self.mic_device_id,
                    samplerate=self.device_input_sample_rate,
                    channels=self.input_channels,
                    dtype=np.float32,
                    blocksize=self._device_input_frame_size,
                    callback=self._input_callback,
                    finished_callback=self._input_finished_callback,
                    latency="low",
                )
                self.input_stream.start()
                logger.info("EntradaNovamenteInicializandoSucesso")
                return True
            else:
                if self.output_stream:
                    self.output_stream.stop()
                    self.output_stream.close()

                self.output_stream = sd.OutputStream(
                    device=self.speaker_device_id,
                    samplerate=self.device_output_sample_rate,
                    channels=self.output_channels,
                    dtype=np.float32,
                    blocksize=self._device_output_frame_size,
                    callback=self._output_callback,
                    finished_callback=self._output_finished_callback,
                    latency="low",
                )
                self.output_stream.start()
                logger.info("SaídaNovamenteInicializandoSucesso")
                return None
        except Exception as e:
            stream_type = "Entrada" if is_input else "Saída"
            logger.error(f"{stream_type}Falha: {e}")
            if is_input:
                return False
            else:
                raise

    async def clear_audio_queue(self):
        """LimpandoáudioFila.

        Usando:
            - usuárioEm  Reprodução
            - áudio
            - erroRestaurando  Limpando  dados
        """
        cleared_count = 0

        # LimpandoReproduçãoFila
        while not self._output_buffer.empty():
            try:
                self._output_buffer.get_nowait()
                cleared_count += 1
            except asyncio.QueueEmpty:
                break

        # Limpando
        if self._resample_input_buffer:
            cleared_count += len(self._resample_input_buffer)
            self._resample_input_buffer.clear()

        if self._resample_output_buffer:
            cleared_count += len(self._resample_output_buffer)
            self._resample_output_buffer.clear()

        if cleared_count > 0:
            logger.info(f"LimpandoÁudioFila， {cleared_count} QuadrosÁudioDados")

        if cleared_count > 100:
            gc.collect()
            logger.debug("")

    # ============= AEC  =============

    async def _cleanup_resampler(self, resampler, name: str):
        """
        DispositivoFonte.
        """
        if not resampler:
            return

        try:
            # 
            if hasattr(resampler, "resample_chunk"):
                empty_array = np.array([], dtype=np.float32)
                resampler.resample_chunk(empty_array, last=True)
        except Exception as e:
            logger.debug(f"{name}DispositivoFalha: {e}")

        try:
            # TentativaFechando
            if hasattr(resampler, "close"):
                resampler.close()
                logger.debug(f"{name}DispositivoJáFechando")
        except Exception as e:
            logger.debug(f"Fechando{name}DispositivoFalha: {e}")

    def _stop_stream_sync(self, stream, name: str):
        """
        Pararáudio.
        """
        if not stream:
            return
        try:
            if stream.active:
                stream.stop()
            stream.close()
        except Exception as e:
            logger.warning(f"Fechando{name}Falha: {e}")

    async def close(self):
        """FechandoáudioDispositivoFonte.

        Ordem:
        1. ConfigurandoFechando，Pararáudio
        2. LimpandoeDispositivo
        3. LimpandoFilae
        4. FechandoAECProcessandoDispositivo
        5. Dispositivo
        6. Dispositivo
        7. 
        """
        if self._is_closing:
            return

        self._is_closing = True
        logger.info("ComeçarFechandoÁudioDispositivo...")

        try:
            # 1. PararÁudio
            self._stop_stream_sync(self.input_stream, "Entrada")
            self._stop_stream_sync(self.output_stream, "Saída")
            self.input_stream = None
            self.output_stream = None

            # AguardandoParar
            await asyncio.sleep(0.05)

            # 2. LimpandoeDispositivo
            self._encoded_callback = None
            self._audio_listeners.clear()

            # 3. LimpandoFilae
            await self.clear_audio_queue()

            # 4. FechandoAECProcessandoDispositivo
            if self.audio_processor:
                try:
                    await self.audio_processor.close()
                except Exception as e:
                    logger.warning(f"FechandoAECProcessando Dispositivo Falha: {e}")
                finally:
                    self.audio_processor = None

            # 5. Dispositivo
            await self._cleanup_resampler(self.input_resampler, "Entrada")
            await self._cleanup_resampler(self.output_resampler, "Saída")
            self.input_resampler = None
            self.output_resampler = None

            # 6. Dispositivo
            self.opus_encoder = None
            self.opus_decoder = None

            # 7. 
            gc.collect()

            logger.info("Áudio  FonteJá")
        except Exception as e:
            logger.error(f"FechandoÁudioDispositivoEmErro: {e}", exc_info=True)
        finally:
            self._is_closing = True

    def __del__(self):
        """ - PesquisarFonte"""
        if not self._is_closing:
            logger.warning("AudioCodecNãoFechando， close() ")
