"""
Main MCP Server for Database Analytics Demo

This is the primary entry point for the MCP server that provides database analytics
and visualization capabilities for e-commerce user behavior data.
"""

import asyncio
import logging
from typing import Any, Sequence
import json

from mcp.server.lowlevel import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
)

# Import our tool modules
from database_tools import get_database_tools, query_database, get_table_schema, get_sample_data, analyze_user_behavior
from analytics_tools import get_analytics_tools, user_segmentation, conversion_funnel, geographic_analysis, product_performance
from visualization_tools import get_visualization_tools, VisualizationTools
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("database-analytics-server")

# Initialize visualization tools instance
viz_tools = VisualizationTools()

@server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """List available resources (database schema information)."""
    return ListResourcesResult(
        resources=[
            Resource(
                uri="schema://database",
                name="Database Schema",
                description="Complete schema information for the e-commerce database",
                mimeType="text/plain",
            ),
            Resource(
                uri="schema://tables",
                name="Table List",
                description="List of all available database tables",
                mimeType="text/plain",
            ),
            Resource(
                uri="config://popular_queries",
                name="Popular Queries",
                description="Pre-built popular queries for common analytics tasks",
                mimeType="application/json",
            ),
        ]
    )

@server.read_resource()
async def handle_read_resource(request: ReadResourceRequest) -> ReadResourceResult:
    """Handle resource reading requests."""
    try:
        if request.uri == "schema://database":
            schema_info = await get_table_schema("")
            return ReadResourceResult(contents=[TextContent(type="text", text=schema_info)])
        
        elif request.uri == "schema://tables":
            # Get list of tables
            from database_tools import DatabaseService
            db_service = DatabaseService.get_instance()
            db_connection = db_service.get_connection()
            
            result = db_connection.execute_query("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            
            table_list = [row[0] for row in result.data]
            table_info = f"Available Tables ({len(table_list)}):\n" + "\n".join(f"• {table}" for table in table_list)
            
            return ReadResourceResult(contents=[TextContent(type="text", text=table_info)])
        
        elif request.uri == "config://popular_queries":
            queries_json = json.dumps(Config.POPULAR_QUERIES, indent=2)
            return ReadResourceResult(contents=[TextContent(type="text", text=queries_json)])
        
        else:
            raise ValueError(f"Unknown resource: {request.uri}")
    
    except Exception as e:
        logger.error(f"Resource reading failed: {e}")
        return ReadResourceResult(
            contents=[TextContent(type="text", text=f"Error reading resource: {str(e)}")]
        )

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List all available tools."""
    all_tools = []
    
    # Add database tools
    all_tools.extend(get_database_tools())
    
    # Add analytics tools
    all_tools.extend(get_analytics_tools())
    
    # Add visualization tools
    all_tools.extend(get_visualization_tools())
    
    logger.info(f"Listing {len(all_tools)} available tools")
    return ListToolsResult(tools=all_tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list:
    """Handle tool execution requests."""
    try:
        logger.info(f"Executing tool: {name} with args: {arguments}")
        
        # Database Tools
        if name == "query_database":
            result = await query_database(arguments.get("query", ""))
            return [TextContent(type="text", text=result)]
        
        elif name == "get_table_schema":
            result = await get_table_schema(arguments.get("table_name", ""))
            return [TextContent(type="text", text=result)]
        
        elif name == "get_sample_data":
            result = await get_sample_data(
                arguments.get("table_name", ""),
                arguments.get("limit", 5)
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "analyze_user_behavior":
            result = await analyze_user_behavior(arguments.get("analysis_type", "overview"))
            return [TextContent(type="text", text=result)]
        
        # Analytics Tools
        elif name == "user_segmentation":
            result = await user_segmentation(arguments.get("segmentation_type", "engagement"))
            return [TextContent(type="text", text=result)]
        
        elif name == "conversion_funnel":
            result = await conversion_funnel(arguments.get("funnel_type", "standard"))
            return [TextContent(type="text", text=result)]
        
        elif name == "geographic_analysis":
            result = await geographic_analysis(arguments.get("analysis_type", "overview"))
            return [TextContent(type="text", text=result)]
        
        elif name == "product_performance":
            result = await product_performance(arguments.get("analysis_type", "popularity"))
            return [TextContent(type="text", text=result)]
        
        # Visualization Tools
        elif name == "create_chart":
            result = await viz_tools.create_chart(
                data_query=arguments.get("data_query", ""),
                chart_type=arguments.get("chart_type", "bar"),
                title=arguments.get("title", "Chart"),
                x_column=arguments.get("x_column"),
                y_column=arguments.get("y_column"),
                aggregation=arguments.get("aggregation", "sum"),
                limit=arguments.get("limit", 20)
            )
            return result
        
        elif name == "create_heatmap":
            result = await viz_tools.create_heatmap(
                data_query=arguments.get("data_query", ""),
                title=arguments.get("title", "Heatmap"),
                x_column=arguments.get("x_column"),
                y_column=arguments.get("y_column"),
                value_column=arguments.get("value_column"),
                aggregation=arguments.get("aggregation", "sum"),
                colormap=arguments.get("colormap", "YlOrRd")
            )
            return result
        
        elif name == "create_funnel_chart":
            result = await viz_tools.create_funnel_chart(
                stages_query=arguments.get("stages_query", ""),
                title=arguments.get("title", "Conversion Funnel"),
                stage_column=arguments.get("stage_column", "stage"),
                value_column=arguments.get("value_column", "count")
            )
            return result
        
        elif name == "create_time_series":
            result = await viz_tools.create_time_series(
                data_query=arguments.get("data_query", ""),
                title=arguments.get("title", "Time Series"),
                date_column=arguments.get("date_column", "date"),
                value_column=arguments.get("value_column", "value"),
                groupby_column=arguments.get("groupby_column")
            )
            return result
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error executing tool '{name}': {str(e)}")]

async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Database Analytics MCP Server...")
    logger.info(f"Database path: {Config.DATABASE_PATH}")
    
    # Count available tools
    total_tools = len(get_database_tools() + get_analytics_tools() + get_visualization_tools())
    logger.info(f"Available tools: {total_tools}")
    
    # Verify database connection
    try:
        from database_tools import DatabaseService
        db_service = DatabaseService.get_instance()
        db_connection = db_service.get_connection()
        
        # Test connection with a simple query
        result = db_connection.execute_query("SELECT COUNT(*) as total_records FROM clickstream LIMIT 1")
        total_records = result.data[0][0] if result.data else 0
        logger.info(f"Database connected successfully - {total_records:,} records available")
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Server may not function properly without database access")
    
    # Import the correct server module
    import mcp.server.stdio
    from mcp.server.models import InitializationOptions
    from mcp.server.lowlevel import NotificationOptions
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server is running and ready for connections")
        logger.info("Server capabilities: resources=True, tools=True, prompts=False")
        
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="database-analytics-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    """
    Run the MCP server.
    
    This server provides:
    - Database query execution with safety controls
    - Pre-built analytics for user behavior analysis
    - Advanced visualization capabilities
    - Resource access to schema information
    
    Usage:
        python server/main.py
    
    The server runs on stdio transport and communicates via JSON-RPC.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise 