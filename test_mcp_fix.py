#!/usr/bin/env python3
"""Quick MCP registration test"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.mcp.mcp_server import McpServer


async def main():
    print("\n" + "="*70)
    print("MCP TOOLS REGISTRATION TEST")
    print("="*70 + "\n")
    
    server = McpServer.get_instance()
    
    print(f"[OK] Initial tools count: {len(server.tools)}")
    
    print("\n[*] Calling add_common_tools()...")
    server.add_common_tools()
    
    print(f"[OK] Tools after add_common_tools(): {len(server.tools)}")
    
    # Show only first 5 tools
    for tool in server.tools[:5]:
        print(f"  - {tool.name}")
    print(f"  ... and {len(server.tools) - 5} more tools")
    
    # Check for take_photo
    has_camera = any(t.name == "take_photo" for t in server.tools)
    print(f"\n[OK] Camera tool (take_photo): {'PRESENT' if has_camera else 'MISSING'}")
    
    if has_camera:
        print("\n" + "="*70)
        print("SUCCESS! MCP SERVER TOOLS ARE PROPERLY REGISTERED!")
        print("="*70)
        return True
    else:
        print("\nERROR: take_photo not found in tools list")
        return False


if __name__ == "__main__":
    asyncio.run(main())
