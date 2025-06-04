#!/usr/bin/env python3
"""
MCP Database Analytics Client - Main Entry Point

This is the main application that provides a natural language interface
for querying e-commerce analytics data through the MCP server.

Usage:
    python main.py
    python -m client.main
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional
import signal

import click
from rich.console import Console
from rich.logging import RichHandler

from config import ClientConfig
from mcp_client import MCPAnalyticsClient, MCPClientContext
from chat_interface import ChatInterface

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()

class AnalyticsClientApp:
    """Main application class for the MCP analytics client"""
    
    def __init__(self):
        self.mcp_client: Optional[MCPAnalyticsClient] = None
        self.chat_interface: Optional[ChatInterface] = None
        self.running = False
    
    async def start(self, interactive: bool = True):
        """Start the analytics client application"""
        try:
            console.print("🚀 Starting MCP Database Analytics Client...", style="bold blue")
            
            # Setup directories
            ClientConfig.setup_directories()
            
            # Validate server exists
            if not ClientConfig.validate_server_exists():
                console.print(
                    f"❌ Server script not found: {ClientConfig.get_server_path()}",
                    style="bold red"
                )
                console.print("💡 Make sure you're running from the correct directory", style="yellow")
                return False
            
            # Connect to MCP server
            console.print("🔌 Connecting to MCP server...", style="yellow")
            
            async with MCPClientContext() as client:
                self.mcp_client = client
                
                if not client.connected:
                    console.print("❌ Failed to connect to MCP server", style="bold red")
                    return False
                
                console.print("✅ Connected to MCP server successfully!", style="bold green")
                
                # Show server capabilities
                await self._show_server_info()
                
                if interactive:
                    # Start interactive chat interface
                    self.chat_interface = ChatInterface(client)
                    
                    # Setup signal handlers
                    self._setup_signal_handlers()
                    
                    # Start chat session
                    self.running = True
                    self.chat_interface.start_session()
                
                return True
                
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!", style="bold blue")
            return True
        except Exception as e:
            console.print(f"❌ Application error: {str(e)}", style="bold red")
            logger.exception("Application failed")
            return False
    
    async def _show_server_info(self):
        """Display server capabilities and status"""
        try:
            tools = await self.mcp_client.list_tools()
            resources = await self.mcp_client.list_resources()
            
            console.print(f"\n📊 Server Status:", style="bold green")
            console.print(f"  • Available tools: {len(tools)}")
            console.print(f"  • Available resources: {len(resources)}")
            console.print(f"  • Database: 165,474 e-commerce records")
            console.print()
            
        except Exception as e:
            logger.error(f"Error getting server info: {e}")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.running = False
            console.print("\n🛑 Shutting down gracefully...", style="yellow")
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def execute_single_query(self, query: str) -> bool:
        """Execute a single query (non-interactive mode)"""
        try:
            async with MCPClientContext() as client:
                if not client.connected:
                    console.print("❌ Failed to connect to MCP server", style="bold red")
                    return False
                
                console.print(f"🔍 Executing query: {query}", style="bold blue")
                
                # Execute query
                response = await client.execute_query(query)
                
                # Display response
                console.print("\n📊 Results:", style="bold green")
                if response.get("text"):
                    console.print(response["text"])
                
                # Handle charts
                if response.get("charts"):
                    from chart_renderer import ChartRenderer
                    renderer = ChartRenderer()
                    
                    console.print(f"\n📈 Generated {len(response['charts'])} chart(s)")
                    for i, chart in enumerate(response["charts"]):
                        title = chart.get("title", f"Chart {i+1}")
                        if "data" in chart:
                            path = renderer.render_chart(chart["data"], title, show=True, save=True)
                            if path:
                                console.print(f"  • {title} (saved to {path})")
                
                return True
                
        except Exception as e:
            console.print(f"❌ Query execution failed: {str(e)}", style="bold red")
            return False

# CLI interface using Click
@click.command()
@click.option(
    "--query", "-q", 
    help="Execute a single query and exit (non-interactive mode)"
)
@click.option(
    "--debug", "-d", 
    is_flag=True, 
    help="Enable debug logging"
)
@click.option(
    "--no-charts", 
    is_flag=True, 
    help="Disable chart rendering"
)
@click.version_option(
    version=ClientConfig.CLIENT_VERSION,
    prog_name=ClientConfig.CLIENT_NAME
)
def main(query: Optional[str], debug: bool, no_charts: bool):
    """
    MCP Database Analytics Client
    
    Interactive natural language interface for e-commerce analytics.
    Ask questions about user behavior, sales trends, and more!
    
    Examples:
      python main.py
      python main.py --query "Show me the top countries by user sessions"
      python main.py --debug
    """
    
    # Configure logging level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Update config based on CLI options
    if no_charts:
        ClientConfig.CHART_DISPLAY_METHOD = "none"
    
    # Create and run app
    app = AnalyticsClientApp()
    
    try:
        if query:
            # Single query mode
            success = asyncio.run(app.execute_single_query(query))
            sys.exit(0 if success else 1)
        else:
            # Interactive mode
            success = asyncio.run(app.start(interactive=True))
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="bold blue")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Application failed: {str(e)}", style="bold red")
        if debug:
            logger.exception("Application error")
        sys.exit(1)

if __name__ == "__main__":
    """
    Entry point for the MCP Database Analytics Client.
    
    This application provides a natural language interface for querying
    e-commerce analytics data through an MCP server.
    
    Features:
    - Interactive chat interface with rich formatting
    - Natural language query processing
    - Automatic chart generation and display
    - Query history and suggestions
    - Command-line interface for scripting
    
    Usage:
        # Interactive mode
        python main.py
        
        # Single query mode
        python main.py --query "Show me user activity by country"
        
        # Debug mode
        python main.py --debug
    """
    main() 