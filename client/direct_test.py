#!/usr/bin/env python3
"""
Direct MCP Server Test

This script tests calling the server directly to isolate the issue.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_direct_call():
    """Test direct tool call"""
    
    # Server path
    server_path = Path(__file__).parent.parent / "server" / "main.py"
    
    print(f"🔌 Testing direct call to: {server_path}")
    
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
                
                # Call a simple query directly
                print("\n🔧 Testing direct tool call...")
                result = await session.call_tool("query_database", {
                    "query": "SELECT COUNT(*) as total_records FROM clickstream"
                })
                
                print(f"✅ Tool call successful!")
                print(f"📄 Response type: {type(result)}")
                if hasattr(result, 'content'):
                    print(f"📄 Content: {result.content}")
                    if result.content and len(result.content) > 0:
                        print(f"📄 First content: {result.content[0].text}")
                else:
                    print(f"📄 Raw result: {result}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Direct MCP Test\n")
    
    success = asyncio.run(test_direct_call())
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1) 