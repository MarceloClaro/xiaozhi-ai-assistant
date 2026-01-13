"""
Gerenciador de modelos de IA com suporte a fallback para modelo local.
Permite usar modelo local (Deepseek) quando a API remota não está disponível.
"""

import os
import json
import subprocess
from typing import Optional, Dict, Any, List
from enum import Enum

import requests

from src.utils.config_manager import ConfigManager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AIModelType(Enum):
    """Tipos de modelos disponíveis."""
    REMOTE_API = "remote_api"  # API remota (WebSocket/REST)
    LOCAL_DEEPSEEK = "local_deepseek"  # Modelo local Deepseek


class AIModelManager:
    """Gerencia modelos de IA com suporte a fallback."""
    
    _instance = None
    
    def __init__(self):
        self.config = ConfigManager.get_instance()
        self.current_model_type = AIModelType.REMOTE_API
        self.remote_api_available = True
        self.local_model_available = False
        self.local_model_path = None
        self.local_model_endpoint = self.config.get_config(
            "AI_MODEL.LOCAL_MODEL_ENDPOINT", "http://127.0.0.1:11434/api/generate"
        )
        self.local_model_name = self.config.get_config("AI_MODEL.LOCAL_MODEL_NAME", "llava")
        self.timeout_local = self.config.get_config("AI_MODEL.TIMEOUT_LOCAL", 30)
        self.timeout_remote = self.config.get_config("AI_MODEL.TIMEOUT_REMOTE", 20)
        
        self._initialize_models()
    
    @classmethod
    def get_instance(cls):
        """Singleton."""
        if cls._instance is None:
            cls._instance = AIModelManager()
        return cls._instance
    
    def _initialize_models(self):
        """Inicializa e verifica disponibilidade dos modelos."""
        logger.info("🔍 Verificando modelos de IA disponíveis...")
        
        # Verificar modelo local
        self._check_local_model()
        
        # Verificar API remota
        self._check_remote_api()
        
        # Definir modelo padrão
        self._set_default_model()
    
    def _check_local_model(self):
        """Verifica disponibilidade do modelo Deepseek local."""
        try:
            # Disponibilidade por endpoint HTTP (Ollama ou servidor local)
            if self.local_model_endpoint:
                self.local_model_available = True
                logger.info(f"✅ Endpoint local configurado: {self.local_model_endpoint}")
                return

            # Fallback: detecção por arquivo (legado)
            model_paths = [
                "models/llm-model-deepseek-r1-1.5B-ax630c_0.3-m5stack1_arm64.deb",
                "./models/deepseek-r1-1.5b",
                "./models/deepseek",
            ]
            for path in model_paths:
                if os.path.exists(path):
                    self.local_model_path = path
                    self.local_model_available = True
                    logger.info(f"✅ Modelo local encontrado: {path}")
                    return

            logger.warning("⚠️ Modelo local não encontrado nem endpoint configurado")
            self.local_model_available = False

        except Exception as e:
            logger.error(f"❌ Erro ao verificar modelo local: {e}")
            self.local_model_available = False
    
    def _check_remote_api(self):
        """Verifica disponibilidade da API remota."""
        try:
            websocket_url = self.config.get_config(
                "SYSTEM_OPTIONS.NETWORK.WEBSOCKET_URL"
            )
            if websocket_url:
                self.remote_api_available = True
                logger.info(f"✅ API remota disponível: {websocket_url}")
            else:
                self.remote_api_available = False
                logger.warning("⚠️ Nenhuma URL de API remota configurada")
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar API remota: {e}")
            self.remote_api_available = False
    
    def _set_default_model(self):
        """Define modelo padrão baseado em disponibilidade."""
        use_local = self.config.get_config("AI_MODEL.USE_LOCAL", False)
        
        if use_local and self.local_model_available:
            self.current_model_type = AIModelType.LOCAL_DEEPSEEK
            logger.info("🎯 Usando modelo LOCAL (Deepseek)")
        elif self.remote_api_available:
            self.current_model_type = AIModelType.REMOTE_API
            logger.info("🎯 Usando modelo REMOTO (API)")
        elif self.local_model_available:
            self.current_model_type = AIModelType.LOCAL_DEEPSEEK
            logger.warning("⚠️ API indisponível, usando modelo LOCAL")
        else:
            logger.error("❌ Nenhum modelo disponível!")
    
    def get_current_model_type(self) -> AIModelType:
        """Retorna tipo de modelo atual."""
        return self.current_model_type
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status dos modelos."""
        return {
            "current_model": self.current_model_type.value,
            "remote_api_available": self.remote_api_available,
            "local_model_available": self.local_model_available,
            "local_model_path": self.local_model_path,
        }
    
    def switch_to_local(self) -> bool:
        """Muda para modelo local."""
        if self.local_model_available:
            self.current_model_type = AIModelType.LOCAL_DEEPSEEK
            logger.info("🔄 Mudando para modelo LOCAL")
            return True
        logger.error("❌ Modelo local não disponível")
        return False
    
    def switch_to_remote(self) -> bool:
        """Muda para API remota."""
        if self.remote_api_available:
            self.current_model_type = AIModelType.REMOTE_API
            logger.info("🔄 Mudando para modelo REMOTO")
            return True
        logger.error("❌ API remota não disponível")
        return False
    
    def switch_to_auto(self):
        """Define modo automático (fallback)."""
        logger.info("🔄 Mudando para modo AUTO (fallback habilitado)")
        self._set_default_model()
    
    def query_remote(self, prompt: str, images: Optional[List[str]] = None) -> Optional[str]:
        """
        Consulta API remota.
        Será implementado pela aplicação principal.
        """
        logger.info(f"🌐 Consultando API remota: {prompt[:50]}...")
        # Será implementado pela aplicação principal que conhece o protocolo
        return None
    
    def query_local(self, prompt: str, images: Optional[List[str]] = None) -> Optional[str]:
        """
        Consulta modelo local Deepseek.
        """
        if not self.local_model_available:
            logger.error("❌ Modelo local não disponível")
            return None
        
        try:
            logger.info(f"💾 Consultando modelo local: {prompt[:50]}...")

            # Se endpoint HTTP estiver configurado, usar (Ollama/servidor local)
            if self.local_model_endpoint:
                result = self._invoke_local_http(prompt, images=images)
            else:
                # fallback para CLI (legado)
                result = self._invoke_local_deepseek(prompt)
            
            if result:
                logger.info("✅ Resposta do modelo local obtida")
                return result
            else:
                logger.error("❌ Falha ao obter resposta do modelo local")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao consultar modelo local: {e}")
            return None
    
    def _invoke_local_deepseek(self, prompt: str) -> Optional[str]:
        """
        Invoca modelo Deepseek local.
        Implementação pode variar conforme o setup do modelo.
        """
        try:
            # Opção 1: Usar subprocess para chamar modelo local via CLI
            # (ajuste conforme o seu setup)
            cmd = [
                "python", "-m", "deepseek",
                "--prompt", prompt,
                "--max-tokens", "512"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Modelo local erro: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao chamar modelo local")
            return None
        except FileNotFoundError:
            logger.error("Modelo local não encontrado no PATH")
            return None
        except Exception as e:
            logger.error(f"Erro ao invocar modelo local: {e}")
            return None

    def _invoke_local_http(self, prompt: str, images: Optional[List[str]] = None) -> Optional[str]:
        """
        Invoca modelo local via endpoint HTTP (ex.: Ollama /api/generate).
        """
        if not self.local_model_endpoint:
            logger.error("❌ Endpoint local não configurado")
            return None

        payload = {
            "model": self.local_model_name,
            "prompt": prompt,
            "stream": False,
        }
        if images:
            payload["images"] = images  # lista de base64

        try:
            response = requests.post(
                self.local_model_endpoint,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout_local,
            )
            if response.status_code != 200:
                logger.error(
                    f"❌ Endpoint local retornou status {response.status_code}: {response.text[:200]}"
                )
                return None

            data = response.json()
            # Ollama /api/generate retorna 'response' ou 'message'
            if isinstance(data, dict):
                if "response" in data:
                    return str(data.get("response", "")).strip()
                if "message" in data and isinstance(data["message"], dict):
                    return str(data["message"].get("content", "")).strip()
            return str(data)

        except requests.Timeout:
            logger.error("⌛ Timeout ao chamar endpoint local")
            return None
        except requests.RequestException as e:
            logger.error(f"❌ Erro de requisição ao endpoint local: {e}")
            return None
    
    def query(self, prompt: str, prefer_local: bool = False, images: Optional[List[str]] = None) -> Optional[str]:
        """
        Consulta modelo com fallback automático.
        
        Args:
            prompt: Prompt para enviar
            prefer_local: Se True, tenta local primeiro
        
        Returns:
            Resposta do modelo ou None
        """
        models_to_try = []
        
        if prefer_local and self.local_model_available:
            models_to_try = [
                AIModelType.LOCAL_DEEPSEEK,
                AIModelType.REMOTE_API
            ]
        else:
            models_to_try = [
                AIModelType.REMOTE_API,
                AIModelType.LOCAL_DEEPSEEK
            ]
        
        for model_type in models_to_try:
            try:
                if model_type == AIModelType.REMOTE_API and self.remote_api_available:
                    logger.info("📡 Tentando API remota...")
                    result = self.query_remote(prompt, images=images)
                    if result:
                        return result
                        
                elif model_type == AIModelType.LOCAL_DEEPSEEK and self.local_model_available:
                    logger.info("💾 Tentando modelo local...")
                    result = self.query_local(prompt, images=images)
                    if result:
                        return result
                        
            except Exception as e:
                logger.warning(f"⚠️ Falha com {model_type.value}: {e}")
                continue
        
        logger.error("❌ Todos os modelos falharam!")
        return None


def get_model_manager() -> AIModelManager:
    """Helper para obter instância do gerenciador."""
    return AIModelManager.get_instance()
