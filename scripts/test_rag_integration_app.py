"""
Teste de integração do RAG na Application.
Valida se todos os métodos estão funcionando corretamente.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.application import Application
from src.utils.logging_config import setup_logging, get_logger

logger = get_logger(__name__)


async def test_rag_integration():
    """Testar integração completa de RAG na Application."""
    setup_logging()

    print("\n" + "=" * 70)
    print("TEST: RAG Integration in Application")
    print("=" * 70)

    try:
        # 1. Obter Application
        print("\n[1] Inicializando Application...")
        app = Application.get_instance()
        print("✅ Application inicializada")

        # 2. Verificar se context_system existe
        print("\n[2] Verificando context_system...")
        if hasattr(app, "context_system"):
            print("✅ context_system encontrado")
        else:
            print("❌ context_system NÃO encontrado")
            return False

        # 3. Testar process_input_with_context
        print("\n[3] Testando process_input_with_context...")
        result = await app.process_input_with_context(
            "Como funciona o RAG?", max_context_length=2000
        )
        user_preview = result["user_input"][:50]
        print(f"✅ Input processado: {user_preview}...")
        print(f"   Contexto gerado: {result['context_length']} chars")

        # 4. Testar get_rag_stats
        print("\n[4] Obtendo estatísticas...")
        stats = app.get_rag_stats()
        print("✅ RAG Stats:")
        print(f"   Chunks: {stats['rag']['total_chunks']}/8000")
        print(f"   Conversas: {stats['rag']['conversation_turns']}")
        print(f"   Reuniões: {stats['meetings']['total_meetings']}")

        # 5. Testar register_conversation_turn
        print("\n[5] Registrando turno de conversa...")
        await app.register_conversation_turn(
            user_input="Como funciona o RAG?",
            assistant_response="RAG é um sistema de recuperação de informações.",
            context_chunks=["test_chunk"],
        )
        print("✅ Turno registrado")

        # 6. Testar meeting recording
        print("\n[6] Testando gravação de reunião...")
        await app.start_meeting_recording("Teste RAG")
        print("   ✅ Gravação iniciada")

        await app.add_meeting_transcript(
            "Primeira fala do teste", speaker="Teste"
        )
        print("   ✅ Transcrição adicionada")

        meeting_info = await app.stop_meeting_recording()
        print(f"   ✅ Reunião finalizada: {meeting_info.get('title')}")

        # 7. Verificar stats novamente
        print("\n[7] Verificando stats finais...")
        final_stats = app.get_rag_stats()
        print(f"✅ Stats finais:")
        print(f"   Chunks: {final_stats['rag']['total_chunks']}/8000")
        print(f"   Conversas: {final_stats['rag']['conversation_turns']}")
        print(f"   Reuniões: {final_stats['meetings']['total_meetings']}")

        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES DE INTEGRAÇÃO PASSARAM!")
        print("=" * 70 + "\n")
        return True

    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_rag_integration())
    sys.exit(0 if success else 1)
