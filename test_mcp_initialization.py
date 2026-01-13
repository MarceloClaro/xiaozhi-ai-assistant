"""
Test MCP Server tool initialization and registration
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp.mcp_server import McpServer
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


async def test_mcp_tools():
    """Test if MCP tools are properly registered"""
    
    print("\n" + "="*60)
    print("MCP SERVER TOOL INITIALIZATION TEST")
    print("="*60 + "\n")
    
    # Get MCP Server instance
    server = McpServer.get_instance()
    
    print(f"[1] Initial tool count: {len(server.tools)}")
    for tool in server.tools:
        print(f"    - {tool.name}")
    
    # Call add_common_tools
    print("\n[2] Calling add_common_tools()...")
    try:
        server.add_common_tools()
        print("    ✅ add_common_tools() executed successfully")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check tools after registration
    print(f"\n[3] Tool count after add_common_tools(): {len(server.tools)}")
    for tool in server.tools:
        print(f"    - {tool.name}")
    
    if len(server.tools) == 0:
        print("\n⚠️  WARNING: No tools were registered!")
        return False
    
    # Check for take_photo specifically
    take_photo_found = any(t.name == "take_photo" for t in server.tools)
    print(f"\n[4] take_photo tool found: {'✅ YES' if take_photo_found else '❌ NO'}")
    
    if take_photo_found:
        print("    ✅ Camera tool is properly registered")
        return True
    else:
        print("    ❌ Camera tool NOT found in tools list")
        return False


async def test_mcp_message_handling():
    """Test MCP message processing"""
    print("\n" + "="*60)
    print("MCP MESSAGE HANDLING TEST")
    print("="*60 + "\n")
    
    server = McpServer.get_instance()
    
    # Simulate tools/list request
    print("[1] Simulating tools/list request...")
    
    # Create a capture for responses
    responses = []
    
    async def capture_response(msg):
        responses.append(msg)
    
    server.set_send_callback(capture_response)
    
    # Parse a tools/list message
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    import json
    await server.parse_message(json.dumps(message))
    
    print(f"\n[2] Response count: {len(responses)}")
    if responses:
        response_json = json.loads(responses[0])
        if "result" in response_json:
            tools = response_json["result"].get("tools", [])
            print(f"    Tools returned: {len(tools)}")
            for tool in tools:
                print(f"      - {tool.get('name', 'unknown')}")
        else:
            print(f"    Response: {json.dumps(response_json, indent=2)[:200]}...")
    
    return len(responses) > 0


async def main():
    """Run all tests"""
    print("\n🔍 MCP INITIALIZATION DIAGNOSTIC TEST\n")
    
    # Test 1: Tool registration
    test1_result = await test_mcp_tools()
    
    # Test 2: Message handling
    test2_result = await test_mcp_message_handling()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"[1] Tool Registration: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"[2] Message Handling: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print("="*60 + "\n")
    
    if test1_result and test2_result:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
