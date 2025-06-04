#!/usr/bin/env python3
"""
Interactive MCP Database Analytics Demo

This script provides a working demonstration of the MCP database analytics
capabilities with a simple menu-driven interface.

This is the production demo - for testing demo functionality, see tests/test_interactive_demo.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AnalyticsDemo:
    """Interactive demo for MCP database analytics"""
    
    def __init__(self):
        self.server_path = Path(__file__).parent.parent.parent / "server" / "main.py"
        self.server_params = StdioServerParameters(
            command="python",
            args=[str(self.server_path)],
        )
    
    def show_menu(self):
        """Display the interactive menu"""
        print("\n" + "="*60)
        print("🚀 MCP Database Analytics Demo")
        print("="*60)
        print("Choose an analysis option:")
        print()
        print("📊 Basic Analytics:")
        print("  1. Database Overview")
        print("  2. Geographic Analysis")
        print("  3. Product Performance")
        print("  4. User Segmentation")
        print()
        print("📈 Advanced Queries:")
        print("  5. Top Countries by Sessions")
        print("  6. Category Performance")
        print("  7. Session Length Analysis")
        print("  8. Custom SQL Query")
        print()
        print("📋 Database Information:")
        print("  9. Database Schema")
        print("  10. Sample Data")
        print()
        print("  0. Exit")
        print("="*60)
    
    async def execute_query(self, tool_name: str, args: Dict[str, Any], description: str):
        """Execute a query and display results"""
        print(f"\n🔍 {description}")
        print("-" * 50)
        
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    result = await session.call_tool(tool_name, args)
                    
                    if result.content:
                        content = result.content[0].text
                        print(content)
                    else:
                        print("No results returned")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def run_interactive_demo(self):
        """Run the interactive demo"""
        print("🚀 Starting MCP Database Analytics Demo...")
        print(f"📡 Server: {self.server_path}")
        
        while True:
            self.show_menu()
            
            try:
                choice = input("\nEnter your choice (0-10): ").strip()
                
                if choice == "0":
                    print("\n👋 Thank you for using the MCP Database Analytics Demo!")
                    break
                
                elif choice == "1":
                    await self.execute_query(
                        "analyze_user_behavior",
                        {"analysis_type": "overview"},
                        "Database Overview - Key Statistics"
                    )
                
                elif choice == "2":
                    await self.execute_query(
                        "geographic_analysis",
                        {"analysis_type": "overview"},
                        "Geographic Analysis - Top Countries"
                    )
                
                elif choice == "3":
                    await self.execute_query(
                        "product_performance",
                        {"analysis_type": "popularity"},
                        "Product Performance - Category Popularity"
                    )
                
                elif choice == "4":
                    await self.execute_query(
                        "user_segmentation",
                        {"segmentation_type": "engagement"},
                        "User Segmentation - Engagement Analysis"
                    )
                
                elif choice == "5":
                    await self.execute_query(
                        "query_database",
                        {"query": "SELECT country, COUNT(DISTINCT session_id) as unique_sessions, COUNT(*) as total_clicks FROM clickstream GROUP BY country ORDER BY unique_sessions DESC LIMIT 10"},
                        "Top 10 Countries by Unique Sessions"
                    )
                
                elif choice == "6":
                    await self.execute_query(
                        "query_database",
                        {"query": "SELECT page_1_main_category as category, COUNT(*) as views, COUNT(DISTINCT session_id) as unique_viewers FROM clickstream WHERE page_1_main_category != 'Unknown' GROUP BY page_1_main_category ORDER BY views DESC LIMIT 8"},
                        "Category Performance Analysis"
                    )
                
                elif choice == "7":
                    await self.execute_query(
                        "query_database",
                        {"query": "SELECT CASE WHEN total_clicks = 1 THEN '1 click' WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks' WHEN total_clicks BETWEEN 6 AND 15 THEN '6-15 clicks' ELSE '15+ clicks' END as session_length, COUNT(*) as sessions, ROUND(AVG(total_clicks), 2) as avg_clicks FROM user_sessions GROUP BY CASE WHEN total_clicks = 1 THEN '1 click' WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks' WHEN total_clicks BETWEEN 6 AND 15 THEN '6-15 clicks' ELSE '15+ clicks' END ORDER BY sessions DESC"},
                        "Session Length Distribution"
                    )
                
                elif choice == "8":
                    print("\n💡 Custom SQL Query")
                    print("Enter your SELECT query (or 'cancel' to return):")
                    custom_query = input("SQL> ").strip()
                    
                    if custom_query.lower() != 'cancel' and custom_query:
                        await self.execute_query(
                            "query_database",
                            {"query": custom_query},
                            f"Custom Query Results"
                        )
                
                elif choice == "9":
                    await self.execute_query(
                        "get_table_schema",
                        {"table_name": ""},
                        "Database Schema Information"
                    )
                
                elif choice == "10":
                    await self.execute_query(
                        "get_sample_data",
                        {"table_name": "clickstream", "limit": 3},
                        "Sample Data from Clickstream Table"
                    )
                
                else:
                    print("❌ Invalid choice. Please enter a number between 0-10.")
                
                if choice != "0":
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")

async def main():
    """Main entry point"""
    demo = AnalyticsDemo()
    await demo.run_interactive_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0) 