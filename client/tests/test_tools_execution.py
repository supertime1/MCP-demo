#!/usr/bin/env python3
"""
MCP Tools Execution Tests

Tests for MCP tool functionality, including database queries, analytics,
and visualization tools execution.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class ToolsTestSuite:
    """Test suite for MCP tools execution"""
    
    def __init__(self):
        self.server_path = Path(__file__).parent.parent.parent / "server" / "main.py"
        self.server_params = StdioServerParameters(
            command="python",
            args=[str(self.server_path)],
        )
        self.results = []
    
    async def _execute_tool_test(self, tool_name: str, args: Dict[str, Any], test_description: str) -> bool:
        """Helper method to execute and test a tool call"""
        print(f"🔧 Testing {test_description}...")
        
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(tool_name, args)
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    if result.content and len(result.content) > 0:
                        content = result.content[0].text
                        self.results.append({
                            "test": test_description,
                            "tool": tool_name,
                            "status": "PASS",
                            "time_ms": elapsed,
                            "response_length": len(content),
                            "details": f"Successfully executed {tool_name}"
                        })
                        print(f"  ✅ Success ({elapsed}ms) - {len(content)} chars response")
                        
                        # Show first few lines of response
                        lines = content.split('\n')[:5]
                        for line in lines:
                            if line.strip():
                                print(f"    {line[:60]}")
                        if len(content.split('\n')) > 5:
                            print(f"    ... ({len(content.split('\n'))-5} more lines)")
                        
                        return True
                    else:
                        raise ValueError("Empty response from tool")
                        
        except Exception as e:
            self.results.append({
                "test": test_description,
                "tool": tool_name,
                "status": "FAIL",
                "error": str(e),
                "details": f"Failed to execute {tool_name}"
            })
            print(f"  ❌ Failed: {e}")
            return False
    
    async def test_database_tools(self) -> List[bool]:
        """Test database tools functionality"""
        print("\n📊 Testing Database Tools")
        print("-" * 40)
        
        tests = []
        
        # Test 1: Basic query
        tests.append(await self._execute_tool_test(
            "query_database",
            {"query": "SELECT COUNT(*) as total_records FROM clickstream"},
            "Basic Database Query"
        ))
        
        # Test 2: Table schema
        tests.append(await self._execute_tool_test(
            "get_table_schema",
            {"table_name": ""},
            "Database Schema Retrieval"
        ))
        
        # Test 3: Sample data
        tests.append(await self._execute_tool_test(
            "get_sample_data",
            {"table_name": "clickstream", "limit": 3},
            "Sample Data Retrieval"
        ))
        
        # Test 4: User behavior analysis
        tests.append(await self._execute_tool_test(
            "analyze_user_behavior",
            {"analysis_type": "overview"},
            "User Behavior Analysis"
        ))
        
        return tests
    
    async def test_analytics_tools(self) -> List[bool]:
        """Test analytics tools functionality"""
        print("\n📈 Testing Analytics Tools")
        print("-" * 40)
        
        tests = []
        
        # Test 1: User segmentation
        tests.append(await self._execute_tool_test(
            "user_segmentation",
            {"segmentation_type": "engagement"},
            "User Segmentation Analysis"
        ))
        
        # Test 2: Geographic analysis
        tests.append(await self._execute_tool_test(
            "geographic_analysis",
            {"analysis_type": "overview"},
            "Geographic Analysis"
        ))
        
        # Test 3: Product performance
        tests.append(await self._execute_tool_test(
            "product_performance",
            {"analysis_type": "popularity"},
            "Product Performance Analysis"
        ))
        
        # Test 4: Conversion funnel
        tests.append(await self._execute_tool_test(
            "conversion_funnel",
            {"funnel_type": "standard"},
            "Conversion Funnel Analysis"
        ))
        
        return tests
    
    async def test_complex_queries(self) -> List[bool]:
        """Test complex SQL queries"""
        print("\n🔍 Testing Complex Queries")
        print("-" * 40)
        
        tests = []
        
        # Test 1: Multi-table join query
        tests.append(await self._execute_tool_test(
            "query_database",
            {"query": """
                SELECT 
                    us.country, 
                    COUNT(*) as sessions,
                    ROUND(AVG(us.total_clicks), 2) as avg_clicks
                FROM user_sessions us
                GROUP BY us.country 
                HAVING COUNT(*) >= 10
                ORDER BY sessions DESC 
                LIMIT 5
            """},
            "Multi-table Analysis Query"
        ))
        
        # Test 2: Aggregation query
        tests.append(await self._execute_tool_test(
            "query_database",
            {"query": """
                SELECT 
                    page_1_main_category as category,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    COUNT(*) as total_views,
                    ROUND(AVG(CASE WHEN price > 0 THEN price END), 2) as avg_price
                FROM clickstream 
                WHERE page_1_main_category != 'Unknown'
                GROUP BY page_1_main_category
                ORDER BY total_views DESC
                LIMIT 5
            """},
            "Category Performance Query"
        ))
        
        return tests
    
    async def test_error_handling(self) -> List[bool]:
        """Test error handling for invalid inputs"""
        print("\n⚠️  Testing Error Handling")
        print("-" * 40)
        
        tests = []
        
        # Test 1: Invalid SQL query
        print("🔧 Testing Invalid SQL Query...")
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool("query_database", {
                        "query": "SELECT * FROM nonexistent_table"
                    })
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    # Should return an error message, not crash
                    if result.content and "Error" in result.content[0].text:
                        self.results.append({
                            "test": "Invalid SQL Error Handling",
                            "status": "PASS",
                            "time_ms": elapsed,
                            "details": "Properly handled invalid SQL"
                        })
                        print(f"  ✅ Properly handled error ({elapsed}ms)")
                        tests.append(True)
                    else:
                        raise ValueError("Should have returned error message")
                        
        except Exception as e:
            self.results.append({
                "test": "Invalid SQL Error Handling",
                "status": "FAIL", 
                "error": str(e),
                "details": "Error handling failed"
            })
            print(f"  ❌ Error handling failed: {e}")
            tests.append(False)
        
        return tests
    
    async def run_all_tests(self) -> dict:
        """Run all tools execution tests"""
        print(f"⚡ Starting MCP Tools Execution Test Suite")
        print(f"📡 Server: {self.server_path}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        all_results = []
        all_results.extend(await self.test_database_tools())
        all_results.extend(await self.test_analytics_tools())
        all_results.extend(await self.test_complex_queries())
        all_results.extend(await self.test_error_handling())
        
        # Calculate summary
        total_time = round((time.time() - start_time) * 1000, 2)
        passed = sum(all_results)
        total = len(all_results)
        
        print("\n" + "=" * 60)
        print(f"📊 Tools Execution Test Results:")
        print(f"   Database Tools: {sum(all_results[:4])}/4")
        print(f"   Analytics Tools: {sum(all_results[4:8])}/4") 
        print(f"   Complex Queries: {sum(all_results[8:10])}/2")
        print(f"   Error Handling: {sum(all_results[10:])}/{len(all_results[10:])}")
        print(f"   Total Passed: {passed}/{total}")
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
    test_suite = ToolsTestSuite()
    results = await test_suite.run_all_tests()
    
    if results["passed"] == results["total"]:
        print("\n🎉 All tools execution tests passed!")
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