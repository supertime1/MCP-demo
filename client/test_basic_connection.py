#!/usr/bin/env python3
"""
Basic MCP Connection Test

This script tests the basic connectivity to our MCP server using
the simplest possible approach.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_basic_connection():
    """Test basic MCP server connection"""
    
    # Server path
    server_path = Path(__file__).parent.parent / "server" / "main.py"
    
    print(f"🔌 Testing connection to: {server_path}")
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
    )
    
    try:
        # Connect to server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")
                
                # Initialize the connection
                await session.initialize()
                print("✅ Session initialized")
                
                # List tools
                try:
                    tools_result = await session.list_tools()
                    print(f"✅ Got tools response: {type(tools_result)}")
                    
                    # Extract tools from the response
                    if hasattr(tools_result, 'tools'):
                        tools = tools_result.tools
                        print(f"📊 Available tools ({len(tools)}):")
                        for tool in tools:
                            print(f"  • {tool.name}: {tool.description}")
                    else:
                        print(f"❓ Tools result format: {tools_result}")
                        
                except Exception as e:
                    print(f"❌ Error listing tools: {e}")
                
                # Try calling a simple tool
                try:
                    print("\n🔧 Testing tool call...")
                    result = await session.call_tool("get_table_schema", {"table_name": ""})
                    print(f"✅ Tool call successful")
                    print(f"📄 Response: {result.content[0].text[:200]}...")
                    
                except Exception as e:
                    print(f"❌ Error calling tool: {e}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting MCP Connection Test\n")
    
    success = asyncio.run(test_basic_connection())
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1) 