# py-xiaozhi - Cliente AI Xiaozhi em Python

<p align="center" class="trendshift">
  <a href="https://trendshift.io/repositories/14130" target="_blank">
    <img src="https://trendshift.io/api/badge/repositories/14130" alt="Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/>
  </a>
</p>
<p align="center">
  <a href="https://github.com/huangjunsen0406/py-xiaozhi/releases/latest">
    <img src="https://img.shields.io/github/v/release/huangjunsen0406/py-xiaozhi?style=flat-square&logo=github&color=blue" alt="Release"/>
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License: MIT"/>
  </a>
  <a href="https://github.com/huangjunsen0406/py-xiaozhi/stargazers">
    <img src="https://img.shields.io/github/stars/huangjunsen0406/py-xiaozhi?style=flat-square&logo=github" alt="Stars"/>
  </a>
  <a href="https://github.com/huangjunsen0406/py-xiaozhi/releases/latest">
    <img src="https://img.shields.io/github/downloads/huangjunsen0406/py-xiaozhi/total?style=flat-square&logo=github&color=52c41a1&maxAge=86400" alt="Download"/>
  </a>
</p>

[简体中文](README.md) | [English](README.en.md) | **Português Brasileiro**

## 📝 Introdução ao Projeto

py-xiaozhi é um cliente de voz AI Xiaozhi implementado em Python, projetado para aprender código e experimentar as funcionalidades de voz do AI Xiaozhi sem hardware dedicado. Este repositório é uma versão portada do [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32).

## 🎬 Demonstração

- [Vídeo de Demonstração no Bilibili](https://www.bilibili.com/video/BV1HmPjeSED2/#reply255921347937)

![Imagem](./documents/docs/guide/images/系统界面.png)

## ✨ Funcionalidades

### 🎯 Funções Principais de IA

- **Interação por Voz com IA**: Suporta entrada e reconhecimento de voz, realizando interação inteligente homem-máquina com experiência de conversa natural e fluida
- **Visão Multimodal**: Suporta reconhecimento e processamento de imagens, proporcionando capacidade de interação multimodal e compreensão de conteúdo visual
- **Ativação Inteligente**: Suporta múltiplas palavras de ativação para iniciar interação, eliminando operações manuais (configurável)
- **Modo de Diálogo Automático**: Implementa experiência de conversa contínua, melhorando a fluidez da interação do usuário

### 🔧 Ecossistema de Ferramentas MCP

- **Ferramentas de Controle do Sistema**: Monitoramento de estado do sistema, gerenciamento de aplicativos, controle de volume, gerenciamento de dispositivos, etc.
- **Ferramentas de Gerenciamento de Agenda**: Gerenciamento completo de agenda, suporta criar, consultar, atualizar e deletar eventos, classificação e lembretes inteligentes
- **Ferramentas de Tarefas Programadas**: Funcionalidade de temporizador, suporta execução com atraso de ferramentas MCP, gerenciamento paralelo de múltiplas tarefas
- **Ferramentas de Reprodução de Música**: Busca e reprodução de música online, suporta controle de reprodução, exibição de letras, gerenciamento de cache local
- **Ferramentas de Consulta 12306**: Consulta de passagens ferroviárias 12306, suporta consulta de bilhetes, consulta de transferências, consulta de rotas de trem
- **Ferramentas de Pesquisa**: Pesquisa na web e obtenção de conteúdo de páginas web, suporta pesquisa Bing e análise inteligente de conteúdo
- **Ferramentas de Receitas**: Biblioteca rica de receitas, suporta busca de receitas, consulta por categoria, recomendações inteligentes
- **Ferramentas de Mapa**: Serviços de mapa Amap, suporta geocodificação, planejamento de rotas, busca nas proximidades, consulta de clima
- **Ferramentas de Astrologia Chinesa**: Análise tradicional de astrologia chinesa Bazi, suporta cálculo de Bazi, análise de casamento, consulta de almanaque
- **Ferramentas de Câmera**: Captura de imagem e análise com IA, suporta reconhecimento por foto e perguntas e respostas inteligentes

### 🏠 Integração de Dispositivos IoT

- **Arquitetura de Gerenciamento de Dispositivos**: Gerenciamento unificado de dispositivos baseado no padrão Thing, suporta chamadas assíncronas de propriedades e métodos
- **Controle de Casa Inteligente**: Suporta controle de dispositivos como iluminação, volume, sensores de temperatura, etc.
- **Mecanismo de Sincronização de Estado**: Monitoramento de estado em tempo real, suporta atualizações incrementais e obtenção de estado concorrente
- **Design Extensível**: Drivers de dispositivos modulares, fácil adição de novos tipos de dispositivos

### 🎵 Processamento Avançado de Áudio

- **Processamento de Áudio Multi-nível**: Suporta codificação/decodificação Opus, reamostragem em tempo real
- **Detecção de Atividade de Voz**: Detector VAD implementa interrupção inteligente, suporta monitoramento de atividade de voz em tempo real
- **Detecção de Palavra de Ativação**: Reconhecimento de voz offline baseado em Sherpa-ONNX, suporta múltiplas palavras de ativação e correspondência fonética
- **Gerenciamento de Fluxo de Áudio**: Fluxos de entrada e saída independentes, suporta reconstrução de fluxo e recuperação de erros
- **Cancelamento de Eco de Áudio**: Integra módulo de processamento de áudio WebRTC, fornece funcionalidade de cancelamento de eco de alta qualidade
- **Gravação de Áudio do Sistema**: Suporta gravação de áudio do sistema, implementa processamento de loopback de áudio

### 🖥️ Interface do Usuário

- **Interface Gráfica**: GUI moderna baseada em PyQt5, suporta expressões e exibição de texto do Xiaozhi, melhorando a experiência visual
- **Modo de Linha de Comando**: Suporta execução em CLI, adequado para dispositivos embarcados ou ambientes sem GUI
- **Bandeja do Sistema**: Suporte para execução em segundo plano, funcionalidade integrada à bandeja do sistema
- **Atalhos Globais**: Suporta operação por atalhos globais, aumentando a conveniência de uso
- **Interface de Configurações**: Interface completa de gerenciamento de configurações, suporta personalização

### 🔒 Segurança e Estabilidade

- **Transmissão de Áudio Criptografada**: Suporta protocolo WSS, garante a segurança dos dados de áudio, prevenindo vazamento de informações
- **Sistema de Ativação de Dispositivos**: Suporta ativação por protocolo duplo v1/v2, processa automaticamente códigos de verificação e impressão digital do dispositivo
- **Recuperação de Erros**: Mecanismo completo de tratamento e recuperação de erros, suporta reconexão após desconexão

### 🌐 Suporte Multiplataforma

- **Compatibilidade de Sistema**: Compatível com Windows 10+, macOS 10.15+ e sistemas Linux
- **Suporte de Protocolo**: Suporta comunicação por protocolo duplo WebSocket e MQTT
- **Implantação Multi-ambiente**: Suporta modo duplo GUI e CLI, adaptando-se a diferentes ambientes de implantação
- **Otimização de Plataforma**: Otimização de áudio e controle de sistema para diferentes plataformas

### 🔧 Amigável para Desenvolvedores

- **Arquitetura Modular**: Estrutura de código clara e separação de responsabilidades, conveniente para desenvolvimento secundário
- **Prioridade Assíncrona**: Arquitetura orientada a eventos baseada em asyncio, processamento concorrente de alto desempenho
- **Gerenciamento de Configuração**: Sistema de configuração em camadas, suporta acesso por notação de ponto e atualização dinâmica
- **Sistema de Logs**: Registro de logs e suporte de depuração completos
- **Documentação da API**: Documentação de código detalhada e guias de uso

## 💻 Requisitos do Sistema

### Requisitos Básicos

- **Versão do Python**: 3.9 - 3.13
- **Sistema Operacional**: Windows 10+, macOS 10.15+, Linux
- **Dispositivos de Áudio**: Dispositivos de microfone e alto-falante
- **Conexão de Rede**: Conexão estável à Internet (para serviços de IA e funcionalidades online)

### Configuração Recomendada

- **Memória**: Pelo menos 4GB RAM (recomendado 8GB+)
- **Processador**: CPU moderna com suporte a conjunto de instruções AVX
- **Armazenamento**: Pelo menos 2GB de espaço livre em disco (para arquivos de modelo e cache)
- **Áudio**: Dispositivos de áudio com suporte a taxa de amostragem de 16kHz

### Requisitos para Funcionalidades Opcionais

- **Ativação por Voz**: Requer download do modelo de reconhecimento de voz Sherpa-ONNX
- **Funcionalidade de Câmera**: Requer dispositivo de câmera e suporte OpenCV

## 📖 Guia de Início Rápido

### **Leia Isto Primeiro**

- Leia atentamente a [Documentação do Projeto](https://huangjunsen0406.github.io/py-xiaozhi/). O tutorial de inicialização e instruções de arquivos estão lá
- A branch main contém o código mais recente. A cada atualização, você precisa reinstalar manualmente as dependências do pip para evitar falta de novas dependências localmente

### 📖 Guias Rápidos

- **[Guia Completo do VSCode (Português)](GUIA_VSCODE_PT.md)** - Guia detalhado de configuração e execução no VSCode
- **[VSCode Complete Guide (English)](VSCODE_GUIDE_EN.md)** - Complete setup and run guide for VSCode
- [Tutorial em Vídeo: Usando o Cliente Xiaozhi do Zero](https://www.bilibili.com/video/BV1dWQhYEEmq/?vd_source=2065ec11f7577e7107a55bbdc3d12fce)

### Instalação

#### Windows

```bash
# Clone o projeto
git clone https://github.com/huangjunsen0406/py-xiaozhi.git
cd py-xiaozhi

# Crie um ambiente virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute o programa - Modo GUI (padrão)
python main.py

# Execute o programa - Modo CLI
python main.py --mode cli
```

#### Linux/macOS

```bash
# Clone o projeto
git clone https://github.com/huangjunsen0406/py-xiaozhi.git
cd py-xiaozhi

# Crie um ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
# Para Linux/Windows:
pip install -r requirements.txt

# Para macOS:
pip install -r requirements_mac.txt

# Execute o programa - Modo GUI (padrão)
python main.py

# Execute o programa - Modo CLI
python main.py --mode cli
```

### Opções de Linha de Comando

```bash
# Especificar protocolo de comunicação
python main.py --protocol websocket  # WebSocket (padrão)
python main.py --protocol mqtt       # Protocolo MQTT

# Especificar modo de execução
python main.py --mode gui            # Interface gráfica (padrão)
python main.py --mode cli            # Linha de comando

# Pular processo de ativação (apenas debug)
python main.py --skip-activation
```

## 🏗️ Arquitetura Técnica

### Design da Arquitetura Principal

- **Arquitetura Orientada a Eventos**: Loop de eventos assíncronos baseado em asyncio, suporta processamento altamente concorrente
- **Design em Camadas**: Separação clara entre camada de aplicação, camada de protocolo, camada de dispositivo e camada de UI
- **Padrão Singleton**: Componentes principais adotam padrão singleton, garantindo gerenciamento unificado de recursos
- **Baseado em Plugins**: Sistema de ferramentas MCP e dispositivos IoT suportam extensão por plugins

### Componentes Técnicos Principais

- **Processamento de Áudio**: Codificação/decodificação Opus, cancelamento de eco WebRTC, reamostragem em tempo real, gravação de áudio do sistema
- **Reconhecimento de Voz**: Modelo offline Sherpa-ONNX, detecção de atividade de voz, reconhecimento de palavra de ativação
- **Comunicação por Protocolo**: Suporte a protocolo duplo WebSocket/MQTT, transmissão criptografada, reconexão automática
- **Sistema de Configuração**: Configuração em camadas, acesso por notação de ponto, atualização dinâmica, suporte JSON/YAML

### Otimização de Desempenho

- **Prioridade Assíncrona**: Arquitetura assíncrona em todo o sistema, evitando operações bloqueantes
- **Gerenciamento de Memória**: Cache inteligente, coleta de lixo
- **Otimização de Áudio**: Processamento de baixa latência de 5ms, gerenciamento de filas, transmissão em fluxo
- **Controle de Concorrência**: Gerenciamento de pool de tarefas, controle de semáforo, thread-safe

### Mecanismos de Segurança

- **Comunicação Criptografada**: Criptografia WSS/TLS, verificação de certificado
- **Autenticação de Dispositivo**: Ativação por protocolo duplo, identificação de impressão digital do dispositivo
- **Controle de Permissões**: Gerenciamento de permissões de ferramentas, controle de acesso à API
- **Isolamento de Erros**: Isolamento de exceções, recuperação de falhas, degradação elegante

## 🔧 Guia de Desenvolvimento

### Estrutura do Projeto

```
py-xiaozhi/
├── main.py                     # Ponto de entrada principal da aplicação
├── src/
│   ├── application.py          # Lógica principal da aplicação
│   ├── audio_codecs/           # Codecs de áudio
│   ├── audio_processing/       # Módulos de processamento de áudio
│   ├── core/                   # Componentes principais
│   ├── display/                # Camada de abstração de interface
│   ├── iot/                    # Gerenciamento de dispositivos IoT
│   ├── mcp/                    # Sistema de ferramentas MCP
│   ├── protocols/              # Protocolos de comunicação
│   ├── utils/                  # Funções utilitárias
│   └── views/                  # Componentes de visualização UI
├── libs/                       # Bibliotecas nativas de terceiros
├── config/                     # Diretório de arquivos de configuração
├── models/                     # Arquivos de modelo de voz
├── assets/                     # Arquivos de recursos estáticos
├── scripts/                    # Scripts auxiliares
├── requirements.txt            # Lista de dependências Python
└── build.json                  # Arquivo de configuração de build
```

### Configuração do Ambiente de Desenvolvimento

```bash
# Formatar código
./format_code.sh  # Linux/macOS
format_code.bat   # Windows

# Executar testes
python -m pytest tests/

# Verificar estilo de código
python -m flake8 src/
```

### Modos de Desenvolvimento Principal

- **Prioridade Assíncrona**: Usar sintaxe `async/await`, evitar operações bloqueantes
- **Tratamento de Erros**: Tratamento de exceções e registro de logs completos
- **Gerenciamento de Configuração**: Usar `ConfigManager` para acesso unificado à configuração
- **Orientado por Testes**: Escrever testes unitários, garantir qualidade do código

### Desenvolvimento de Extensões

- **Adicionar Ferramentas MCP**: Criar novos módulos de ferramentas no diretório `src/mcp/tools/`
- **Adicionar Dispositivos IoT**: Herdar classe base `Thing` para implementar novos dispositivos
- **Adicionar Protocolo**: Implementar classe abstrata base `Protocol`
- **Adicionar Interface**: Estender `BaseDisplay` para implementar novos componentes UI

## 👥 Guia de Contribuição

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

1. O estilo de código deve estar em conformidade com as normas PEP8
2. PRs submetidos devem incluir testes apropriados
3. Atualize a documentação relacionada

## 🙏 Agradecimentos

### Agradecimentos aos seguintes colaboradores open source
> Sem ordem específica

[Xiaoxia](https://github.com/78)
[zhh827](https://github.com/zhh827)
[四博智联-李洪刚](https://github.com/SmartArduino)
[HonestQiao](https://github.com/HonestQiao)
[vonweller](https://github.com/vonweller)
[孙卫公](https://space.bilibili.com/416954647)
[isamu2025](https://github.com/isamu2025)
[Rain120](https://github.com/Rain120)
[kejily](https://github.com/kejily)
[电波bilibili君](https://space.bilibili.com/119751)
[赛搏智能](https://shop115087494.m.taobao.com/)

### ❤️ Apoio de Patrocinadores

<div align="center">
  <h3>Agradecemos a todos os patrocinadores pelo seu apoio ❤️</h3>
  <p>Seja recursos de interface, testes de compatibilidade de dispositivos ou suporte financeiro, cada ajuda torna o projeto mais completo</p>
  
  <a href="https://huangjunsen0406.github.io/py-xiaozhi/sponsors/" target="_blank">
    <img src="https://img.shields.io/badge/Ver-Lista_de_Patrocinadores-brightgreen?style=for-the-badge&logo=github" alt="Lista de Patrocinadores">
  </a>
  <a href="https://huangjunsen0406.github.io/py-xiaozhi/sponsors/" target="_blank">
    <img src="https://img.shields.io/badge/Torne--se-Patrocinador_do_Projeto-orange?style=for-the-badge&logo=heart" alt="Torne-se Patrocinador">
  </a>
</div>

## 📊 Estatísticas do Projeto

[![Star History Chart](https://api.star-history.com/svg?repos=huangjunsen0406/py-xiaozhi&type=Date)](https://www.star-history.com/#huangjunsen0406/py-xiaozhi&Date)

## 📄 Licença

[Licença MIT](LICENSE)

---

<div align="center">
  <p>Feito com ❤️ pela comunidade py-xiaozhi</p>
  <p>
    <a href="https://github.com/huangjunsen0406/py-xiaozhi">GitHub</a> •
    <a href="https://gitee.com/huang-jun-sen/py-xiaozhi">Gitee</a> •
    <a href="https://huangjunsen0406.github.io/py-xiaozhi/">Documentação</a>
  </p>
</div>
