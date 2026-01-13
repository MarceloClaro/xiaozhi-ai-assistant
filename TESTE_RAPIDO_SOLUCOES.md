# 🚀 GUIA RÁPIDO - TESTAR SOLUÇÕES

**Objetivo**: Validar que as soluções de câmera e música funcionam

---

## ✅ Checklist Pré-Teste

- [ ] Gemini API Key configurada em `.env`
- [ ] GUI ainda está rodando (ou pronta para rodar)
- [ ] Terminal com acesso aos logs
- [ ] Câmera funcionando
- [ ] Microfone funcionando

---

## 🎬 Teste 1: Câmera com Fallback (5 minutos)

### Passo 1: Iniciar GUI
```bash
# No terminal
python main.py --mode gui --protocol websocket
```

### Passo 2: Interagir com Câmera
1. Abrir GUI do assistente
2. Falar: **"Fotografe este objeto"** ou simplesmente usar Ctrl+J
3. Apontar câmera para qualquer objeto
4. Aguardar resposta

### Passo 3: Verificar Logs
Procure por uma destas mensagens:

#### ✅ Sucesso com Zhipu
```
[src.mcp.tools.camera.vl_camera] INFO - Tentando análise de imagem com Zhipu...
[src.mcp.tools.camera.vl_camera] INFO - Análise Zhipu concluída com sucesso
```

#### ✅ Fallback para Gemini
```
[src.mcp.tools.camera.vl_camera] WARNING - Zhipu falhou: ..., tentando Gemini...
[src.mcp.tools.camera.vl_camera] INFO - Usando fallback: Gemini Vision API...
[src.mcp.tools.camera.vl_camera] INFO - Análise Gemini concluída com sucesso
```

#### ❌ Falha Completa (não esperado)
```
[src.mcp.tools.camera.vl_camera] ERROR - Failed to analyze image: ...
```

### Resultado Esperado
- 🟢 **Ideal**: "Análise Zhipu concluída" (primeira API funciona)
- 🟡 **Aceitável**: "Análise Gemini concluída" (fallback disparou, mas funcionou)
- 🔴 **Problema**: "Failed to analyze image" (nem Zhipu nem Gemini funcionou)

---

## 🎵 Teste 2: Música com Retry (5 minutos)

### Passo 1: GUI Ainda Rodando
Continuar no mesmo GUI da câmera.

### Passo 2: Solicitar Música
1. Falar: **"Toque uma música animada"** ou **"Toque Jazz"**
2. Aguardar resposta do assistente

### Passo 3: Verificar Logs
Procure por uma destas mensagens:

#### ✅ Sucesso na Tentativa 1
```
[src.mcp.tools.music.music_player] INFO - Tentativa 1/3 para 'música animada' (timeout=10s)
[src.mcp.tools.music.music_player] INFO - Concluído，Encontrado X Música
```

#### ✅ Retry Disparou (1 timeout + sucesso)
```
[src.mcp.tools.music.music_player] INFO - Tentativa 1/3 para 'música animada' (timeout=10s)
[src.mcp.tools.music.music_player] WARNING - Timeout na tentativa 1, tentando novamente...
[src.mcp.tools.music.music_player] INFO - Tentativa 2/3 para 'música animada' (timeout=12s)
[src.mcp.tools.music.music_player] INFO - Concluído，Encontrado X Música
```

#### ✅ Múltiplos Retries (2-3 timeouts + sucesso)
```
[src.mcp.tools.music.music_player] INFO - Tentativa 1/3... (timeout=10s)
[src.mcp.tools.music.music_player] WARNING - Timeout na tentativa 1...
[src.mcp.tools.music.music_player] INFO - Tentativa 2/3... (timeout=12s)
[src.mcp.tools.music.music_player] WARNING - Timeout na tentativa 2...
[src.mcp.tools.music.music_player] INFO - Tentativa 3/3... (timeout=14s)
[src.mcp.tools.music.music_player] INFO - Concluído，Encontrado X Música
```

#### ❌ Falha Completa (todas as 3 tentativas falharam)
```
[src.mcp.tools.music.music_player] ERROR - Falha ao buscar 'música animada' após 3 tentativas
```

### Resultado Esperado
- 🟢 **Ideal**: Música toca na tentativa 1 (sem timeout)
- 🟡 **Aceitável**: Música toca após retry (1-2 timeouts)
- 🔴 **Problema**: Falha após todas as tentativas

---

## 📊 Matriz de Resultado

| Teste | Resultado | Status | Ação |
|-------|-----------|--------|------|
| Câmera (Zhipu) | "Análise concluída" | ✅ OK | Sem ação |
| Câmera (Gemini) | "Análise Gemini concluída" | ✅ OK | Fallback funcionando |
| Câmera (Falha) | "Failed to analyze" | ❌ Falha | Verificar logs |
| Música (1ª tentativa) | Música toca | ✅ OK | Sem ação |
| Música (Retry) | Música toca após retry | ✅ OK | Retry funcionando |
| Música (Falha) | "Não Encontrado" | ❌ Falha | Verificar internet |

---

## 🔧 Troubleshooting

### Problema: Câmera retorna "Failed to analyze image"

**Solução**:
1. Verificar se `.env` tem `GEMINI_API_KEY` preenchida
2. Verificar se Gemini quota não está esgotada (erro 429)
3. Testar manualmente: `python src/mcp/tools/providers/vllm_provider.py`

### Problema: Música sempre retorna "Não Encontrado"

**Solução**:
1. Testar conectividade: `ping api.xiaodaokg.com`
2. Se ping falhar, servidor está offline
3. Verificar se internet está ok
4. Verificar firewall/VPN

### Problema: Logs não aparecem

**Solução**:
1. Verificar se logs estão em: `logs/app.log`
2. Usar `tail -f logs/app.log` para ver em tempo real
3. Grep específico: `grep "vl_camera\|music_player" logs/app.log`

---

## 📝 Log de Teste

Copie e preencha após testar:

```
Data/Hora: __________________
Teste Câmera: [ ] Zhipu [ ] Gemini [ ] Falha
Teste Música: [ ] 1ª tentativa [ ] Com retry [ ] Falha
Erros encontrados: _________________________
Status geral: [ ] ✅ Sucesso [ ] 🟡 Parcial [ ] ❌ Falha
```

---

## 🎯 Próximas Ações

### Se Tudo Funcionou ✅
1. ✅ Documentar resultado
2. ✅ Fazer merge das alterações
3. ✅ Considerar casos de uso avançados

### Se Câmera Falhou ❌
1. ❌ Verificar config.json (CAMERA_OPTIONS)
2. ❌ Testar Gemini API manualmente
3. ❌ Aumentar timeout em vl_camera.py

### Se Música Falhou ❌
1. ❌ Testar conectividade do servidor
2. ❌ Verificar se api.xiaodaokg.com está acessível
3. ❌ Aumentar retry limit em music_player.py

---

**Tempo Estimado de Teste**: 10 minutos  
**Dificuldade**: 🟢 Fácil  
**Interatividade**: 🟢 Gui + Voz
