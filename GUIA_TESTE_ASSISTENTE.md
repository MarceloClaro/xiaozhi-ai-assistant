# 🧪 Guia de Teste - Assistente Xiaozhi com Vision

## ✅ Status: Assistente Iniciado

```
✅ Modo: GUI (Interface Gráfica)
✅ Protocolo: WebSocket
✅ Camera: Ativa
✅ Vision: Pronta (Gemini 2.0 ou Zhipu)
✅ PID: Rodando em background
```

---

## 🎯 Como Testar

### 1. Interface GUI
- A janela do assistente deve ter aberto
- Procure o ícone na bandeja do Windows
- Ou use os atalhos configurados

### 2. Atalhos de Teclado
```
Ctrl+J  → Pressionar para gravar áudio
Ctrl+K  → Alternar modo automático/manual
```

### 3. Testar Câmera
```
1. Clique no botão de câmera na interface
2. Captura uma imagem
3. Sistema analisa com Vision API
4. Resultado aparece na tela
```

### 4. Testar Áudio
```
1. Pressione Ctrl+J (ou clique no ícone)
2. Fale sua pergunta
3. Solte para enviar
4. Escute a resposta
```

---

## 🔍 Testes Recomendados

### Teste 1: Verificar que Tudo Está Funcionando
```
Comando: "Oi, como você está?"
Esperado: Resposta em português
Tempo: ~2s
```

### Teste 2: Análise de Imagem
```
Comando: "Descreva o que você vê"
Ação: Ter algo na frente da câmera
Esperado: Descrição detalhada
Tempo: ~3-5s (depende da API)
```

### Teste 3: Pergunta Complexa
```
Comando: "O que tem na minha mesa?"
Ação: Apontar câmera para mesa
Esperado: Lista dos objetos
Tempo: ~4-6s
```

### Teste 4: Múltiplas Análises
```
Repita teste 2 e 3 várias vezes
Esperado: Funcionar sem erros
Status: Verifica se quota está ok
```

---

## 🐛 Troubleshooting

### Problema: Janela GUI não aparece
**Solução**:
1. Aguarde 5 segundos (pode demorar para inicializar)
2. Procure ícone na bandeja de tarefas
3. Se não aparecer, veja logs:
   ```bash
   # Executar em novo terminal
   python main.py --mode cli --protocol websocket
   ```

### Problema: Câmera não funciona
**Solução**:
1. Verifique câmera: `python scripts/camera_scanner.py`
2. Permita acesso à câmera no Windows
3. Reinicie o assistente

### Problema: Erro ao analisar imagem (429)
**Solução**:
1. Quota Gemini esgotada? Esperar 24h ou:
   - Adicionar cartão de crédito
   - Ou mudar para Zhipu em `.env`

### Problema: Áudio não funciona
**Solução**:
1. Testar áudio: `python scripts/py_audio_scanner.py`
2. Verificar microfone em settings Windows
3. Permitir acesso ao microfone

---

## 📊 Checklist de Testes

- [ ] Interface GUI abre
- [ ] Atalhos de teclado funcionam
- [ ] Câmera captura imagem
- [ ] Análise de imagem funciona
- [ ] Áudio é capturado
- [ ] Resposta em voz
- [ ] Múltiplas análises sem erro
- [ ] Sistema não trava

---

## 🔗 Arquivos Importantes para Teste

```
📁 Projeto
├── main.py                          ← Ponto de entrada
├── config/config.json               ← Configuração (com ${VAR_NAME})
├── .env                             ← Suas chaves (não comita)
├── src/
│   ├── application.py               ← Lógica principal
│   ├── display/
│   │   ├── gui_display.py          ← Interface GUI
│   │   └── gui_display.qml         ← Design QML
│   ├── mcp/tools/providers/
│   │   └── vllm_provider.py        ← Vision API
│   └── audio_processing/
│       └── wake_word_detect.py     ← Detecção de voz
└── scripts/
    ├── camera_scanner.py            ← Testar câmera
    └── py_audio_scanner.py          ← Testar áudio
```

---

## 🚨 Logs e Debug

### Ver logs em tempo real
```bash
# Em novo terminal
python main.py --mode cli --protocol websocket
```

### Ativar debug verbose
```bash
# Adicionar ao config.json
"DEBUG": true
```

### Verificar conexão WebSocket
```bash
# Testar endpoint
curl -i wss://api.tenclass.net/xiaozhi/v1/
```

---

## 📈 Métricas Durante Teste

### Velocidade Esperada
| Ação | Tempo | Status |
|------|-------|--------|
| Captura de imagem | ~0.5s | ✅ Rápido |
| Análise (Gemini) | 2-4s | ✅ OK |
| Análise (Zhipu) | 3-5s | ✅ OK |
| Resposta em voz | ~1-2s | ✅ Rápido |

### Qualidade Esperada
- ✅ Descrições detalhadas de imagens
- ✅ Respostas coerentes em português
- ✅ Sem stuttering de áudio
- ✅ Sem travamentos

---

## ✨ Recursos Disponíveis

### Vision (Análise de Imagens)
- ✅ Google Gemini 2.0 Flash
- ✅ Zhipu GLM-4V Flash
- ✅ Detecção de objetos
- ✅ Análise de cenas

### Áudio (Entrada/Saída)
- ✅ Captura de microfone
- ✅ Síntese de voz
- ✅ Wake word detection
- ✅ Echo cancellation

### Interface
- ✅ GUI com PyQt5
- ✅ CLI para debug
- ✅ Atalhos de teclado
- ✅ Tray icon

---

## 🎊 Sucesso!

Se todos os testes passarem, você tem:

✅ Sistema de Visão (Image Analysis) operacional  
✅ Sistema de Áudio (Voice Input/Output) operacional  
✅ Interface GUI funcional  
✅ Assistente AI completo  

**Parabéns! 🎉**

---

## 🔄 Próximos Passos Após Teste

1. **Se Tudo Funciona** ✅
   - Use normalmente
   - Ajuste configurações conforme necessário
   - Aproveite o assistente!

2. **Se Houver Problemas** ⚠️
   - Verifique logs
   - Consulte troubleshooting acima
   - Abra issue no GitHub

3. **Para Melhorar** 🚀
   - Configure Zhipu como fallback
   - Ajuste temperatura (mais criativo vs. mais focado)
   - Implemente novos comandos

---

**Status**: 🟢 **PRONTO PARA TESTE**  
**Data**: 13 de janeiro de 2026  
**Assistente**: xiaozhi-ai-assistant v1.0

🎮 **Divirta-se testando!**

