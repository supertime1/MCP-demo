"""
MCP Client for Database Analytics

This module implements the core MCP client that communicates with the
database analytics server using the Model Context Protocol.
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import signal
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import (
    CallToolRequest, CallToolRequestParams, CallToolResult,
    ListToolsRequest, ListToolsResult,
    ListResourcesRequest, ListResourcesResult,
    ReadResourceRequest, ReadResourceRequestParams, ReadResourceResult,
    TextContent, ImageContent
)

from config import ClientConfig

logger = logging.getLogger(__name__)

class MCPAnalyticsClient:
    """MCP client for database analytics server communication"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict] = []
        self.available_resources: List[Dict] = []
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            logger.info("Starting MCP server connection...")
            
            # Validate server exists
            if not ClientConfig.validate_server_exists():
                raise ConnectionError(f"Server script not found: {ClientConfig.get_server_path()}")
            
            # Start server process
            server_path = ClientConfig.get_server_path()
            logger.info(f"Starting server: {server_path}")
            
            # Create server parameters for stdio connection
            self.server_params = StdioServerParameters(
                command=ClientConfig.SERVER_COMMAND,
                args=[str(server_path)],
                env=dict(os.environ)
            )
            
            self.connected = True
            logger.info("MCP client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        try:
            self.connected = False
            self.session = None
            logger.info("Disconnected from MCP server")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def _load_capabilities(self, session: ClientSession):
        """Load available tools and resources from server"""
        try:
            # Load tools
            tools_result = await session.list_tools()
            
            if hasattr(tools_result, 'tools'):
                self.available_tools = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in tools_result.tools
                ]
                logger.info(f"Loaded {len(self.available_tools)} tools")
            
            # Load resources
            resources_result = await session.list_resources()
            
            if hasattr(resources_result, 'resources'):
                self.available_resources = [
                    {
                        "uri": resource.uri,
                        "name": resource.name,
                        "description": resource.description
                    }
                    for resource in resources_result.resources
                ]
                logger.info(f"Loaded {len(self.available_resources)} resources")
                
        except Exception as e:
            logger.error(f"Failed to load capabilities: {e}")
    
    async def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a natural language query by determining the best tool and calling it
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary containing response text and any charts
        """
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
        
        try:
            # Use stdio client to connect to server
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Load capabilities
                    await self._load_capabilities(session)
                    
                    # Simple query routing logic (can be enhanced with LLM)
                    tool_name, arguments = self._route_query(query)
                    
                    if not tool_name:
                        return {
                            "text": "I couldn't understand your query. Please try rephrasing or use 'help' for guidance.",
                            "charts": []
                        }
                    
                    # Execute the tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Parse response
                    return self._parse_tool_response(result)
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "text": f"Error executing query: {str(e)}",
                "charts": []
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call a specific MCP tool"""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
        
        try:
            # Use stdio client to connect to server
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)
                    logger.info(f"Tool '{tool_name}' executed successfully")
                    return result
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise
    
    async def list_tools(self) -> List[Dict]:
        """Get list of available tools"""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
        
        try:
            # Use stdio client to connect to server
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Load capabilities
                    await self._load_capabilities(session)
                    
                    return self.available_tools
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def list_resources(self) -> List[Dict]:
        """Get list of available resources"""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
        
        try:
            # Use stdio client to connect to server
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Load capabilities
                    await self._load_capabilities(session)
                    
                    return self.available_resources
            
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource by URI"""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
        
        try:
            # Use stdio client to connect to server
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Read the resource
                    result = await session.read_resource(uri)
                    
                    if result.contents:
                        return result.contents[0].text
                    else:
                        return "No content found"
                
        except Exception as e:
            logger.error(f"Resource reading failed: {e}")
            return f"Error reading resource: {str(e)}"
    
    def _route_query(self, query: str) -> tuple[Optional[str], Dict[str, Any]]:
        """
        Route natural language query to appropriate MCP tool
        
        This is a simple rule-based router. In a production system,
        this could be enhanced with an LLM or more sophisticated NLP.
        """
        query_lower = query.lower().strip()
        
        # Chart/visualization requests
        if any(word in query_lower for word in ['chart', 'graph', 'plot', 'visualize', 'show']):
            if 'heatmap' in query_lower:
                return self._create_heatmap_query(query)
            elif 'funnel' in query_lower:
                return self._create_funnel_query(query)
            elif 'time' in query_lower or 'daily' in query_lower or 'trend' in query_lower:
                return self._create_time_series_query(query)
            else:
                return self._create_chart_query(query)
        
        # Analytics requests
        elif 'segment' in query_lower or 'segmentation' in query_lower:
            return "user_segmentation", {"segmentation_type": "engagement"}
        
        elif 'conversion' in query_lower or 'funnel' in query_lower:
            return "conversion_funnel", {"funnel_type": "standard"}
        
        elif 'geographic' in query_lower or 'country' in query_lower or 'countries' in query_lower:
            return "geographic_analysis", {"analysis_type": "overview"}
        
        elif 'product' in query_lower or 'category' in query_lower:
            return "product_performance", {"analysis_type": "popularity"}
        
        # Database queries
        elif 'schema' in query_lower or 'table' in query_lower or 'structure' in query_lower:
            return "get_table_schema", {"table_name": ""}
        
        elif 'sample' in query_lower or 'preview' in query_lower or 'example' in query_lower:
            return "get_sample_data", {"table_name": "clickstream", "limit": 5}
        
        # General analysis
        elif any(word in query_lower for word in ['analyze', 'analysis', 'overview', 'summary']):
            return "analyze_user_behavior", {"analysis_type": "overview"}
        
        # Direct SQL (for advanced users)
        elif query.upper().strip().startswith(('SELECT', 'WITH')):
            return "query_database", {"query": query}
        
        # Default fallback
        else:
            return "analyze_user_behavior", {"analysis_type": "overview"}
    
    def _create_chart_query(self, query: str) -> tuple[str, Dict[str, Any]]:
        """Create chart query arguments"""
        query_lower = query.lower()
        
        # Determine chart type
        chart_type = "bar"  # default
        if 'line' in query_lower:
            chart_type = "line"
        elif 'pie' in query_lower:
            chart_type = "pie"
        elif 'scatter' in query_lower:
            chart_type = "scatter"
        elif 'histogram' in query_lower:
            chart_type = "histogram"
        
        # Create data query based on common patterns
        if 'country' in query_lower or 'countries' in query_lower:
            data_query = "SELECT country, COUNT(*) as sessions FROM clickstream GROUP BY country ORDER BY sessions DESC LIMIT 10"
            title = "User Sessions by Country"
        elif 'category' in query_lower:
            data_query = "SELECT page_1_main_category as category, COUNT(*) as views FROM clickstream WHERE page_1_main_category != 'Unknown' GROUP BY page_1_main_category ORDER BY views DESC LIMIT 10"
            title = "Views by Product Category"
        elif 'daily' in query_lower or 'day' in query_lower:
            data_query = "SELECT day, COUNT(*) as sessions FROM clickstream GROUP BY day ORDER BY day"
            title = "Daily User Activity"
        else:
            # Default query
            data_query = "SELECT country, COUNT(*) as sessions FROM clickstream GROUP BY country ORDER BY sessions DESC LIMIT 5"
            title = "Top Countries by Sessions"
        
        return "create_chart", {
            "data_query": data_query,
            "chart_type": chart_type,
            "title": title
        }
    
    def _create_heatmap_query(self, query: str) -> tuple[str, Dict[str, Any]]:
        """Create heatmap query arguments"""
        data_query = """
            SELECT country, page_1_main_category as category, COUNT(*) as interactions
            FROM clickstream 
            WHERE page_1_main_category != 'Unknown'
            GROUP BY country, page_1_main_category
            ORDER BY interactions DESC
            LIMIT 100
        """
        
        return "create_heatmap", {
            "data_query": data_query,
            "title": "User Interactions Heatmap",
            "x_column": "country",
            "y_column": "category",
            "value_column": "interactions"
        }
    
    def _create_funnel_query(self, query: str) -> tuple[str, Dict[str, Any]]:
        """Create funnel chart query arguments"""
        stages_query = """
            SELECT 
                'All Sessions' as stage, COUNT(DISTINCT session_id) as count
            FROM clickstream
            UNION ALL
            SELECT 
                'Product Views' as stage, COUNT(DISTINCT session_id) as count
            FROM clickstream WHERE page_1_main_category != 'Unknown'
            UNION ALL
            SELECT 
                'Multiple Clicks' as stage, COUNT(DISTINCT s.session_id) as count
            FROM (
                SELECT session_id, COUNT(*) as clicks 
                FROM clickstream 
                GROUP BY session_id 
                HAVING clicks > 1
            ) s
            ORDER BY count DESC
        """
        
        return "create_funnel_chart", {
            "stages_query": stages_query,
            "title": "User Engagement Funnel"
        }
    
    def _create_time_series_query(self, query: str) -> tuple[str, Dict[str, Any]]:
        """Create time series query arguments"""
        data_query = """
            SELECT 
                day as date,
                COUNT(*) as activity_count
            FROM clickstream 
            GROUP BY day 
            ORDER BY day
        """
        
        return "create_time_series", {
            "data_query": data_query,
            "title": "Daily Activity Trends",
            "date_column": "date",
            "value_column": "activity_count"
        }
    
    def _parse_tool_response(self, result: CallToolResult) -> Dict[str, Any]:
        """Parse MCP tool response into structured format"""
        response = {
            "text": "",
            "charts": []
        }
        
        try:
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        response["text"] += content.text + "\n"
                    elif isinstance(content, ImageContent):
                        response["charts"].append({
                            "title": "Generated Chart",
                            "data": content.data,
                            "mime_type": content.mimeType
                        })
            
            response["text"] = response["text"].strip()
            
        except Exception as e:
            logger.error(f"Error parsing tool response: {e}")
            response["text"] = f"Error parsing response: {str(e)}"
        
        return response

# Async context manager for easy client usage
class MCPClientContext:
    """Async context manager for MCP client"""
    
    def __init__(self):
        self.client = MCPAnalyticsClient()
    
    async def __aenter__(self):
        await self.client.connect()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect() 