# 🎥 Por Que a Assistente Não Aciona a Câmera?

## ✅ Status do Sistema

**Componentes Testados e Funcionando:**
- ✅ Câmera física: Detectada (índice 0, 640x480)
- ✅ Vision API: Configurada (http://api.xiaozhi.me/vision/explain)
- ✅ Token: Válido (d66ea037-1b07-4283-b49b-b629e005c074)
- ✅ VL Camera: Inicializada com sucesso
- ✅ MCP Tool: `take_photo` registrada no código
- ✅ WebSocket: Conexão ativa

## ❌ Problema Identificado

Nos logs você viu:
```
[MCP] Processando: tools/list, ID: 2
[MCP] EnviandoSucesso: ID=2, Comprimento=13
```

**Comprimento=13 bytes é MUITO PEQUENO!**

Uma resposta vazia de JSON seria `{"tools":[]}` = 13 bytes.

**Conclusão: O MCP Server está retornando uma lista VAZIA de ferramentas para o LLM.**

## 🔍 Diagnóstico

O problema está na **ordem de inicialização**:

```
1. MCP Server cria instância
2. Cliente envia "initialize" + "tools/list"
3. MCP processa tools/list ANTES de registrar as tools
4. Retorna lista vazia
5. LLM não sabe que pode usar câmera
```

## 🔧 Solução Definitiva

### Modificação no `src/mcp/mcp_server.py`

Adicionei logs de debug. Agora execute novamente:

```bash
python main.py --mode gui --protocol websocket
```

Nos logs (`logs/app.log`), procure por:
```
[MCP TOOLS/LIST] Total de tools registradas: X
[MCP TOOLS/LIST] Tools disponíveis:
  - take_photo
  - take_screenshot
  - (outras tools)
```

Se aparecer "Total: 0" → As tools não foram registradas
Se aparecer "Total: 10+" → As tools estão OK, problema é no cliente

## 🎯 Testes Imediatos

### Teste 1: Verificar Registro de Tools

Execute em um terminal Python:

```python
import sys
sys.path.append(".")
from src.mcp.mcp_server import MCPServer

server = MCPServer()
print(f"Total de tools: {len(server.tools)}")
for tool in server.tools:
    print(f"  - {tool.name}")
```

**Resultado Esperado:** Deve mostrar 10+ tools incluindo `take_photo`

### Teste 2: Chamar Câmera Diretamente

```python
import sys
sys.path.append(".")
from src.mcp.tools.camera import take_photo

result = take_photo({"question": "O que você está vendo?"})
print(result)
```

**Resultado Esperado:** Captura foto e retorna JSON com análise

### Teste 3: Comando MCP Direto

Se você tiver acesso ao WebSocket client, envie:

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

## 📝 Comandos de Voz que Deveriam Funcionar

Quando o problema for resolvido:

- 🗣️ **"Tire uma foto"**
- 🗣️ **"O que você está vendo?"**
- 🗣️ **"Descreva o que está na sua frente"**
- 🗣️ **"Me mostre o que você vê"**
- 🗣️ **"Faça uma captura de imagem"**
- 🗣️ **"Analise a cena"**

## 🔄 Fluxo Correto

```
Usuário: "Tire uma foto"
    ↓
LLM: Reconhece intenção
    ↓
LLM: Consulta lista de tools (tools/list)
    ↓
LLM: Encontra "take_photo" na lista ✅
    ↓
LLM: Envia tools/call com take_photo
    ↓
MCP Server: Executa take_photo()
    ↓
Câmera: Captura frame
    ↓
Vision API: Analisa imagem
    ↓
Retorna: Descrição da imagem
    ↓
Assistente: Responde ao usuário
```

## 🐛 Debug Avançado

Se os logs mostrarem que as tools estão registradas mas o LLM não as usa:

1. **Problema no Cliente WebSocket/MQTT:**
   - O cliente pode estar descartando a resposta do tools/list
   - Verificar se o cliente está repassando as tools para o LLM

2. **Problema no LLM:**
   - O modelo pode não suportar function calling
   - O modelo pode não estar configurado para usar tools
   - Verificar config/config.json → configurações de LLM

3. **Problema de Timing:**
   - O tools/list pode estar sendo chamado antes das tools serem registradas
   - Solução: Mover _register_all_tools() para o início do __init__

## ✅ Próximas Ações

1. Execute com os novos logs de debug
2. Verifique o output de "[MCP TOOLS/LIST]"
3. Se total=0 → Problema de registro
4. Se total>0 → Problema no cliente/LLM
5. Teste comando direto (Teste 2 ou 3 acima)

## 📊 Checklist

- [ ] Logs mostram tools registradas (>0)
- [ ] take_photo aparece na lista
- [ ] Teste direto funciona
- [ ] Cliente recebe tools/list response
- [ ] LLM está fazendo function calls
- [ ] Comandos de voz são reconhecidos

Quando TODOS estiverem marcados ✅ a câmera funcionará!
