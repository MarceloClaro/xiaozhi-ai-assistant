# 🔴 DIAGNÓSTICO - ERROS DE CÂMERA E MÚSICA

**Data**: 13 de janeiro de 2026  
**Status**: ⚠️ 2 Problemas Críticos Encontrados

---

## 1. ❌ ERRO DA CÂMERA: HTTP 404 Not Found

### Sintoma
```
HTTP Request: POST https://api.tenclass.net/xiaozhi/vision/explain/chat/completions "HTTP/1.1 404 Not Found"
Failed to analyze image with VL: <html><head><title>404 Not Found</title></head>...
```

### Causa Raiz
O arquivo [src/mcp/tools/camera/vl_camera.py](src/mcp/tools/camera/vl_camera.py) usa `OpenAI()` client que **automaticamente adiciona** `/chat/completions` ao `base_url`.

**Configuração atual**:
- `base_url`: `https://open.bigmodel.cn/api/paas/v4/chat/completions` (padrão)
- Endpoint real em teste: `https://api.tenclass.net/xiaozhi/vision/explain`
- Resultado: `https://api.tenclass.net/xiaozhi/vision/explain/chat/completions` ❌

### Solução

#### Opção A: Usar URL de Visão Correta (Recomendado)
Se o endpoint correto é `https://api.tenclass.net/xiaozhi/vision/explain`, deveria ser configurado sem o sufixo `/chat/completions`:

```python
# ERRADO:
base_url = "https://api.tenclass.net/xiaozhi/vision/explain"
client = OpenAI(api_key=api_key, base_url=base_url)
# Resultado: base_url + "/chat/completions" = 404

# CORRETO - usar endpoint raiz:
base_url = "https://api.tenclass.net/xiaozhi/vision"  # sem /explain
client = OpenAI(api_key=api_key, base_url=base_url)
# Resultado: base_url + "/chat/completions" = /vision/chat/completions ✅
```

#### Opção B: Integrar Vision API Local (Recomendado para produção)
Usar o Gemini API implementado em [src/mcp/tools/providers/vllm_provider.py](src/mcp/tools/providers/vllm_provider.py):

```python
# Em vl_camera.py, adicionar fallback para Gemini:
from src.mcp.tools.providers.vllm_provider import VLLMProvider

def analyze(self, question: str, context: str = "") -> str:
    try:
        # Tentar com Gemini primeiro
        provider = VLLMProvider()
        result = provider.analyze_image(
            image_base64=image_base64,
            question=question,
            context=context
        )
        return result
    except Exception as e:
        # Fallback para Zhipu/local se necessário
        logger.error(f"Gemini falhou: {e}")
        return self._fallback_analysis()
```

---

## 2. ❌ ERRO DA MÚSICA: Connection Timeout

### Sintoma
```
HTTPConnectionPool(host='api.xiaodaokg.com', port=80): Max retries exceeded
Connection to api.xiaodaokg.com timed out. (connect timeout=10)
Resultado: Não Encontrado: música animada
```

### Causa Raiz
O servidor `api.xiaodaokg.com` está **offline, bloqueado ou inacessível** na sua rede.

**Localização do erro**:
- Arquivo: [src/mcp/tools/music/music_player.py](src/mcp/tools/music/music_player.py)
- Linha: ~145
- URL: `http://api.xiaodaokg.com/kuwo.php`

### Diagnóstico

Teste a conectividade:
```powershell
# 1. Testar ping
ping api.xiaodaokg.com

# 2. Testar conexão HTTP
curl -I http://api.xiaodaokg.com/kuwo.php

# 3. Verificar status
Invoke-WebRequest -Uri "http://api.xiaodaokg.com/kuwo.php" -TimeoutSec 5
```

### Possíveis Causas
1. ❌ Servidor `api.xiaodaokg.com` está **offline**
2. ❌ Rede corporativa bloqueia o domínio
3. ❌ VPN desconectada
4. ❌ Firewall bloqueia porta 80
5. ❌ DNS resolver falha

### Soluções

#### Solução 1: Usar Servidor Alternativo
Substituir endpoint inacessível por alternativas:

```python
MUSIC_SOURCES = {
    "primary": "http://api.xiaodaokg.com/kuwo.php",      # Atual (offline)
    "backup1": "https://music.toutiao.com/api/v1/music",  # Toutiao
    "backup2": "https://www.kuwo.cn/api/",                # Kuwo direto
    "backup3": "https://api.music.qq.com/",               # QQ Music
    "local": "file://localhost/music/"                     # Local
}
```

#### Solução 2: Implementar Retry com Fallback
```python
def search_music(song_name: str, max_retries: int = 3) -> Optional[str]:
    """Buscar música com fallback automático"""
    
    sources = [
        "http://api.xiaodaokg.com/kuwo.php",
        "https://music.toutiao.com/api/v1/music",
        # ... outros
    ]
    
    for attempt, source in enumerate(sources):
        try:
            result = requests.get(
                source,
                params={"song": song_name},
                timeout=5
            )
            if result.status_code == 200:
                logger.info(f"✅ Música encontrada em {source}")
                return result
        except requests.Timeout:
            logger.warning(f"⏱ Timeout em {source}, tentando próximo...")
        except requests.ConnectionError:
            logger.warning(f"❌ Conexão recusada em {source}")
        
    logger.error(f"❌ Não conseguiu buscar '{song_name}' em nenhuma fonte")
    return None
```

#### Solução 3: Usar Música Local
Se servidor está offline, usar playlist local:

```python
# Verificar músicas locais primeiro
local_music_dir = Path.home() / "Music"
local_songs = list(local_music_dir.glob("*.mp3"))

if local_songs:
    logger.info(f"Usando playlist local ({len(local_songs)} músicas)")
    # Play from local
else:
    logger.error("Nenhuma música local disponível")
    # Retornar erro ao usuário
```

---

## 3. ⚠️ MODELO FALTANDO: encoder.onnx

### Sintoma
```
Falha ao Inicializar Sherpa-ONNX KeywordSpotter: 
Modelo ausente: C:\...\models\encoder.onnx
```

### Solução
Descarregar o modelo:
```bash
# 1. Navegar para diretório do projeto
cd c:\Users\marce\Downloads\py-xiaozhi-main\py-xiaozhi-main

# 2. Criar diretório models
mkdir models

# 3. Descarregar modelo
# Opção A: Via python
python -c "from sherpa_onnx import download_model; download_model('sherpa-onnx-kws-en-small')"

# Opção B: Manual - usar modelo pré-treinado
# https://github.com/k2-fsa/sherpa-onnx/releases
```

---

## 4. ⚠️ sentence-transformers Não Carregado

### Sintoma
```
Não foi possível carregar sentence-transformers
```

### Causa
O pacote `sentence-transformers` é opcional e não foi instalado.

### Solução
```bash
# Instalar pacote
pip install sentence-transformers

# Ou adicionar a requirements.txt
```

---

## 📊 Resumo de Ações Recomendadas

| Problema | Prioridade | Ação | Status |
|----------|-----------|------|--------|
| Camera 404 | 🔴 CRÍTICA | Integrar Vision API (Gemini) | ⏳ Pendente |
| Música Timeout | 🟠 ALTA | Implementar fallback automático | ⏳ Pendente |
| encoder.onnx | 🟡 MÉDIA | Descarregar modelo | ⏳ Pendente |
| sentence-transformers | 🟡 MÉDIA | Instalar pacote | ⏳ Pendente |

---

## 🎯 Próximos Passos

### Curto Prazo (Imediato)
1. ✅ Criar este diagnóstico
2. ⏳ Testar conectividade de `api.xiaodaokg.com`
3. ⏳ Descarregar modelo `encoder.onnx`

### Médio Prazo (Esta semana)
1. ⏳ Implementar Vision API (Gemini) com fallback
2. ⏳ Implementar retry automático para música
3. ⏳ Instalar dependências faltantes

### Longo Prazo (Produção)
1. ⏳ Usar cache local de músicas
2. ⏳ Implementar múltiplas fontes de música
3. ⏳ Adicionar monitoramento de API health

---

**Última atualização**: 2026-01-13 10:44:00  
**Próxima revisão**: Após implementar soluções
