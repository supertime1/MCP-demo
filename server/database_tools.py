"""
Database Tools for MCP Database Analytics Demo

This module provides MCP tools for safe database operations including
queries, schema inspection, and user behavior analysis.
"""

import logging
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from mcp.types import Tool
from pydantic import BaseModel

from config import Config

logger = logging.getLogger(__name__)

class QueryResult(BaseModel):
    """Result structure for database queries"""
    columns: List[str]
    data: List[List[Any]]
    row_count: int
    execution_time_ms: float

class DatabaseConnection:
    """Database connection handler with safety controls"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> QueryResult:
        """Execute a database query with safety checks and timing"""
        start_time = time.time()
        
        # Safety check
        if not self._is_safe_query(query):
            raise ValueError("Query contains unsafe operations. Only SELECT, WITH, and EXPLAIN are allowed.")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchall()
            
            conn.close()
            
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                columns=columns,
                data=rows,
                row_count=len(rows),
                execution_time_ms=round(execution_time, 2)
            )
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise Exception(f"Database error: {str(e)}")
    
    def _is_safe_query(self, query: str) -> bool:
        """Check if query is safe (read-only operations only)"""
        query_upper = query.upper().strip()
        
        # Allow only SELECT, WITH, and EXPLAIN statements
        safe_starts = ('SELECT', 'WITH', 'EXPLAIN')
        
        # Block dangerous keywords
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
            'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE', 'PRAGMA'
        ]
        
        if not any(query_upper.startswith(start) for start in safe_starts):
            return False
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        return True
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes_info = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            conn.close()
            
            columns = []
            for col in columns_info:
                columns.append({
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                })
            
            indexes = [idx[1] for idx in indexes_info]
            
            return {
                'table_name': table_name,
                'columns': columns,
                'indexes': indexes,
                'row_count': row_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            raise Exception(f"Table info error: {str(e)}")

class DatabaseService:
    """Service class for database operations with lazy initialization"""
    
    _instance: Optional['DatabaseService'] = None
    _connection: Optional[DatabaseConnection] = None
    
    @classmethod
    def get_instance(cls) -> 'DatabaseService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_connection(self) -> DatabaseConnection:
        if self._connection is None:
            db_path = Path(Config.DATABASE_PATH)
            if not db_path.exists():
                raise FileNotFoundError(f"Database not found at {db_path}")
            self._connection = DatabaseConnection(db_path)
        return self._connection
    
    def reset_connection(self) -> None:
        """Reset connection for testing or config changes"""
        self._connection = None

class DatabaseTools:
    """Collection of database tools for the MCP server."""
    
    def __init__(self):
        self.db_service = DatabaseService.get_instance()
    
    def _format_query_result(self, result: QueryResult) -> str:
        """Format query results for display"""
        output = []
        output.append(f"Query executed successfully in {result.execution_time_ms}ms")
        output.append(f"Returned {result.row_count} rows")
        output.append("")
        
        if result.row_count == 0:
            output.append("No results found.")
            return "\n".join(output)
        
        # Format as table
        if result.columns and result.data:
            # Create header
            header = " | ".join(f"{col:15}" for col in result.columns)
            output.append(header)
            output.append("-" * len(header))
            
            # Add data rows (limit to 50 for readability)
            for i, row in enumerate(result.data[:50]):
                formatted_row = " | ".join(f"{str(val):15}" for val in row)
                output.append(formatted_row)
            
            if result.row_count > 50:
                output.append(f"... ({result.row_count - 50} more rows)")
        
        return "\n".join(output)

    async def query_database(self, query: str) -> str:
        """
        Execute SQL queries on the e-commerce database.
        Only SELECT, WITH, and EXPLAIN queries are allowed for safety.
        """
        try:
            if not query.strip():
                return "Error: Empty query provided"
            
            db_connection = self.db_service.get_connection()
            result = db_connection.execute_query(query)
            
            return self._format_query_result(result)
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return f"Error executing query: {str(e)}"

    async def get_table_schema(self, table_name: str = "") -> str:
        """
        Get schema information for database tables.
        Shows columns, types, constraints, and indexes.
        """
        try:
            db_connection = self.db_service.get_connection()
            
            # If no table specified, list all tables
            if not table_name.strip():
                result = db_connection.execute_query("""
                    SELECT name, type, sql 
                    FROM sqlite_master 
                    WHERE type IN ('table', 'view')
                    ORDER BY type, name
                """)
                
                output = ["📋 Database Schema Overview"]
                output.append("=" * 30)
                output.append(f"Found {result.row_count} tables/views\n")
                
                for row in result.data:
                    name, obj_type, sql = row
                    output.append(f"🔸 {obj_type.upper()}: {name}")
                    if sql:
                        # Show just the table structure, not full SQL
                        if "CREATE TABLE" in sql:
                            lines = sql.split('\n')
                            output.append(f"   Structure: {lines[0][:60]}...")
                    output.append("")
                
                return "\n".join(output)
            
            # Get specific table information
            table_info = db_connection.get_table_info(table_name)
            
            output = []
            output.append(f"📋 Table Schema: {table_name}")
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

    async def get_sample_data(self, table_name: str, limit: int = 5) -> str:
        """
        Get sample data from a specified table.
        Shows first few rows to preview the data structure.
        """
        try:
            if limit <= 0 or limit > 50:
                limit = 5
            
            db_connection = self.db_service.get_connection()
            
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

    async def analyze_user_behavior(self, analysis_type: str = "overview") -> str:
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
            
            db_connection = self.db_service.get_connection()
            
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
def get_database_tools() -> List[Tool]:
    """Return list of database tools for MCP server."""
    return [
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
                        "maximum": 50,
                        "default": 5
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
                        "enum": ["overview", "countries_by_sessions", "top_products", "category_performance", "session_length_distribution", "daily_activity"],
                        "default": "overview"
                    }
                }
            }
        )
    ]

# Create global database tools instance for backward compatibility
_database_tools = None

def get_database_service() -> DatabaseTools:
    """Get or create the global database tools instance."""
    global _database_tools
    if _database_tools is None:
        _database_tools = DatabaseTools()
    return _database_tools

# Wrapper functions for backward compatibility with main.py
async def query_database(query: str) -> str:
    return await get_database_service().query_database(query)

async def get_table_schema(table_name: str = "") -> str:
    return await get_database_service().get_table_schema(table_name)

async def get_sample_data(table_name: str, limit: int = 5) -> str:
    return await get_database_service().get_sample_data(table_name, limit)

async def analyze_user_behavior(analysis_type: str = "overview") -> str:
    return await get_database_service().analyze_user_behavior(analysis_type)

# Export the tools list for backward compatibility
DATABASE_TOOLS = get_database_tools() 