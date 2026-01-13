#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Comandos de Câmera MCP
Verifica se os comandos de câmera estão disponíveis e funcionais
"""

import asyncio
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s[%(name)s] - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_camera_mcp_tools():
    """Testa os comandos MCP de câmera"""
    
    print("\n" + "="*70)
    print("🎥 TESTE DE COMANDOS MCP DE CÂMERA")
    print("="*70 + "\n")
    
    try:
        # Importar MCP Server
        from src.mcp.mcp_server import MCPServer
        
        print("[1/4] Inicializando MCP Server...")
        mcp_server = MCPServer()
        print("  ✅ MCP Server inicializado\n")
        
        print("[2/4] Listando ferramentas disponíveis...")
        tools = mcp_server._tools  # Acesso direto às tools registradas
        
        # Procurar ferramentas de câmera
        camera_tools = [tool for tool in tools if 'photo' in tool.name.lower() or 'camera' in tool.name.lower() or 'screenshot' in tool.name.lower()]
        
        print(f"  📋 Total de ferramentas: {len(tools)}")
        print(f"  📸 Ferramentas de câmera/foto: {len(camera_tools)}\n")
        
        if camera_tools:
            print("  ✅ Ferramentas de câmera encontradas:")
            for tool in camera_tools:
                print(f"     - {tool.name}")
                print(f"       Descrição: {tool.description[:100]}...")
                # Listar parâmetros
                if hasattr(tool, 'input_schema') and tool.input_schema:
                    props = tool.input_schema.properties
                    if props:
                        print(f"       Parâmetros: {[p.name for p in props]}")
                print()
        else:
            print("  ❌ Nenhuma ferramenta de câmera encontrada!\n")
            return False
        
        print("[3/4] Testando mensagem MCP tools/list...")
        
        # Simular mensagem tools/list do protocolo MCP
        tools_list_message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1,
            "params": {}
        }
        
        # Processar mensagem
        response = await mcp_server.handle_json_rpc(json.dumps(tools_list_message))
        response_data = json.loads(response)
        
        if "result" in response_data and "tools" in response_data["result"]:
            tools_in_response = response_data["result"]["tools"]
            camera_in_response = [t for t in tools_in_response if 'photo' in t.get('name', '').lower()]
            
            print(f"  ✅ Resposta MCP recebida")
            print(f"  📋 Total de tools no response: {len(tools_in_response)}")
            print(f"  📸 Camera tools no response: {len(camera_in_response)}")
            
            if camera_in_response:
                print("\n  📸 Tools de câmera disponíveis via MCP:")
                for tool in camera_in_response:
                    print(f"     - {tool.get('name')}")
                    print(f"       {tool.get('description', '')[:80]}...")
            print()
        else:
            print("  ⚠️  Resposta inesperada do MCP\n")
        
        print("[4/4] Informações de uso...")
        print("\n  💡 COMO A ASSISTENTE PODE USAR:")
        print("  "+"─"*60)
        print("  Comando MCP: tools/call")
        print("  Tool name: 'take_photo'")
        print("  Parâmetros:")
        print("    - question (obrigatório): Pergunta sobre a foto")
        print("    - context (opcional): Contexto adicional")
        print()
        print("  📝 EXEMPLOS DE COMANDOS DE VOZ QUE DEVEM FUNCIONAR:")
        print("  "+"─"*60)
        print("  ✓ 'Tire uma foto'")
        print("  ✓ 'O que você está vendo?'")
        print("  ✓ 'Descreva o que está na sua frente'")
        print("  ✓ 'Faça uma foto e me diga o que é'")
        print("  ✓ 'Capture uma imagem'")
        print()
        print("  🔄 FLUXO DE PROCESSAMENTO:")
        print("  "+"─"*60)
        print("  1. Usuário: 'Tire uma foto'")
        print("  2. LLM identifica: Usar ferramenta 'take_photo'")
        print("  3. MCP Server: Executa take_photo(question='O que você vê?')")
        print("  4. Câmera: Captura frame")
        print("  5. Vision API: Analisa imagem")
        print("  6. Assistente: Responde com descrição")
        print()
        
        print("="*70)
        print("📊 RESULTADO DO TESTE")
        print("="*70)
        print(f"✅ MCP Server: FUNCIONANDO")
        print(f"✅ Ferramentas registradas: {len(tools)}")
        print(f"✅ Camera tools: {len(camera_tools)}")
        print(f"✅ Vision API configurada: {mcp_server._vision_url if hasattr(mcp_server, '_vision_url') else 'Não'}")
        print("="*70)
        
        print("\n⚠️  SE A ASSISTENTE NÃO ACIONA A CÂMERA:")
        print("  1. Verifique se o LLM está recebendo a lista de tools")
        print("  2. Verifique se o LLM está fazendo tool calls")
        print("  3. Verifique os logs em tempo real: logs/app.log")
        print("  4. Teste com comando direto via WebSocket/MQTT")
        print()
        
        # Criar exemplo de mensagem para testar
        print("📝 EXEMPLO DE MENSAGEM MCP PARA TESTAR DIRETAMENTE:")
        print("─"*70)
        test_message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": "take_photo",
                "arguments": {
                    "question": "O que você está vendo?"
                }
            }
        }
        print(json.dumps(test_message, indent=2, ensure_ascii=False))
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    try:
        result = asyncio.run(test_camera_mcp_tools())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
