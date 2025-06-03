#!/usr/bin/env python3
"""
MCP Database Analytics Server - Test Runner
===========================================

This script runs all tests for the MCP Database Analytics Server in sequence
and provides a comprehensive report of the results.

Usage:
    python run_all_tests.py
    python -m tests.run_all_tests
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test functions
from test_initialization import test_server_initialization
from test_mcp_protocol import test_mcp_protocol_functionality  
from test_visualization import test_visualization_functionality

class TestResult:
    """Container for test results"""
    def __init__(self, name: str, success: bool, duration: float, error: str = None):
        self.name = name
        self.success = success
        self.duration = duration
        self.error = error

class TestRunner:
    """Test runner for MCP server tests"""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    async def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a single test function and capture results"""
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        try:
            success = await test_func()
            duration = time.time() - start_time
            
            if success:
                print(f"✅ {test_name} PASSED ({duration:.2f}s)")
                return TestResult(test_name, True, duration)
            else:
                print(f"❌ {test_name} FAILED ({duration:.2f}s)")
                return TestResult(test_name, False, duration, "Test returned False")
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ {test_name} FAILED ({duration:.2f}s)")
            print(f"Error: {str(e)}")
            return TestResult(test_name, False, duration, str(e))
    
    async def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        print("🧪 MCP Database Analytics Server - Test Suite")
        print("=" * 60)
        print(f"Python: {sys.version}")
        print(f"Test directory: {Path(__file__).parent}")
        print(f"Server directory: {Path(__file__).parent.parent}")
        
        # Define tests to run
        tests = [
            (test_server_initialization, "Server Initialization"),
            (test_mcp_protocol_functionality, "MCP Protocol Functionality"),
            (test_visualization_functionality, "Visualization Functionality"),
        ]
        
        # Run all tests
        for test_func, test_name in tests:
            result = await self.run_test(test_func, test_name)
            self.results.append(result)
        
        # Generate final report
        self.print_final_report()
        
        # Return overall success
        return all(result.success for result in self.results)
    
    def print_final_report(self):
        """Print comprehensive test report"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY REPORT")
        print(f"{'='*60}")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)
        
        print(f"Total Tests:     {total_tests}")
        print(f"Passed:          {passed_tests} ✅")
        print(f"Failed:          {failed_tests} ❌")
        print(f"Success Rate:    {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Duration:  {total_duration:.2f}s")
        
        print(f"\nDETAILED RESULTS:")
        print("-" * 60)
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{result.name:<30} {status:<8} {result.duration:>6.2f}s")
            if result.error and not result.success:
                print(f"    Error: {result.error}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! Server is ready for production.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please review the errors above.")
        
        print(f"\nNext Steps:")
        if failed_tests == 0:
            print("  ✅ Server testing complete")
            print("  🔄 Ready for MCP client implementation")
            print("  🚀 Ready for demo script development")
        else:
            print("  🔧 Fix failing tests")
            print("  🔄 Re-run test suite")
            print("  📋 Review error messages above")

async def main():
    """Main entry point for test runner"""
    runner = TestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 