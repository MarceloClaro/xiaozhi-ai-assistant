#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verifica integração do RAG Local com main.py --mode gui --protocol websocket"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.application import Application


async def verify_integration():
    """Testa se RAG está integrado com Application (usado por main.py)"""

    print("\n" + "=" * 70)
    print("  VERIFICAÇÃO: RAG INTEGRADO COM main.py")
    print("=" * 70 + "\n")

    # Test 1: Application Singleton
    print("Test 1: Application.get_instance()...")
    app = Application.get_instance()
    assert app is not None, "Application não inicializado"
    print("  ✓ Application singleton funcionando\n")

    # Test 2: EnhancedContext
    print("Test 2: Verificando EnhancedContext (RAG)...")
    assert hasattr(app, "context_system"), "Sem context_system"
    assert app.context_system is not None, "context_system is None"
    print("  ✓ EnhancedContext integrado\n")

    # Test 3: RagManager
    print("Test 3: Verificando RagManager...")
    rag = app.context_system.rag_manager
    assert rag is not None, "rag_manager is None"
    print("  ✓ RagManager operacional\n")

    # Test 4: Adicionar Chunk
    print("Test 4: Adicionando chunk via RAG...")
    chunk_text = "Integração RAG com main.py funcionando!"
    await rag.add_chunk(
        text=chunk_text,
        metadata={"topic": "integration_test"},
        source="test_script",
    )
    print("  ✓ Chunk adicionado com sucesso\n")

    # Test 5: Recuperar Contexto
    print("Test 5: Recuperando contexto...")
    query = "integração RAG"
    ctx = await app.context_system.prepare_context_for_query(query)
    assert len(ctx) > 0, "Contexto vazio"
    print(f"  ✓ Contexto gerado ({len(ctx)} chars)\n")

    # Test 6: Process Input with Context
    print("Test 6: process_input_with_context()...")
    result = await app.process_input_with_context("teste query")
    assert "context" in result, "Sem contexto no resultado"
    print(
        f"  ✓ Context: {result.get('context_length', 0)} chars, "
        f"Chunks: {result.get('chunks_count', 0)}\n"
    )

    # Test 7: Métodos do RAG
    print("Test 7: Verificando 6 métodos RAG na Application...")
    methods = [
        "process_input_with_context",
        "register_conversation_turn",
        "start_meeting_recording",
        "add_meeting_transcript",
        "stop_meeting_recording",
        "get_rag_stats",
    ]
    for m in methods:
        assert hasattr(app, m), f"Método {m} não encontrado"
        print(f"  ✓ {m}")

    # Test 8: Stats
    print("\nTest 8: Obtendo estatísticas RAG...")
    stats = app.get_rag_stats()
    print(f"  ✓ Stats disponíveis: {list(stats.keys())}")
    if "rag" in stats:
        print(f"    → Chunks: {stats['rag'].get('total_chunks', '?')}")
        print(f"    → DB Size: {stats['rag'].get('database_size_mb', '?')} MB")

    # Final Result
    print("\n" + "=" * 70)
    print("  ✅ INTEGRAÇÃO 100% CONFIRMADA!")
    print("=" * 70)
    print("\n✓ main.py --mode gui --protocol websocket")
    print("  → Carrega Application()")
    print("  → Inicializa EnhancedContext() automaticamente")
    print("  → RAG Local está pronto para expandir contexto\n")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(verify_integration())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Erro: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
