#!/usr/bin/env python3
"""
MCP Client Test Suite Runner

Comprehensive test runner for all MCP client functionality tests.
Executes connection tests, tools tests, and interactive demo tests with detailed reporting.
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Import test suites
from test_connection import ConnectionTestSuite
from test_tools_execution import ToolsTestSuite  
from test_interactive_demo import InteractiveDemoTestSuite

class TestRunner:
    """Comprehensive test runner for all MCP client tests"""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
        self.all_test_results = []
    
    def print_header(self):
        """Print test suite header"""
        print("=" * 80)
        print("🧪 MCP Database Analytics Client - Comprehensive Test Suite")
        print("=" * 80)
        print(f"📅 Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Test Directory: {Path(__file__).parent}")
        print(f"🎯 Target: MCP Server Integration")
        print()
    
    def print_test_category(self, category: str, description: str):
        """Print test category header"""
        print(f"\n{'🔥' if 'connection' in category.lower() else '⚡' if 'tools' in category.lower() else '🎭'} {category}")
        print(f"   {description}")
        print("-" * 60)
    
    async def run_connection_tests(self) -> Dict[str, Any]:
        """Run connection test suite"""
        self.print_test_category("CONNECTION TESTS", "Basic MCP server connectivity and initialization")
        
        test_suite = ConnectionTestSuite()
        results = await test_suite.run_all_tests()
        
        self.results["connection"] = results
        self.all_test_results.extend(results["results"])
        
        return results
    
    async def run_tools_tests(self) -> Dict[str, Any]:
        """Run tools execution test suite"""
        self.print_test_category("TOOLS EXECUTION TESTS", "MCP tools functionality and database operations")
        
        test_suite = ToolsTestSuite()
        results = await test_suite.run_all_tests()
        
        self.results["tools"] = results
        self.all_test_results.extend(results["results"])
        
        return results
    
    async def run_interactive_demo_tests(self) -> Dict[str, Any]:
        """Run interactive demo test suite"""
        self.print_test_category("INTERACTIVE DEMO TESTS", "Demo scenarios and user interface testing")
        
        test_suite = InteractiveDemoTestSuite()
        results = await test_suite.run_all_tests()
        
        self.results["interactive"] = results
        self.all_test_results.extend(results["results"])
        
        return results
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_time = round((time.time() - self.start_time) * 1000, 2)
        
        # Calculate totals
        total_passed = sum(r["passed"] for r in self.results.values())
        total_tests = sum(r["total"] for r in self.results.values()) 
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        # Category breakdown
        for category, results in self.results.items():
            status_icon = "✅" if results["passed"] == results["total"] else "⚠️"
            print(f"{status_icon} {category.upper():20} | {results['passed']:2}/{results['total']:2} | {results['success_rate']:5.1f}% | {results['total_time_ms']:6.1f}ms")
        
        print("-" * 80)
        print(f"📈 OVERALL RESULTS        | {total_passed:2}/{total_tests:2} | {overall_success_rate:5.1f}% | {total_time:6.1f}ms")
        
        # Performance metrics
        print(f"\n⏱️  PERFORMANCE METRICS:")
        print(f"   Total Execution Time: {total_time:,.1f}ms ({total_time/1000:.2f}s)")
        print(f"   Average Test Time: {total_time/total_tests:.1f}ms")
        print(f"   Tests per Second: {total_tests/(total_time/1000):.1f}")
        
        # Quality metrics
        print(f"\n🎯 QUALITY METRICS:")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Test Coverage: {len(self.all_test_results)} individual tests")
        print(f"   Test Categories: {len(self.results)} categories")
        
        # Status assessment
        if overall_success_rate == 100:
            print(f"\n🎉 RESULT: ALL TESTS PASSED - CLIENT READY FOR PRODUCTION")
        elif overall_success_rate >= 90:
            print(f"\n✅ RESULT: TESTS MOSTLY PASSED - CLIENT READY WITH MINOR ISSUES")
        else:
            print(f"\n⚠️  RESULT: SIGNIFICANT FAILURES - CLIENT NEEDS ATTENTION")
        
        print("=" * 80)
    
    def save_test_report(self):
        """Save detailed test report to JSON file"""
        report = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_time_ms": round((time.time() - self.start_time) * 1000, 2),
            "summary": {
                "total_passed": sum(r["passed"] for r in self.results.values()),
                "total_tests": sum(r["total"] for r in self.results.values()),
                "success_rate": sum(r["passed"] for r in self.results.values()) / sum(r["total"] for r in self.results.values()) * 100,
                "categories": len(self.results)
            },
            "categories": self.results,
            "detailed_results": self.all_test_results
        }
        
        report_file = Path(__file__).parent / f"test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved: {report_file.name}")
    
    async def run_all_tests(self) -> bool:
        """Run all test suites and return overall success"""
        self.start_time = time.time()
        self.print_header()
        
        try:
            # Run all test suites
            await self.run_connection_tests()
            await self.run_tools_tests()
            await self.run_interactive_demo_tests()
            
            # Print results
            self.print_summary()
            self.save_test_report()
            
            # Determine overall success
            total_passed = sum(r["passed"] for r in self.results.values())
            total_tests = sum(r["total"] for r in self.results.values())
            
            return total_passed == total_tests
            
        except Exception as e:
            print(f"\n❌ Test suite execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Main entry point"""
    runner = TestRunner()
    success = await runner.run_all_tests()
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1) 