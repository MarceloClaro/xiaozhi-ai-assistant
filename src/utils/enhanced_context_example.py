"""
Exemplo de integração do RAG local + Memória Expandida na aplicação.
Mostra como usar RAG para aumentar contexto e resumir reuniões.
"""

import asyncio
from pathlib import Path

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

try:
    from src.utils.rag_manager import RagManager
    from src.utils.meeting_summary_manager import MeetingSummaryManager
except ImportError as e:
    logger.error(f"Erro ao importar módulos RAG: {e}")
    raise


class EnhancedContext:
    """
    Sistema de contexto expandido que combina:
    - RAG local (8000 chunks de 2000 caracteres)
    - Histórico expandido de conversas
    - Resumo automático de reuniões
    - Recuperação inteligente por embeddings
    """

    def __init__(self):
        """Inicializar sistema de contexto expandido."""
        self.rag_manager = RagManager()
        self.meeting_manager = MeetingSummaryManager(self.rag_manager)
        logger.info("Sistema de Contexto Expandido inicializado")

    async def prepare_context_for_query(
        self, user_query: str, max_context_length: int = 4000
    ) -> dict:
        """
        Preparar contexto expandido para uma query do usuário.

        Args:
            user_query: Query do usuário
            max_context_length: Máximo de caracteres para contexto

        Returns:
            Dicionário com contexto expandido
        """
        context_parts = []
        total_length = 0

        # 1. Recuperar chunks relevantes do RAG (busca vetorial)
        logger.info("Recuperando chunks relevantes...")
        relevant_chunks = await self.rag_manager.retrieve_chunks(
            user_query, top_k=5
        )

        if relevant_chunks:
            chunks_context = "=== CONHECIMENTO RECUPERADO ===\n\n"
            for chunk in relevant_chunks:
                chunk_text = (
                    f"[{chunk['source']}] {chunk['text']}"
                )
                if (
                    total_length + len(chunk_text)
                    <= max_context_length
                ):
                    chunks_context += chunk_text + "\n\n"
                    total_length += len(chunk_text)

            context_parts.append(chunks_context)

        # 2. Adicionar histórico recente de conversa
        logger.info("Adicionando histórico de conversa...")
        conv_context = (
            self.rag_manager.get_conversation_context(window_size=5)
        )
        if total_length + len(conv_context) <= max_context_length:
            context_parts.append(conv_context)
            total_length += len(conv_context)

        # 3. Buscar reuniões relevantes se aplicável
        if "reunião" in user_query.lower() or (
            "resumo" in user_query.lower()
        ):
            logger.info("Buscando reuniões relevantes...")
            meetings = await self.meeting_manager.search_meetings(
                user_query
            )
            if meetings:
                meeting_context = (
                    "=== REUNIÕES RELEVANTES ===\n\n"
                )
                for meeting in meetings:
                    meeting_summary = (
                        f"📋 {meeting['title']}\n"
                        f"Resumo: {meeting['summary']}\n\n"
                    )
                    if (
                        total_length + len(meeting_summary)
                        <= max_context_length
                    ):
                        meeting_context += meeting_summary
                        total_length += len(meeting_summary)

                if len(meeting_context) > len(
                    "=== REUNIÕES RELEVANTES ===\n\n"
                ):
                    context_parts.append(meeting_context)

        full_context = "".join(context_parts)

        return {
            "context": full_context,
            "context_length": len(full_context),
            "chunks_used": len(relevant_chunks),
            "parts": context_parts,
        }

    async def add_conversation_turn(
        self,
        user_input: str,
        assistant_response: str,
        context_chunks: list[str] = None,
    ):
        """
        Registrar um turno de conversa no RAG.

        Args:
            user_input: Input do usuário
            assistant_response: Resposta do assistente
            context_chunks: Chunks usados como contexto
        """
        await self.rag_manager.add_conversation_turn(
            user_input,
            assistant_response,
            context_chunks,
        )

    async def start_meeting_recording(self, title: str = None) -> dict:
        """
        Iniciar gravação de reunião.

        Args:
            title: Título da reunião

        Returns:
            Info da gravação iniciada
        """
        return await self.meeting_manager.start_recording(title)

    async def add_transcript_chunk(
        self, text: str, speaker: str = "Falante"
    ) -> bool:
        """
        Adicionar parte de transcrição.

        Args:
            text: Texto transcrito
            speaker: Nome do falante

        Returns:
            Sucesso da operação
        """
        return await self.meeting_manager.add_transcript_chunk(
            text, speaker
        )

    # Alias para Application.add_meeting_transcript() para compatibilidade
    async def add_meeting_transcript(
        self, text: str, speaker: str = "Falante"
    ) -> bool:
        """Alias para add_transcript_chunk (compatibilidade com Application)."""
        return await self.add_transcript_chunk(text, speaker)

    async def stop_meeting_recording(self) -> dict:
        """
        Parar gravação e gerar resumo.

        Returns:
            Info da reunião criada
        """
        meeting_id = await self.meeting_manager.stop_recording()
        if meeting_id:
            details = (
                await self.meeting_manager.get_meeting_details(
                    meeting_id
                )
            )
            return details or {}
        return {}

    def get_rag_stats(self) -> dict:
        """Obter estatísticas do RAG."""
        return {
            "rag": self.rag_manager.get_stats(),
            "meetings": self.meeting_manager.get_stats(),
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================
async def example_usage():
    """Exemplo completo de uso do sistema expandido."""

    logger.info("=== EXEMPLO: Sistema de Contexto Expandido ===")

    # 1. Inicializar sistema
    context_system = EnhancedContext()

    # 2. Adicionar alguns chunks à base de conhecimento
    logger.info("\n1️⃣ Adicionando chunks ao RAG...")
    await context_system.rag_manager.add_chunk(
        "Python é uma linguagem de programação versátil e poderosa. "
        "Ela é usada em desenvolvimento web, ciência de dados, "
        "automação e muito mais.",
        metadata={"topic": "python", "difficulty": "beginner"},
        source="documentation",
    )

    await context_system.rag_manager.add_chunk(
        "RAG (Retrieval-Augmented Generation) permite que modelos de IA "
        "acessem conhecimento externo durante a geração de respostas. "
        "Isso melhora significativamente a qualidade e precisão.",
        metadata={"topic": "rag", "difficulty": "advanced"},
        source="documentation",
    )

    # 3. Simular uma conversa
    logger.info("\n2️⃣ Simulando conversa com histórico...")
    await context_system.add_conversation_turn(
        user_input="Como funciona RAG?",
        assistant_response=(
            "RAG permite que sistemas acessem "
            "conhecimento externo para respostas melhores."
        ),
    )

    # 4. Preparar contexto para nova query
    logger.info("\n3️⃣ Preparando contexto para query...")
    context = await context_system.prepare_context_for_query(
        "Qual é a relação entre Python e RAG?"
    )
    logger.info("Contexto preparado: %d caracteres", context["context_length"])
    logger.info("Chunks usados: %d", context["chunks_used"])

    # 5. Iniciar gravação de reunião
    logger.info("\n4️⃣ Iniciando gravação de reunião...")
    await context_system.start_meeting_recording(
        "Reunião de Planejamento 2026-01-12"
    )

    # Simular adição de transcrição
    await context_system.add_transcript_chunk(
        "Vamos discutir a implementação de RAG no projeto.",
        speaker="João",
    )
    await context_system.add_transcript_chunk(
        "Sim, precisamos de embeddings locais para performance.",
        speaker="Maria",
    )
    await context_system.add_transcript_chunk(
        "Vamos usar sentence-transformers para isso.",
        speaker="João",
    )

    # Finalizar reunião
    logger.info("\n5️⃣ Finalizando reunião e gerando resumo...")
    meeting_info = await context_system.stop_meeting_recording()
    logger.info("Reunião criada: %s", meeting_info.get("title"))
    logger.info("Resumo: %s", meeting_info.get("summary", "")[:100])

    # 6. Buscar reuniões
    logger.info("\n6️⃣ Buscando reuniões sobre RAG...")
    meetings = await context_system.meeting_manager.search_meetings(
        "RAG embeddings"
    )
    logger.info("Reuniões encontradas: %d", len(meetings))

    # 7. Exibir estatísticas
    logger.info("\n7️⃣ Estatísticas do Sistema...")
    stats = context_system.get_rag_stats()
    logger.info(
        "RAG Stats: %d chunks, %d conversas",
        stats["rag"]["total_chunks"],
        stats["rag"]["conversation_turns"],
    )
    logger.info(
        "Meetings: %d reuniões",
        stats["meetings"]["total_meetings"],
    )

    logger.info("\n✅ Exemplo concluído!")


if __name__ == "__main__":
    asyncio.run(example_usage())
