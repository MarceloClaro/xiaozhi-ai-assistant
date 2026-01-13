# ⚡ QUICK REFERENCE: RAG INTEGRADO COM main.py

## ✅ Status: 100% INTEGRADO

---

## 🚀 Iniciar Aplicação

```bash
# GUI + WebSocket (Recomendado)
python main.py --mode gui --protocol websocket

# CLI + WebSocket
python main.py --mode cli --protocol websocket

# GUI + MQTT
python main.py --mode gui --protocol mqtt
```

**RAG é inicializado AUTOMATICAMENTE em qualquer modo!**

---

## 💻 Usar RAG em Código

```python
from src.application import Application

app = Application.get_instance()

# 1. Adicionar conhecimento
await app.context_system.rag_manager.add_chunk(
    text="Seu conhecimento aqui",
    metadata={"topic": "xyz"},
    source="sua_fonte"
)

# 2. Processar input COM contexto expandido
result = await app.process_input_with_context(
    user_input="Sua pergunta",
    max_context_length=4000  # até 4KB de contexto
)
print(result['context'])  # Contexto expandido!

# 3. Registrar conversa
await app.register_conversation_turn(
    user_input="pergunta",
    assistant_response="resposta",
    context_chunks=5
)

# 4. Gravar reunião
await app.start_meeting_recording(title="Minha Reunião")
await app.add_meeting_transcript("fala aqui", speaker="Nome")
await app.stop_meeting_recording()  # Auto-summariza!

# 5. Obter stats
stats = app.get_rag_stats()
print(f"Chunks: {stats['rag']['total_chunks']}/8000")
```

---

## 📊 Capacidades

| Recurso | Valor |
|---------|-------|
| Max Chunks | 8.000 |
| Chars/Chunk | 2.000 |
| Storage | ~16 MB |
| Conversas | Ilimitadas |
| Reuniões | Ilimitadas |
| Speed | < 50ms |

---

## 📁 Arquivos Principais

```
src/application.py           ← RAG integrado aqui (linha 60)
src/utils/rag_manager.py     ← Core RAG (406 linhas)
src/utils/enhanced_context.py ← Orquestrador (290 linhas)
data/rag_database.db         ← Database (SQLite)
scripts/test_main_py_integration.py ← Teste de integração
examples/rag_usage_example.py       ← Exemplo prático
```

---

## ✅ Verificação

Integração verificada em:
- ✅ src/application.py (linha 28: import, linha 60: init)
- ✅ Database SQLite criado (45 KB)
- ✅ 6 métodos async disponíveis
- ✅ 9/9 testes passando
- ✅ Exemplo prático funcionando

---

## 🔗 Integração Visual

```
main.py
  ↓
Application.get_instance()
  ↓
Application.__init__()
  ├─ self.context_system = EnhancedContext()  ← RAG AQUI
  └─ RAG Ready!
```

---

## 📚 Documentação

- [INTEGRATION_STATUS.md](INTEGRATION_STATUS.md) - Verificação técnica
- [INTEGRATION_VERIFICATION.md](INTEGRATION_VERIFICATION.md) - Detalhes
- [RAG_INTEGRATION_MAIN_PY.md](RAG_INTEGRATION_MAIN_PY.md) - Resumo
- [INTEGRATION_SUMMARY.txt](INTEGRATION_SUMMARY.txt) - Executivo

---

## 🎯 Próximos Passos

1. Execute: `python main.py --mode gui --protocol websocket`
2. GUI abrirá automaticamente
3. WebSocket estará ativo
4. **RAG LOCAL PRONTO PARA USAR!**

---

**Integração: 12/01/2026** ✅  
**Status: PRONTO PARA PRODUÇÃO** 🟢
