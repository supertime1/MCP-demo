"""
Configuration settings for the MCP Database Analytics Client
"""

import os
from pathlib import Path
from typing import Optional

class ClientConfig:
    """Configuration class for MCP client settings"""
    
    # Client Information
    CLIENT_NAME = "database-analytics-client"
    CLIENT_VERSION = "1.0.0"
    CLIENT_DESCRIPTION = "E-commerce Analytics MCP Client"
    
    # Server Connection
    SERVER_COMMAND = "python"
    SERVER_SCRIPT = "../server/main.py"
    SERVER_TIMEOUT = 30  # seconds
    
    # UI Settings
    PROMPT_STYLE = "bold blue"
    ERROR_STYLE = "bold red"
    SUCCESS_STYLE = "bold green"
    INFO_STYLE = "dim white"
    
    # Chart Display
    CHART_DISPLAY_METHOD = "matplotlib"  # or "plotly" or "both"
    CHART_SAVE_DIR = Path(__file__).parent / "charts"
    CHART_DPI = 150
    CHART_FIGSIZE = (10, 6)
    
    # Query History
    HISTORY_FILE = Path(__file__).parent / ".query_history"
    MAX_HISTORY_SIZE = 100
    
    # Response Limits
    MAX_RESPONSE_LENGTH = 5000  # characters
    MAX_CHART_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Suggested Queries
    SAMPLE_QUERIES = [
        "Show me the top 5 countries by user sessions",
        "Create a chart of daily user activity trends",
        "Analyze conversion funnel for e-commerce",
        "What are the most popular product categories?",
        "Show user segmentation by behavior patterns",
        "Create a heatmap of user activity by country and category",
        "Analyze geographic distribution of users",
        "Show session length distribution",
        "What's the average session duration by country?",
        "Create a funnel chart for user journey analysis"
    ]
    
    # Error Messages
    ERROR_MESSAGES = {
        "connection_failed": "❌ Failed to connect to MCP server. Is the server running?",
        "server_timeout": "⏰ Server request timed out. Please try again.",
        "invalid_query": "❓ Invalid query format. Please try rephrasing your question.",
        "no_data": "📊 No data returned for your query.",
        "chart_error": "📈 Error generating chart. Please check your query.",
        "server_error": "🔧 Server error occurred. Please check server logs."
    }
    
    @classmethod
    def setup_directories(cls) -> None:
        """Create necessary directories"""
        cls.CHART_SAVE_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_server_path(cls) -> Path:
        """Get absolute path to server script"""
        return (Path(__file__).parent / cls.SERVER_SCRIPT).resolve()
    
    @classmethod
    def validate_server_exists(cls) -> bool:
        """Check if server script exists"""
        return cls.get_server_path().exists()

# Environment-specific overrides
if os.getenv("MCP_CLIENT_ENV") == "development":
    ClientConfig.SERVER_TIMEOUT = 60
    ClientConfig.MAX_RESPONSE_LENGTH = 10000

if os.getenv("MCP_CLIENT_ENV") == "demo":
    ClientConfig.CHART_DISPLAY_METHOD = "both"
    ClientConfig.CHART_DPI = 200 