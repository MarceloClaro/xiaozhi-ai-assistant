"""
MCP Tools Providers - Modelos de Visão e Processamento de Imagens

Este módulo contém implementações de diferentes provedores de Vision API,
permitindo integração com múltiplos serviços de análise de imagens.

Providers disponíveis:
- ZhipuVisionAPIProvider: Zhipu GLM-4V Vision API
- Extensível: Adicione novos providers registrando no VisionProviderFactory
"""

from .vllm_provider import (
    ZhipuVisionAPIProvider,
    VisionProviderFactory,
    explain_image_via_mcp,
)

__all__ = [
    "ZhipuVisionAPIProvider",
    "VisionProviderFactory",
    "explain_image_via_mcp",
]
