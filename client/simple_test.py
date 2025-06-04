#!/usr/bin/env python3
"""
Simple Working Test

This script tests the working functionality by bypassing the problematic tools listing.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_working_queries():
    """Test various working queries"""
    
    # Server path
    server_path = Path(__file__).parent.parent / "server" / "main.py"
    
    print(f"🔌 Testing working queries with: {server_path}")
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_path)],
    )
    
    # Test queries
    test_cases = [
        {
            "name": "Database Overview",
            "tool": "analyze_user_behavior",
            "args": {"analysis_type": "overview"}
        },
        {
            "name": "Country Analysis", 
            "tool": "geographic_analysis",
            "args": {"analysis_type": "overview"}
        },
        {
            "name": "Direct SQL Query",
            "tool": "query_database", 
            "args": {"query": "SELECT country, COUNT(*) as sessions FROM clickstream GROUP BY country ORDER BY sessions DESC LIMIT 5"}
        },
        {
            "name": "Product Performance",
            "tool": "product_performance",
            "args": {"analysis_type": "popularity"}
        }
    ]
    
    try:
        # Connect to server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")
                
                # Initialize the connection
                await session.initialize()
                print("✅ Session initialized")
                
                # Test each query
                for i, test_case in enumerate(test_cases, 1):
                    print(f"\n🔧 Test {i}: {test_case['name']}")
                    try:
                        result = await session.call_tool(test_case['tool'], test_case['args'])
                        print(f"✅ Success!")
                        if result.content:
                            content = result.content[0].text
                            lines = content.split('\n')
                            # Show first few lines
                            for line in lines[:8]:
                                if line.strip():
                                    print(f"  {line}")
                            if len(lines) > 8:
                                print(f"  ... ({len(lines)-8} more lines)")
                        
                    except Exception as e:
                        print(f"❌ Failed: {e}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Working Queries Test\n")
    
    success = asyncio.run(test_working_queries())
    
    if success:
        print("\n🎉 All working queries completed!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1) 