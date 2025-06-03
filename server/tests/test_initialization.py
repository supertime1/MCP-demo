#!/usr/bin/env python3
"""
Test script to validate MCP server initialization
"""

import asyncio
import sys
from pathlib import Path

# Add server directory to path (go up one level from tests folder)
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_server_initialization():
    """Test server components initialization"""
    try:
        print("🧪 Testing MCP Server Initialization...")
        
        # Test imports
        print("📦 Testing imports...")
        import database_tools
        import analytics_tools  
        import visualization_tools
        import config
        from main import get_database_tools, get_analytics_tools, get_visualization_tools
        print("✅ All modules imported successfully")
        
        # Test configuration
        print("⚙️  Testing configuration...")
        from config import Config
        print(f"   - Database path: {Config.DATABASE_PATH}")
        print(f"   - Database exists: {Config.validate_database()}")
        print(f"   - Chart output dir: {Config.CHART_OUTPUT_DIR}")
        
        # Test database connection
        print("🗄️  Testing database connection...")
        from database_tools import DatabaseService
        db_service = DatabaseService.get_instance()
        db_connection = db_service.get_connection()
        
        # Test simple query
        result = db_connection.execute_query("SELECT COUNT(*) as total FROM clickstream LIMIT 1")
        if result.data:
            total_records = result.data[0][0]
            print(f"✅ Database connection successful - {total_records:,} records available")
        else:
            print("⚠️  Database query returned no results")
        
        # Test table structure
        tables_result = db_connection.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in tables_result.data]
        print(f"   - Available tables: {', '.join(tables)}")
        
        # Test tools registration
        print("🔧 Testing tools registration...")
        db_tools = get_database_tools()
        analytics_tools = get_analytics_tools()
        viz_tools = get_visualization_tools()
        
        total_tools = len(db_tools) + len(analytics_tools) + len(viz_tools)
        print(f"   - Database tools: {len(db_tools)}")
        print(f"   - Analytics tools: {len(analytics_tools)}")
        print(f"   - Visualization tools: {len(viz_tools)}")
        print(f"   - Total tools available: {total_tools}")
        
        # Test sample query
        print("🔍 Testing sample analytics query...")
        sample_result = db_connection.execute_query("""
            SELECT country, COUNT(*) as sessions 
            FROM clickstream 
            GROUP BY country 
            ORDER BY sessions DESC 
            LIMIT 5
        """)
        print("   - Top 5 countries by sessions:")
        for row in sample_result.data:
            print(f"     • {row[0]}: {row[1]:,} sessions")
        
        print("\n🎉 All tests passed! Server is ready to run.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_initialization())
    sys.exit(0 if success else 1) 