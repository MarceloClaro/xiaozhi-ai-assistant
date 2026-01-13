"""
Vision API Provider - Implementação Correta para PY-Xiaozhi
Baseado no repositório: https://github.com/MarceloClaro/xiaozhi-esp32-server

Arquivo: src/mcp/tools/providers/vllm_provider.py
"""

import asyncio
import base64
import logging
import os
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


def _resolve_env_var(value: str) -> str:
    """Resolve variáveis de ambiente no formato ${VAR_NAME}"""
    if isinstance(value, str) and value.startswith("${") and \
            value.endswith("}"):
        var_name = value[2:-1]
        env_value = os.getenv(var_name)
        if not env_value:
            msg = f"Variável de ambiente não encontrada: {var_name}"
            raise ValueError(msg)
        return env_value
    return value


class ZhipuVisionAPIProvider:
    """
    Provider para análise de imagens usando Zhipu Vision API (GLM-4V)
    
    Configuração necessária em config.yaml:
    ```yaml
    VLLM:
      zhipu:
        type: "zhipu"
        api_key: "d66ea037-1b07-4283-b49b-b629e005c074"
        model: "glm-4v-vision"
        api_url: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        temperature: 0.7
        max_tokens: 2048
    ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provider com configuração.
        
        Args:
            config: Dicionário com configurações do provider
                - api_key: Token de autenticação Zhipu
                - model: Nome do modelo (padrão glm-4v-vision)
                - api_url: URL da API (padrão Zhipu oficial)
                - temperature: Temperatura para respostas (0-1)
                - max_tokens: Máximo de tokens na resposta
        """
        self.api_key = _resolve_env_var(config.get("api_key", ""))
        self.model = config.get("model", "glm-4v-flash")
        self.api_url = config.get(
            "api_url",
            "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        )
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
        self.timeout = config.get("timeout", 30.0)
        
        log_msg = f"[Vision] Provider Zhipu inicializado com modelo: " \
                  f"{self.model}"
        logger.info(log_msg)
    
    async def analyze_image(
        self,
        image_base64: str,
        question: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analisa uma imagem usando Vision API
        
        Args:
            image_base64: Imagem codificada em base64
            question: Pergunta/descrição sobre a imagem
            context: Contexto adicional (opcional)
        
        Returns:
            Dicionário com resultado:
            {
                "status": "success" | "error",
                "analysis": "Texto da análise",
                "tokens": número de tokens usados,
                "error": "Mensagem de erro (se houver)"
            }
        """
        try:
            logger.debug("[Vision] Iniciando análise de imagem...")
            
            # Validar entrada
            if not image_base64:
                raise ValueError("Imagem base64 não fornecida")
            if not question:
                question = "Descreva detalhadamente tudo que você vê nesta imagem"
            
            # Montar headers dependendo do tipo de API
            headers = {
                "Content-Type": "application/json"
            }
            
            # Adicionar auth (compatível com OpenAI e Zhipu)
            if self.api_url.startswith(
                "https://generativelanguage.googleapis.com"
            ):
                # Google Gemini - usar x-goog-api-key
                headers["x-goog-api-key"] = self.api_key
            else:
                # Zhipu e outros - usar Bearer token
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Montar mensagem para LLM
            content = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": question
                }
            ]
            
            # Adicionar contexto se fornecido
            if context:
                content.append({
                    "type": "text",
                    "text": f"\n\nContexto adicional: {context}"
                })
            
            # Montar payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            logger.debug(f"[Vision] Enviando requisição para {self.api_url}")
            
            # Enviar para API - detectar tipo
            async with httpx.AsyncClient() as client:
                # Detectar provider pelo tipo ou URL
                if self.api_url.startswith(
                    "https://generativelanguage.googleapis.com"
                ):
                    # Google Gemini
                    url = f"{self.api_url}/{self.model}:generateContent?key={self.api_key}"  # noqa
                    headers = {"Content-Type": "application/json"}
                    # Converter para formato Gemini
                    gemini_payload = {
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "inlineData": {
                                            "mimeType": "image/jpeg",
                                            "data": image_base64
                                        }
                                    },
                                    {"text": question}
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": self.temperature,
                            "maxOutputTokens": self.max_tokens
                        }
                    }
                    response = await client.post(
                        url,
                        json=gemini_payload,
                        headers=headers,
                        timeout=self.timeout
                    )
                else:
                    # Zhipu e outros
                    response = await client.post(
                        self.api_url,
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        timeout=self.timeout
                    )
            
            # Processar resposta
            if response.status_code == 200:
                result = response.json()
                
                # Extrair texto dependendo do provider
                if self.api_url.startswith(
                    "https://generativelanguage.googleapis.com"
                ):
                    # Gemini
                    candidates = result.get("candidates", [])
                    if candidates:
                        parts = (
                            candidates[0]
                            .get("content", {})
                            .get("parts", [])
                        )
                        if parts:
                            analysis_text = parts[0].get("text", "")
                        else:
                            analysis_text = ""
                    else:
                        analysis_text = ""
                    tokens_used = result.get(
                        "usageMetadata", {}
                    ).get("totalTokenCount", 0)
                else:
                    # Zhipu
                    analysis_text = result["choices"][0]["message"]["content"]
                    tokens_used = (
                        result.get("usage", {}).get("total_tokens", 0)
                    )
                
                if not analysis_text:
                    return {
                        "status": "error",
                        "error": "Empty response from API",
                        "analysis": None
                    }
                
                msg = f"[Vision] Análise concluída ({tokens_used} tokens)"
                logger.info(msg)
                
                return {
                    "status": "success",
                    "analysis": analysis_text,
                    "tokens": tokens_used,
                    "model": self.model
                }
            else:
                msg = f"API Error {response.status_code}: {response.text}"
                logger.error(f"[Vision] {msg}")
                
                return {
                    "status": "error",
                    "error": msg,
                    "analysis": None
                }
        
        except asyncio.TimeoutError:
            error_msg = "Timeout ao conectar com Vision API"
            logger.error(f"[Vision] {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "analysis": None
            }
        
        except Exception as e:
            error_msg = f"Erro na análise da imagem: {str(e)}"
            logger.error(f"[Vision] {error_msg}", exc_info=True)
            return {
                "status": "error",
                "error": error_msg,
                "analysis": None
            }


class VisionProviderFactory:
    """Factory para criar providers de Vision baseado no tipo"""
    
    _providers = {
        "zhipu": ZhipuVisionAPIProvider,
        # Adicionar mais providers aqui conforme necessário
    }
    
    @classmethod
    def create(cls, provider_type: str, config: Dict[str, Any]):
        """
        Cria instância de provider
        
        Args:
            provider_type: Tipo de provider ("zhipu", etc)
            config: Configuração do provider
        
        Returns:
            Instância do provider
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Provider desconhecido: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def register(cls, provider_type: str, provider_class):
        """Registra um novo tipo de provider"""
        cls._providers[provider_type] = provider_class


# ============================================================================
# INTEGRAÇÃO COM MCP TOOLS
# ============================================================================

async def explain_image_via_mcp(
    image_base64: str,
    question: str,
    vision_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Função helper para usar Vision API nas MCP Tools
    
    Exemplo de uso em camera.py:
    ```python
    from src.mcp.tools.providers.vllm_provider import explain_image_via_mcp
    
    # Na ferramenta take_photo:
    result = await explain_image_via_mcp(
        image_base64=image_base64,
        question=arguments.get("question", "Descreva a imagem"),
        vision_config=config.get("VLLM", {}).get("zhipu", {})
    )
    ```
    """
    provider = VisionProviderFactory.create("zhipu", vision_config)
    return await provider.analyze_image(
        image_base64=image_base64,
        question=question
    )


# ============================================================================
# TESTES
# ============================================================================

async def test_vision_api():
    """Teste rápido da Vision API"""
    
    import cv2
    import json
    import os
    
    # Carregar configuração do config.json
    config_path = "config/config.json"
    
    if not os.path.exists(config_path):
        print(f"[Erro] Arquivo {config_path} não encontrado!")
        return
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = json.load(f)
        
        # Obter configuração do provider selecionado
        selected_prov = (
            full_config.get("selected_module", {}).get("VLLM", "zhipu")
        )
        vllm_configs = full_config.get("VLLM", {})
        
        if selected_prov not in vllm_configs:
            msg = f"[Erro] Provider '{selected_prov}' "
            msg += "não encontrado em VLLM!"
            print(msg)
            return
        
        config = vllm_configs[selected_prov]
        provider_type = config.get("type", selected_prov)
        
        print(f"[Teste] Usando provider: {selected_prov}")
        print(f"[Teste] Tipo: {provider_type}")
        print(f"[Teste] Modelo: {config.get('model')}")
        
    except Exception as e:
        print(f"[Erro] Ao carregar config.json: {e}")
        return
    
    print("[Teste] Iniciando teste da Vision API...")
    
    # 1. Capturar imagem
    print("[Teste] Capturando imagem da câmera...")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("[Erro] Não foi possível capturar imagem")
        return
    
    # 2. Converter para base64
    print("[Teste] Convertendo imagem para base64...")
    _, buffer = cv2.imencode('.jpg', frame)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    print(f"[Teste] Tamanho da imagem: {len(image_base64)} caracteres")
    
    # 3. Criar provider
    print("[Teste] Criando provider...")
    if provider_type == "openai":
        # Para OpenAI-compatible (Gemini, Aliyun, etc)
        provider = ZhipuVisionAPIProvider(config)
    else:
        # Para Zhipu nativo
        provider = ZhipuVisionAPIProvider(config)
    
    # 4. Analisar imagem
    print("[Teste] Enviando imagem para análise...")
    question_text = (
        "Descreva detalhadamente tudo que você vê nesta imagem. "
        "Inclua cores, objetos, layout da cena."
    )
    context_text = (
        "Esta é uma imagem capturada por um assistente de IA. "
        "Use linguagem clara e descritiva."
    )
    result = await provider.analyze_image(
        image_base64=image_base64,
        question=question_text,
        context=context_text
    )
    
    # 5. Exibir resultado
    print("\n" + "="*70)
    print("RESULTADO DA ANÁLISE")
    print("="*70)
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"Tokens usados: {result['tokens']}")
        print(f"\nAnálise:\n{result['analysis']}")
    else:
        print(f"Erro: {result.get('error', 'Desconhecido')}")
    
    print("="*70)


if __name__ == "__main__":
    # Executar teste
    asyncio.run(test_vision_api())
