#!/usr/bin/env python3
"""
Script de teste rápido do sistema RAG Local.
Execute com: python scripts/test_rag_system.py
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logging_config import get_logger, setup_logging
from src.utils.enhanced_context_example import EnhancedContext

logger = get_logger(__name__)


async def main():
    """Executar testes do sistema RAG."""
    setup_logging()

    logger.info("=" * 60)
    logger.info("🧪 TESTE DO SISTEMA RAG LOCAL + MEMÓRIA EXPANDIDA")
    logger.info("=" * 60)

    try:
        # 1. Inicializar sistema
        logger.info("\n[1/6] Inicializando sistema...")
        context_system = EnhancedContext()
        logger.info("✅ Sistema inicializado")

        # 2. Testar adição de chunks
        logger.info("\n[2/6] Testando adição de chunks...")
        await context_system.rag_manager.add_chunk(
            "RAG permite aumentar o contexto de modelos de IA "
            "através de recuperação de documentos relevantes. "
            "Isso melhora significativamente a qualidade das respostas.",
            metadata={"topic": "rag", "difficulty": "advanced"},
            source="test",
        )

        await context_system.rag_manager.add_chunk(
            "O sistema local pode processar até 8000 chunks "
            "de 2000 caracteres cada, totalizando 16MB de texto. "
            "Isso permite um histórico muito mais expansivo.",
            metadata={"topic": "memory", "difficulty": "advanced"},
            source="test",
        )

        await context_system.rag_manager.add_chunk(
            "Embeddings locais com sentence-transformers "
            "permitem busca vetorial rápida sem dependência "
            "de APIs externas.",
            metadata={"topic": "embeddings"},
            source="test",
        )
        logger.info(f"✅ 3 chunks adicionados")

        # 3. Testar busca de chunks
        logger.info("\n[3/6] Testando busca de chunks...")
        chunks = await context_system.rag_manager.retrieve_chunks(
            "Como aumentar contexto de IA?", top_k=2
        )
        logger.info(f"✅ {len(chunks)} chunks recuperados")
        for i, chunk in enumerate(chunks, 1):
            similarity = chunk.get("similarity", 0)
            logger.info(
                f"  - Chunk {i}: {chunk['text'][:60]}... "
                f"(similaridade: {similarity:.3f})"
            )

        # 4. Testar histórico de conversas
        logger.info("\n[4/6] Testando histórico de conversas...")
        await context_system.add_conversation_turn(
            user_input="Como usar RAG?",
            assistant_response=(
                "RAG permite acessar conhecimento externo "
                "durante a geração de respostas."
            ),
        )

        await context_system.add_conversation_turn(
            user_input="Qual o tamanho máximo?",
            assistant_response="Até 8000 chunks de 2000 caracteres.",
        )

        conv_context = (
            context_system.rag_manager.get_conversation_context(
                window_size=5
            )
        )
        logger.info(f"✅ Histórico de conversa gerado:")
        logger.info(conv_context)

        # 5. Testar gravação de reunião
        logger.info("\n[5/6] Testando gravação de reunião...")
        await context_system.start_meeting_recording(
            "Teste de Reunião RAG"
        )

        await context_system.add_transcript_chunk(
            "Vamos implementar um sistema de RAG local "
            "para aumentar a memória da aplicação.",
            speaker="João",
        )

        await context_system.add_transcript_chunk(
            "Sim! Isso vai permitir processar reuniões "
            "inteiras como contexto.",
            speaker="Maria",
        )

        meeting_info = await context_system.stop_meeting_recording()
        logger.info(f"✅ Reunião criada: {meeting_info.get('title')}")
        logger.info(f"   Resumo: {meeting_info.get('summary')[:100]}...")

        # 6. Testar preparação de contexto expandido
        logger.info("\n[6/6] Testando contexto expandido para query...")
        full_context = (
            await context_system.prepare_context_for_query(
                "Como implementar sistema de memória expandida?",
                max_context_length=2000,
            )
        )

        logger.info(
            f"✅ Contexto preparado: "
            f"{full_context['context_length']} caracteres"
        )
        logger.info(f"   Chunks usados: {full_context['chunks_used']}")
        logger.info(f"   Partes: {len(full_context['parts'])}")

        # Estatísticas finais
        logger.info("\n" + "=" * 60)
        logger.info("📊 ESTATÍSTICAS FINAIS")
        logger.info("=" * 60)

        stats = context_system.get_rag_stats()
        logger.info(f"RAG Manager:")
        logger.info(f"  - Chunks: {stats['rag']['total_chunks']}/8000")
        logger.info(
            f"  - Conversas: {stats['rag']['conversation_turns']}"
        )
        logger.info(
            f"  - Embeddings: "
            f"{'✅ Habilitado' if stats['rag']['embedding_enabled'] else '❌ Desabilitado'}"
        )
        logger.info(f"  - DB: {stats['rag']['db_path']}")

        logger.info(f"\nMeeting Manager:")
        logger.info(f"  - Reuniões: {stats['meetings']['total_meetings']}")
        logger.info(
            f"  - Tamanho total: "
            f"{stats['meetings']['total_transcript_size']} chars"
        )
        logger.info(
            f"  - Gravação ativa: "
            f"{'Sim' if stats['meetings']['active_recording'] else 'Não'}"
        )

        logger.info("\n" + "=" * 60)
        logger.info("✅ TODOS OS TESTES PASSARAM!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error("❌ Erro durante os testes: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
