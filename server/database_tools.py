"""
Database Tools for E-commerce Analytics MCP Server
Provides safe database query capabilities and schema inspection
"""

import sqlite3
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from .config import Config

logger = logging.getLogger(__name__)

class QueryResult(BaseModel):
    """Result structure for database queries"""
    columns: List[str]
    data: List[List[Any]]
    row_count: int
    execution_time_ms: float

class DatabaseConnection:
    """Thread-safe database connection manager"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.timeout = Config.DATABASE_TIMEOUT
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> QueryResult:
        """Execute a query safely with timeout and result limits"""
        import time
        start_time = time.time()
        
        if not self._is_safe_query(query):
            raise ValueError("Query contains potentially unsafe operations")
        
        try:
            with sqlite3.connect(self.db_path, timeout=self.timeout) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Get column names
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Fetch results with limit
                if query.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchmany(Config.MAX_QUERY_RESULTS)
                    if len(rows) == Config.MAX_QUERY_RESULTS:
                        logger.warning(f"Query result truncated to {Config.MAX_QUERY_RESULTS} rows")
                else:
                    rows = []
                
                execution_time = (time.time() - start_time) * 1000
                
                # Convert rows to list format
                data = [list(row) for row in rows]
                
                return QueryResult(
                    columns=columns,
                    data=data,
                    row_count=len(data),
                    execution_time_ms=round(execution_time, 2)
                )
                
        except sqlite3.Error as e:
            logger.error(f"Database query failed: {e}")
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in query execution: {e}")
            raise
    
    def _is_safe_query(self, query: str) -> bool:
        """Check if query contains only safe operations"""
        query_upper = query.upper().strip()
        
        # Allow only SELECT, WITH (for CTEs), and EXPLAIN
        allowed_starts = ['SELECT', 'WITH', 'EXPLAIN']
        if not any(query_upper.startswith(start) for start in allowed_starts):
            return False
        
        # Disallow dangerous keywords
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
            'TRUNCATE', 'REPLACE', 'PRAGMA', 'ATTACH', 'DETACH'
        ]
        
        for keyword in dangerous_keywords:
            if re.search(r'\b' + keyword + r'\b', query_upper):
                return False
        
        return True
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # Get indexes
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                
                return {
                    "table_name": table_name,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "not_null": bool(col[3]),
                            "default_value": col[4],
                            "primary_key": bool(col[5])
                        }
                        for col in columns
                    ],
                    "row_count": row_count,
                    "indexes": [idx[1] for idx in indexes]
                }
        except sqlite3.Error as e:
            raise ValueError(f"Failed to get table info: {str(e)}")

class DatabaseService:
    """Service class for database operations with lazy initialization"""
    
    _instance: Optional['DatabaseService'] = None
    _connection: Optional[DatabaseConnection] = None
    
    @classmethod
    def get_instance(cls) -> 'DatabaseService':
        """Get singleton instance with lazy initialization"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_connection(self) -> DatabaseConnection:
        """Get database connection with lazy initialization"""
        if self._connection is None:
            if not Config.validate_database():
                raise ValueError(f"Database not found at {Config.DATABASE_PATH}")
            self._connection = DatabaseConnection(Config.DATABASE_PATH)
        return self._connection
    
    def reset_connection(self) -> None:
        """Reset connection (useful for testing)"""
        self._connection = None

# Tool Functions
async def query_database(query: str) -> str:
    """
    Execute a SQL query on the e-commerce database.
    Only SELECT, WITH, and EXPLAIN queries are allowed for safety.
    Results are limited to prevent overwhelming responses.
    """
    try:
        if not query.strip():
            return "Error: Empty query provided"
        
        db_service = DatabaseService.get_instance()
        db_connection = db_service.get_connection()
        result = db_connection.execute_query(query)
        
        # Format results for display
        if result.row_count == 0:
            return f"Query executed successfully but returned no results.\nExecution time: {result.execution_time_ms}ms"
        
        # Create formatted table
        output = []
        output.append(f"Query Results ({result.row_count} rows, {result.execution_time_ms}ms):")
        output.append("=" * 60)
        
        # Add header
        header = " | ".join(f"{col:12}" for col in result.columns)
        output.append(header)
        output.append("-" * len(header))
        
        # Add data rows (limit display for readability)
        display_limit = min(20, result.row_count)
        for i, row in enumerate(result.data[:display_limit]):
            formatted_row = " | ".join(f"{str(val):12}" for val in row)
            output.append(formatted_row)
        
        if result.row_count > display_limit:
            output.append(f"... ({result.row_count - display_limit} more rows)")
        
        if result.row_count == Config.MAX_QUERY_RESULTS:
            output.append(f"\n⚠️  Results truncated at {Config.MAX_QUERY_RESULTS} rows")
        
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return f"Error executing query: {str(e)}"

async def get_table_schema(table_name: str = "") -> str:
    """
    Get schema information for database tables.
    If no table_name provided, lists all tables.
    """
    try:
        db_service = DatabaseService.get_instance()
        db_connection = db_service.get_connection()
        
        if not table_name:
            # List all tables
            result = db_connection.execute_query("""
                SELECT name, type FROM sqlite_master 
                WHERE type IN ('table', 'view')
                ORDER BY name
            """)
            
            output = ["Available Tables and Views:"]
            output.append("=" * 30)
            for row in result.data:
                output.append(f"📋 {row[0]} ({row[1]})")
            
            return "\n".join(output)
        
        else:
            # Get specific table info
            table_info = db_connection.get_table_info(table_name)
            
            output = [f"Table: {table_info['table_name']}"]
            output.append(f"Rows: {table_info['row_count']:,}")
            output.append("=" * 40)
            output.append("\nColumns:")
            
            for col in table_info['columns']:
                pk_marker = " (PK)" if col['primary_key'] else ""
                null_marker = " NOT NULL" if col['not_null'] else ""
                default_info = f" DEFAULT {col['default_value']}" if col['default_value'] else ""
                
                output.append(f"  • {col['name']}: {col['type']}{pk_marker}{null_marker}{default_info}")
            
            if table_info['indexes']:
                output.append("\nIndexes:")
                for idx in table_info['indexes']:
                    output.append(f"  • {idx}")
            
            return "\n".join(output)
            
    except Exception as e:
        logger.error(f"Schema inspection failed: {e}")
        return f"Error getting table schema: {str(e)}"

async def get_sample_data(table_name: str, limit: int = 5) -> str:
    """
    Get sample data from a specified table.
    Shows first few rows to preview the data structure.
    """
    try:
        if limit <= 0 or limit > 50:
            limit = 5
        
        db_service = DatabaseService.get_instance()
        db_connection = db_service.get_connection()
        
        # Validate table name exists
        table_check = db_connection.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        if table_check.row_count == 0:
            return f"Error: Table '{table_name}' not found"
        
        # Get sample data
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        result = db_connection.execute_query(query)
        
        if result.row_count == 0:
            return f"Table '{table_name}' exists but contains no data"
        
        # Format output
        output = [f"Sample data from '{table_name}' (showing {result.row_count} rows):"]
        output.append("=" * 60)
        
        # Show each row with column names
        for i, row in enumerate(result.data, 1):
            output.append(f"\nRow {i}:")
            for col_name, value in zip(result.columns, row):
                output.append(f"  {col_name}: {value}")
        
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Sample data retrieval failed: {e}")
        return f"Error getting sample data: {str(e)}"

async def analyze_user_behavior(analysis_type: str = "overview") -> str:
    """
    Run pre-built analytics queries for common user behavior insights.
    
    Analysis types:
    - overview: Basic dataset statistics
    - countries: Country-wise session analysis  
    - products: Product performance metrics
    - categories: Category popularity analysis
    - sessions: Session length distribution
    - daily: Daily activity patterns
    """
    try:
        if analysis_type not in Config.POPULAR_QUERIES and analysis_type != "overview":
            available = ", ".join(list(Config.POPULAR_QUERIES.keys()) + ["overview"])
            return f"Invalid analysis type. Available options: {available}"
        
        db_service = DatabaseService.get_instance()
        db_connection = db_service.get_connection()
        
        if analysis_type == "overview":
            # Basic overview statistics
            query = """
            SELECT 
                'Total Clicks' as metric, COUNT(*) as value FROM clickstream
            UNION ALL
            SELECT 
                'Unique Sessions', COUNT(DISTINCT session_id) FROM clickstream
            UNION ALL
            SELECT 
                'Countries', COUNT(DISTINCT country) FROM clickstream
            UNION ALL
            SELECT 
                'Product Categories', COUNT(DISTINCT page_1_main_category) 
                FROM clickstream WHERE page_1_main_category != 'Unknown'
            UNION ALL
            SELECT 
                'Unique Products', COUNT(DISTINCT page_2_clothing_model) 
                FROM clickstream WHERE page_2_clothing_model != 'Unknown'
            """
            title = "E-commerce Dataset Overview"
        else:
            query = Config.POPULAR_QUERIES[analysis_type]
            title = f"User Behavior Analysis: {analysis_type.replace('_', ' ').title()}"
        
        result = db_connection.execute_query(query)
        
        # Format results
        output = [title]
        output.append("=" * len(title))
        output.append(f"Generated: {result.execution_time_ms}ms\n")
        
        if result.row_count == 0:
            output.append("No data found for this analysis.")
        else:
            # Create formatted table
            header = " | ".join(f"{col:15}" for col in result.columns)
            output.append(header)
            output.append("-" * len(header))
            
            for row in result.data:
                formatted_row = " | ".join(f"{str(val):15}" for val in row)
                output.append(formatted_row)
        
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"User behavior analysis failed: {e}")
        return f"Error in analysis: {str(e)}"

# Define MCP tools
DATABASE_TOOLS = [
    Tool(
        name="query_database",
        description="Execute SQL queries on the e-commerce database. Only SELECT, WITH, and EXPLAIN queries allowed.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT statements only)"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_table_schema",
        description="Get schema information for database tables. Shows columns, types, and constraints.",
        inputSchema={
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of table to inspect (empty to list all tables)"
                }
            }
        }
    ),
    Tool(
        name="get_sample_data",
        description="Get sample data from a specified table to preview its contents.",
        inputSchema={
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Name of table to sample"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of rows to return (1-50, default 5)",
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": ["table_name"]
        }
    ),
    Tool(
        name="analyze_user_behavior",
        description="Run pre-built analytics for common user behavior insights.",
        inputSchema={
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis: overview, countries_by_sessions, top_products, category_performance, session_length_distribution, daily_activity",
                    "enum": ["overview", "countries_by_sessions", "top_products", "category_performance", "session_length_distribution", "daily_activity"]
                }
            }
        }
    )
] 