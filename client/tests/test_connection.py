#!/usr/bin/env python3
"""
MCP Connection Tests

Tests for basic MCP server connectivity, initialization, and communication.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class ConnectionTestSuite:
    """Test suite for MCP connection functionality"""
    
    def __init__(self):
        self.server_path = Path(__file__).parent.parent.parent / "server" / "main.py"
        self.server_params = StdioServerParameters(
            command="python",
            args=[str(self.server_path)],
        )
        self.results = []
    
    async def test_basic_connection(self) -> bool:
        """Test basic server connection and initialization"""
        print("🔌 Testing basic MCP server connection...")
        
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    self.results.append({
                        "test": "Basic Connection",
                        "status": "PASS",
                        "time_ms": elapsed,
                        "details": "Successfully connected and initialized"
                    })
                    print(f"  ✅ Connected and initialized ({elapsed}ms)")
                    return True
                    
        except Exception as e:
            self.results.append({
                "test": "Basic Connection", 
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to connect or initialize"
            })
            print(f"  ❌ Connection failed: {e}")
            return False
    
    async def test_tools_listing(self) -> bool:
        """Test listing available tools from server"""
        print("📋 Testing tools listing...")
        
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tools_result = await session.list_tools()
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    if hasattr(tools_result, 'tools'):
                        tools = tools_result.tools
                        self.results.append({
                            "test": "Tools Listing",
                            "status": "PASS",
                            "time_ms": elapsed,
                            "details": f"Found {len(tools)} tools",
                            "tools_count": len(tools)
                        })
                        print(f"  ✅ Listed {len(tools)} tools ({elapsed}ms)")
                        
                        # Show first few tools
                        for tool in tools[:3]:
                            print(f"    • {tool.name}")
                        if len(tools) > 3:
                            print(f"    ... and {len(tools)-3} more")
                        
                        return True
                    else:
                        raise ValueError("Invalid tools response format")
                        
        except Exception as e:
            self.results.append({
                "test": "Tools Listing",
                "status": "FAIL", 
                "error": str(e),
                "details": "Failed to list tools"
            })
            print(f"  ❌ Tools listing failed: {e}")
            return False
    
    async def test_resources_listing(self) -> bool:
        """Test listing available resources from server"""
        print("📚 Testing resources listing...")
        
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    resources_result = await session.list_resources()
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    if hasattr(resources_result, 'resources'):
                        resources = resources_result.resources
                        self.results.append({
                            "test": "Resources Listing",
                            "status": "PASS",
                            "time_ms": elapsed,
                            "details": f"Found {len(resources)} resources",
                            "resources_count": len(resources)
                        })
                        print(f"  ✅ Listed {len(resources)} resources ({elapsed}ms)")
                        
                        # Show resources
                        for resource in resources:
                            print(f"    • {resource.name}")
                        
                        return True
                    else:
                        raise ValueError("Invalid resources response format")
                        
        except Exception as e:
            self.results.append({
                "test": "Resources Listing",
                "status": "FAIL",
                "error": str(e), 
                "details": "Failed to list resources"
            })
            print(f"  ❌ Resources listing failed: {e}")
            return False
    
    async def test_simple_tool_call(self) -> bool:
        """Test calling a simple tool"""
        print("🔧 Testing simple tool call...")
        
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Call a simple schema tool
                    result = await session.call_tool("get_table_schema", {"table_name": ""})
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    if result.content and len(result.content) > 0:
                        content = result.content[0].text
                        self.results.append({
                            "test": "Simple Tool Call",
                            "status": "PASS",
                            "time_ms": elapsed,
                            "details": f"Schema returned {len(content)} characters",
                            "response_length": len(content)
                        })
                        print(f"  ✅ Tool call successful ({elapsed}ms)")
                        print(f"    Response length: {len(content)} characters")
                        return True
                    else:
                        raise ValueError("Empty response from tool call")
                        
        except Exception as e:
            self.results.append({
                "test": "Simple Tool Call",
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to execute tool"
            })
            print(f"  ❌ Tool call failed: {e}")
            return False
    
    async def run_all_tests(self) -> dict:
        """Run all connection tests"""
        print(f"🚀 Starting MCP Connection Test Suite")
        print(f"📡 Server: {self.server_path}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        test_results = []
        test_results.append(await self.test_basic_connection())
        test_results.append(await self.test_tools_listing())
        test_results.append(await self.test_resources_listing()) 
        test_results.append(await self.test_simple_tool_call())
        
        # Calculate summary
        total_time = round((time.time() - start_time) * 1000, 2)
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 60)
        print(f"📊 Connection Test Results:")
        print(f"   Passed: {passed}/{total}")
        print(f"   Success Rate: {passed/total*100:.1f}%")
        print(f"   Total Time: {total_time}ms")
        
        return {
            "passed": passed,
            "total": total,
            "success_rate": passed/total*100,
            "total_time_ms": total_time,
            "results": self.results
        }

async def main():
    """Main test runner"""
    test_suite = ConnectionTestSuite()
    results = await test_suite.run_all_tests()
    
    if results["passed"] == results["total"]:
        print("\n🎉 All connection tests passed!")
        return True
    else:
        print(f"\n⚠️  {results['total'] - results['passed']} test(s) failed")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted")
        sys.exit(1) 