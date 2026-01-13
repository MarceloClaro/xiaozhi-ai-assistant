@echo off
REM Setup Script para Configurar APIs de Forma Segura
REM Windows PowerShell / Command Prompt

echo.
echo ================================================
echo  Setup de APIs Vision - Google Gemini + Zhipu
echo ================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Instale Python 3.8+
    pause
    exit /b 1
)

echo [1/5] Copiando arquivo de configuração...
if exist .env (
    echo [!] .env já existe. Pulando...
) else (
    if exist .env.example (
        copy .env.example .env
        echo [OK] .env criado de .env.example
    ) else (
        echo [AVISO] .env.example não encontrado
    )
)

echo.
echo [2/5] Verificando python-dotenv...
pip list | findstr python-dotenv >nul 2>&1
if errorlevel 1 (
    echo [OK] Instalando python-dotenv...
    pip install python-dotenv
) else (
    echo [OK] python-dotenv já instalado
)

echo.
echo [3/5] Verificando configuração...
if exist config/config.json (
    echo [OK] config.json encontrado
) else (
    echo [AVISO] config.json não encontrado em config/
)

echo.
echo ================================================
echo  PRÓXIMOS PASSOS
echo ================================================
echo.
echo 1. Edite o arquivo .env com suas chaves:
echo    - Abra: .env
echo    - Preenchea: GEMINI_API_KEY=sua_chave_aqui
echo    - Preencha: ZHIPU_API_KEY=seu_token_aqui
echo.
echo 2. Onde obter as chaves:
echo    - Google Gemini: https://aistudio.google.com/app/apikey
echo    - Zhipu AI: https://open.bigmodel.cn/usercenter/apikeys
echo.
echo 3. Testar a configuração:
echo    python src/mcp/tools/providers/vllm_provider.py
echo.
echo 4. Usar no projeto:
echo    python main.py
echo.
echo ================================================
echo.

REM Abrir arquivo .env no editor padrão
if exist .env (
    echo [4/5] Abrindo .env para edição...
    start notepad .env
    echo [OK] Editor aberto
) else (
    echo [AVISO] Crie o arquivo .env manualmente
)

echo.
echo [5/5] Setup concluído!
echo.
echo ================================================
echo  LEMBRETE DE SEGURANÇA
echo ================================================
echo - NUNCA commite o arquivo .env no Git
echo - NUNCA compartilhe suas chaves por email/chat
echo - Mude as chaves se forem vazadas publicamente
echo.

pause
