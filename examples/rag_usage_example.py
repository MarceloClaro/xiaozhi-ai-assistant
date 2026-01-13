#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exemplo de uso do RAG Local integrado com main.py
Demonstra como usar o sistema depois que Application é inicializado.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.application import Application


async def example_usage():
    """Exemplos de como usar o RAG Local via Application"""

    print("\n" + "=" * 70)
    print("  EXEMPLO: USO DO RAG LOCAL COM main.py")
    print("=" * 70 + "\n")

    # Obter instância (já inicializada por main.py)
    app = Application.get_instance()
    print("✓ Application obtida (inicializada por main.py)\n")

    # ========================================
    # Exemplo 1: Adicionar Conhecimento
    # ========================================
    print("Exemplo 1: Adicionar Chunks ao RAG")
    print("-" * 70)

    knowledge_base = [
        {
            "text": "Python é uma linguagem de programação interpretada.",
            "metadata": {"topic": "python", "type": "intro"},
            "source": "knowledge_base",
        },
        {
            "text": "RAG (Retrieval-Augmented Generation) expande contexto.",
            "metadata": {"topic": "rag", "type": "ml"},
            "source": "knowledge_base",
        },
        {
            "text": "Xiaozhi é um assistente inteligente offline.",
            "metadata": {"topic": "xiaozhi", "type": "product"},
            "source": "knowledge_base",
        },
    ]

    for kb in knowledge_base:
        await app.context_system.rag_manager.add_chunk(
            text=kb["text"], metadata=kb["metadata"], source=kb["source"]
        )
        print(f"  ✓ Adicionado: {kb['text'][:50]}...")

    print()

    # ========================================
    # Exemplo 2: Processar Input com Contexto
    # ========================================
    print("Exemplo 2: Processar Input com Contexto Expandido")
    print("-" * 70)

    queries = ["O que é Python?", "Como RAG funciona?", "O que é Xiaozhi?"]

    for query in queries:
        result = await app.process_input_with_context(query)
        print(f"  Query: {query}")
        print(f"    Contexto: {result.get('context_length', 0)} chars")
        print(f"    Status: {result.get('status', 'ok')}")
        print(f"    Context: {result.get('context', '')[:70]}...\n")

    # ========================================
    # Exemplo 3: Registrar Conversas
    # ========================================
    print("Exemplo 3: Registrar Conversas para Histórico")
    print("-" * 70)

    conv = {
        "user": "Como Xiaozhi funciona?",
        "assistant": "Xiaozhi é um assistente baseado em IA...",
        "chunks": 3,
    }

    await app.register_conversation_turn(
        user_input=conv["user"],
        assistant_response=conv["assistant"],
        context_chunks=conv["chunks"],
    )
    print(f"  ✓ Conversa registrada em histórico SQLite")
    print(f"    User: {conv['user']}")
    print(f"    Assistant: {conv['assistant'][:50]}...\n")

    # ========================================
    # Exemplo 4: Gravar Reunião
    # ========================================
    print("Exemplo 4: Gravar Reunião com Auto-Summarização")
    print("-" * 70)

    await app.start_meeting_recording(title="Briefing RAG Local")
    print("  ✓ Reunião iniciada\n")

    meeting_speeches = [
        ("João", "Vamos implementar RAG Local"),
        ("Maria", "Precisamos de 8000 chunks de capacidade"),
        ("João", "Concordo, vamos usar SQLite"),
    ]

    for speaker, text in meeting_speeches:
        await app.add_meeting_transcript(text, speaker=speaker)
        print(f"  ✓ {speaker}: {text}")

    await app.stop_meeting_recording()
    print("  ✓ Reunião finalizada (resumo gerado automaticamente)\n")

    # ========================================
    # Exemplo 5: Obter Estatísticas
    # ========================================
    print("Exemplo 5: Monitorar Estatísticas do RAG")
    print("-" * 70)

    stats = app.get_rag_stats()
    print("  RAG Statistics:")
    for key, value in stats["rag"].items():
        print(f"    {key}: {value}")

    print("\n  Meeting Statistics:")
    if "meetings" in stats:
        for key, value in stats["meetings"].items():
            print(f"    {key}: {value}")

    # ========================================
    # Resumo
    # ========================================
    print("\n" + "=" * 70)
    print("  RESUMO DOS EXEMPLOS")
    print("=" * 70)
    print("""
✓ Knowledge Base adicionado (3 chunks)
✓ Queries processadas com contexto expandido
✓ Conversas registradas em histórico permanente
✓ Reunião gravada e auto-summarizada
✓ Estatísticas monitoradas

O RAG Local está pronto para uso em produção!
    """)


if __name__ == "__main__":
    try:
        asyncio.run(example_usage())
    except Exception as e:
        print(f"\n✗ Erro: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
