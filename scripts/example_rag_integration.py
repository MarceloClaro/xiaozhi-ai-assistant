"""
Exemplo de uso do RAG Local integrado na Application.

Demonstra como usar o contexto expandido em uma aplicação real.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.application import Application
from src.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


async def example_with_context():
    """Exemplo: Usar RAG com contexto expandido."""
    setup_logging()

    logger.info("=" * 70)
    logger.info("EXEMPLO: Integração de RAG com Application")
    logger.info("=" * 70)

    # 1. Obter instância da Application (singleton)
    logger.info("\n[1] Obtendo instância da Application...")
    app = Application.get_instance()
    logger.info("✅ Application inicializada")

    # 2. Adicionar conhecimento ao RAG
    logger.info("\n[2] Adicionando conhecimento ao RAG...")
    await app.context_system.rag_manager.add_chunk(
        "A Aplicação Xiaozhi é um assistente de IA baseado em Python "
        "com suporte a múltiplos protocolos (WebSocket, MQTT) e modos "
        "(GUI, CLI). Ela integra plugins para áudio, MCP, IoT, calendário "
        "e atalhos.",
        metadata={"topic": "xiaozhi", "type": "general"},
        source="documentation",
    )

    await app.context_system.rag_manager.add_chunk(
        "O sistema RAG Local permite aumentar o contexto da IA em até 20x. "
        "Com 8000 chunks de 2000 caracteres, é possível armazenar 16MB de "
        "texto local. Isso compensa o contexto curto das APIs.",
        metadata={"topic": "rag", "type": "feature"},
        source="documentation",
    )

    logger.info("✅ 2 chunks adicionados ao RAG")

    # 3. Processar input com contexto expandido
    logger.info("\n[3] Processando input com contexto expandido...")
    user_query = "Como a aplicação usa RAG?"

    result = await app.process_input_with_context(
        user_query, max_context_length=2000
    )

    logger.info(f"User input: {result['user_input']}")
    logger.info(
        f"Contexto gerado: {result['context_length']} caracteres"
    )
    logger.info(f"Chunks usados: {result['chunks_used']}")
    logger.info(f"\n--- Full Prompt (para IA) ---")
    logger.info(result["full_prompt"])
    logger.info("--- Fim ---\n")

    # 4. Registrar turno de conversa
    logger.info("\n[4] Registrando turno de conversa...")
    await app.register_conversation_turn(
        user_input=user_query,
        assistant_response=(
            "A Aplicação Xiaozhi usa RAG para expandir o contexto de IA. "
            "Com 8000 chunks locais, ela consegue compensar limitações "
            "de contexto curto das APIs."
        ),
        context_chunks=["chunk_0", "chunk_1"],
    )
    logger.info("✅ Turno registrado")

    # 5. Simular gravação de reunião
    logger.info("\n[5] Simulando gravação de reunião...")

    await app.start_meeting_recording("Reunião sobre RAG")
    logger.info("✅ Gravação iniciada")

    # Adicionar transcrição progressivamente
    await app.add_meeting_transcript(
        "Vamos discutir a implementação de RAG na aplicação Xiaozhi.",
        speaker="João",
    )
    await app.add_meeting_transcript(
        "Sim, precisamos integrar o EnhancedContext.",
        speaker="Maria",
    )

    # Finalizar reunião
    meeting_info = await app.stop_meeting_recording()
    logger.info(f"✅ Reunião finalizada: {meeting_info.get('title')}")
    logger.info(f"   Resumo: {meeting_info.get('summary', '')[:100]}...")

    # 6. Obter estatísticas
    logger.info("\n[6] Estatísticas do RAG...")
    stats = app.get_rag_stats()

    logger.info(f"RAG Stats:")
    logger.info(f"  • Chunks: {stats['rag']['total_chunks']}/8000")
    logger.info(
        f"  • Conversas: {stats['rag']['conversation_turns']}"
    )
    logger.info(f"  • Reuniões: {stats['meetings']['total_meetings']}")
    logger.info(f"  • DB: {stats['rag']['db_path']}")

    logger.info("\n" + "=" * 70)
    logger.info("✅ EXEMPLO CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 70)


async def example_with_api_fallback():
    """
    Exemplo: Usar contexto expandido com API Ollama como fallback.

    Mostra como integrar com um modelo local.
    """
    setup_logging()

    logger.info("=" * 70)
    logger.info("EXEMPLO: RAG + Ollama Fallback")
    logger.info("=" * 70)

    app = Application.get_instance()

    # 1. Preparar contexto
    logger.info("\n[1] Preparando contexto...")
    result = await app.process_input_with_context(
        "Qual é a melhor forma de usar RAG com IA?",
        max_context_length=3000,
    )

    logger.info(f"Contexto: {result['context_length']} chars")

    # 2. Em produção, você chamaria sua API aqui:
    logger.info("\n[2] Chamando API com contexto...")
    logger.info("Prompt para enviar à API:")
    logger.info(f"  {result['full_prompt'][:200]}...")

    # Exemplo (comentado):
    # response = await ollama_client.complete(
    #     prompt=result["full_prompt"],
    #     model="llava",
    #     temperature=0.7
    # )

    # 3. Registrar conversação
    logger.info("\n[3] Registrando na memória...")
    await app.register_conversation_turn(
        user_input=result["user_input"],
        assistant_response="Resposta simulada da IA com contexto...",
        context_chunks=result.get("chunks_used", []),
    )

    logger.info("✅ Conversa registrada e persistida!")
    logger.info("\n" + "=" * 70)


if __name__ == "__main__":
    # Executar exemplo básico
    asyncio.run(example_with_context())

    # Opcional: Executar exemplo com fallback
    # asyncio.run(example_with_api_fallback())
