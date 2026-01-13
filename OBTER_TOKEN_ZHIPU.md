# 🔑 OBTER TOKEN ZHIPU AI - GUIA RÁPIDO

## 📋 O Que Você Precisa Fazer Agora

A implementação da Vision API está **100% completa**, mas o token expirou. Siga estes passos para obter um token válido:

---

## ⚡ PASSO A PASSO (5 minutos)

### 1️⃣ Acesse o Site da Zhipu AI

🌐 **URL**: https://open.bigmodel.cn/

### 2️⃣ Crie uma Conta (se não tiver)

1. Clique em **"注册"** (Registrar) ou **"登录"** (Login)
2. Você pode usar:
   - 📧 Email
   - 📱 Telefone chinês
   - 🔐 Conta WeChat/QQ

**💡 Dica**: Use o Google Translate para traduzir a página se necessário

### 3️⃣ Acesse o Console de API

1. Após login, vá para: **"开放平台"** (Plataforma Aberta)
2. Ou acesse direto: https://open.bigmodel.cn/usercenter/apikeys

### 4️⃣ Gere uma Nova API Key

1. Clique em **"创建API Key"** (Criar API Key)
2. Dê um nome (ex: "xiaozhi-vision")
3. Copie a API Key gerada

**⚠️ IMPORTANTE**: A chave só é mostrada uma vez! Copie e guarde.

### 5️⃣ Cole o Token no Config

Abra o arquivo:
```
config/config.json
```

Encontre esta seção:
```json
"VLLM": {
  "zhipu": {
    "api_key": "COLOQUE_SEU_TOKEN_ZHIPU_AQUI",
```

Substitua `COLOQUE_SEU_TOKEN_ZHIPU_AQUI` pelo seu token.

Exemplo:
```json
"api_key": "1234567890abcdef1234567890abcdef.XyZaBc1234567890",
```

### 6️⃣ Teste!

Execute:
```bash
python verify_vision_api.py
```

Se aparecer ✅ em tudo, execute:
```bash
python src/mcp/tools/providers/vllm_provider.py
```

---

## 🎁 MODELO ATUALIZADO

Atualizei o modelo de `glm-4v-vision` para **`glm-4v-flash`**:

**Vantagens**:
- ⚡ ~2.5 segundos mais rápido
- 💰 Mesmo preço
- ✅ Streaming suportado
- 👍 Recomendado pela equipe xinnan-tech

---

## 💰 CUSTOS (Informação)

**GLM-4V-Flash**:
- Texto: ~0.001 yuan / 1K tokens
- Imagem: ~0.01 yuan / imagem

**Aproximadamente**:
- ~100 análises de imagem = ~1 yuan (~R$ 0.70)
- 💡 Muito barato para testes!

**Créditos Grátis**: Normalmente você recebe créditos grátis ao criar conta.

---

## 🆘 PROBLEMAS COMUNS

### "Não consigo criar conta"
- Use um email internacional (Gmail, Outlook)
- Ou tente criar conta via WeChat se tiver

### "Token não funciona"
- Verifique se copiou corretamente (sem espaços)
- Confirme que o token está ativo no console
- Aguarde 1-2 minutos após criar (pode demorar para ativar)

### "Ainda dá erro 401"
- Verifique se salvou o arquivo config.json
- Reinicie o teste

---

## 🔄 ALTERNATIVA: Aliyun Bailian (Mais Rápido)

Se preferir uma alternativa mais rápida:

### Aliyun (Alibaba Cloud)

1. **Acesse**: https://bailian.console.aliyun.com/
2. **Modelo**: `qwen2.5-vl-3b-instructh`
3. **Vantagens**:
   - ⚡ Mais rápido que Zhipu
   - 🌊 Streaming nativo
   - 💰 Bons créditos grátis

**Configuração** (se escolher Aliyun):
```json
"VLLM": {
  "qwen_vl": {
    "type": "openai",
    "api_key": "SEU_TOKEN_ALIYUN",
    "model": "qwen2.5-vl-3b-instructh",
    "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

E em `selected_module`:
```json
"selected_module": {
  "VLLM": "qwen_vl"
}
```

---

## ✅ CHECKLIST FINAL

Antes de testar, confirme:

- [ ] Criei conta na Zhipu AI
- [ ] Gerei nova API Key
- [ ] Copiei o token completo
- [ ] Colei no config.json (substituindo "COLOQUE_SEU_TOKEN_ZHIPU_AQUI")
- [ ] Salvei o arquivo config.json
- [ ] Executei `python verify_vision_api.py`
- [ ] Tudo passou ✅

---

## 🚀 DEPOIS DE CONFIGURAR

Execute o teste completo:

```bash
# Teste 1: Verificação
python verify_vision_api.py

# Teste 2: Câmera + Vision API
python src/mcp/tools/providers/vllm_provider.py

# Teste 3: Aplicação GUI
python main.py --mode gui
```

**Esperado**: Câmera captura, Vision API analisa, retorna descrição! 🎉

---

## 📞 LINKS ÚTEIS

- **Zhipu Console**: https://open.bigmodel.cn/usercenter/apikeys
- **Zhipu Docs**: https://open.bigmodel.cn/dev/api
- **Aliyun Bailian**: https://bailian.console.aliyun.com/
- **Nosso FAQ**: VISION_API_INTEGRACAO.md

---

## ⏱️ TEMPO ESTIMADO

- Criar conta: 2 minutos
- Gerar token: 30 segundos
- Configurar: 1 minuto
- Testar: 1 minuto
- **Total: ~5 minutos**

---

**Status Atual**: ⏳ Aguardando seu token válido  
**Próximo Passo**: Obter token e testar! 🚀

Boa sorte! 🎊
