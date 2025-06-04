#!/usr/bin/env python3
"""
Interactive Demo Tests

Tests for the interactive MCP database analytics demo functionality.
This includes menu navigation, user interface, and demo scenario testing.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class InteractiveDemoTestSuite:
    """Test suite for interactive demo functionality"""
    
    def __init__(self):
        self.server_path = Path(__file__).parent.parent.parent / "server" / "main.py"
        self.server_params = StdioServerParameters(
            command="python",
            args=[str(self.server_path)],
        )
        self.results = []
    
    async def test_demo_scenarios(self) -> List[bool]:
        """Test common demo scenarios automatically"""
        print("\n🎭 Testing Demo Scenarios")
        print("-" * 40)
        
        demo_scenarios = [
            {
                "name": "Database Overview Demo",
                "tool": "analyze_user_behavior",
                "args": {"analysis_type": "overview"},
                "description": "Comprehensive database statistics"
            },
            {
                "name": "Geographic Analysis Demo", 
                "tool": "geographic_analysis",
                "args": {"analysis_type": "overview"},
                "description": "Top countries analysis"
            },
            {
                "name": "Product Performance Demo",
                "tool": "product_performance", 
                "args": {"analysis_type": "popularity"},
                "description": "Category popularity analysis"
            },
            {
                "name": "User Segmentation Demo",
                "tool": "user_segmentation",
                "args": {"segmentation_type": "engagement"},
                "description": "User engagement segmentation"
            },
            {
                "name": "Top Countries Query Demo",
                "tool": "query_database",
                "args": {"query": "SELECT country, COUNT(DISTINCT session_id) as unique_sessions, COUNT(*) as total_clicks FROM clickstream GROUP BY country ORDER BY unique_sessions DESC LIMIT 10"},
                "description": "Direct SQL query example"
            }
        ]
        
        test_results = []
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"🎬 Scenario {i}: {scenario['name']}")
            
            try:
                start_time = time.time()
                async with stdio_client(self.server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        result = await session.call_tool(scenario['tool'], scenario['args'])
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        
                        if result.content and len(result.content) > 0:
                            content = result.content[0].text
                            
                            self.results.append({
                                "test": scenario['name'],
                                "status": "PASS",
                                "time_ms": elapsed,
                                "response_length": len(content),
                                "scenario": scenario['description']
                            })
                            
                            print(f"  ✅ Success ({elapsed}ms)")
                            print(f"    {scenario['description']}")
                            print(f"    Response: {len(content)} characters")
                            
                            # Show demo-relevant excerpt
                            lines = content.split('\n')
                            for line in lines[:3]:
                                if line.strip() and not line.startswith('='):
                                    print(f"    📊 {line[:50]}")
                            
                            test_results.append(True)
                        else:
                            raise ValueError("Empty demo response")
                            
            except Exception as e:
                self.results.append({
                    "test": scenario['name'],
                    "status": "FAIL",
                    "error": str(e),
                    "scenario": scenario['description']
                })
                print(f"  ❌ Demo failed: {e}")
                test_results.append(False)
        
        return test_results
    
    async def test_popular_queries(self) -> List[bool]:
        """Test popular demo queries that would be commonly used"""
        print("\n🔥 Testing Popular Demo Queries")
        print("-" * 40)
        
        popular_queries = [
            {
                "name": "Session Length Distribution",
                "query": """
                    SELECT 
                        CASE 
                            WHEN total_clicks = 1 THEN '1 click'
                            WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks'
                            WHEN total_clicks BETWEEN 6 AND 15 THEN '6-15 clicks'
                            ELSE '15+ clicks'
                        END as session_length,
                        COUNT(*) as sessions,
                        ROUND(AVG(total_clicks), 2) as avg_clicks
                    FROM user_sessions
                    GROUP BY 
                        CASE 
                            WHEN total_clicks = 1 THEN '1 click'
                            WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks'
                            WHEN total_clicks BETWEEN 6 AND 15 THEN '6-15 clicks'
                            ELSE '15+ clicks'
                        END
                    ORDER BY sessions DESC
                """
            },
            {
                "name": "Category Performance Analysis",
                "query": """
                    SELECT 
                        page_1_main_category as category,
                        COUNT(*) as views,
                        COUNT(DISTINCT session_id) as unique_viewers,
                        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                    FROM clickstream 
                    WHERE page_1_main_category != 'Unknown'
                    GROUP BY page_1_main_category
                    ORDER BY views DESC
                    LIMIT 8
                """
            },
            {
                "name": "Price Interest Analysis",
                "query": """
                    SELECT 
                        CASE 
                            WHEN price = 0 THEN 'No Price Shown'
                            WHEN price BETWEEN 0.01 AND 50 THEN 'Budget (0-50)'
                            WHEN price BETWEEN 50.01 AND 100 THEN 'Mid-range (50-100)'
                            ELSE 'Premium (100+)'
                        END as price_range,
                        COUNT(*) as views,
                        COUNT(DISTINCT session_id) as unique_viewers
                    FROM clickstream
                    GROUP BY 
                        CASE 
                            WHEN price = 0 THEN 'No Price Shown'
                            WHEN price BETWEEN 0.01 AND 50 THEN 'Budget (0-50)'
                            WHEN price BETWEEN 50.01 AND 100 THEN 'Mid-range (50-100)'
                            ELSE 'Premium (100+)'
                        END
                    ORDER BY views DESC
                """
            }
        ]
        
        test_results = []
        
        for i, query_test in enumerate(popular_queries, 1):
            print(f"🔍 Query {i}: {query_test['name']}")
            
            try:
                start_time = time.time()
                async with stdio_client(self.server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        result = await session.call_tool("query_database", {
                            "query": query_test['query']
                        })
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        
                        if result.content and len(result.content) > 0:
                            content = result.content[0].text
                            
                            self.results.append({
                                "test": f"Popular Query: {query_test['name']}",
                                "status": "PASS",
                                "time_ms": elapsed,
                                "response_length": len(content)
                            })
                            
                            print(f"  ✅ Success ({elapsed}ms)")
                            
                            # Show meaningful results
                            lines = content.split('\n')
                            for line in lines:
                                if '|' in line and not line.startswith('-'):
                                    print(f"    {line}")
                                    break
                            
                            test_results.append(True)
                        else:
                            raise ValueError("Empty query response")
                            
            except Exception as e:
                self.results.append({
                    "test": f"Popular Query: {query_test['name']}",
                    "status": "FAIL",
                    "error": str(e)
                })
                print(f"  ❌ Query failed: {e}")
                test_results.append(False)
        
        return test_results
    
    async def test_schema_resources(self) -> List[bool]:
        """Test database schema and resource access for demos"""
        print("\n📋 Testing Schema Resources")
        print("-" * 40)
        
        test_results = []
        
        # Test 1: Database schema
        print("🔧 Testing Database Schema Access...")
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool("get_table_schema", {"table_name": ""})
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    if result.content and len(result.content) > 0:
                        content = result.content[0].text
                        
                        self.results.append({
                            "test": "Schema Resource Access",
                            "status": "PASS",
                            "time_ms": elapsed,
                            "tables_found": content.count("CREATE TABLE")
                        })
                        
                        print(f"  ✅ Schema retrieved ({elapsed}ms)")
                        print(f"    Found {content.count('CREATE TABLE')} tables")
                        test_results.append(True)
                    else:
                        raise ValueError("Empty schema response")
                        
        except Exception as e:
            self.results.append({
                "test": "Schema Resource Access",
                "status": "FAIL",
                "error": str(e)
            })
            print(f"  ❌ Schema access failed: {e}")
            test_results.append(False)
        
        # Test 2: Sample data for demo
        print("🔧 Testing Sample Data Access...")
        try:
            start_time = time.time()
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool("get_sample_data", {
                        "table_name": "clickstream", 
                        "limit": 3
                    })
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    
                    if result.content and len(result.content) > 0:
                        content = result.content[0].text
                        
                        self.results.append({
                            "test": "Sample Data Access",
                            "status": "PASS",
                            "time_ms": elapsed,
                            "sample_records": 3
                        })
                        
                        print(f"  ✅ Sample data retrieved ({elapsed}ms)")
                        print(f"    3 sample records for demo")
                        test_results.append(True)
                    else:
                        raise ValueError("Empty sample data response")
                        
        except Exception as e:
            self.results.append({
                "test": "Sample Data Access",
                "status": "FAIL",
                "error": str(e)
            })
            print(f"  ❌ Sample data access failed: {e}")
            test_results.append(False)
        
        return test_results
    
    async def run_all_tests(self) -> dict:
        """Run all interactive demo tests"""
        print(f"🎭 Starting Interactive Demo Test Suite")
        print(f"📡 Server: {self.server_path}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        all_results = []
        all_results.extend(await self.test_demo_scenarios())
        all_results.extend(await self.test_popular_queries())
        all_results.extend(await self.test_schema_resources())
        
        # Calculate summary
        total_time = round((time.time() - start_time) * 1000, 2)
        passed = sum(all_results)
        total = len(all_results)
        
        scenario_tests = len(all_results[:5])
        query_tests = len(all_results[5:8])
        resource_tests = len(all_results[8:])
        
        print("\n" + "=" * 60)
        print(f"📊 Interactive Demo Test Results:")
        print(f"   Demo Scenarios: {sum(all_results[:scenario_tests])}/{scenario_tests}")
        print(f"   Popular Queries: {sum(all_results[scenario_tests:scenario_tests+query_tests])}/{query_tests}")
        print(f"   Schema Resources: {sum(all_results[scenario_tests+query_tests:])}/{resource_tests}")
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
    test_suite = InteractiveDemoTestSuite()
    results = await test_suite.run_all_tests()
    
    if results["passed"] == results["total"]:
        print("\n🎉 All interactive demo tests passed!")
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