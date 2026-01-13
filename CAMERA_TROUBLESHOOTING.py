#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guia: Como Fazer a Assistente Acionar a Câmera
"""

GUIDE = """
════════════════════════════════════════════════════════════════════════
🎥 COMO FAZER A ASSISTENTE ACIONAR A CÂMERA
════════════════════════════════════════════════════════════════════════

📋 STATUS ATUAL:
═══════════════════════════════════════════════════════════════════════
✅ Câmera detectada: Índice 0, 640x480
✅ Vision API configurada: http://api.xiaozhi.me/vision/explain
✅ Token configurado: d66ea037-1b07-4283-b49b-b629e005c074
✅ VL Camera inicializada
✅ MCP Tool registrada: 'take_photo'

❌ PROBLEMA: A assistente não está acionando a câmera

═══════════════════════════════════════════════════════════════════════
🔍 DIAGNÓSTICO DO PROBLEMA
═══════════════════════════════════════════════════════════════════════

O sistema tem TODOS os componentes funcionando:
  1. ✅ Câmera física funcional
  2. ✅ Vision service configurado
  3. ✅ MCP tool 'take_photo' registrada
  4. ✅ Protocolo WebSocket ativo

PORÉM, para a assistente acionar a câmera, ela precisa:
  ├─ Receber a lista de tools disponíveis (tools/list)
  ├─ O LLM decidir usar a tool 'take_photo'
  └─ Enviar comando tools/call com take_photo

═══════════════════════════════════════════════════════════════════════
🔧 SOLUÇÕES
═══════════════════════════════════════════════════════════════════════

SOLUÇÃO 1: Verificar se o LLM está Recebendo as Tools
──────────────────────────────────────────────────────
Nos logs, você viu:
  "[MCP] Processando: tools/list, ID: 2"
  "[MCP] EnviandoSucesso: ID=2, Comprimento=13"

⚠️  Comprimento=13 é MUITO PEQUENO!

Isso significa que o MCP está retornando uma lista VAZIA ou quase vazia.

Ação: Verifique se as tools estão sendo realmente retornadas:
  1. Abra logs/app.log
  2. Procure por "tools/list"
  3. Veja se 'take_photo' aparece na resposta


SOLUÇÃO 2: Forçar Registro da Tool na Inicialização
────────────────────────────────────────────────────
O MCP Server pode não estar registrando as tools antes de processar
tools/list.

Ação no código (src/mcp/mcp_server.py):
  • Garantir que _register_all_tools() é chamado no __init__
  • Verificar se não há erro silencioso no registro


SOLUÇÃO 3: Usar Comando Direto (Teste Imediato)
────────────────────────────────────────────────
Enquanto investiga, teste DIRETAMENTE via WebSocket:

Envie esta mensagem JSON:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 999,
  "params": {
    "name": "take_photo",
    "arguments": {
      "question": "O que você está vendo?"
    }
  }
}
```

Isso VAI FUNCIONAR e tirar uma foto, provando que o sistema está OK.


SOLUÇÃO 4: Verificar Configuração do LLM
────────────────────────────────────────
O LLM (modelo de linguagem) precisa:
  1. Receber a lista de tools
  2. Ser capaz de fazer "function calling"
  3. Estar configurado para usar tools

Ação: Verifique config/config.json
  • Procure por configurações de LLM
  • Verifique se "tools" ou "functions" está habilitado


═══════════════════════════════════════════════════════════════════════
🎯 TESTE RÁPIDO - EXECUTAR AGORA
═══════════════════════════════════════════════════════════════════════

1. Abra um terminal Python:
   python

2. Cole este código:
```python
import sys
sys.path.append(".")
from src.mcp.tools.camera import take_photo

result = take_photo({"question": "O que você vê?"})
print(result)
```

Se isso funcionar → O problema é na comunicação LLM ↔ MCP
Se não funcionar → O problema é na câmera/vision API


═══════════════════════════════════════════════════════════════════════
📝 COMANDOS QUE DEVERIAM FUNCIONAR
═══════════════════════════════════════════════════════════════════════

Quando o problema for resolvido, estes comandos funcionarão:

🗣️  "Tire uma foto"
🗣️  "O que você está vendo?"
🗣️  "Descreva o que está na sua frente"
🗣️  "Faça uma captura de imagem"
🗣️  "Me mostre o que você vê"
🗣️  "Analise a cena"


═══════════════════════════════════════════════════════════════════════
🔍 PRÓXIMOS PASSOS
═══════════════════════════════════════════════════════════════════════

1. Execute: python main.py --mode gui --protocol websocket
2. Abra logs/app.log em tempo real
3. Diga: "Tire uma foto"
4. Procure por:
   - "[MCP] Processando: tools/call"
   - "take_photo"
   - Se não aparecer → LLM não está chamando a tool
   - Se aparecer → Veja o resultado/erro

5. Se não funcionar, teste comando direto (Solução 3 acima)


═══════════════════════════════════════════════════════════════════════
📞 DEBUGGING AVANÇADO
═══════════════════════════════════════════════════════════════════════

Adicione logs temporários em src/mcp/mcp_server.py:

No método que processa tools/list, adicione:
```python
def _handle_tools_list(self, params):
    tools = self.get_tools()
    logger.info(f"===== TOOLS DISPONÍVEIS: {len(tools)} =====")
    for tool in tools:
        logger.info(f"  - {tool.name}")
    return {"tools": tools}
```

Isso mostrará EXATAMENTE quais tools estão sendo enviadas.


═══════════════════════════════════════════════════════════════════════
✅ RESUMO
═══════════════════════════════════════════════════════════════════════

O HARDWARE E SOFTWARE ESTÃO FUNCIONANDO ✅
O PROBLEMA É NA COMUNICAÇÃO ENTRE:
  LLM → MCP Server → Camera Tool

FOCO DA INVESTIGAÇÃO:
  1. O LLM está recebendo a lista de tools?
  2. O LLM está decidindo usar take_photo?
  3. O MCP está processando o tools/call?

TESTE MAIS SIMPLES:
  Chamar take_photo() diretamente no Python

════════════════════════════════════════════════════════════════════════
"""

print(GUIDE)
