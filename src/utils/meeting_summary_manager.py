"""
Módulo de resumo de reuniões/áudio capturado.
Integra com RAG para armazenar e consultar transcrições.
"""

from datetime import datetime
from typing import Optional

from src.utils.logging_config import get_logger
from src.utils.rag_manager import RagManager

logger = get_logger(__name__)


class MeetingSummaryManager:
    """Gerenciador de resumos de reuniões com RAG."""

    def __init__(self, rag_manager: RagManager):
        """
        Inicializar gerenciador de reuniões.

        Args:
            rag_manager: Instância do gerenciador RAG
        """
        self.rag_manager = rag_manager
        self.active_recording: Optional[dict] = None
        logger.info("Gerenciador de Resumos de Reuniões inicializado")

    async def start_recording(self, title: str = None) -> dict:
        """
        Iniciar gravação de reunião.

        Args:
            title: Título da reunião (auto-gerado se não informado)

        Returns:
            Dicionário com informações da gravação
        """
        if title is None:
            title = f"Reunião {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        self.active_recording = {
            "title": title,
            "start_time": datetime.now(),
            "transcript_parts": [],
            "duration": 0,
        }

        logger.info("Gravação iniciada: %s", title)
        return self.active_recording

    async def add_transcript_chunk(
        self, text: str, speaker: str = "Falante"
    ) -> bool:
        """
        Adicionar parte de transcrição à reunião ativa.

        Args:
            text: Texto transcrito
            speaker: Nome do falante

        Returns:
            Sucesso da operação
        """
        if self.active_recording is None:
            logger.warning("Nenhuma gravação ativa")
            return False

        self.active_recording["transcript_parts"].append({
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.now().isoformat(),
        })

        logger.debug(
            "Chunk de transcrição adicionado (%d caracteres)",
            len(text),
        )
        return True

    async def stop_recording(self) -> Optional[str]:
        """
        Parar gravação e processar reunião.

        Returns:
            ID da reunião criada ou None se erro
        """
        if self.active_recording is None:
            logger.warning("Nenhuma gravação ativa para parar")
            return None

        # Calcular duração
        self.active_recording["duration"] = (
            datetime.now() - self.active_recording["start_time"]
        ).total_seconds()

        # Formatar transcrição completa
        full_transcript = "\n".join([
            f"[{part['timestamp']}] {part['speaker']}: {part['text']}"
            for part in self.active_recording["transcript_parts"]
        ])

        # Armazenar no RAG
        meeting_id = await self.rag_manager.add_meeting_transcript(
            title=self.active_recording["title"],
            transcript=full_transcript,
            duration_seconds=int(self.active_recording["duration"]),
        )

        logger.info(
            "Gravação concluída: %s (%d segundos)",
            self.active_recording["title"],
            self.active_recording["duration"],
        )

        self.active_recording = None
        return meeting_id

    async def get_meeting_summary(
        self, meeting_title: str
    ) -> Optional[str]:
        """
        Obter resumo de uma reunião.

        Args:
            meeting_title: Título da reunião

        Returns:
            Resumo da reunião ou None
        """
        for meeting in self.rag_manager.meeting_transcripts:
            if meeting["title"] == meeting_title:
                return meeting["summary"]

        logger.warning("Reunião não encontrada: %s", meeting_title)
        return None

    async def search_meetings(self, query: str) -> list[dict]:
        """
        Buscar reuniões por query.

        Args:
            query: Texto para buscar

        Returns:
            Lista de reuniões relevantes
        """
        logger.info("Buscando reuniões: %s", query)
        return await self.rag_manager.search_meetings(query)

    async def get_meeting_details(
        self, meeting_title: str
    ) -> Optional[dict]:
        """
        Obter detalhes completos de uma reunião.

        Args:
            meeting_title: Título da reunião

        Returns:
            Dicionário com detalhes completos
        """
        for meeting in self.rag_manager.meeting_transcripts:
            if meeting["title"] == meeting_title:
                return {
                    "title": meeting["title"],
                    "summary": meeting["summary"],
                    "duration_seconds": meeting["duration_seconds"],
                    "timestamp": meeting["timestamp"],
                    "chunks_count": len(meeting.get("chunk_ids", [])),
                }

        return None

    async def list_all_meetings(self) -> list[dict]:
        """
        Listar todas as reuniões registradas.

        Returns:
            Lista de meetings com resumos
        """
        return [
            {
                "title": m["title"],
                "summary": m["summary"][:200] + "..."
                if len(m["summary"]) > 200
                else m["summary"],
                "duration": m["duration_seconds"],
                "date": m["timestamp"],
            }
            for m in self.rag_manager.meeting_transcripts
        ]

    def get_stats(self) -> dict:
        """Obter estatísticas de reuniões."""
        return {
            "total_meetings": len(
                self.rag_manager.meeting_transcripts
            ),
            "total_transcript_size": sum(
                len(m["transcript"])
                for m in self.rag_manager.meeting_transcripts
            ),
            "active_recording": self.active_recording is not None,
        }
