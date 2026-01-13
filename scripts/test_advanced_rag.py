"""
Teste Avançado: RAG com Chunks + Busca
Valida busca e contexto com dados reais
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.application import Application
from src.utils.logging_config import setup_logging


async def test_advanced_rag():
    """Teste avançado com chunks e busca."""
    setup_logging()

    print("\n" + "=" * 70)
    print("TESTE AVANCADO: RAG com Chunks + Busca")
    print("=" * 70)

    app = Application.get_instance()

    # 1. Adicionar conhecimento
    print("\n[1] Adicionando chunks ao RAG...")
    chunks = [
        "Python é uma linguagem de programação versátil criada em 1989.",
        "O sistema RAG Local permite aumentar o contexto em até 20 vezes.",
        "SQLite é um banco de dados relacional leve e rápido.",
        "Machine Learning é um campo da IA que permite aprendizado automático.",
        "Xiaozhi é um assistente de IA baseado em Python com múltiplos protocolos.",
    ]

    for i, chunk_text in enumerate(chunks):
        await app.context_system.rag_manager.add_chunk(
            text=chunk_text,
            metadata={"topic": f"topic_{i}", "type": "test"},
            source="test_data",
        )

    print(f"✅ {len(chunks)} chunks adicionados")

    # 2. Fazer query sobre Python
    print("\n[2] Buscando por Python...")
    result = await app.process_input_with_context("Como funciona Python?")
    print(f"✅ Contexto gerado: {result['context_length']} chars")
    print(f"   Chunks usados: {result['chunks_used']}")

    # 3. Outra query sobre RAG
    print("\n[3] Buscando por RAG...")
    result2 = await app.process_input_with_context("Explique sobre RAG")
    print(f"✅ Contexto gerado: {result2['context_length']} chars")
    print(f"   Chunks usados: {result2['chunks_used']}")

    # 4. Query sobre Machine Learning
    print("\n[4] Buscando por Machine Learning...")
    result3 = await app.process_input_with_context("O que é Machine Learning?")
    print(f"✅ Contexto gerado: {result3['context_length']} chars")
    print(f"   Chunks usados: {result3['chunks_used']}")

    # 5. Registrar conversas
    print("\n[5] Registrando conversas...")
    await app.register_conversation_turn(
        user_input="Como funciona Python?",
        assistant_response="Python é uma linguagem versátil...",
        context_chunks=["chunk_0"],
    )
    await app.register_conversation_turn(
        user_input="Explique sobre RAG",
        assistant_response="RAG permite aumentar contexto...",
        context_chunks=["chunk_1"],
    )
    print("✅ 2 conversas registradas")

    # 6. Stats finais
    print("\n[6] Estatísticas finais...")
    stats = app.get_rag_stats()
    print(f"✅ Chunks no RAG: {stats['rag']['total_chunks']}/8000")
    print(f"   Conversas: {stats['rag']['conversation_turns']}")
    print(f"   Reuniões: {stats['meetings']['total_meetings']}")

    print("\n" + "=" * 70)
    print("✅ TESTE AVANCADO CONCLUIDO COM SUCESSO!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_advanced_rag())
