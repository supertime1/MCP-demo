"""
Advanced Analytics Tools for E-commerce MCP Server
Provides sophisticated user behavior analysis and business intelligence
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from mcp.types import Tool
from pydantic import BaseModel

from config import Config
from database_tools import DatabaseService

logger = logging.getLogger(__name__)

class AnalyticsResult(BaseModel):
    """Result structure for analytics operations"""
    analysis_type: str
    data: List[Dict[str, Any]]
    insights: List[str]
    execution_time_ms: float
    metadata: Dict[str, Any]

class AnalyticsService:
    """Service for advanced analytics operations with shared functionality"""
    
    def __init__(self):
        self.db_service = DatabaseService.get_instance()
    
    def _execute_analytics_query(self, query: str, analysis_type: str, insights: List[str], metadata: Dict[str, Any]) -> AnalyticsResult:
        """Shared method for executing analytics queries with timing and formatting"""
        start_time = time.time()
        
        db_connection = self.db_service.get_connection()
        result = db_connection.execute_query(query)
        execution_time = (time.time() - start_time) * 1000
        
        # Convert to analytics result format
        data = []
        for row in result.data:
            row_dict = {}
            for i, col in enumerate(result.columns):
                row_dict[col] = row[i]
            data.append(row_dict)
        
        return AnalyticsResult(
            analysis_type=analysis_type,
            data=data,
            insights=insights,
            execution_time_ms=round(execution_time, 2),
            metadata=metadata
        )
    
    def _format_analytics_output(self, result: AnalyticsResult) -> str:
        """Format analytics results for display"""
        output = []
        output.append(f"📊 {result.analysis_type}")
        output.append("=" * (len(result.analysis_type) + 4))
        output.append(f"⏱️  Execution time: {result.execution_time_ms}ms")
        output.append("")
        
        # Add insights
        if result.insights:
            output.append("🔍 Key Insights:")
            for insight in result.insights:
                output.append(f"  • {insight}")
            output.append("")
        
        # Add data table
        if result.data:
            # Get column headers from first row
            headers = list(result.data[0].keys())
            
            # Format header
            header_row = " | ".join(f"{col:15}" for col in headers)
            output.append(header_row)
            output.append("-" * len(header_row))
            
            # Add data rows
            for row in result.data[:20]:  # Limit display
                data_row = " | ".join(f"{str(row[col]):15}" for col in headers)
                output.append(data_row)
            
            if len(result.data) > 20:
                output.append(f"... ({len(result.data) - 20} more rows)")
        
        # Add metadata
        if result.metadata:
            output.append("")
            output.append("📈 Analysis Metadata:")
            for key, value in result.metadata.items():
                output.append(f"  {key}: {value}")
        
        return "\n".join(output)

    async def user_segmentation(self, segmentation_type: str = "engagement") -> str:
        """
        Segment users based on behavior patterns.
        
        Segmentation types:
        - engagement: Based on session activity levels
        - value: Based on potential purchasing behavior (price views)
        - exploration: Based on browsing diversity
        - geographic: Based on country patterns
        """
        try:
            if segmentation_type == "engagement":
                query = """
                SELECT 
                    CASE 
                        WHEN total_clicks = 1 THEN 'Bouncers'
                        WHEN total_clicks BETWEEN 2 AND 5 THEN 'Browsers'
                        WHEN total_clicks BETWEEN 6 AND 15 THEN 'Engaged Users'
                        WHEN total_clicks BETWEEN 16 AND 30 THEN 'Active Users'
                        ELSE 'Power Users'
                    END as segment,
                    COUNT(*) as user_count,
                    ROUND(AVG(total_clicks), 2) as avg_clicks_per_session,
                    ROUND(AVG(unique_products_viewed), 2) as avg_products_viewed,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                FROM user_sessions
                GROUP BY 
                    CASE 
                        WHEN total_clicks = 1 THEN 'Bouncers'
                        WHEN total_clicks BETWEEN 2 AND 5 THEN 'Browsers'
                        WHEN total_clicks BETWEEN 6 AND 15 THEN 'Engaged Users'
                        WHEN total_clicks BETWEEN 16 AND 30 THEN 'Active Users'
                        ELSE 'Power Users'
                    END
                ORDER BY user_count DESC
                """
                
                insights = [
                    "Bouncers (1 click) represent single-page visitors",
                    "Engaged Users show genuine interest in products",
                    "Power Users are potential high-value customers"
                ]
                
                metadata = {
                    "segmentation_method": segmentation_type,
                    "data_source": "user_sessions",
                    "business_value": "User targeting and personalization"
                }
                
            elif segmentation_type == "value":
                query = """
                WITH user_value_metrics AS (
                    SELECT 
                        session_id,
                        COUNT(CASE WHEN price > 0 THEN 1 END) as price_views,
                        MAX(price) as max_price_viewed,
                        AVG(CASE WHEN price > 0 THEN price END) as avg_price_viewed,
                        COUNT(DISTINCT page_1_main_category) as categories_explored
                    FROM clickstream 
                    GROUP BY session_id
                )
                SELECT 
                    CASE 
                        WHEN price_views = 0 THEN 'Non-Commercial'
                        WHEN price_views BETWEEN 1 AND 2 THEN 'Price Curious'
                        WHEN price_views BETWEEN 3 AND 10 THEN 'Price Conscious'
                        ELSE 'High Intent'
                    END as value_segment,
                    COUNT(*) as user_count,
                    ROUND(AVG(price_views), 2) as avg_price_views,
                    ROUND(AVG(max_price_viewed), 2) as avg_max_price,
                    ROUND(AVG(categories_explored), 2) as avg_categories
                FROM user_value_metrics
                GROUP BY 
                    CASE 
                        WHEN price_views = 0 THEN 'Non-Commercial'
                        WHEN price_views BETWEEN 1 AND 2 THEN 'Price Curious'
                        WHEN price_views BETWEEN 3 AND 10 THEN 'Price Conscious'
                        ELSE 'High Intent'
                    END
                ORDER BY user_count DESC
                """
                
                insights = [
                    "Price views indicate purchase intent",
                    "High Intent users view multiple prices",
                    "Non-Commercial users focus on browsing"
                ]
                
                metadata = {
                    "segmentation_method": segmentation_type,
                    "data_source": "clickstream",
                    "business_value": "Revenue optimization"
                }
                
            elif segmentation_type == "exploration":
                query = """
                SELECT 
                    CASE 
                        WHEN unique_categories_viewed = 1 THEN 'Category Focused'
                        WHEN unique_categories_viewed = 2 THEN 'Comparison Shoppers'
                        WHEN unique_categories_viewed >= 3 THEN 'Explorers'
                        ELSE 'Undetermined'
                    END as exploration_segment,
                    COUNT(*) as user_count,
                    ROUND(AVG(unique_categories_viewed), 2) as avg_categories,
                    ROUND(AVG(unique_products_viewed), 2) as avg_products,
                    ROUND(AVG(total_clicks), 2) as avg_session_length
                FROM user_sessions
                WHERE unique_categories_viewed > 0
                GROUP BY 
                    CASE 
                        WHEN unique_categories_viewed = 1 THEN 'Category Focused'
                        WHEN unique_categories_viewed = 2 THEN 'Comparison Shoppers'
                        WHEN unique_categories_viewed >= 3 THEN 'Explorers'
                        ELSE 'Undetermined'
                    END
                ORDER BY user_count DESC
                """
                
                insights = [
                    "Category Focused users know what they want",
                    "Explorers browse across multiple categories",
                    "Comparison Shoppers evaluate options carefully"
                ]
                
                metadata = {
                    "segmentation_method": segmentation_type,
                    "data_source": "user_sessions",
                    "business_value": "Product recommendation strategy"
                }
                
            elif segmentation_type == "geographic":
                query = """
                SELECT 
                    country,
                    COUNT(*) as sessions,
                    ROUND(AVG(total_clicks), 2) as avg_session_length,
                    ROUND(AVG(unique_products_viewed), 2) as avg_products,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as market_share
                FROM user_sessions
                GROUP BY country
                HAVING COUNT(*) >= 10
                ORDER BY sessions DESC
                LIMIT 15
                """
                
                insights = [
                    "Geographic patterns show market preferences",
                    "Session length varies by country",
                    "Market share indicates business opportunities"
                ]
                
                metadata = {
                    "segmentation_method": segmentation_type,
                    "data_source": "user_sessions",
                    "business_value": "Market expansion strategy"
                }
                
            else:
                return f"Invalid segmentation type. Available: engagement, value, exploration, geographic"
            
            result = self._execute_analytics_query(
                query,
                f"User Segmentation: {segmentation_type.title()}",
                insights,
                {**metadata, "total_segments": "calculated_after_query"}
            )
            
            # Update metadata with actual segment count
            result.metadata["total_segments"] = len(result.data)
            
            return self._format_analytics_output(result)
            
        except Exception as e:
            logger.error(f"User segmentation failed: {e}")
            return f"Error in user segmentation: {str(e)}"

    async def conversion_funnel(self, funnel_type: str = "standard") -> str:
        """
        Analyze conversion funnels and user journey drop-offs.
        
        Funnel types:
        - standard: Basic page view funnel
        - product: Product-specific conversion funnel
        - price: Price interaction funnel
        - category: Category-based funnel
        """
        try:
            if funnel_type == "standard":
                query = """
                WITH funnel_steps AS (
                    SELECT 
                        session_id,
                        MAX(CASE WHEN page_1_main_category != 'Unknown' THEN 1 ELSE 0 END) as viewed_category,
                        MAX(CASE WHEN page_2_clothing_model != 'Unknown' THEN 1 ELSE 0 END) as viewed_product,
                        MAX(CASE WHEN price > 0 THEN 1 ELSE 0 END) as viewed_price,
                        MAX(CASE WHEN colour != 'Unknown' THEN 1 ELSE 0 END) as viewed_details
                    FROM clickstream
                    GROUP BY session_id
                ),
                funnel_summary AS (
                    SELECT 
                        'All Sessions' as stage, COUNT(*) as users, 1 as step_order FROM funnel_steps
                    UNION ALL
                    SELECT 
                        'Viewed Category', SUM(viewed_category) as users, 2 as step_order FROM funnel_steps
                    UNION ALL
                    SELECT 
                        'Viewed Product', SUM(viewed_product) as users, 3 as step_order FROM funnel_steps
                    UNION ALL
                    SELECT 
                        'Viewed Price', SUM(viewed_price) as users, 4 as step_order FROM funnel_steps
                    UNION ALL
                    SELECT 
                        'Viewed Details', SUM(viewed_details) as users, 5 as step_order FROM funnel_steps
                )
                SELECT stage, users,
                    ROUND(users * 100.0 / FIRST_VALUE(users) OVER(ORDER BY step_order), 2) as conversion_rate,
                    ROUND(users * 100.0 / LAG(users) OVER(ORDER BY step_order), 2) as step_conversion_rate
                FROM funnel_summary
                ORDER BY step_order
                """
                
                insights = [
                    "Each funnel step shows user engagement depth",
                    "Drop-off rates identify optimization opportunities",
                    "Price viewing indicates purchase consideration"
                ]
                
                metadata = {
                    "funnel_type": funnel_type,
                    "data_source": "clickstream",
                    "business_value": "Conversion optimization"
                }
                
            elif funnel_type == "product":
                query = """
                WITH product_funnel AS (
                    SELECT 
                        page_1_main_category as category,
                        COUNT(DISTINCT session_id) as total_sessions,
                        COUNT(DISTINCT CASE WHEN page_2_clothing_model != 'Unknown' THEN session_id END) as product_viewers,
                        COUNT(DISTINCT CASE WHEN price > 0 THEN session_id END) as price_viewers,
                        COUNT(DISTINCT CASE WHEN colour != 'Unknown' THEN session_id END) as detail_viewers
                    FROM clickstream
                    WHERE page_1_main_category != 'Unknown'
                    GROUP BY page_1_main_category
                    HAVING COUNT(DISTINCT session_id) >= 20
                )
                SELECT 
                    category,
                    total_sessions,
                    product_viewers,
                    price_viewers,
                    detail_viewers,
                    ROUND(product_viewers * 100.0 / total_sessions, 2) as product_conversion,
                    ROUND(price_viewers * 100.0 / total_sessions, 2) as price_conversion,
                    ROUND(detail_viewers * 100.0 / total_sessions, 2) as detail_conversion
                FROM product_funnel
                ORDER BY total_sessions DESC
                """
                
                insights = [
                    "Category-specific conversion patterns vary",
                    "Product viewing rates indicate category appeal",
                    "Detail conversion shows purchase intent by category"
                ]
                
                metadata = {
                    "funnel_type": funnel_type,
                    "data_source": "clickstream",
                    "business_value": "Category optimization"
                }
                
            elif funnel_type == "price":
                query = """
                WITH price_funnel AS (
                    SELECT 
                        CASE 
                            WHEN price BETWEEN 0 AND 50 THEN 'Budget (0-50)'
                            WHEN price BETWEEN 51 AND 100 THEN 'Mid-range (51-100)'
                            WHEN price BETWEEN 101 AND 150 THEN 'Premium (101-150)'
                            ELSE 'Luxury (150+)'
                        END as price_tier,
                        COUNT(DISTINCT session_id) as sessions_with_price,
                        COUNT(*) as total_price_views,
                        COUNT(DISTINCT CASE WHEN colour != 'Unknown' THEN session_id END) as detail_viewers,
                        AVG(price) as avg_price_in_tier
                    FROM clickstream
                    WHERE price > 0
                    GROUP BY 
                        CASE 
                            WHEN price BETWEEN 0 AND 50 THEN 'Budget (0-50)'
                            WHEN price BETWEEN 51 AND 100 THEN 'Mid-range (51-100)'
                            WHEN price BETWEEN 101 AND 150 THEN 'Premium (101-150)'
                            ELSE 'Luxury (150+)'
                        END
                )
                SELECT 
                    price_tier,
                    sessions_with_price,
                    total_price_views,
                    detail_viewers,
                    ROUND(avg_price_in_tier, 2) as avg_price,
                    ROUND(detail_viewers * 100.0 / sessions_with_price, 2) as detail_conversion_rate,
                    ROUND(total_price_views * 1.0 / sessions_with_price, 2) as avg_price_views_per_session
                FROM price_funnel
                ORDER BY avg_price
                """
                
                insights = [
                    "Price tiers show different engagement patterns",
                    "Higher prices may correlate with more detailed viewing",
                    "Budget items might have faster decision cycles"
                ]
                
                metadata = {
                    "funnel_type": funnel_type,
                    "data_source": "clickstream",
                    "business_value": "Pricing strategy optimization"
                }
                
            elif funnel_type == "category":
                query = """
                WITH category_journey AS (
                    SELECT 
                        session_id,
                        COUNT(DISTINCT page_1_main_category) as categories_visited,
                        COUNT(*) as total_clicks,
                        MAX(CASE WHEN price > 0 THEN 1 ELSE 0 END) as viewed_any_price
                    FROM clickstream
                    WHERE page_1_main_category != 'Unknown'
                    GROUP BY session_id
                )
                SELECT 
                    CASE 
                        WHEN categories_visited = 1 THEN 'Single Category'
                        WHEN categories_visited = 2 THEN 'Two Categories'
                        WHEN categories_visited >= 3 THEN 'Multi-Category'
                        ELSE 'Other'
                    END as journey_type,
                    COUNT(*) as sessions,
                    ROUND(AVG(total_clicks), 2) as avg_clicks,
                    SUM(viewed_any_price) as price_viewers,
                    ROUND(SUM(viewed_any_price) * 100.0 / COUNT(*), 2) as price_view_rate
                FROM category_journey
                GROUP BY 
                    CASE 
                        WHEN categories_visited = 1 THEN 'Single Category'
                        WHEN categories_visited = 2 THEN 'Two Categories'
                        WHEN categories_visited >= 3 THEN 'Multi-Category'
                        ELSE 'Other'
                    END
                ORDER BY sessions DESC
                """
                
                insights = [
                    "Multi-category browsers show exploration behavior",
                    "Single category focus may indicate targeted shopping",
                    "Cross-category journeys reveal related product interests"
                ]
                
                metadata = {
                    "funnel_type": funnel_type,
                    "data_source": "clickstream",
                    "business_value": "Cross-selling opportunities"
                }
                
            else:
                return f"Invalid funnel type. Available: standard, product, price, category"
            
            result = self._execute_analytics_query(
                query,
                f"Conversion Funnel: {funnel_type.title()}",
                insights,
                metadata
            )
            
            return self._format_analytics_output(result)
            
        except Exception as e:
            logger.error(f"Conversion funnel analysis failed: {e}")
            return f"Error in conversion funnel analysis: {str(e)}"

    async def geographic_analysis(self, analysis_type: str = "overview") -> str:
        """
        Analyze geographic patterns, market opportunities, and regional behavior differences.
        
        Analysis types:
        - overview: Basic geographic distribution
        - preferences: Category preferences by country
        - behavior: Behavioral patterns by region
        - market_size: Market opportunity assessment
        """
        try:
            if analysis_type == "overview":
                query = """
                SELECT 
                    cs.country,
                    COUNT(DISTINCT cs.session_id) as unique_sessions,
                    COUNT(*) as total_clicks,
                    ROUND(AVG(us.total_clicks), 2) as avg_clicks_per_session,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as click_share,
                    ROUND(COUNT(DISTINCT cs.session_id) * 100.0 / SUM(COUNT(DISTINCT cs.session_id)) OVER(), 2) as session_share
                FROM clickstream cs
                JOIN user_sessions us ON cs.session_id = us.session_id
                GROUP BY cs.country
                HAVING COUNT(DISTINCT cs.session_id) >= 5
                ORDER BY unique_sessions DESC
                LIMIT 15
                """
                
                insights = [
                    "Geographic distribution shows market penetration",
                    "Click-to-session ratios reveal engagement differences",
                    "Market share indicates growth opportunities"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream + user_sessions",
                    "business_value": "Market expansion planning"
                }
                
            elif analysis_type == "preferences":
                query = """
                WITH country_categories AS (
                    SELECT 
                        country,
                        page_1_main_category as category,
                        COUNT(*) as category_clicks,
                        COUNT(DISTINCT session_id) as unique_sessions
                    FROM clickstream
                    WHERE page_1_main_category != 'Unknown'
                    GROUP BY country, page_1_main_category
                    HAVING COUNT(DISTINCT session_id) >= 3
                ),
                country_totals AS (
                    SELECT country, SUM(category_clicks) as total_clicks
                    FROM country_categories
                    GROUP BY country
                )
                SELECT 
                    cc.country,
                    cc.category,
                    cc.category_clicks,
                    cc.unique_sessions,
                    ROUND(cc.category_clicks * 100.0 / ct.total_clicks, 2) as category_preference_pct
                FROM country_categories cc
                JOIN country_totals ct ON cc.country = ct.country
                WHERE ct.total_clicks >= 50
                ORDER BY cc.country, cc.category_clicks DESC
                """
                
                insights = [
                    "Category preferences vary significantly by country",
                    "Cultural differences influence product interest",
                    "Localization opportunities in popular categories"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream",
                    "business_value": "Product localization strategy"
                }
                
            elif analysis_type == "behavior":
                query = """
                SELECT 
                    country,
                    COUNT(DISTINCT session_id) as sessions,
                    ROUND(AVG(total_clicks), 2) as avg_session_length,
                    ROUND(AVG(unique_products_viewed), 2) as avg_products_per_session,
                    ROUND(AVG(unique_categories_viewed), 2) as avg_categories_per_session,
                    ROUND(SUM(CASE WHEN total_clicks = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as bounce_rate
                FROM user_sessions
                GROUP BY country
                HAVING COUNT(*) >= 10
                ORDER BY sessions DESC
                LIMIT 12
                """
                
                insights = [
                    "Session behavior patterns differ by geography",
                    "Bounce rates indicate regional user experience",
                    "Product exploration varies across markets"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "user_sessions",
                    "business_value": "Regional UX optimization"
                }
                
            elif analysis_type == "market_size":
                query = """
                WITH market_metrics AS (
                    SELECT 
                        country,
                        COUNT(DISTINCT session_id) as total_sessions,
                        COUNT(*) as total_interactions,
                        COUNT(CASE WHEN price > 0 THEN 1 END) as price_interactions,
                        ROUND(AVG(CASE WHEN price > 0 THEN price END), 2) as avg_price_viewed,
                        COUNT(DISTINCT page_1_main_category) as categories_explored
                    FROM clickstream
                    GROUP BY country
                    HAVING COUNT(DISTINCT session_id) >= 10
                )
                SELECT 
                    country,
                    total_sessions,
                    total_interactions,
                    price_interactions,
                    avg_price_viewed,
                    categories_explored,
                    ROUND(price_interactions * 100.0 / total_interactions, 2) as commercial_intent_pct,
                    CASE 
                        WHEN total_sessions >= 1000 THEN 'Large Market'
                        WHEN total_sessions >= 100 THEN 'Medium Market'
                        ELSE 'Small Market'
                    END as market_size
                FROM market_metrics
                ORDER BY total_sessions DESC
                """
                
                insights = [
                    "Market size categorization based on session volume",
                    "Commercial intent varies by geographic market",
                    "Price sensitivity differs across regions"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream",
                    "business_value": "Market prioritization and investment"
                }
                
            else:
                return f"Invalid analysis type. Available: overview, preferences, behavior, market_size"
            
            result = self._execute_analytics_query(
                query,
                f"Geographic Analysis: {analysis_type.title()}",
                insights,
                metadata
            )
            
            return self._format_analytics_output(result)
            
        except Exception as e:
            logger.error(f"Geographic analysis failed: {e}")
            return f"Error in geographic analysis: {str(e)}"

    async def product_performance(self, analysis_type: str = "popularity") -> str:
        """
        Analyze product popularity, engagement metrics, and cross-category patterns.
        
        Analysis types:
        - popularity: Most viewed products and categories
        - engagement: User engagement with specific products
        - pricing: Price-performance relationships
        - cross_category: Cross-category browsing patterns
        """
        try:
            if analysis_type == "popularity":
                query = """
                SELECT 
                    page_1_main_category as category,
                    COUNT(*) as total_views,
                    COUNT(DISTINCT session_id) as unique_viewers,
                    COUNT(DISTINCT page_2_clothing_model) as unique_products,
                    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT session_id), 2) as views_per_viewer,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as market_share
                FROM clickstream
                WHERE page_1_main_category != 'Unknown'
                GROUP BY page_1_main_category
                ORDER BY total_views DESC
                LIMIT 15
                """
                
                insights = [
                    "Category popularity drives overall engagement",
                    "Market share concentration in top categories",
                    "Product portfolio optimization opportunities"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream",
                    "business_value": "Product strategy optimization"
                }
                
            elif analysis_type == "engagement":
                query = """
                WITH product_metrics AS (
                    SELECT 
                        page_2_clothing_model as product,
                        page_1_main_category as category,
                        COUNT(*) as total_views,
                        COUNT(DISTINCT session_id) as unique_sessions,
                        AVG(CASE WHEN price > 0 THEN price END) as avg_price
                    FROM clickstream
                    WHERE page_2_clothing_model != 'Unknown'
                    GROUP BY page_2_clothing_model, page_1_main_category
                    HAVING COUNT(DISTINCT session_id) >= 3
                )
                SELECT 
                    product,
                    category,
                    total_views,
                    unique_sessions,
                    ROUND(total_views * 1.0 / unique_sessions, 2) as views_per_session,
                    ROUND(avg_price, 2) as avg_price,
                    CASE 
                        WHEN total_views > 20 THEN 'High Traffic'
                        WHEN total_views > 10 THEN 'Medium Traffic'
                        ELSE 'Low Traffic'
                    END as traffic_level
                FROM product_metrics
                ORDER BY views_per_session DESC, total_views DESC
                LIMIT 20
                """
                
                insights = [
                    "High engagement products drive repeat views",
                    "Views per session indicates product appeal",
                    "Traffic levels vary significantly by product"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream",
                    "business_value": "Product merchandising optimization"
                }
                
            elif analysis_type == "pricing":
                query = """
                WITH price_performance AS (
                    SELECT 
                        page_1_main_category as category,
                        CASE 
                            WHEN price BETWEEN 0 AND 50 THEN 'Budget'
                            WHEN price BETWEEN 51 AND 100 THEN 'Mid-range'
                            WHEN price BETWEEN 101 AND 150 THEN 'Premium'
                            ELSE 'Luxury'
                        END as price_tier,
                        COUNT(*) as views,
                        COUNT(DISTINCT session_id) as unique_viewers,
                        COUNT(DISTINCT page_2_clothing_model) as unique_products
                    FROM clickstream 
                    WHERE price > 0 AND page_1_main_category != 'Unknown'
                    GROUP BY page_1_main_category, 
                        CASE 
                            WHEN price BETWEEN 0 AND 50 THEN 'Budget'
                            WHEN price BETWEEN 51 AND 100 THEN 'Mid-range'
                            WHEN price BETWEEN 101 AND 150 THEN 'Premium'
                            ELSE 'Luxury'
                        END
                )
                SELECT 
                    category,
                    price_tier,
                    views,
                    unique_viewers,
                    unique_products,
                    ROUND(views * 1.0 / unique_viewers, 2) as avg_views_per_user
                FROM price_performance
                WHERE views >= 10
                ORDER BY category, views DESC
                """
                
                insights = [
                    "Price tiers perform differently by category",
                    "Customer price sensitivity varies",
                    "Pricing strategy optimization needed"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream",
                    "business_value": "Pricing strategy optimization"
                }
                
            elif analysis_type == "cross_category":
                query = """
                WITH category_combinations AS (
                    SELECT 
                        c1.session_id,
                        c1.page_1_main_category as primary_category,
                        c2.page_1_main_category as secondary_category,
                        COUNT(*) as co_occurrence
                    FROM clickstream c1
                    JOIN clickstream c2 ON c1.session_id = c2.session_id
                    WHERE c1.page_1_main_category != c2.page_1_main_category 
                        AND c1.page_1_main_category != 'Unknown'
                        AND c2.page_1_main_category != 'Unknown'
                    GROUP BY c1.session_id, c1.page_1_main_category, c2.page_1_main_category
                )
                SELECT 
                    primary_category,
                    secondary_category,
                    COUNT(DISTINCT session_id) as sessions_with_both,
                    SUM(co_occurrence) as total_cross_views,
                    ROUND(AVG(co_occurrence), 2) as avg_cross_views_per_session
                FROM category_combinations
                GROUP BY primary_category, secondary_category
                HAVING sessions_with_both >= 5
                ORDER BY sessions_with_both DESC
                LIMIT 15
                """
                
                insights = [
                    "Cross-category browsing reveals related interests",
                    "Bundle opportunities in popular combinations",
                    "Customer journey spans multiple categories"
                ]
                
                metadata = {
                    "analysis_type": analysis_type,
                    "data_source": "clickstream",
                    "business_value": "Cross-selling and bundling opportunities"
                }
                
            else:
                return f"Invalid analysis type. Available: popularity, engagement, pricing, cross_category"
            
            result = self._execute_analytics_query(
                query,
                f"Product Performance: {analysis_type.title()}",
                insights,
                metadata
            )
            
            # Add products analyzed count to metadata
            result.metadata["products_analyzed"] = len(result.data)
            
            return self._format_analytics_output(result)
            
        except Exception as e:
            logger.error(f"Product performance analysis failed: {e}")
            return f"Error in product analysis: {str(e)}"


# Define MCP tools for analytics
def get_analytics_tools() -> List[Tool]:
    """Return list of analytics tools for MCP server."""
    return [
        Tool(
            name="user_segmentation",
            description="Segment users based on behavior patterns for targeted marketing and UX optimization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "segmentation_type": {
                        "type": "string",
                        "description": "Type of segmentation analysis",
                        "enum": ["engagement", "value", "exploration", "geographic"],
                        "default": "engagement"
                    }
                }
            }
        ),
        Tool(
            name="conversion_funnel",
            description="Analyze conversion funnels and identify user journey drop-off points.",
            inputSchema={
                "type": "object",
                "properties": {
                    "funnel_type": {
                        "type": "string",
                        "description": "Type of funnel analysis to perform",
                        "enum": ["standard", "product", "price", "category"],
                        "default": "standard"
                    }
                }
            }
        ),
        Tool(
            name="geographic_analysis",
            description="Analyze geographic patterns, market opportunities, and regional behavior differences.",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of geographic analysis",
                        "enum": ["overview", "preferences", "behavior", "market_size"],
                        "default": "overview"
                    }
                }
            }
        ),
        Tool(
            name="product_performance",
            description="Analyze product popularity, engagement metrics, and cross-category patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of product performance analysis",
                        "enum": ["popularity", "engagement", "pricing", "cross_category"],
                        "default": "popularity"
                    }
                }
            }
        )
    ]

# Create global analytics service instance for backward compatibility
_analytics_service = None

def get_analytics_service() -> AnalyticsService:
    """Get or create the global analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

# Wrapper functions for backward compatibility with main.py
async def user_segmentation(segmentation_type: str = "engagement") -> str:
    return await get_analytics_service().user_segmentation(segmentation_type)

async def conversion_funnel(funnel_type: str = "standard") -> str:
    return await get_analytics_service().conversion_funnel(funnel_type)

async def geographic_analysis(analysis_type: str = "overview") -> str:
    return await get_analytics_service().geographic_analysis(analysis_type)

async def product_performance(analysis_type: str = "popularity") -> str:
    return await get_analytics_service().product_performance(analysis_type)

# Export the tools list for backward compatibility
ANALYTICS_TOOLS = get_analytics_tools() 