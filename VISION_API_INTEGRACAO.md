# Integração Vision API - Guia de Implementação

## 📋 Resumo Executivo

Este documento descreve como integrar a **Vision API Correta** no py-xiaozhi-main.

**APIs e Tokens Descobertos:**
- **Token**: `d66ea037-1b07-4283-b49b-b629e005c074`
- **API**: Zhipu Vision API (GLM-4V)
- **Endpoint**: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- **Modelo**: `glm-4v-vision`

Esses valores foram extraídos do repositório **xiaozhi-esp32-server** que é a implementação de referência funcional.

---

## 🔧 Passo 1: Configurar config.yaml

Adicione a seção VLLM ao seu `config.yaml`:

```yaml
# Configuração de módulos selecionados
selected_module:
  VLLM: "zhipu"  # Provedor de Vision API a usar

# Configuração de VLLM providers
VLLM:
  zhipu:
    type: "zhipu"
    api_key: "d66ea037-1b07-4283-b49b-b629e005c074"
    model: "glm-4v-vision"
    api_url: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    temperature: 0.7
    max_tokens: 2048
    timeout: 30.0
```

---

## 📂 Passo 2: Estrutura de Arquivos

Os seguintes arquivos foram criados/atualizados:

```
src/mcp/tools/
├── providers/
│   ├── __init__.py                 # ✅ CRIADO
│   └── vllm_provider.py            # ✅ CRIADO - ZhipuVisionAPIProvider
├── camera/
│   ├── __init__.py                 # ⏳ ATUALIZAR - Importar vision
│   └── camera.py                   # ⏳ ATUALIZAR - Integrar take_photo
└── ...
```

---

## 🎬 Passo 3: Atualizar camera.py

Atualize a ferramenta `take_photo` em `src/mcp/tools/camera/camera.py`:

### Antes (Versão Atual - Não Funcional):

```python
async def take_photo(arguments: dict) -> dict:
    """Captura foto da câmera"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {"error": "Camera não disponível"}
        
        # ❌ Aqui estava faltando: não faz nada com a imagem
        return {"photo": "Foto capturada mas não analisada"}
    except Exception as e:
        return {"error": str(e)}
```

### Depois (Versão Corrigida com Vision API):

```python
import base64
import cv2
from src.mcp.tools.providers import explain_image_via_mcp
from src.utils.config_manager import ConfigManager

async def take_photo(arguments: dict) -> dict:
    """
    Captura foto da câmera e analisa com Vision API.
    
    Argumentos:
        question: (opcional) Pergunta sobre a imagem
        
    Retorna:
        {
            "status": "success" | "error",
            "photo_description": "Descrição da imagem",
            "error": "Mensagem de erro (se houver)"
        }
    """
    try:
        logger.info("[Camera] Capturando foto...")
        
        # 1. Capturar imagem
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {
                "status": "error",
                "error": "Câmera não disponível ou não respondeu"
            }
        
        # 2. Converter para base64
        logger.info("[Camera] Convertendo imagem...")
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 3. Carregar configuração
        config_manager = ConfigManager()
        vision_config = config_manager.get("VLLM", {}).get("zhipu", {})
        
        if not vision_config.get("api_key"):
            return {
                "status": "error",
                "error": "Vision API não configurada. Configure VLLM.zhipu em config.yaml"
            }
        
        # 4. Enviar para análise
        question = arguments.get("question", 
            "Descreva detalhadamente tudo que você vê nesta imagem")
        
        logger.info("[Camera] Enviando para Vision API...")
        result = await explain_image_via_mcp(
            image_base64=image_base64,
            question=question,
            vision_config=vision_config
        )
        
        # 5. Retornar resultado
        if result["status"] == "success":
            logger.info("[Camera] Análise concluída com sucesso")
            return {
                "status": "success",
                "photo_description": result["analysis"],
                "tokens_used": result.get("tokens", 0)
            }
        else:
            logger.error(f"[Camera] Erro na análise: {result.get('error')}")
            return {
                "status": "error",
                "error": f"Erro ao analisar imagem: {result.get('error')}"
            }
    
    except Exception as e:
        logger.error(f"[Camera] Erro fatal: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": f"Erro ao capturar/analisar foto: {str(e)}"
        }
```

---

## 🧪 Passo 4: Testar Integração

### Opção A: Teste Rápido (Python)

```bash
# Navegar para o diretório do projeto
cd c:\Users\marce\Downloads\py-xiaozhi-main\py-xiaozhi-main

# Executar teste
python src/mcp/tools/providers/vllm_provider.py
```

**Saída esperada:**
```
[Teste] Iniciando teste da Vision API...
[Teste] Capturando imagem da câmera...
[Teste] Convertendo imagem para base64...
[Teste] Tamanho da imagem: 12345 caracteres
[Teste] Criando provider...
[Teste] Enviando imagem para análise...

======================================================================
RESULTADO DA ANÁLISE
======================================================================
Status: success
Tokens usados: 456

Análise:
[Descrição detalhada da imagem capturada]
======================================================================
```

### Opção B: Teste via MCP Tool

```python
# No seu cliente MCP ou aplicação
import asyncio
from src.mcp.tools.camera.camera import take_photo

result = asyncio.run(take_photo({
    "question": "Quem está nesta foto? Descreva as pessoas e o ambiente."
}))

print(result)
# Saída esperada:
# {
#     "status": "success",
#     "photo_description": "Na imagem vejo...",
#     "tokens_used": 256
# }
```

---

## 🔐 Segurança e Autenticação

### Token de API
- **Valor**: `d66ea037-1b07-4283-b49b-b629e005c074`
- **Tipo**: Bearer Token (Zhipu API)
- **Uso**: Enviado no header `Authorization: Bearer {token}`
- **Armazenamento**: Em `config.yaml` (não commitir em produção)

### Proteção Recomendada
```python
# Use variáveis de ambiente em produção
import os

api_key = os.getenv("ZHIPU_API_KEY", "d66ea037-1b07-4283-b49b-b629e005c074")
```

---

## 🏗️ Arquitetura Completa

```
┌─────────────────────────────────────────────────────────────────┐
│                     Usuário / Aplicação                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    take_photo() [MCP Tool]
                               │
                ┌──────────────▼──────────────┐
                │    camera.py                 │
                │  - Captura imagem           │
                │  - Converte para base64     │
                └──────────────┬──────────────┘
                               │
                    explain_image_via_mcp()
                               │
    ┌──────────────────────────▼──────────────────────────┐
    │  src/mcp/tools/providers/vllm_provider.py            │
    │                                                      │
    │  ZhipuVisionAPIProvider:                             │
    │  - Prepara payload JSON                             │
    │  - Envia para Zhipu Vision API                      │
    │  - Processa resposta                                │
    └──────────────────────────┬──────────────────────────┘
                               │
     ┌─────────────────────────▼─────────────────────┐
     │  Zhipu Vision API                              │
     │  https://open.bigmodel.cn/api/paas/v4/...     │
     │                                               │
     │  Modelo: glm-4v-vision                       │
     │  Token: d66ea037-1b07-4283-b49b-b629e005c074 │
     └─────────────────────────┬─────────────────────┘
                               │
    ┌──────────────────────────▼──────────────────────────┐
    │  LLM analisa imagem                                 │
    │  Gera descrição textual detalhada                  │
    └──────────────────────────┬──────────────────────────┘
                               │
                  Retorna análise ao usuário
```

---

## 📊 Formato de Requisição/Resposta

### Requisição (enviada para Zhipu API):

```json
{
  "model": "glm-4v-vision",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
          }
        },
        {
          "type": "text",
          "text": "Descreva detalhadamente tudo que você vê nesta imagem"
        }
      ]
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### Resposta (retornada por vllm_provider.py):

```python
{
    "status": "success",
    "analysis": "Na imagem vejo uma sala bem iluminada com...",
    "tokens": 256,
    "model": "glm-4v-vision"
}
```

---

## ⚙️ Variáveis de Ambiente

Para maior segurança, use variáveis de ambiente:

```bash
# .env ou arquivo de configuração
ZHIPU_API_KEY=d66ea037-1b07-4283-b49b-b629e005c074
ZHIPU_MODEL=glm-4v-vision
ZHIPU_API_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
```

Leia no código:
```python
import os
api_key = os.getenv("ZHIPU_API_KEY")
```

---

## 🚀 Próximos Passos

1. ✅ Criou `src/mcp/tools/providers/vllm_provider.py`
2. ✅ Criou `src/mcp/tools/providers/__init__.py`
3. ⏳ **PRÓXIMO**: Atualizar `src/mcp/tools/camera/camera.py`
4. ⏳ Adicionar configuração em `config.yaml`
5. ⏳ Testar com `python src/mcp/tools/providers/vllm_provider.py`
6. ⏳ Testar integração end-to-end
7. ⏳ Integrar com voice (TTS feedback)

---

## 🐛 Troubleshooting

### Erro: "API Key não encontrada"
```
Vision API não configurada. Configure VLLM.zhipu em config.yaml
```
**Solução**: Adicione a chave `api_key` em `config.yaml` sob `VLLM.zhipu`

### Erro: "Timeout ao conectar"
```
Timeout ao conectar com Vision API
```
**Solução**: 
- Verifique conexão de internet
- Aumente timeout em config.yaml: `timeout: 60.0`
- Verifique se Token está correto

### Erro: "Câmera não disponível"
```
Câmera não disponível ou não respondeu
```
**Solução**:
- Verifique permissões de câmera
- Teste câmera: `python scripts/camera_scanner.py`
- Verifique se câmera não está em uso por outro programa

---

## 📞 Referências

- **ESP32 Server (Referência)**: https://github.com/MarceloClaro/xiaozhi-esp32-server
- **Vision Handler**: https://github.com/MarceloClaro/xiaozhi-esp32-server/tree/main/main/xiaozhi-server/core/api
- **Zhipu API Docs**: https://open.bigmodel.cn/

---

**Atualizado em**: 2024
**Status**: ✅ Documentação Completa
