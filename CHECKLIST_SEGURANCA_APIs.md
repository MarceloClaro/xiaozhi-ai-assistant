# 🔍 Checklist: Configuração Segura de APIs

## ✅ Antes de Commitar

### Segurança

- [ ] `.env` criado com `.env` template
- [ ] `.env` está no `.gitignore`
- [ ] Nenhuma chave real em `config.json`
- [ ] Chaves usam formato `${VAR_NAME}`
- [ ] Arquivo `.env` NÃO será comitado

### Configuração

- [ ] Python 3.8+ instalado
- [ ] `python-dotenv` instalado (`pip install python-dotenv`)
- [ ] `.env.example` preenchido com instruções
- [ ] `setup_apis.bat` ou `setup_apis.sh` executable

### Testes

- [ ] Teste rápido funciona: `python verify_vision_api.py` (5/5 checks)
- [ ] Vision provider inicializa corretamente
- [ ] Variáveis de ambiente são lidas

---

## 🚀 Checklist: Pronto Para Usar

### Setup Inicial

```bash
# 1. Executar script de setup
./setup_apis.sh        # Linux/Mac
setup_apis.bat         # Windows

# OU manual
cp .env.example .env
pip install python-dotenv
```

### Configurar Chaves

```bash
# Editar .env
nano .env              # Linux/Mac
notepad .env           # Windows

# Adicionar suas chaves reais
GEMINI_API_KEY=AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU
ZHIPU_API_KEY=seu_token_aqui
```

### Verificar Git

```bash
# Confirmar que .env não será comitado
git status .env
# Output: On branch master, nothing to commit

# Confirmar que .env.example será comitado
git status .env.example
# Output: Untracked files: .env.example
```

### Testar

```bash
# Verificação rápida
python verify_vision_api.py
# Esperado: ✅ 5/5 checks passed

# Teste completo
python src/mcp/tools/providers/vllm_provider.py
# Esperado: Análise da imagem completa
```

---

## 🔒 Segurança: Verificações

### ❌ NÃO FAZER

```bash
# ❌ Commitar chave real
git add config/config.json -f
git commit "add api keys"

# ❌ Expor em logs
logger.info(f"API Key: {os.getenv('GEMINI_API_KEY')}")

# ❌ Adicionar ao histórico
python main.py --key="AIzaSyDx..."

# ❌ Comentar código com chaves
# key = "AIzaSyDx..."
```

### ✅ FAZER

```bash
# ✅ Variáveis de ambiente
GEMINI_API_KEY="sua_chave" python main.py

# ✅ Arquivo .env (ignorado)
# .env nunca é comitado
ls -la .env
# Output: .env -> .gitignore

# ✅ Log seguro
logger.info("API initialized successfully")

# ✅ Verificar segurança
git check-ignore .env
# Output: .env
```

---

## 📋 Troubleshooting

### Problema: "ImportError: No module named 'dotenv'"

**Solução**:
```bash
pip install python-dotenv
```

### Problema: "Variável de ambiente não encontrada"

**Verificar**:
```bash
# Linux/Mac
echo $GEMINI_API_KEY

# Windows PowerShell
$env:GEMINI_API_KEY
```

**Solução**: Certifique-se de que `.env` existe e tem suas chaves

### Problema: ".env não está sendo ignorado"

**Solução**:
```bash
# Adicionar ao .gitignore
echo ".env" >> .gitignore

# Remover do git (se já foi comitado)
git rm --cached .env
git commit "remove .env from tracking"
```

### Problema: "config.json tem ${VAR_NAME} mas não funciona"

**Solução**: 
1. Instale python-dotenv: `pip install python-dotenv`
2. Certifique-se de que `.env` existe com as chaves
3. Reinicie a aplicação

---

## 🎯 Resumo

| Item | Status | Ação |
|------|--------|------|
| Python | ✅ Instalado | - |
| .env | ✅ Criado | Editar com suas chaves |
| python-dotenv | ✅ Instalado | - |
| config.json | ✅ Seguro | ${VAR_NAME} usados |
| .gitignore | ✅ Pronto | .env ignorado |
| Chaves | ⏳ Pendente | Adicione suas chaves em .env |

---

## 📚 Documentação

- [GUIA_CONFIGURACAO_SEGURA_APIs.md](GUIA_CONFIGURACAO_SEGURA_APIs.md) - Setup completo
- [RESUMO_GEMINI_FUNCIONA.md](RESUMO_GEMINI_FUNCIONA.md) - Status Gemini
- [.env.example](.env.example) - Template de configuração

---

**Status**: ✅ Pronto para produção  
**Segurança**: ✅ Implementada  
**Próximo**: Preencher chaves em `.env`

