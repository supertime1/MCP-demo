"""
Configuration settings for the E-commerce Analytics MCP Server
"""

import os
import logging
from pathlib import Path
from typing import Optional

class Config:
    """Configuration class for MCP server settings"""
    
    # Server Information
    SERVER_NAME = "ecommerce-analytics"
    SERVER_VERSION = "1.0.0"
    SERVER_DESCRIPTION = "E-commerce User Behavior Analytics MCP Server"
    
    # Database Configuration
    DATABASE_PATH = Path(__file__).parent.parent / "data" / "ecommerce.db"
    DATABASE_TIMEOUT = 30  # seconds
    
    # Query Limits (for safety)
    MAX_QUERY_RESULTS = 10000
    QUERY_TIMEOUT = 30  # seconds
    
    # Visualization Settings
    CHART_OUTPUT_DIR = Path(__file__).parent / "charts"
    CHART_WIDTH = 800
    CHART_HEIGHT = 600
    CHART_DPI = 100
    
    # Supported chart types
    SUPPORTED_CHART_TYPES = [
        "bar", "horizontal_bar", "line", "pie", 
        "scatter", "histogram", "heatmap", "funnel"
    ]
    
    # Logging Configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # MCP Server Settings
    MCP_SERVER_HOST = "localhost"
    MCP_SERVER_PORT = 8080
    
    # Analytics Presets
    POPULAR_QUERIES = {
        "countries_by_sessions": """
            SELECT country, COUNT(*) as sessions, 
                   AVG(total_clicks) as avg_clicks_per_session
            FROM user_sessions 
            GROUP BY country 
            ORDER BY sessions DESC 
            LIMIT 10
        """,
        "top_products": """
            SELECT product_code, category, total_views, unique_sessions
            FROM product_analytics 
            ORDER BY total_views DESC 
            LIMIT 20
        """,
        "category_performance": """
            SELECT page_1_main_category as category,
                   COUNT(*) as total_views,
                   COUNT(DISTINCT session_id) as unique_sessions,
                   COUNT(DISTINCT country) as countries
            FROM clickstream 
            WHERE page_1_main_category != 'Unknown'
            GROUP BY page_1_main_category 
            ORDER BY total_views DESC
        """,
        "daily_activity": """
            SELECT day, COUNT(*) as clicks, 
                   COUNT(DISTINCT session_id) as sessions
            FROM clickstream 
            GROUP BY day 
            ORDER BY day
        """,
        "session_length_distribution": """
            SELECT 
                CASE 
                    WHEN total_clicks = 1 THEN '1 click'
                    WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks'
                    WHEN total_clicks BETWEEN 6 AND 10 THEN '6-10 clicks'
                    WHEN total_clicks BETWEEN 11 AND 20 THEN '11-20 clicks'
                    ELSE '20+ clicks'
                END as session_length,
                COUNT(*) as session_count
            FROM user_sessions
            GROUP BY 
                CASE 
                    WHEN total_clicks = 1 THEN '1 click'
                    WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks'
                    WHEN total_clicks BETWEEN 6 AND 10 THEN '6-10 clicks'
                    WHEN total_clicks BETWEEN 11 AND 20 THEN '11-20 clicks'
                    ELSE '20+ clicks'
                END
            ORDER BY session_count DESC
        """
    }
    
    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    Path(__file__).parent / "mcp_server.log",
                    mode='a'
                )
            ]
        )
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories"""
        cls.CHART_OUTPUT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_database(cls) -> bool:
        """Check if database exists and is accessible"""
        return cls.DATABASE_PATH.exists() and cls.DATABASE_PATH.is_file()
    
    @classmethod
    def get_database_uri(cls) -> str:
        """Get database URI for SQLite connection"""
        return f"sqlite:///{cls.DATABASE_PATH}"

# Environment-specific overrides
if os.getenv("MCP_ENV") == "development":
    Config.LOG_LEVEL = logging.DEBUG
    Config.MAX_QUERY_RESULTS = 100  # Smaller limit for dev

if os.getenv("MCP_ENV") == "production":
    Config.LOG_LEVEL = logging.WARNING
    Config.QUERY_TIMEOUT = 15  # Shorter timeout for prod 