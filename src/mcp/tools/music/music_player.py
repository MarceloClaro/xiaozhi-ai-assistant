import asyncio
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import requests

from src.audio_codecs.music_decoder import MusicDecoder
from src.constants.constants import AudioConfig
from src.utils.logging_config import get_logger
from src.utils.resource_finder import get_user_cache_dir

# TentativaMúsica  DadosBanco de dados
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError

    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

logger = get_logger(__name__)


class MusicMetadata:
    """
    Música  dados.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self.file_id = file_path.stem  # Arquivo，ID
        self.file_size = file_path.stat().st_size

        # deArquivode  Dados
        self.title = None
        self.artist = None
        self.album = None
        self.duration = None  # Segundos

    def extract_metadata(self) -> bool:
        """
        Músicaarquivo  dados.
        """
        if not MUTAGEN_AVAILABLE:
            return False

        try:
            audio_file = MutagenFile(self.file_path)
            if audio_file is None:
                return False

            # Informação
            if hasattr(audio_file, "info"):
                self.duration = getattr(audio_file.info, "length", None)

            # ID3Informação
            tags = audio_file.tags if audio_file.tags else {}

            # Título
            self.title = self._get_tag_value(tags, ["TIT2", "TITLE", "\xa9nam"])

            # Artista
            self.artist = self._get_tag_value(tags, ["TPE1", "ARTIST", "\xa9ART"])

            # Álbum
            self.album = self._get_tag_value(tags, ["TALB", "ALBUM", "\xa9alb"])

            return True

        except ID3NoHeaderError:
            # NenhumID3，Não  Erro
            return True
        except Exception as e:
            logger.debug(f"DadosFalha {self.filename}: {e}")
            return False

    def _get_tag_value(self, tags: dict, tag_names: List[str]) -> Optional[str]:
        """
        dedeEmValor.
        """
        for tag_name in tag_names:
            if tag_name in tags:
                value = tags[tag_name]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None

    def format_duration(self) -> str:
        """
        Formato Conversão Reprodução.
        """
        if self.duration is None:
            return "Não"

        minutes = int(self.duration) // 60
        seconds = int(self.duration) % 60
        return f"{minutes:02d}:{seconds:02d}"


class MusicPlayer:
    def __init__(self):
        # FFmpeg DispositivoeReproduçãoFila
        self.decoder: Optional[MusicDecoder] = None
        self._music_queue: Optional[asyncio.Queue] = None
        self._playback_task: Optional[asyncio.Task] = None

        # ReproduçãoEstado
        self.current_song = ""
        self.current_url = ""
        self.song_id = ""
        self.total_duration = 0
        self.is_playing = False
        self.paused = False
        self.current_position = 0
        self.start_play_time = 0
        self._pause_source: Optional[str] = None  # "tts" | "manual" | None

        # ReproduçãoArquivoCaminho（Pausado/Restaurando）
        self._current_file_path: Optional[Path] = None

        # Iniciando：AguardandoTTSFinal  Iniciando
        self._deferred_start_path: Optional[Path] = None
        self._deferred_start_position: float = 0.0

        #
        self.lyrics = []  # ，Formatopara [(Tempo, ), ...]
        self.current_lyric_index = -1  #

        # DiretórioConfigurando - UsandoDiretório
        user_cache_dir = get_user_cache_dir()
        self.cache_dir = user_cache_dir / "music"
        self.temp_cache_dir = self.cache_dir / "temp"
        self._init_cache_dirs()

        # API
        self.config = {
            "SEARCH_URL": "http://search.kuwo.cn/r.s",
            "PLAY_URL": "http://api.xiaodaokg.com/kuwo.php",
            "LYRIC_URL": "https://api.xiaodaokg.com/kw/kwlyric.php",
            "HEADERS": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36"
                ),
                "Accept": "*/*",
                "Connection": "keep-alive",
            },
        }

        #
        self._clean_temp_cache()

        # Aplicação e AudioCodec
        self.app = None
        self.audio_codec = None
        self._initialize_app_reference()

        # Lista local em cache
        self._local_playlist = None
        self._last_scan_time = 0

        logger.info(
            "MúsicaReproduçãoDispositivoInicialização concluída (FFmpeg + AudioCodec Modo)"
        )

    def _initialize_app_reference(self):
        """
        Inicializandoaplicaçãoprogramae AudioCodec.
        """
        try:
            from src.application import Application

            self.app = Application.get_instance()
            self.audio_codec = getattr(self.app, "audio_codec", None)

            if not self.audio_codec:
                logger.warning("AudioCodec NãoInicializando，MúsicaReproduçãoNão")

        except Exception as e:
            logger.warning(f"ApplicationFalha: {e}")
            self.app = None

    def _init_cache_dirs(self):
        """
        InicializandoDiretório.
        """
        try:
            # Diretório
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # Diretório
            self.temp_cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"MúsicaDiretórioInicialização concluída: {self.cache_dir}")
        except Exception as e:
            logger.error(f"DiretórioFalha: {e}")
            # paraDiretório
            self.cache_dir = Path(tempfile.gettempdir()) / "xiaozhi_music_cache"
            self.temp_cache_dir = self.cache_dir / "temp"
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.temp_cache_dir.mkdir(parents=True, exist_ok=True)

    def _clean_temp_cache(self):
        """
        arquivo.
        """
        try:
            # LimpandoDiretórioEmdeArquivo
            for file_path in self.temp_cache_dir.glob("*"):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        logger.debug(f"JáDeletandoArquivo: {file_path.name}")
                except Exception as e:
                    logger.warning(f"DeletandoArquivoFalha: {file_path.name}, {e}")

            logger.info("MúsicaConcluído")
        except Exception as e:
            logger.error(f"DiretórioFalha: {e}")

    def _scan_local_music(self, force_refresh: bool = False) -> List[MusicMetadata]:
        """
        Música，Retorno.
        """
        current_time = time.time()

        # SeNãoForçarNão（5），Retorno
        if (
            not force_refresh
            and self._local_playlist is not None
            and (current_time - self._last_scan_time) < 300
        ):
            return self._local_playlist

        playlist = []

        if not self.cache_dir.exists():
            logger.warning(f"DiretórioNãoExiste: {self.cache_dir}")
            return playlist

        # PesquisarMúsicaArquivo
        music_files = []
        for pattern in ["*.mp3", "*.m4a", "*.flac", "*.wav", "*.ogg"]:
            music_files.extend(self.cache_dir.glob(pattern))

        logger.debug(f"Encontrado {len(music_files)} MúsicaArquivo")

        # Arquivo
        for file_path in music_files:
            try:
                metadata = MusicMetadata(file_path)

                # TentativaDados
                if MUTAGEN_AVAILABLE:
                    metadata.extract_metadata()

                playlist.append(metadata)

            except Exception as e:
                logger.debug(f"ProcessandoMúsicaArquivoFalha {file_path.name}: {e}")

        # e
        playlist.sort(key=lambda x: (x.artist or "Unknown", x.title or x.filename))

        # Lista local atualizada
        self._local_playlist = playlist
        self._last_scan_time = current_time

        logger.info(f"Concluído，Encontrado {len(playlist)} Música")
        return playlist

    async def get_local_playlist(self, force_refresh: bool = False) -> dict:
        """
        Música.
        """
        try:
            playlist = self._scan_local_music(force_refresh)

            if not playlist:
                return {
                    "status": "info",
                    "message": "EmNenhumMúsicaArquivo",
                    "playlist": [],
                    "total_count": 0,
                }

            # Formato de conversão para IA
            formatted_playlist = []
            for metadata in playlist:
                title = metadata.title or "Não"
                artist = metadata.artist or "Não"
                song_info = f"{title} - {artist}"
                formatted_playlist.append(song_info)

            return {
                "status": "success",
                "message": f"Encontrado {len(playlist)} Música",
                "playlist": formatted_playlist,
                "total_count": len(playlist),
            }

        except Exception as e:
            logger.error(f"Falha: {e}")
            return {
                "status": "error",
                "message": f"Falha: {str(e)}",
                "playlist": [],
                "total_count": 0,
            }

    async def search_local_music(self, query: str) -> dict:
        """
        PesquisaMúsica.
        """
        try:
            playlist = self._scan_local_music()

            if not playlist:
                return {
                    "status": "info",
                    "message": "EmNenhumMúsicaArquivo",
                    "results": [],
                    "found_count": 0,
                }

            query = query.lower()
            results = []

            for metadata in playlist:
                # Em、、Arquivo  EmPesquisa
                searchable_text = " ".join(
                    filter(
                        None,
                        [
                            metadata.title,
                            metadata.artist,
                            metadata.album,
                            metadata.filename,
                        ],
                    )
                ).lower()

                if query in searchable_text:
                    title = metadata.title or "Não"
                    artist = metadata.artist or "Não"
                    song_info = f"{title} - {artist}"
                    results.append(
                        {
                            "song_info": song_info,
                            "file_id": metadata.file_id,
                            "duration": metadata.format_duration(),
                        }
                    )

            return {
                "status": "success",
                "message": f"EmMúsicaEmEncontrado {len(results)} Correspondênciade",
                "results": results,
                "found_count": len(results),
            }

        except Exception as e:
            logger.error(f"PesquisaMúsicaFalha: {e}")
            return {
                "status": "error",
                "message": f"PesquisaFalha: {str(e)}",
                "results": [],
                "found_count": 0,
            }

    async def play_local_song_by_id(self, file_id: str) -> dict:
        """
        arquivoIDReprodução.
        """
        try:
            # ArquivoCaminho
            file_path = self.cache_dir / f"{file_id}.mp3"

            if not file_path.exists():
                # TentativaFormato
                for ext in [".m4a", ".flac", ".wav", ".ogg"]:
                    alt_path = self.cache_dir / f"{file_id}{ext}"
                    if alt_path.exists():
                        file_path = alt_path
                        break
                else:
                    return {
                        "status": "error",
                        "message": f"ArquivoNãoExiste: {file_id}",
                    }

            # Informação
            metadata = MusicMetadata(file_path)
            if MUTAGEN_AVAILABLE:
                metadata.extract_metadata()

            # Informação
            title = metadata.title or "Não"
            artist = metadata.artist or "Não"
            self.current_song = f"{title} - {artist}"
            self.song_id = file_id
            self.total_duration = metadata.duration or 0
            self.current_url = str(file_path)  # ArquivoCaminho
            self.lyrics = []  # Arquivo  NãoSuportado

            # ComeçarReprodução
            success = await self._start_playback(file_path)

            if success:
                # RetornoInformação（AguardarInformação）
                duration_str = self._format_time(self.total_duration)
                return {
                    "status": "success",
                    "message": f"EmReprodução: {self.current_song}",
                    "song": self.current_song,
                    "duration": duration_str,
                    "total_seconds": self.total_duration,
                }
            else:
                return {"status": "error", "message": "ReproduçãoFalha"}

        except Exception as e:
            logger.error(f"ReproduçãoMúsicaFalha: {e}")
            return {"status": "error", "message": f"ReproduçãoFalha: {str(e)}"}

    # ：Posiçãoe
    async def get_position(self):
        if not self.is_playing or self.paused:
            return self.current_position

        current_pos = min(self.total_duration, time.time() - self.start_play_time)

        # PesquisarReproduçãoConcluído
        if current_pos >= self.total_duration and self.total_duration > 0:
            await self._handle_playback_finished()

        return current_pos

    async def get_progress(self):
        """
        Reprodução.
        """
        if self.total_duration <= 0:
            return 0
        position = await self.get_position()
        return round(position * 100 / self.total_duration, 1)

    async def _handle_playback_finished(self):
        """
        ProcessandoReproduçãoconcluído.
        """
        if self.is_playing:
            logger.info(f"ReproduçãoConcluído: {self.current_song}")
            # PararDispositivo
            if self.decoder:
                await self.decoder.stop()
                self.decoder = None

            self.is_playing = False
            self.paused = False
            self.current_position = self.total_duration

            # UIConcluídoEstado
            if self.app and hasattr(self.app, "set_chat_message"):
                dur_str = self._format_time(self.total_duration)
                await self._safe_update_ui(
                    f"ReproduçãoConcluído: {self.current_song} [{dur_str}]"
                )

    #
    async def search_and_play(self, song_name: str) -> dict:
        """
        Pesquisa  Reprodução.
        """
        try:
            # Pesquisa
            song_id, url = await self._search_song(song_name)
            if not song_id or not url:
                return {"status": "error", "message": f"NãoEncontrado: {song_name}"}

            # Reprodução
            success = await self._play_url(url)
            if success:
                # RetornoInformação（AguardarInformação）
                duration_str = self._format_time(self.total_duration)
                return {
                    "status": "success",
                    "message": f"EmReprodução: {self.current_song}",
                    "song": self.current_song,
                    "duration": duration_str,
                    "total_seconds": self.total_duration,
                }
            else:
                return {"status": "error", "message": "ReproduçãoFalha"}

        except Exception as e:
            logger.error(f"PesquisaReproduçãoFalha: {e}")
            return {"status": "error", "message": f"OperaçãoFalha: {str(e)}"}

    async def stop(self) -> dict:
        """
        PararReprodução.
        """
        try:
            if not self.is_playing and not self._pending_play:
                return {"status": "info", "message": "Nenhum  EmReproduçãode"}

            current_song = self.current_song

            # PararDispositivo
            if self.decoder:
                await self.decoder.stop()
                self.decoder = None

            # Reprodução
            if self._playback_task and not self._playback_task.done():
                self._playback_task.cancel()
                try:
                    await self._playback_task
                except asyncio.CancelledError:
                    pass

            # LimpandoFila
            if self._music_queue:
                while not self._music_queue.empty():
                    try:
                        self._music_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

            # Estado
            self.is_playing = False
            self.paused = False
            self._pause_source = None  # PausadoOrigem
            self._pending_play = False
            self._pending_file_path = None
            self.current_position = 0

            # UI
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(f"JáParar: {current_song}")

            logger.info(f"PararReprodução: {current_song}")
            return {"status": "success", "message": "JáParar"}

        except Exception as e:
            logger.error(f"PararReproduçãoFalha: {e}")
            return {"status": "error", "message": f"PararFalha: {str(e)}"}

    async def pause(self, source: str = "manual") -> dict:
        """PausadoReprodução（PararDispositivo，NãoLimpandoFila）.

        Args:
            source: PausadoOrigem，"manual"=usuárioPausado, "tts"=TTSdePausado
        """
        try:
            if not self.is_playing:
                return {"status": "info", "message": "Nenhum  EmReproduçãode"}

            if self.paused:
                # SeJáPausado，OrigemNão，Origem（）
                if self._pause_source != source:
                    old_source = self._pause_source
                    self._pause_source = source
                    logger.info(f"PausadoOrigem: {old_source} → {source}")
                return {"status": "info", "message": "JáPausadoEstado"}

            # ✅ ImediatamenteConfigurandoPausado，
            self.paused = True
            self._pause_source = source

            # Pausado  deReproduçãoPosição
            if self.start_play_time > 0:
                self.current_position = time.time() - self.start_play_time

            # PararDispositivo（PararDados）
            if self.decoder:
                await self.decoder.stop()
                self.decoder = None

            # AguardandoDispositivoParar
            await asyncio.sleep(0.05)

            # LimpandoMúsicaFila（NãoLimpando AudioCodec Fila）
            cleared_count = 0
            if self._music_queue:
                while not self._music_queue.empty():
                    try:
                        self._music_queue.get_nowait()
                        cleared_count += 1
                    except asyncio.QueueEmpty:
                        break

            logger.info(
                f"PausadoReprodução: {self.current_song} at {self._format_time(self.current_position)}, "
                f"Origem: {source}, Limpando {cleared_count} QuadrosMúsicaFila"
            )

            return {"status": "success", "message": "JáPausado"}

        except Exception as e:
            logger.error(f"PausadoReproduçãoFalha: {e}", exc_info=True)
            return {"status": "error", "message": f"PausadoFalha: {str(e)}"}

    async def resume(self) -> dict:
        """
        RestaurandoReprodução（dePausadoPosição）.
        """
        try:
            if not self.is_playing:
                return {"status": "info", "message": "Nenhum  EmReproduçãode"}

            if not self.paused:
                return {"status": "info", "message": "NãoPausado"}

            if not self._current_file_path or not self._current_file_path.exists():
                return {
                    "status": "error",
                    "message": "Incapaz deEncontradoÁudioArquivo",
                }

            # ✅ dePausadoPosiçãoNovamenteIniciandoeReprodução
            logger.info(
                f"RestaurandoReprodução: {self.current_song} from {self._format_time(self.current_position)}"
            )
            # NovamenteMúsicaFila
            self._music_queue = asyncio.Queue(maxsize=100)

            # NovamenteIniciando FFmpeg Dispositivo（dePausadoPosiçãoComeçar）
            self.decoder = MusicDecoder(
                sample_rate=AudioConfig.OUTPUT_SAMPLE_RATE,
                channels=AudioConfig.CHANNELS,
            )

            success = await self.decoder.start_decode(
                self._current_file_path, self._music_queue, self.current_position
            )
            if not success:
                logger.error("DispositivoFalha")
                return {"status": "error", "message": "RestaurandoReproduçãoFalha"}

            # deReprodução（SeExiste）
            if self._playback_task and not self._playback_task.done():
                self._playback_task.cancel()
                try:
                    await self._playback_task
                except asyncio.CancelledError:
                    pass

            # Iniciando  deReprodução
            self._playback_task = asyncio.create_task(self._playback_loop())

            # RestaurandoEstado
            self.paused = False
            self._pause_source = None  # PausadoOrigem
            self.start_play_time = time.time() - self.current_position  # Tempo

            # UI
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(f"ContinuarReprodução: {self.current_song}")

            return {"status": "success", "message": "JáRestaurandoReprodução"}

        except Exception as e:
            logger.error(f"RestaurandoReproduçãoFalha: {e}")
            return {"status": "error", "message": f"RestaurandoFalha: {str(e)}"}

    async def seek(self, position: float) -> dict:
        """
        Pulando paraparaPosição（Através deNovamente）.
        """
        try:
            if not self.is_playing:
                return {"status": "error", "message": "Nenhum  EmReproduçãode"}

            if not self._current_file_path or not self._current_file_path.exists():
                return {
                    "status": "error",
                    "message": "Incapaz deEncontradoÁudioArquivo",
                }

            # Limitado aPulando para
            if position < 0:
                position = 0
            elif position >= self.total_duration:
                position = max(0, self.total_duration - 1)

            # ✅ ：ImediatamentePararReprodução（）
            # PararDispositivo
            if self.decoder:
                await self.decoder.stop()
                self.decoder = None

            # AguardandoDispositivoParar
            await asyncio.sleep(0.05)

            # LimpandoMúsicaFila
            cleared_count = 0
            if self._music_queue:
                while not self._music_queue.empty():
                    try:
                        self._music_queue.get_nowait()
                        cleared_count += 1
                    except asyncio.QueueEmpty:
                        break

            # Limpando AudioCodec ReproduçãoFila（ImediatamentePararReprodução）
            if self.audio_codec:
                await self.audio_codec.clear_audio_queue()

            logger.info(
                f"Pulando parapara {self._format_time(position)}, Limpando {cleared_count} QuadrosMúsicaDados"
            )

            # de  PosiçãoNovamenteComeçarReprodução
            success = await self._start_playback(self._current_file_path, position)

            if success:
                return {
                    "status": "success",
                    "message": f"JáPulando parapara {self._format_time(position)}",
                }
            else:
                return {"status": "error", "message": "Pulando paraFalha"}

        except Exception as e:
            logger.error(f"Pulando paraFalha: {e}", exc_info=True)
            return {"status": "error", "message": f"Pulando paraFalha: {str(e)}"}

    async def get_lyrics(self) -> dict:
        """
        .
        """
        if not self.lyrics:
            return {"status": "info", "message": "Nenhum", "lyrics": []}

        # ，para
        lyrics_text = []
        for time_sec, text in self.lyrics:
            time_str = self._format_time(time_sec)
            lyrics_text.append(f"[{time_str}] {text}")

        return {
            "status": "success",
            "message": f"para {len(self.lyrics)} ",
            "lyrics": lyrics_text,
        }

    async def get_status(self) -> dict:
        """Reprodução Dispositivo estado.

        ：Retornousuáriodeestado，NãoRetornoPausado。 TTS PausadoNão AI paraMúsica"JáPausado"。
        """
        position = await self.get_position()
        progress = await self.get_progress()

        # ReproduçãoEstado（ TTS Pausado）
        if not self.is_playing:
            playing_state = "NãoReprodução"
        elif self.paused and self._pause_source == "manual":
            # Pausado"JáPausado"
            playing_state = "JáPausado"
        elif self.is_playing:
            playing_state = "ReproduçãoEm"
        else:
            playing_state = "Não"

        duration_str = self._format_time(self.total_duration)
        position_str = self._format_time(position)

        return {
            "status": "success",
            "message": (
                f": {self.current_song}\n"
                f"ReproduçãoEstado: {playing_state}\n"
                f"PausadoOrigemEstado: {self._pause_source} ttsPausado\n"
                f"Reprodução: {duration_str}\n"
                f"Posição: {position_str}\n"
                f"Reprodução: {progress}%\n"
                f": {'' if len(self.lyrics) > 0 else ''}"
            ),
        }

    #
    async def _search_song(self, song_name: str) -> Tuple[str, str]:
        """
        Pesquisa ID e URL da música com fallback automático.
        """
        try:
            # Tentar fonte primária com retry
            result = await self._search_song_with_retry(
                song_name,
                max_retries=3
            )
            if result[0]:  # Se encontrou (song_id não vazio)
                return result

            # Fallback para fonte alternativa
            logger.warning(
                f"Fonte primária falhou para '{song_name}', "
                "tentando alternativa..."
            )
            return "", ""

        except Exception as e:
            logger.error(f"Erro na busca de música: {e}")
            return "", ""

    async def _search_song_with_retry(
        self, song_name: str, max_retries: int = 3
    ) -> Tuple[str, str]:
        """
        Pesquisa com retry automático e timeout adaptativo.
        """
        for attempt in range(max_retries):
            try:
                timeout = 10 + (attempt * 2)  # 10s, 12s, 14s
                logger.info(
                    f"Tentativa {attempt + 1}/{max_retries} "
                    f"para '{song_name}' (timeout={timeout}s)"
                )

                return await self._search_song_impl(
                    song_name,
                    timeout=timeout
                )
            except requests.Timeout:
                logger.warning(
                    f"Timeout na tentativa {attempt + 1}, "
                    f"tentando novamente..."
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                continue
            except requests.ConnectionError as e:
                logger.error(
                    f"Erro de conexão: {e}, tentativa {attempt + 1}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                continue
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                return "", ""

        logger.error(
            f"Falha ao buscar '{song_name}' após {max_retries} "
            "tentativas"
        )
        return "", ""

    async def _search_song_impl(
        self, song_name: str, timeout: int = 10
    ) -> Tuple[str, str]:
        """
        Implementação real da busca de música.
        """
        try:
            # Parâmetros da Pesquisa
            params = {
                "all": song_name,
                "ft": "music",
                "newsearch": "1",
                "alflac": "1",
                "itemset": "web_2013",
                "client": "kt",
                "cluster": "0",
                "pn": "0",
                "rn": "1",
                "vermerge": "1",
                "rformat": "json",
                "encoding": "utf8",
                "show_copyright_off": "1",
                "pcmp4": "1",
                "ver": "mbox",
                "vipver": "MUSIC_8.7.6.0.BCS31",
                "plat": "pc",
                "devid": "0",
            }

            # Pesquisa com timeout configurável
            response = await asyncio.to_thread(
                requests.get,
                self.config["SEARCH_URL"],
                params=params,
                headers=self.config["HEADERS"],
                timeout=timeout,
            )
            response.raise_for_status()

            # Analisando resposta
            text = response.text.replace("'", '"')

            # Extrair ID da música
            song_id = (
                self._extract_value(text, '"DC_TARGETID":"', '"')
            )
            if not song_id:
                return "", ""

            # Extrair informações da música
            title = (
                self._extract_value(text, '"NAME":"', '"')
                or song_name
            )
            artist = (
                self._extract_value(text, '"ARTIST":"', '"')
            )
            album = (
                self._extract_value(text, '"ALBUM":"', '"')
            )
            duration_str = (
                self._extract_value(text, '"DURATION":"', '"')
            )

            if duration_str:
                try:
                    self.total_duration = int(duration_str)
                except ValueError:
                    self.total_duration = 0

            # Configurando nome de exibição
            display_name = title
            if artist:
                display_name = f"{title} - {artist}"
                if album:
                    display_name += f" ({album})"
            self.current_song = display_name
            self.song_id = song_id

            # Obter URL de reprodução com retry
            play_url = f"{self.config['PLAY_URL']}?ID={song_id}"
            url_response = await asyncio.to_thread(
                requests.get,
                play_url,
                headers=self.config["HEADERS"],
                timeout=timeout
            )
            url_response.raise_for_status()

            play_url_text = url_response.text.strip()
            if play_url_text and play_url_text.startswith("http"):
                #
                await self._fetch_lyrics(song_id)
                return song_id, play_url_text

            return song_id, ""

        except Exception as e:
            logger.error(f"PesquisaFalha: {e}")
            return "", ""

    async def _play_url(self, url: str) -> bool:
        """
        ReproduçãoURL（：Usando FFmpeg + AudioCodec）
        """
        try:
            # Verificar AudioCodec
            if not self.audio_codec:
                logger.error("AudioCodec NãoInicializando，Incapaz deReproduçãoMúsica")
                return False

            # PararReprodução
            if self.is_playing:
                await self.stop()

            # Pesquisarou
            file_path = await self._get_or_download_file(url)
            if not file_path:
                return False

            # ComeçarReprodução
            return await self._start_playback(file_path)

        except Exception as e:
            logger.error(f"ReproduçãoFalha: {e}")
            return False

    async def _start_playback(
        self, file_path: Path, start_position: float = 0.0
    ) -> bool:
        """IniciandoReproduçãoMúsica（）

        Args:
            file_path: áudioarquivoCaminho
            start_position: IniciandoPosição（Segundos），de  Iniciando
        """
        try:
            # ✅ Pesquisar TTS Estado：SeTTS  EmReprodução，Iniciando
            if self.app and self.app.is_speaking():
                logger.info("TTS ReproduçãoEm，MúsicaIniciando")
                self._deferred_start_path = file_path
                self._deferred_start_position = start_position
                # para"Reprodução"Estado（AudioPluginRestaurandoPesquisar）
                self.is_playing = True
                self.paused = True
                return True

            # Iniciando
            self._deferred_start_path = None
            self._deferred_start_position = 0.0

            # ArquivoCaminho（Pausado/Restaurando）
            self._current_file_path = file_path

            # MúsicaFila
            self._music_queue = asyncio.Queue(maxsize=100)

            # Iniciando FFmpeg Dispositivo（SuportadodePosiçãoComeçar）
            self.decoder = MusicDecoder(
                sample_rate=AudioConfig.OUTPUT_SAMPLE_RATE,  # 24000Hz
                channels=AudioConfig.CHANNELS,  # 1 channel
            )

            success = await self.decoder.start_decode(
                file_path, self._music_queue, start_position
            )
            if not success:
                logger.error("IniciandoÁudioDispositivoFalha")
                return False

            # IniciandoReprodução
            self._playback_task = asyncio.create_task(self._playback_loop())

            # ReproduçãoEstado
            self.is_playing = True
            self.paused = False
            self._pending_play = False
            self.current_position = start_position  # dePosiçãoComeçar
            self.start_play_time = time.time() - start_position  # Tempo
            self.current_lyric_index = -1

            position_info = f" from {start_position:.1f}s" if start_position > 0 else ""
            logger.info(f"ComeçarReprodução: {self.current_song}{position_info}")

            # UI
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(f"EmReprodução: {self.current_song}")

            # Iniciando
            asyncio.create_task(self._lyrics_update_task())

            return True

        except Exception as e:
            logger.error(f"IniciandoReproduçãoFalha: {e}")
            return False

    async def _playback_loop(self):
        """
        Reprodução：deFila  PCM，AudioCodec.
        """
        try:
            while self.is_playing:
                if self.paused:
                    await asyncio.sleep(0.1)
                    continue

                # deMúsicaFila  Dados
                try:
                    audio_data = await asyncio.wait_for(
                        self._music_queue.get(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    logger.warning("MúsicaFilaTimeout")
                    continue

                if audio_data is None:
                    # EOF，ReproduçãoFinal
                    logger.info("MúsicaReproduçãoConcluído")
                    await self._handle_playback_finished()
                    break

                #  AudioCodec ReproduçãoFila
                await self._write_to_audio_codec(audio_data)

        except asyncio.CancelledError:
            logger.debug("Reprodução")
        except Exception as e:
            logger.error(f"ReproduçãoExceção: {e}", exc_info=True)

    async def _write_to_audio_codec(self, pcm_data: np.ndarray):
        """
        PCM dados AudioCodec ReproduçãoFila.
        """
        try:
            if not self.audio_codec:
                logger.error("AudioCodec NãoInicializando")
                return

            # CanaisDados
            if pcm_data.ndim > 1:
                # Canais（）
                pcm_data = pcm_data.mean(axis=1).astype(np.int16)

            # Envio direto para AudioCodec via write_pcm_direct
            await self.audio_codec.write_pcm_direct(pcm_data)

        except Exception as e:
            logger.error(f" AudioCodec Falha: {e}", exc_info=True)

    async def _get_or_download_file(self, url: str) -> Optional[Path]:
        """ouarquivo.

        Pesquisar，SeEmNenhumentão
        """
        try:
            # UsandoID  paraArquivo
            cache_filename = f"{self.song_id}.mp3"
            cache_path = self.cache_dir / cache_filename

            # PesquisarExiste
            if cache_path.exists():
                logger.info(f"Usando: {cache_path}")
                return cache_path

            # NãoExiste，
            return await self._download_file(url, cache_filename)

        except Exception as e:
            logger.error(f"ArquivoFalha: {e}")
            return None

    async def _download_file(self, url: str, filename: str) -> Optional[Path]:
        """arquivoparaDiretório.

        paraDiretório，concluídoparaDiretório
        """
        temp_path = None
        try:
            # ArquivoCaminho
            temp_path = self.temp_cache_dir / f"temp_{int(time.time())}_{filename}"

            #
            response = await asyncio.to_thread(
                requests.get,
                url,
                headers=self.config["HEADERS"],
                stream=True,
                timeout=30,
            )
            response.raise_for_status()

            # Arquivo
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Concluído，paraDiretório
            cache_path = self.cache_dir / filename
            shutil.move(str(temp_path), str(cache_path))

            logger.info(f"MúsicaConcluído: {cache_path}")
            return cache_path

        except Exception as e:
            logger.error(f"Falha: {e}")
            # Arquivo
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                    logger.debug(f"JáArquivo: {temp_path}")
                except Exception:
                    pass
            return None

    async def _fetch_lyrics(self, song_id: str):
        """
        .
        """
        try:
            #
            self.lyrics = []

            # API
            lyric_url = self.config.get("LYRIC_URL")
            lyric_api_url = f"{lyric_url}?id={song_id}"
            logger.info(f"URL: {lyric_api_url}")

            response = await asyncio.to_thread(
                requests.get, lyric_api_url, headers=self.config["HEADERS"], timeout=10
            )
            response.raise_for_status()

            # AnalisandoJSON
            data = response.json()

            # Analisando
            if (
                data.get("code") == 200
                and data.get("data")
                and data["data"].get("content")
            ):
                lrc_content = data["data"]["content"]

                # AnalisandoLRCFormato
                lines = lrc_content.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # CorrespondênciaTempoFormato [mm:ss.xx]
                    import re

                    time_match = re.match(r"\[(\d{2}):(\d{2})\.(\d{2})\](.+)", line)
                    if time_match:
                        minutes = int(time_match.group(1))
                        seconds = int(time_match.group(2))
                        centiseconds = int(time_match.group(3))
                        text = time_match.group(4).strip()

                        # para  Segundos
                        time_sec = minutes * 60 + seconds + centiseconds / 100.0

                        # e  Informação
                        if (
                            text
                            and not text.startswith("")
                            and not text.startswith("")
                            and not text.startswith("")
                            and not text.startswith("ti:")
                            and not text.startswith("ar:")
                            and not text.startswith("al:")
                            and not text.startswith("by:")
                            and not text.startswith("offset:")
                        ):
                            self.lyrics.append((time_sec, text))

                logger.info(f"Sucesso， {len(self.lyrics)} ")
            else:
                logger.warning(f"NãoparaouFormatoErro: {data.get('msg', '')}")

        except Exception as e:
            logger.error(f"Falha: {e}")

    async def _lyrics_update_task(self):
        """
        .
        """
        if not self.lyrics:
            return

        try:
            while self.is_playing:
                if self.paused:
                    await asyncio.sleep(0.5)
                    continue

                current_time = time.time() - self.start_play_time

                # PesquisarReproduçãoConcluído
                if current_time >= self.total_duration:
                    await self._handle_playback_finished()
                    break

                # PesquisarTempode
                current_index = self._find_current_lyric_index(current_time)

                # SeConversão，
                if current_index != self.current_lyric_index:
                    await self._display_current_lyric(current_index)

                await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Exceção: {e}")

    def _find_current_lyric_index(self, current_time: float) -> int:
        """
        PesquisarTempode.
        """
        # Pesquisar
        next_lyric_index = None
        for i, (time_sec, _) in enumerate(self.lyrics):
            # de(0.5Segundos)，
            if time_sec > current_time - 0.5:
                next_lyric_index = i
                break

        #
        if next_lyric_index is not None and next_lyric_index > 0:
            # SeEncontrado，de
            return next_lyric_index - 1
        elif next_lyric_index is None and self.lyrics:
            # Se  Encontrado，Jápara
            return len(self.lyrics) - 1
        else:
            # （Reprodução  Começar）
            return 0

    async def _display_current_lyric(self, current_index: int):
        """
        .
        """
        self.current_lyric_index = current_index

        if current_index < len(self.lyrics):
            time_sec, text = self.lyrics[current_index]

            # EmTempoeInformação
            position_str = self._format_time(time.time() - self.start_play_time)
            duration_str = self._format_time(self.total_duration)
            display_text = f"[{position_str}/{duration_str}] {text}"

            # UI
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(display_text)
                logger.debug(f": {text}")

    def _extract_value(self, text: str, start_marker: str, end_marker: str) -> str:
        """
        deEmValor.
        """
        start_pos = text.find(start_marker)
        if start_pos == -1:
            return ""

        start_pos += len(start_marker)
        end_pos = text.find(end_marker, start_pos)

        if end_pos == -1:
            return ""

        return text[start_pos:end_pos]

    def _format_time(self, seconds: float) -> str:
        """
        Segundos  Formato Conversão para mm:ss Formato.
        """
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"

    async def _safe_update_ui(self, message: str):
        """
        UI.
        """
        if not self.app or not hasattr(self.app, "set_chat_message"):
            return

        try:
            self.app.set_chat_message("assistant", message)
        except Exception as e:
            logger.error(f"UIFalha: {e}")

    def __del__(self):
        """
        Fonte.
        """
        try:
            # Se，Vezes
            self._clean_temp_cache()
        except Exception:
            # Erro，paraEmExceção
            pass


# MúsicaReproduçãoDispositivo
_music_player_instance = None


def get_music_player_instance() -> MusicPlayer:
    """
    MúsicaReproduçãoDispositivo.
    """
    global _music_player_instance
    if _music_player_instance is None:
        _music_player_instance = MusicPlayer()
        logger.info("[MusicPlayer] MúsicaReproduçãoDispositivo")
    return _music_player_instance
