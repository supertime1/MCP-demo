#!/usr/bin/env python3
"""
Test script to validate MCP server protocol functionality
"""

import asyncio
import json
import sys
from pathlib import Path

# Add server directory to path (go up one level from tests folder)
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_mcp_protocol_functionality():
    """Test MCP server tools by directly calling the handler functions"""
    try:
        print("🧪 Testing MCP Server Tool Functionality...")
        
        # Import the main server module
        from main import handle_list_tools, handle_call_tool, handle_list_resources
        
        # Test 1: List available tools
        print("\n📋 Testing tool listing...")
        tools_result = await handle_list_tools()
        print(f"✅ Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools[:5]:  # Show first 5 tools
            print(f"   • {tool.name}: {tool.description}")
        if len(tools_result.tools) > 5:
            print(f"   ... and {len(tools_result.tools) - 5} more")
        
        # Test 2: List resources
        print("\n🗂️  Testing resource listing...")
        resources_result = await handle_list_resources()
        print(f"✅ Found {len(resources_result.resources)} resources:")
        for resource in resources_result.resources:
            print(f"   • {resource.name}: {resource.description}")
        
        # Test 3: Execute a simple database query tool
        print("\n🔍 Testing database query tool...")
        from mcp.types import CallToolRequest, CallToolRequestParams
        query_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="query_database",
                arguments={"query": "SELECT COUNT(*) as total_records FROM clickstream"}
            )
        )
        query_result = await handle_call_tool(query_request)
        print("✅ Database query result:")
        print(f"   {query_result.content[0].text}")
        
        # Test 4: Test analytics tool
        print("\n📊 Testing analytics tool...")
        analytics_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="geographic_analysis",
                arguments={"analysis_type": "overview"}
            )
        )
        analytics_result = await handle_call_tool(analytics_request)
        print("✅ Geographic analysis result:")
        result_text = analytics_result.content[0].text
        print(f"   {result_text[:300]}..." if len(result_text) > 300 else f"   {result_text}")
        
        # Test 5: Test get sample data
        print("\n📝 Testing sample data tool...")
        sample_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="get_sample_data",
                arguments={"table_name": "clickstream", "limit": 3}
            )
        )
        sample_result = await handle_call_tool(sample_request)
        print("✅ Sample data result:")
        sample_text = sample_result.content[0].text
        print(f"   {sample_text[:400]}..." if len(sample_text) > 400 else f"   {sample_text}")
        
        # Test 6: Test user behavior analysis
        print("\n👥 Testing user behavior analysis...")
        behavior_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="analyze_user_behavior",
                arguments={"analysis_type": "overview"}
            )
        )
        behavior_result = await handle_call_tool(behavior_request)
        print("✅ User behavior analysis result:")
        behavior_text = behavior_result.content[0].text
        print(f"   {behavior_text[:300]}..." if len(behavior_text) > 300 else f"   {behavior_text}")
        
        print("\n🎉 All MCP tool tests passed! Server is fully functional.")
        return True
        
    except Exception as e:
        print(f"\n❌ MCP tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_protocol_functionality())
    sys.exit(0 if success else 1) 