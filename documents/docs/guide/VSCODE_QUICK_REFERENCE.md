# VSCode Quick Reference for py-xiaozhi | Referência Rápida VSCode para py-xiaozhi

## 🚀 Quick Start | Início Rápido

### 1. Open in VSCode | Abrir no VSCode
```bash
cd py-xiaozhi
code .
```

### 2. Select Python Interpreter | Selecionar Interpretador Python
`Ctrl+Shift+P` → "Python: Select Interpreter" → Select `py-xiaozhi` env

### 3. Run | Executar
Press `F5` or click ▶️ button | Pressione `F5` ou clique no botão ▶️

---

## 🎯 Debug Configurations | Configurações de Depuração

| Configuration | Description | Configuração | Descrição |
|--------------|-------------|--------------|-----------|
| `Python: py-xiaozhi GUI Mode` | Standard GUI with WebSocket | Modo GUI padrão | GUI padrão com WebSocket |
| `Python: py-xiaozhi CLI Mode` | Command line interface | Interface linha de comando | Interface de linha de comando |
| `Python: py-xiaozhi GUI (MQTT)` | GUI with MQTT protocol | GUI com protocolo MQTT | GUI com protocolo MQTT |
| `Python: Skip Activation (Debug)` | Skip device activation | Pular ativação | Pular ativação do dispositivo |
| `Python: Test Camera Scanner` | Test camera functionality | Testar câmera | Testar funcionalidade da câmera |
| `Python: Test Audio Scanner` | Test audio devices | Testar áudio | Testar dispositivos de áudio |

**To use**: Press `F5` → Select configuration | **Para usar**: Pressione `F5` → Selecione configuração

---

## ⚡ Keyboard Shortcuts | Atalhos de Teclado

### Running & Debugging | Execução e Depuração
| Shortcut | Action | Atalho | Ação |
|----------|--------|--------|------|
| `F5` | Start debugging | Iniciar depuração | Iniciar depuração |
| `Ctrl+F5` | Run without debugging | Executar sem depuração | Executar sem depuração |
| `Shift+F5` | Stop debugging | Parar depuração | Parar depuração |
| `Ctrl+Shift+F5` | Restart | Reiniciar | Reiniciar |
| `F10` | Step over | Próxima linha | Próxima linha |
| `F11` | Step into | Entrar na função | Entrar na função |
| `Shift+F11` | Step out | Sair da função | Sair da função |

### General | Geral
| Shortcut | Action | Atalho | Ação |
|----------|--------|--------|------|
| `Ctrl+Shift+P` | Command palette | Paleta de comandos | Paleta de comandos |
| `Ctrl+P` | Quick file open | Abrir arquivo rápido | Abrir arquivo rápido |
| `` Ctrl+` `` | Toggle terminal | Alternar terminal | Alternar terminal |
| `Ctrl+Shift+F` | Search in files | Buscar em arquivos | Buscar em arquivos |
| `Ctrl+/` | Toggle comment | Alternar comentário | Alternar comentário |
| `Shift+Alt+F` | Format document | Formatar documento | Formatar documento |

---

## 📋 VSCode Tasks | Tarefas do VSCode

Access with `Ctrl+Shift+P` → "Tasks: Run Task" | Acesse com `Ctrl+Shift+P` → "Tasks: Run Task"

### Run Tasks | Tarefas de Execução
- **Run: GUI Mode (WebSocket)** - Run in GUI mode
- **Run: CLI Mode (WebSocket)** - Run in CLI mode
- **Run: GUI Mode (MQTT)** - Run with MQTT protocol
- **Run: Skip Activation (Debug)** - Run without activation

### Development Tasks | Tarefas de Desenvolvimento
- **Format: Black (All Files)** - Format all Python files
- **Lint: Flake8 (Check All)** - Check code style
- **Clean: Remove Python Cache** - Clean `__pycache__` folders

### Testing Tasks | Tarefas de Teste
- **Test: Camera Scanner** - Test camera
- **Test: Audio Scanner** - Test audio devices
- **Test: Music Cache Scanner** - Test music cache

### Installation Tasks | Tarefas de Instalação
- **Install: Requirements (Linux/Windows)** - Install dependencies
- **Install: Requirements (macOS)** - Install macOS dependencies
- **Verify: Installation** - Verify all imports work

---

## 🔧 Command Line Quick Reference | Referência Rápida Linha de Comando

### Basic Commands | Comandos Básicos
```bash
# Run GUI mode | Executar modo GUI
python main.py

# Run CLI mode | Executar modo CLI
python main.py --mode cli

# Use MQTT protocol | Usar protocolo MQTT
python main.py --protocol mqtt

# Skip activation (debug) | Pular ativação (debug)
python main.py --skip-activation
```

### Development Commands | Comandos de Desenvolvimento
```bash
# Format code | Formatar código
python -m black src/ main.py

# Check code style | Verificar estilo do código
python -m flake8 src/ main.py

# Test camera | Testar câmera
python scripts/camera_scanner.py

# Test audio | Testar áudio
python scripts/py_audio_scanner.py
```

### Environment Setup | Configuração do Ambiente
```bash
# Activate conda environment | Ativar ambiente conda
conda activate py-xiaozhi

# Activate venv | Ativar venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies | Instalar dependências
pip install -r requirements.txt
```

---

## 🔍 Quick Troubleshooting | Solução Rápida de Problemas

### Problem | Problema: Module not found | Módulo não encontrado
```bash
# Solution | Solução:
conda activate py-xiaozhi  # or | ou: source .venv/bin/activate
pip install -r requirements.txt
```

### Problem | Problema: PyQt5 issues | Problemas com PyQt5
```bash
# Solution | Solução:
conda install -c conda-forge pyqt=5.15
```

### Problem | Problema: Audio not working | Áudio não funciona
```bash
# Linux
sudo apt-get install -y portaudio19-dev libportaudio2 pulseaudio-utils
pip install sounddevice --force-reinstall

# macOS
brew reinstall portaudio
pip install sounddevice --force-reinstall

# Windows
pip install sounddevice --force-reinstall
```

### Problem | Problema: Activation fails | Falha na ativação
```bash
# Solution | Solução: Remove activation file | Remover arquivo de ativação
rm config/efuse.json
python main.py
```

---

## 📚 Documentation Links | Links de Documentação

### English
- **[Complete VSCode Guide](../VSCODE_GUIDE_EN.md)** - Full setup and usage guide
- **[Main README](../README.en.md)** - Project overview
- **[System Dependencies](系统依赖安装.md)** - Dependency installation
- **[Configuration Guide](配置说明.md)** - Configuration details

### Português
- **[Guia Completo VSCode](../GUIA_VSCODE_PT.md)** - Guia completo de configuração e uso
- **[README Principal](../README.md)** - Visão geral do projeto
- **[Dependências do Sistema](系统依赖安装.md)** - Instalação de dependências
- **[Guia de Configuração](配置说明.md)** - Detalhes de configuração

### 中文
- **[项目文档](https://huangjunsen0406.github.io/py-xiaozhi/)** - 完整文档
- **[主README](../README.md)** - 项目概述
- **[系统依赖安装](系统依赖安装.md)** - 依赖安装指南
- **[配置说明](配置说明.md)** - 配置详细说明

---

## 🎯 Recommended Extensions | Extensões Recomendadas

The project includes `.vscode/extensions.json` which will prompt you to install:
O projeto inclui `.vscode/extensions.json` que irá sugerir a instalação de:

- ✅ **Python** (ms-python.python) - Essential | Essencial
- ✅ **Pylance** (ms-python.vscode-pylance) - IntelliSense
- ✅ **Python Debugger** (ms-python.debugpy) - Debugging | Depuração
- ✅ **Black Formatter** (ms-python.black-formatter) - Code formatting | Formatação
- ⭐ **autoDocstring** (njpwerner.autodocstring) - Docstrings
- ⭐ **GitLens** (eamodio.gitlens) - Git tools | Ferramentas Git
- ⭐ **Error Lens** (usernamehw.errorlens) - Error display | Exibição de erros

---

## 💡 Tips | Dicas

### Multi-cursor editing | Edição com múltiplos cursores
- `Alt+Click` - Add cursor | Adicionar cursor
- `Ctrl+D` - Select next occurrence | Selecionar próxima ocorrência
- `Ctrl+Alt+Up/Down` - Add cursor above/below | Adicionar cursor acima/abaixo

### Quick navigation | Navegação rápida
- `F12` - Go to definition | Ir para definição
- `Shift+F12` - Find all references | Encontrar todas as referências
- `Ctrl+T` - Search symbols | Buscar símbolos

### Zen mode | Modo zen
- `Ctrl+K Z` - Enter zen mode (distraction-free) | Entrar no modo zen (sem distrações)

---

## 📞 Getting Help | Obtendo Ajuda

### Documentation | Documentação
- 📖 [Complete VSCode Guide](../VSCODE_GUIDE_EN.md) | [Guia Completo VSCode](../GUIA_VSCODE_PT.md)
- 🌐 [Official Docs](https://huangjunsen0406.github.io/py-xiaozhi/)
- 🎥 [Video Tutorial](https://www.bilibili.com/video/BV1dWQhYEEmq/)

### Community | Comunidade
- 🐛 [GitHub Issues](https://github.com/huangjunsen0406/py-xiaozhi/issues)
- 💬 [Gitee](https://gitee.com/huang-jun-sen/py-xiaozhi)

---

**Last Updated | Última Atualização**: 2026-01-12
**Version | Versão**: 1.0
