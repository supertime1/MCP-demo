#!/usr/bin/env python3
"""
Test script to validate MCP server visualization functionality
"""

import asyncio
import sys
from pathlib import Path

# Add server directory to path (go up one level from tests folder)
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_visualization_functionality():
    """Test visualization tools"""
    try:
        print("🎨 Testing MCP Server Visualization Functionality...")
        
        from main import handle_call_tool
        from mcp.types import CallToolRequest, CallToolRequestParams
        
        # Test chart creation
        print("\n📊 Testing chart creation...")
        viz_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(
                name="create_chart",
                arguments={
                    "data_query": "SELECT country, COUNT(*) as sessions FROM clickstream GROUP BY country ORDER BY sessions DESC LIMIT 5",
                    "chart_type": "bar",
                    "title": "Top 5 Countries by Sessions"
                }
            )
        )
        result = await handle_call_tool(viz_request)
        print("✅ Chart creation result:")
        print(f"   Content items: {len(result.content)}")
        for i, content in enumerate(result.content):
            if hasattr(content, 'type'):
                print(f"   Item {i+1}: {content.type}")
                if content.type == "text":
                    print(f"     Text: {content.text[:100]}...")
                elif content.type == "image":
                    print(f"     Image: {len(content.data)} bytes")
        
        print("\n🎉 Visualization test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_visualization_functionality())
    sys.exit(0 if success else 1) 