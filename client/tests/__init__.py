"""
MCP Database Analytics Client Tests

This package contains comprehensive tests for the MCP client functionality,
including connection tests, tool execution tests, and interactive demo tests.

Test Categories:
- Connection: Basic MCP server connectivity and initialization
- Tools: MCP tool execution and functionality
- Integration: End-to-end testing with server
- Interactive: User interface and demo testing
"""

__version__ = "1.0.0"
__author__ = "MCP Database Analytics Team"

# Test categories
TEST_CATEGORIES = {
    "connection": "Basic connectivity and initialization tests",
    "tools": "MCP tool execution and functionality tests", 
    "integration": "End-to-end integration with server",
    "interactive": "User interface and demo tests"
}

# Test configuration
TEST_CONFIG = {
    "server_timeout": 30,
    "max_retries": 3,
    "test_database": "../server/ecommerce_behavior.db"
} 