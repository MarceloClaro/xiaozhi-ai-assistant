#!/bin/bash
# Setup Script para Configurar APIs de Forma Segura
# Linux / macOS

set -e  # Exit on error

echo ""
echo "================================================"
echo "  Setup de APIs Vision - Google Gemini + Zhipu"
echo "================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado. Instale Python 3.8+"
    exit 1
fi

echo "[1/5] Verificando Python..."
python3 --version

echo ""
echo "[2/5] Copiando arquivo de configuração..."
if [ -f .env ]; then
    echo "[!] .env já existe. Pulando..."
else
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "[OK] .env criado de .env.example"
    else
        echo "[AVISO] .env.example não encontrado"
    fi
fi

echo ""
echo "[3/5] Verificando python-dotenv..."
if python3 -c "import dotenv" 2>/dev/null; then
    echo "[OK] python-dotenv já instalado"
else
    echo "[OK] Instalando python-dotenv..."
    pip3 install python-dotenv
fi

echo ""
echo "[4/5] Verificando configuração..."
if [ -f config/config.json ]; then
    echo "[OK] config.json encontrado"
else
    echo "[AVISO] config.json não encontrado em config/"
fi

echo ""
echo "================================================"
echo "  PRÓXIMOS PASSOS"
echo "================================================"
echo ""
echo "1. Edite o arquivo .env com suas chaves:"
echo "   $ nano .env"
echo "   Ou no seu editor favorito"
echo ""
echo "2. Preencha com suas chaves:"
echo "   GEMINI_API_KEY=AIzaSyDxSiSJhxp6F_AD6rph7adO0fkkSoPaohU"
echo "   ZHIPU_API_KEY=seu_token_aqui"
echo ""
echo "3. Onde obter as chaves:"
echo "   - Google Gemini: https://aistudio.google.com/app/apikey"
echo "   - Zhipu AI: https://open.bigmodel.cn/usercenter/apikeys"
echo ""
echo "4. Testar a configuração:"
echo "   python3 src/mcp/tools/providers/vllm_provider.py"
echo ""
echo "5. Usar no projeto:"
echo "   python3 main.py"
echo ""
echo "================================================"
echo ""

echo "[5/5] Setup concluído!"
echo ""

# Abrir editor se disponível
if command -v nano &> /dev/null; then
    read -p "Abrir .env em editor? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        nano .env
    fi
fi

echo ""
echo "================================================"
echo "  LEMBRETE DE SEGURANÇA"
echo "================================================"
echo "- NUNCA commite o arquivo .env no Git"
echo "- NUNCA compartilhe suas chaves por email/chat"
echo "- Mude as chaves se forem vazadas publicamente"
echo ""
echo "Verificar se .env está ignorado:"
echo "  git status .env"
echo ""
