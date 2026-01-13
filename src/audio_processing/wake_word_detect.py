import asyncio
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import sherpa_onnx

from src.constants.constants import AudioConfig
from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger
from src.utils.resource_finder import resource_finder

logger = get_logger(__name__)


class WakeWordDetector:

    def __init__(self):
        # Estado interno de áudio
        self.audio_codec = None
        self.is_running_flag = False
        self.paused = False
        self.detection_task = None

        # Fila de áudio (Processando)
        self._audio_queue = asyncio.Queue(maxsize=100)

        # Controle de cooldown
        self.last_detection_time = 0
        self.detection_cooldown = 1.5  # 1.5 segundos

        # Callbacks externos
        self.on_detected_callback: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Verificar configuração
        config = ConfigManager.get_instance()
        if not config.get_config("WAKE_WORD_OPTIONS.USE_WAKE_WORD", False):
            logger.info("Wake word desativado")
            self.enabled = False
            return

        # Inicializando parâmetros
        self.enabled = True
        self.sample_rate = AudioConfig.INPUT_SAMPLE_RATE

        # Sherpa-ONNX KWS
        self.keyword_spotter = None
        self.stream = None

        # Inicializando
        self._load_config(config)
        self._init_kws_model()
        self._validate_config()

    def _load_config(self, config):
        """
        Carregando configuração de parâmetros.
        """
        # Configuração de Caminho do Modelo
        model_path = config.get_config(
            "WAKE_WORD_OPTIONS.MODEL_PATH", "models"
        )
        found_dir = resource_finder.find_directory(model_path)
        self.model_dir: Path = (
            found_dir if found_dir is not None else Path(model_path)
        )

        if found_dir is None:
            # Plano de contingência: Tentar usar caminho direto
            logger.warning(
                "ResourceFinder não achou diretório do modelo; usando: %s",
                self.model_dir,
            )

        # Configuração de Parâmetro KWS - otimizar velocidade
        self.num_threads = config.get_config(
            "WAKE_WORD_OPTIONS.NUM_THREADS", 4
        )  # Aumentar número de threads
        self.provider = config.get_config("WAKE_WORD_OPTIONS.PROVIDER", "cpu")
        self.max_active_paths = config.get_config(
            "WAKE_WORD_OPTIONS.MAX_ACTIVE_PATHS", 2
        )  # PesquisaCaminho
        self.keywords_score = config.get_config(
            "WAKE_WORD_OPTIONS.KEYWORDS_SCORE", 1.8
        )  # Pontuação
        self.keywords_threshold = config.get_config(
            "WAKE_WORD_OPTIONS.KEYWORDS_THRESHOLD", 0.2
        )  # Limiar
        self.num_trailing_blanks = config.get_config(
            "WAKE_WORD_OPTIONS.NUM_TRAILING_BLANKS", 1
        )

        logger.info(
            "KWS configurado - limiar: %s, pontuação: %s",
            self.keywords_threshold,
            self.keywords_score,
        )

    def _init_kws_model(self):
        """
        InicializandoSherpa-ONNX KeywordSpotterModelo.
        """
        try:
            # PesquisarModeloArquivo
            encoder_path = self.model_dir / "encoder.onnx"
            decoder_path = self.model_dir / "decoder.onnx"
            joiner_path = self.model_dir / "joiner.onnx"
            tokens_path = self.model_dir / "tokens.txt"
            keywords_path = self.model_dir / "keywords.txt"

            required_files = [
                encoder_path,
                decoder_path,
                joiner_path,
                tokens_path,
                keywords_path,
            ]
            for file_path in required_files:
                if not file_path.exists():
                    raise FileNotFoundError(f"Modelo ausente: {file_path}")

            logger.info(f"Sherpa-ONNX KeywordSpotterModelo: {self.model_dir}")
            logger.info(
                "Sherpa-ONNX versao instalada: %s",
                getattr(sherpa_onnx, "__version__", "desconhecida"),
            )

            # KeywordSpotter
            self.keyword_spotter = sherpa_onnx.KeywordSpotter(
                tokens=str(tokens_path),
                encoder=str(encoder_path),
                decoder=str(decoder_path),
                joiner=str(joiner_path),
                keywords_file=str(keywords_path),
                num_threads=self.num_threads,
                sample_rate=self.sample_rate,
                feature_dim=80,
                max_active_paths=self.max_active_paths,
                keywords_score=self.keywords_score,
                keywords_threshold=self.keywords_threshold,
                num_trailing_blanks=self.num_trailing_blanks,
                provider=self.provider,
            )

            logger.info("Sherpa-ONNX KeywordSpotterModeloSucesso")

        except Exception as e:
            logger.error(
                "Falha ao Inicializar Sherpa-ONNX KeywordSpotter: %s",
                e,
                exc_info=True,
            )
            self.enabled = False

    def on_detected(self, callback: Callable):
        """
        Configurando callback para detecção de palavra-chave de ativação.
        """
        self.on_detected_callback = callback

    def on_audio_data(self, audio_data: np.ndarray):
        if not self.enabled or not self.is_running_flag or self.paused:
            return

        try:
            # Fila de áudio (Processando)
            self._audio_queue.put_nowait(audio_data.copy())
        except asyncio.QueueFull:
            # FilaDados
            try:
                self._audio_queue.get_nowait()
                self._audio_queue.put_nowait(audio_data.copy())
            except asyncio.QueueEmpty:
                self._audio_queue.put_nowait(audio_data.copy())
        except Exception as e:
            logger.debug(f"ÁudioDadosFalha: {e}")

    async def start(self, audio_codec) -> bool:
        if not self.enabled:
            logger.warning("Não")
            return False

        if not self.keyword_spotter:
            logger.error("KeywordSpotterNãoInicializando")
            return False

        try:
            self.audio_codec = audio_codec
            self.is_running_flag = True
            self.paused = False

            # Cria stream de detecção
            self.stream = self.keyword_spotter.create_stream()

            # paraÁudioDispositivo（Modo）
            self.audio_codec.add_audio_listener(self)

            # Iniciando
            self.detection_task = asyncio.create_task(self._detection_loop())

            logger.info(
                "Sherpa-ONNX KeywordSpotterDispositivoIniciandoSucesso（Modo）"
            )
            return True
        except Exception as e:
            logger.error(f"IniciandoKeywordSpotterDispositivoFalha: {e}")
            self.enabled = False
            return False

    async def _detection_loop(self):
        """
        .
        """
        error_count = 0
        MAX_ERRORS = 5

        while self.is_running_flag:
            try:
                if self.paused:
                    await asyncio.sleep(0.1)
                    continue

                # ProcessandoÁudioDados
                await self._process_audio()

                # Pequeno intervalo para cooperar com o loop de eventos
                await asyncio.sleep(0.005)
                error_count = 0

            except asyncio.CancelledError:
                break
            except Exception as e:
                error_count += 1
                logger.error(f"KWSErro({error_count}/{MAX_ERRORS}): {e}")

                # Erro
                if self.on_error:
                    try:
                        if asyncio.iscoroutinefunction(self.on_error):
                            await self.on_error(e)
                        else:
                            self.on_error(e)
                    except Exception as callback_error:
                        logger.error(f"ErroFalha: {callback_error}")

                if error_count >= MAX_ERRORS:
                    logger.critical("AtingidoMáximoErroVezes，PararKWS")
                    break
                await asyncio.sleep(1)

    async def _process_audio(self):
        """
        Processandoáudiodados.
        """
        try:
            if not self.stream:
                return

            try:
                audio_data = self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            if audio_data is None or len(audio_data) == 0:
                return

            # ÁudioFormatopara float32
            if audio_data.dtype == np.int16:
                samples = audio_data.astype(np.float32) / 32768.0
            else:
                samples = audio_data.astype(np.float32)

            # ÁudioDadosparaKeywordSpotter
            self.stream.accept_waveform(
                sample_rate=self.sample_rate, waveform=samples
            )

            # Pesquisar
            if (
                self.keyword_spotter
                and self.keyword_spotter.is_ready(self.stream)
            ):
                self.keyword_spotter.decode_stream(self.stream)
                result = self.keyword_spotter.get_result(self.stream)

                if result:
                    await self._handle_detection_result(result)
                    # Estado
                    self.keyword_spotter.reset_stream(self.stream)

        except Exception as e:
            logger.error(f"Erro ao Processar Áudio KWS: {e}", exc_info=True)
            raise  # Lançar Exceção novamente, deixar _detection_loop Capturar

    async def _handle_detection_result(self, result):
        """
        Processando resultado de detecção.
        """
        # Verificação para evitar disparo duplicado
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_cooldown:
            return

        self.last_detection_time = current_time

        # Dispara callback de detecção
        if self.on_detected_callback:
            try:
                if asyncio.iscoroutinefunction(self.on_detected_callback):
                    await self.on_detected_callback(result, result)
                else:
                    self.on_detected_callback(result, result)
            except Exception as e:
                logger.error(f"Falha: {e}")

    async def stop(self):
        """
        PararDispositivo.
        """
        self.is_running_flag = False

        # deAudioCodecDispositivo
        if self.audio_codec:
            self.audio_codec.remove_audio_listener(self)

        if self.detection_task:
            self.detection_task.cancel()
            try:
                await self.detection_task
            except asyncio.CancelledError:
                pass

        # LimpandoFila
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.info("Detector de palavra-chave parado")

    def _validate_config(self):
        """
        ValidandoconfiguraçãoParâmetro.
        """
        if not self.enabled:
            return

        # ValidandoLimiarParâmetro
        if not 0.1 <= self.keywords_threshold <= 1.0:
            logger.warning(
                "Limiar %s fora do intervalo; usando 0.25",
                self.keywords_threshold,
            )
            self.keywords_threshold = 0.25

        if not 0.1 <= self.keywords_score <= 10.0:
            logger.warning(
                "Pontuação %s fora do intervalo; usando 2.0",
                self.keywords_score,
            )
            self.keywords_score = 2.0

        logger.info(
            "KWS Validação Concluída - Limiar: %s, Pontuação: %s",
            self.keywords_threshold,
            self.keywords_score,
        )
