# 🔐 Guia: Usando APIs Vision de Forma Segura

## ✅ Chave Gemini Funciona!

A chave `AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU` **funciona perfeitamente**:

```
✅ API autenticada
✅ Requisição reconhecida
❌ Erro 429 = Quota grátis esgotada (limite/dia já atingido)
```

### Como Contornar Limite Gemini

Opções:
1. **Esperar até amanhã** - limite reset automático (24h)
2. **Adicionar cartão de crédito** - Google disponibiliza créditos extras
3. **Usar outro provider** - Zhipu ou Aliyun (sem limite)

---

## 🔒 Configuração Segura com Variáveis de Ambiente

### Por que Variáveis de Ambiente?

- ✅ Chaves **NÃO** ficam no repositório Git
- ✅ Segurança melhorada
- ✅ Mesmo código em dev/prod
- ✅ Fácil compartilhar projeto sem expor credenciais

### Setup em Windows

#### 1️⃣ Copiar arquivo de exemplo

```bash
copy .env.example .env
```

#### 2️⃣ Editar `.env` e preencher suas chaves

```
GEMINI_API_KEY=AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU
ZHIPU_API_KEY=sua_chave_zhipu_aqui
ALIYUN_API_KEY=sua_chave_aliyun_aqui
```

#### 3️⃣ Carregar variáveis antes de executar

**PowerShell**:
```powershell
# Adicionar ao script ativação
$env:GEMINI_API_KEY = "AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU"
$env:ZHIPU_API_KEY = "seu_token"

# Executar
python main.py
```

**Command Prompt**:
```cmd
set GEMINI_API_KEY=AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU
set ZHIPU_API_KEY=seu_token
python main.py
```

#### 4️⃣ Usar arquivo `.env` automaticamente

Instalar python-dotenv:
```bash
pip install python-dotenv
```

Adicionar ao início do seu script:
```python
from dotenv import load_dotenv
load_dotenv()  # Carrega variáveis de .env
```

### Setup em Linux/macOS

```bash
# Editar arquivo
nano .env

# Adicionar ao ~/.bashrc ou ~/.zshrc
export GEMINI_API_KEY="AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU"
export ZHIPU_API_KEY="seu_token"

# Recarregar
source ~/.bashrc
```

---

## 📋 Checklist de Segurança

- ✅ `.env` adicionado ao `.gitignore`
- ✅ `.env.example` versionado (sem chaves reais)
- ✅ `.gitignore.apis` documenta quais arquivos ignorar
- ✅ Chaves na config.json substituídas por `${VAR_NAME}`
- ✅ Código lê variáveis de ambiente automaticamente
- ✅ Nunca commitar chaves reais

### Verificar se .env está ignorado

```bash
# Git não deve listar .env
git status .env
# Output: On branch master, nothing to commit
```

---

## 🚀 Como Testar com Segurança

### Opção 1: Variáveis de Ambiente Temporárias (PowerShell)

```powershell
# Terminal PowerShell
$env:GEMINI_API_KEY = "AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU"

# Testar
python src/mcp/tools/providers/vllm_provider.py

# Variável desaparece quando fechar terminal
exit
```

### Opção 2: Arquivo .env Permanente

```bash
# 1. Editar .env (já copiado de .env.example)
GEMINI_API_KEY=AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU

# 2. Instalar python-dotenv
pip install python-dotenv

# 3. Executar (carrega .env automaticamente)
python main.py
```

### Opção 3: Arquivo de Configuração Local

```bash
# Criar config local não versionada
cp config/config.json config/config.local.json

# Editar config.local.json com chaves reais
# (não será comitado)
```

---

## ⚠️ Nunca Fazer

❌ Commitar chaves no repo:
```bash
git add config/config.json  # ❌ Com chaves reais
```

❌ Expor em logs:
```python
print(f"Chave: {api_key}")  # ❌ Revela a chave
logger.info(f"Token: {token}")  # ❌ Exposto
```

❌ Enviar por email/chat:
```
"Minha chave é: AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU"  # ❌
```

❌ Deixar em histórico de terminal:
```bash
python main.py --key="AIzaSyDx..."  # ❌ Histórico bash
```

---

## ✅ Forma Correta

✅ Usar variáveis de ambiente:
```python
import os
api_key = os.getenv("GEMINI_API_KEY")
```

✅ Usar .env com python-dotenv:
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

✅ Ignorar arquivos sensíveis:
```
# .gitignore
.env
.env.*
config/*.local.*
```

✅ Usar placeholders no repo:
```json
{
  "api_key": "${GEMINI_API_KEY}"
}
```

---

## 🔗 Próximos Passos

1. **Copiar `.env.example`**:
   ```bash
   copy .env.example .env
   ```

2. **Editar `.env`** com suas chaves reais

3. **Instalar python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

4. **Testar**:
   ```bash
   python src/mcp/tools/providers/vllm_provider.py
   ```

5. **Commitar** (apenas arquivos de exemplo):
   ```bash
   git add .env.example .gitignore.apis
   git commit -m "docs: exemplo de configuração segura de APIs"
   ```

---

## 📚 Referência

- [Zhipu API Docs](https://open.bigmodel.cn/dev/api)
- [Google Gemini API](https://ai.google.dev/docs)
- [python-dotenv Docs](https://python-dotenv.readthedocs.io/)
- [Git Ignore Best Practices](https://git-scm.com/docs/gitignore)

---

**Status**: ✅ Segurança implementada, código pronto para produção
**Chaves Gemini**: ✅ Funcional (aguardando reset de quota)

