#!/usr/bin/env python3
"""
Verificação da Integração Vision API
Arquivo: verify_vision_api.py

Use este script para verificar se a Vision API foi configurada corretamente.
"""

import sys
import os

def check_imports():
    """Verifica se todos os imports necessários estão disponíveis"""
    print("=" * 70)
    print("1. Verificando Imports...")
    print("=" * 70)
    
    imports = {
        "base64": "Base64 encoding",
        "cv2": "OpenCV (câmera)",
        "httpx": "HTTP client assíncrono",
    }
    
    all_ok = True
    for module, description in imports.items():
        try:
            __import__(module)
            print(f"✅ {module:<15} - {description}")
        except ImportError as e:
            print(f"❌ {module:<15} - FALTANDO: {e}")
            all_ok = False
    
    return all_ok


def check_files():
    """Verifica se os arquivos foram criados corretamente"""
    print("\n" + "=" * 70)
    print("2. Verificando Arquivos...")
    print("=" * 70)
    
    files_to_check = [
        "src/mcp/tools/providers/vllm_provider.py",
        "src/mcp/tools/providers/__init__.py",
        "src/mcp/tools/camera/camera.py",
        "VISION_API_INTEGRACAO.md",
    ]
    
    all_ok = True
    for filepath in files_to_check:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {filepath:<50} ({size} bytes)")
        else:
            print(f"❌ {filepath:<50} FALTANDO")
            all_ok = False
    
    return all_ok


def check_config():
    """Verifica se config.yaml tem as configurações corretas"""
    print("\n" + "=" * 70)
    print("3. Verificando Configuração...")
    print("=" * 70)
    
    try:
        from src.utils.config_manager import ConfigManager
        
        config = ConfigManager.get_instance()
        vllm_config = config.get_config("VLLM", {})
        
        if not vllm_config:
            print("❌ VLLM não configurado em config.yaml")
            print("   Adicione a seguinte seção:")
            print("""
   VLLM:
     zhipu:
       type: "zhipu"
       api_key: "d66ea037-1b07-4283-b49b-b629e005c074"
       model: "glm-4v-vision"
       api_url: "https://open.bigmodel.cn/api/paas/v4/chat/completions"
       temperature: 0.7
       max_tokens: 2048
            """)
            return False
        
        zhipu = vllm_config.get("zhipu", {})
        
        checks = {
            "api_key": "API Key do Zhipu",
            "model": "Modelo Vision",
            "api_url": "URL da API",
        }
        
        all_ok = True
        for key, description in checks.items():
            value = zhipu.get(key)
            if value:
                # Ocultar parte do token para segurança
                if key == "api_key" and len(value) > 20:
                    display_value = value[:10] + "..." + value[-5:]
                else:
                    display_value = value
                print(f"✅ {key:<15} - {display_value}")
            else:
                print(f"❌ {key:<15} - NÃO CONFIGURADO")
                all_ok = False
        
        return all_ok
    
    except Exception as e:
        print(f"❌ Erro ao verificar config: {e}")
        return False


def check_provider():
    """Verifica se o provider pode ser importado"""
    print("\n" + "=" * 70)
    print("4. Verificando Vision Provider...")
    print("=" * 70)
    
    try:
        from src.mcp.tools.providers import (
            ZhipuVisionAPIProvider,
            VisionProviderFactory,
        )
        
        print("✅ ZhipuVisionAPIProvider pode ser importado")
        print("✅ VisionProviderFactory pode ser importado")
        
        # Tentar criar uma instância
        config = {
            "api_key": "test_key",
            "model": "glm-4v-vision",
        }
        
        provider = ZhipuVisionAPIProvider(config)
        print(f"✅ Provider instanciado: {provider.__class__.__name__}")
        print(f"✅ Modelo configurado: {provider.model}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao verificar provider: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_camera():
    """Verifica se o módulo camera.py foi atualizado"""
    print("\n" + "=" * 70)
    print("5. Verificando Integração Camera...")
    print("=" * 70)
    
    try:
        from src.mcp.tools.camera.camera import take_photo
        
        print("✅ take_photo() pode ser importado")
        
        # Verificar se é uma função async
        import inspect
        sig = inspect.signature(take_photo)
        
        print(f"✅ take_photo() assinatura: {sig}")
        
        # Verificar docstring
        if take_photo.__doc__:
            first_line = take_photo.__doc__.split('\n')[0]
            print(f"✅ Documentação: {first_line}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao verificar camera: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_tests():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "VERIFICAÇÃO VISION API" + " " * 31 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        "Imports": check_imports(),
        "Arquivos": check_files(),
        "Configuração": check_config(),
        "Provider": check_provider(),
        "Camera": check_camera(),
    }
    
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TUDO OK! Vision API está pronta para usar!")
        print("\nProximos passos:")
        print("1. python src/mcp/tools/providers/vllm_provider.py  (teste isolado)")
        print("2. python main.py --mode cli  (teste integrado)")
        print("3. Tire uma foto: take_photo({'question': 'O que vê?'})")
    else:
        print("❌ Existem problemas a corrigir.")
        print("Veja a documentação: VISION_API_INTEGRACAO.md")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_tests())
