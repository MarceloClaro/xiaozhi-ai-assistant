import asyncio
import subprocess
from pathlib import Path
from typing import Optional

import numpy as np

from src.constants.constants import AudioConfig
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class MusicDecoder:

    def __init__(self, sample_rate: int = 24000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._process: Optional[subprocess.Process] = None
        self._decode_task: Optional[asyncio.Task] = None
        self._stopped = False

    async def start_decode(
        self, file_path: Path, output_queue: asyncio.Queue, start_position: float = 0.0
    ) -> bool:
        if not file_path.exists():
            logger.error(f"ÁudioArquivoNãoExiste: {file_path}")
            return False

        self._stopped = False

        try:
            try:
                result = await asyncio.create_subprocess_exec(
                    "ffmpeg",
                    "-version",
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                await result.wait()
            except FileNotFoundError:
                logger.error("FFmpeg NãoouNãoEm PATH Em")
                return False

            cmd = ["ffmpeg"]

            if start_position > 0:
                cmd.extend(["-ss", str(start_position)])

            cmd.extend(
                [
                    "-i",
                    str(file_path),  # EntradaArquivo
                    "-f",
                    "s16le",  # SaídaFormato：16Bits PCM
                    "-ar",
                    str(self.sample_rate),  # Taxa de amostragem
                    "-ac",
                    str(self.channels),  # Canais
                    "-loglevel",
                    "error",  # SaídaErroInformação
                    "-",  # Saídapara stdout
                ]
            )

            self._process = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Iniciando
            self._decode_task = asyncio.create_task(self._read_pcm_stream(output_queue))

            position_info = f" from {start_position:.1f}s" if start_position > 0 else ""
            logger.info(
                f"ComeçarÁudio: {file_path.name}{position_info} "
                f"[{self.sample_rate}Hz, {self.channels}ch]"
            )
            return True

        except Exception as e:
            logger.error(f"IniciandoÁudioFalha: {e}")
            return False

    async def _read_pcm_stream(self, output_queue: asyncio.Queue):
        """ PCM Fila,UsandoFila + Tempode."""
        import time

        frame_duration_ms = AudioConfig.FRAME_DURATION
        frame_size_samples = int(self.sample_rate * (frame_duration_ms / 1000))
        frame_size_bytes = frame_size_samples * 2 * self.channels
        logger.info(
            f"DispositivoParâmetro: QuadrosTamanho={frame_size_samples}, "
            f"{frame_size_bytes}Bytes, {frame_duration_ms}ms"
        )

        eof_reached = False
        frame_count = 0
        start_time = time.time()  # ComeçarTempo

        try:
            while not self._stopped:
                # QuadrosDados
                chunk = await self._process.stdout.read(frame_size_bytes)

                if not chunk:
                    # EOF - ArquivoConcluído
                    duration_decoded = frame_count * frame_duration_ms / 1000
                    logger.info(
                        f"ÁudioConcluído， {frame_count} Quadros， {duration_decoded:.1f}Segundos"
                    )

                    if self._process and self._process.returncode is not None:
                        try:
                            stderr_output = await self._process.stderr.read()
                            if stderr_output:
                                logger.error(
                                    f"FFmpeg ErroSaída: {stderr_output.decode('utf-8', errors='ignore')}"
                                )
                        except Exception:
                            pass

                    eof_reached = True
                    break

                frame_count += 1

                audio_array = np.frombuffer(chunk, dtype=np.int16)

                if self.channels > 1:
                    audio_array = audio_array.reshape(-1, self.channels)

                # ==========  ==========

                # 1: Filade
                queue_ratio = output_queue.qsize() / output_queue.maxsize if output_queue.maxsize > 0 else 0

                if queue_ratio < 0.3:
                    # Fila30%，
                    queue_based_sleep = 0
                elif queue_ratio < 0.7:
                    # Fila30-70%，
                    queue_based_sleep = 0.03
                else:
                    # Fila70%+，
                    queue_based_sleep = 0.06

                # 2: Tempo，NãoReprodução
                expected_elapsed = frame_count * (frame_duration_ms / 1000.0)
                actual_elapsed = time.time() - start_time

                if actual_elapsed < expected_elapsed:
                    # Reprodução，ForçarAguardando
                    time_based_sleep = expected_elapsed - actual_elapsed
                else:
                    time_based_sleep = 0

                # deMáximoValor，NãoFila，NãoReprodução
                target_sleep = max(queue_based_sleep, time_based_sleep)

                if target_sleep > 0:
                    await asyncio.sleep(target_sleep)

                # Fila（Timeout）
                try:
                    await asyncio.wait_for(output_queue.put(audio_array), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning(f"ÁudioFilaTimeout，Quadros {frame_count}")
                    continue

        except asyncio.CancelledError:
            logger.debug("")
        except Exception as e:
            logger.error(f" PCM Falha: {e}")
        finally:
            if eof_reached:
                try:
                    await output_queue.put(None)
                except Exception:
                    pass

    async def stop(self):
        if self._stopped:
            return

        self._stopped = True
        logger.debug("PararÁudioDispositivo")

        if self._decode_task and not self._decode_task.done():
            self._decode_task.cancel()
            try:
                await self._decode_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        if self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                # Forçar
                try:
                    self._process.kill()
                    await self._process.wait()
                except Exception:
                    pass
            except Exception as e:
                logger.debug(f" FFmpeg ProcessoFalha: {e}")

    def is_running(self) -> bool:
        return (
            not self._stopped
            and self._process is not None
            and self._process.returncode is None
        )

    async def wait_completion(self):
        if self._decode_task and not self._decode_task.done():
            try:
                await self._decode_task
            except Exception:
                pass
