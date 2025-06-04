"""
Chat Interface for MCP Database Analytics Client

This module provides a rich, interactive chat interface for natural language
querying of the e-commerce analytics database through the MCP server.
"""

import asyncio
import json
import pickle
import readline
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from config import ClientConfig
from chart_renderer import ChartRenderer, ChartRenderingError

logger = logging.getLogger(__name__)

class QueryHistory:
    """Manages query history with persistence"""
    
    def __init__(self, history_file: Path = None):
        self.history_file = history_file or ClientConfig.HISTORY_FILE
        self.history: List[Dict[str, Any]] = []
        self.load_history()
    
    def add_query(self, query: str, response: str, success: bool = True, charts: int = 0):
        """Add a query to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:500] + "..." if len(response) > 500 else response,
            "success": success,
            "charts": charts
        }
        
        self.history.append(entry)
        
        # Limit history size
        if len(self.history) > ClientConfig.MAX_HISTORY_SIZE:
            self.history = self.history[-ClientConfig.MAX_HISTORY_SIZE:]
        
        self.save_history()
    
    def get_recent_queries(self, n: int = 5) -> List[str]:
        """Get recent successful queries"""
        successful = [h for h in self.history if h["success"]]
        return [h["query"] for h in successful[-n:]]
    
    def save_history(self):
        """Save history to disk"""
        try:
            with open(self.history_file, 'wb') as f:
                pickle.dump(self.history, f)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def load_history(self):
        """Load history from disk"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'rb') as f:
                    self.history = pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            self.history = []

class ChatInterface:
    """Rich interactive chat interface for MCP client"""
    
    def __init__(self, mcp_client=None):
        self.console = Console()
        self.mcp_client = mcp_client
        self.chart_renderer = ChartRenderer()
        self.query_history = QueryHistory()
        self.session_stats = {
            "queries": 0,
            "successful": 0,
            "charts_generated": 0,
            "start_time": datetime.now()
        }
    
    def start_session(self):
        """Start interactive chat session"""
        self.show_welcome()
        self.show_suggestions()
        
        while True:
            try:
                # Get user input
                query = self.get_user_input()
                
                if not query:
                    continue
                
                # Handle special commands
                if self.handle_special_commands(query):
                    continue
                
                # Process query through MCP
                self.process_query(query)
                
            except KeyboardInterrupt:
                if Confirm.ask("\n🤔 Do you want to exit?"):
                    break
            except EOFError:
                break
            except Exception as e:
                self.show_error(f"Unexpected error: {str(e)}")
        
        self.show_goodbye()
    
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🏪 E-commerce Analytics Assistant

Welcome to the **MCP Database Analytics Client**! 

I can help you analyze e-commerce data using natural language queries. 
Ask me about user behavior, sales trends, geographic patterns, and more!

**Available data**: 165,474 e-commerce user sessions across 47 countries

💡 **Tip**: Try asking questions like:
- "Show me the top countries by user sessions"
- "Create a chart of daily activity trends"
- "Analyze the conversion funnel"
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="🚀 Analytics Assistant",
            title_align="center",
            border_style="bold blue"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_suggestions(self):
        """Display sample queries as suggestions"""
        suggestion_table = Table(title="💡 Sample Queries", show_header=False, box=None)
        
        # Split suggestions into columns
        suggestions = ClientConfig.SAMPLE_QUERIES[:8]  # Show first 8
        mid = len(suggestions) // 2
        
        for i in range(mid):
            left = f"• {suggestions[i]}"
            right = f"• {suggestions[i + mid]}" if i + mid < len(suggestions) else ""
            suggestion_table.add_row(left, right)
        
        self.console.print(suggestion_table)
        self.console.print()
    
    def get_user_input(self) -> str:
        """Get user input with rich prompt"""
        try:
            query = Prompt.ask(
                "[bold blue]🤖 Ask me anything",
                console=self.console
            ).strip()
            
            return query
            
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            self.show_error(f"Input error: {str(e)}")
            return ""
    
    def handle_special_commands(self, query: str) -> bool:
        """Handle special commands like help, history, etc."""
        query_lower = query.lower().strip()
        
        if query_lower in ['help', '/help', '?']:
            self.show_help()
            return True
        
        elif query_lower in ['history', '/history']:
            self.show_history()
            return True
        
        elif query_lower in ['suggestions', '/suggestions', 'examples']:
            self.show_suggestions()
            return True
        
        elif query_lower in ['stats', '/stats']:
            self.show_session_stats()
            return True
        
        elif query_lower in ['clear', '/clear']:
            self.console.clear()
            self.show_welcome()
            return True
        
        elif query_lower.startswith('clear charts'):
            count = self.chart_renderer.clear_saved_charts()
            self.console.print(f"✅ Cleared {count} saved charts")
            return True
        
        elif query_lower in ['exit', '/exit', 'quit', '/quit', 'bye']:
            raise KeyboardInterrupt
        
        return False
    
    def process_query(self, query: str):
        """Process a query through the MCP client"""
        if not self.mcp_client:
            self.show_error("MCP client not connected. Please restart the application.")
            return
        
        self.session_stats["queries"] += 1
        
        # Show processing indicator
        with self.console.status("[bold green]🔍 Processing your query...", spinner="dots"):
            try:
                # Execute query through MCP client
                response = asyncio.run(self.mcp_client.execute_query(query))
                
                if response:
                    self.display_response(response, query)
                    self.session_stats["successful"] += 1
                else:
                    self.show_error("No response received from server")
                    
            except Exception as e:
                self.show_error(f"Query processing failed: {str(e)}")
                self.query_history.add_query(query, str(e), success=False)
    
    def display_response(self, response: Dict, original_query: str):
        """Display MCP server response"""
        try:
            # Display text response
            if "text" in response:
                response_panel = Panel(
                    Markdown(response["text"]),
                    title="📊 Analysis Results",
                    border_style="green"
                )
                self.console.print(response_panel)
            
            # Display charts if present
            charts_rendered = 0
            if "charts" in response and response["charts"]:
                self.console.print("\n📈 **Generated Charts:**")
                
                for i, chart_data in enumerate(response["charts"]):
                    try:
                        title = chart_data.get("title", f"Chart {i+1}")
                        image_data = chart_data.get("data", "")
                        
                        if image_data:
                            self.chart_renderer.render_chart(image_data, title)
                            charts_rendered += 1
                            self.console.print(f"✅ Chart rendered: {title}")
                        
                    except ChartRenderingError as e:
                        self.console.print(f"❌ Chart rendering failed: {str(e)}")
            
            # Update stats and history
            self.session_stats["charts_generated"] += charts_rendered
            self.query_history.add_query(
                original_query, 
                response.get("text", ""), 
                success=True, 
                charts=charts_rendered
            )
            
            self.console.print()  # Add spacing
            
        except Exception as e:
            self.show_error(f"Error displaying response: {str(e)}")
    
    def show_help(self):
        """Display help information"""
        help_text = """
# 🆘 Help & Commands

## Natural Language Queries
Ask questions about the e-commerce data in plain English:
- "What are the top selling products?"
- "Show me user activity by country"
- "Create a funnel chart for conversions"

## Special Commands
- `help` or `?` - Show this help
- `history` - Show recent queries
- `suggestions` - Show sample queries
- `stats` - Show session statistics
- `clear` - Clear screen
- `clear charts` - Clear saved charts
- `exit` or `quit` - Exit the application

## Tips
- Be specific about what you want to see
- Ask for charts or visualizations explicitly
- Use phrases like "show me", "create a chart", "analyze"
        """
        
        panel = Panel(
            Markdown(help_text),
            title="📚 Help Guide",
            border_style="yellow"
        )
        self.console.print(panel)
    
    def show_history(self):
        """Display query history"""
        recent = self.query_history.get_recent_queries(10)
        
        if not recent:
            self.console.print("📝 No query history yet.")
            return
        
        history_table = Table(title="📝 Recent Queries", show_header=True)
        history_table.add_column("#", style="dim", width=3)
        history_table.add_column("Query", style="cyan")
        
        for i, query in enumerate(reversed(recent), 1):
            history_table.add_row(str(i), query)
        
        self.console.print(history_table)
    
    def show_session_stats(self):
        """Display session statistics"""
        duration = datetime.now() - self.session_stats["start_time"]
        success_rate = (self.session_stats["successful"] / max(1, self.session_stats["queries"])) * 100
        
        stats_table = Table(title="📊 Session Statistics", show_header=False)
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Session Duration", str(duration).split('.')[0])
        stats_table.add_row("Total Queries", str(self.session_stats["queries"]))
        stats_table.add_row("Successful", str(self.session_stats["successful"]))
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%")
        stats_table.add_row("Charts Generated", str(self.session_stats["charts_generated"]))
        
        self.console.print(stats_table)
    
    def show_error(self, message: str):
        """Display error message"""
        error_panel = Panel(
            f"❌ {message}",
            title="Error",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def show_goodbye(self):
        """Display goodbye message"""
        duration = datetime.now() - self.session_stats["start_time"]
        
        goodbye_text = f"""
# 👋 Thanks for using the Analytics Assistant!

**Session Summary:**
- Duration: {str(duration).split('.')[0]}
- Queries processed: {self.session_stats["queries"]}
- Charts generated: {self.session_stats["charts_generated"]}

Your charts have been saved to: `{ClientConfig.CHART_SAVE_DIR}`

Come back anytime for more analytics insights! 🚀
        """
        
        panel = Panel(
            Markdown(goodbye_text),
            title="👋 Goodbye!",
            border_style="blue"
        )
        self.console.print(panel) 