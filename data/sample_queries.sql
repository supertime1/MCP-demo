-- Sample Queries for E-commerce MCP Demo
-- These queries demonstrate analytics capabilities for the MCP server

-- =====================================================
-- BASIC DATA EXPLORATION QUERIES
-- =====================================================

-- 1. Get basic dataset statistics
SELECT 
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(DISTINCT country) as unique_countries,
    COUNT(DISTINCT page_1_main_category) as unique_categories,
    COUNT(DISTINCT page_2_clothing_model) as unique_products
FROM clickstream;

-- 2. Show data sample
SELECT * FROM clickstream LIMIT 10;

-- 3. Check data quality
SELECT 
    'clickstream' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN page_1_main_category IS NULL OR page_1_main_category = 'Unknown' THEN 1 END) as missing_category,
    COUNT(CASE WHEN price IS NULL OR price = 0 THEN 1 END) as missing_price
FROM clickstream;

-- =====================================================
-- GEOGRAPHIC ANALYSIS QUERIES
-- =====================================================

-- 4. Top countries by sessions
SELECT 
    country,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_clicks,
    ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT session_id), 2) as avg_clicks_per_session
FROM clickstream 
GROUP BY country 
ORDER BY total_sessions DESC 
LIMIT 10;

-- 5. Country conversion analysis (if we had purchase data)
SELECT 
    ca.country,
    ca.total_sessions,
    ca.avg_session_length,
    ROUND(ca.avg_session_length, 2) as avg_clicks_per_session
FROM country_analytics ca
ORDER BY ca.total_sessions DESC;

-- =====================================================
-- PRODUCT ANALYSIS QUERIES  
-- =====================================================

-- 6. Most popular product categories
SELECT 
    page_1_main_category as category,
    COUNT(*) as total_views,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(DISTINCT page_2_clothing_model) as unique_products
FROM clickstream 
WHERE page_1_main_category != 'Unknown'
GROUP BY page_1_main_category 
ORDER BY total_views DESC;

-- 7. Top products by views
SELECT 
    page_2_clothing_model as product_code,
    page_1_main_category as category,
    COUNT(*) as total_views,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(DISTINCT country) as countries_viewed_in
FROM clickstream 
WHERE page_2_clothing_model != 'Unknown'
GROUP BY page_2_clothing_model, page_1_main_category
ORDER BY total_views DESC 
LIMIT 20;

-- 8. Price analysis by category
SELECT 
    page_1_main_category as category,
    COUNT(CASE WHEN price > 0 THEN 1 END) as products_with_price,
    ROUND(AVG(CASE WHEN price > 0 THEN price END), 2) as avg_price,
    ROUND(MIN(CASE WHEN price > 0 THEN price END), 2) as min_price,
    ROUND(MAX(CASE WHEN price > 0 THEN price END), 2) as max_price
FROM clickstream 
WHERE page_1_main_category != 'Unknown'
GROUP BY page_1_main_category
HAVING COUNT(CASE WHEN price > 0 THEN 1 END) > 0
ORDER BY avg_price DESC;

-- =====================================================
-- USER BEHAVIOR ANALYSIS QUERIES
-- =====================================================

-- 9. Session length distribution
SELECT 
    CASE 
        WHEN total_clicks = 1 THEN '1 click'
        WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks'
        WHEN total_clicks BETWEEN 6 AND 10 THEN '6-10 clicks'
        WHEN total_clicks BETWEEN 11 AND 20 THEN '11-20 clicks'
        ELSE '20+ clicks'
    END as session_length_bucket,
    COUNT(*) as session_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM user_sessions
GROUP BY 
    CASE 
        WHEN total_clicks = 1 THEN '1 click'
        WHEN total_clicks BETWEEN 2 AND 5 THEN '2-5 clicks'
        WHEN total_clicks BETWEEN 6 AND 10 THEN '6-10 clicks'
        WHEN total_clicks BETWEEN 11 AND 20 THEN '11-20 clicks'
        ELSE '20+ clicks'
    END
ORDER BY session_count DESC;

-- 10. Daily activity patterns
SELECT 
    day,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_sessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage_of_traffic
FROM clickstream 
GROUP BY day 
ORDER BY day;

-- 11. Monthly trends
SELECT 
    month,
    CASE month 
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May' 
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
    END as month_name,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_sessions
FROM clickstream 
GROUP BY month 
ORDER BY month;

-- =====================================================
-- PAGE BEHAVIOR ANALYSIS
-- =====================================================

-- 12. Page location analysis (heat map data)
SELECT 
    location,
    COUNT(*) as total_clicks,
    COUNT(DISTINCT session_id) as unique_sessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as click_percentage
FROM clickstream 
WHERE location > 0
GROUP BY location 
ORDER BY location;

-- 13. Color preferences
SELECT 
    colour,
    COUNT(*) as total_views,
    COUNT(DISTINCT session_id) as unique_sessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as preference_percentage
FROM clickstream 
WHERE colour != 'Unknown' AND colour IS NOT NULL
GROUP BY colour 
ORDER BY total_views DESC;

-- =====================================================
-- FUNNEL ANALYSIS QUERIES
-- =====================================================

-- 14. User journey analysis (simplified funnel)
WITH session_pages AS (
    SELECT 
        session_id,
        MAX(CASE WHEN page_1_main_category != 'Unknown' THEN 1 ELSE 0 END) as viewed_category,
        MAX(CASE WHEN page_2_clothing_model != 'Unknown' THEN 1 ELSE 0 END) as viewed_product,
        MAX(CASE WHEN price > 0 THEN 1 ELSE 0 END) as saw_price
    FROM clickstream 
    GROUP BY session_id
)
SELECT 
    'Step 1: Category View' as funnel_step,
    SUM(viewed_category) as sessions,
    ROUND(SUM(viewed_category) * 100.0 / COUNT(*), 2) as conversion_rate
FROM session_pages
UNION ALL
SELECT 
    'Step 2: Product View' as funnel_step,
    SUM(viewed_product) as sessions,
    ROUND(SUM(viewed_product) * 100.0 / SUM(viewed_category), 2) as conversion_rate
FROM session_pages
WHERE viewed_category = 1
UNION ALL
SELECT 
    'Step 3: Price View' as funnel_step,
    SUM(saw_price) as sessions,
    ROUND(SUM(saw_price) * 100.0 / SUM(viewed_product), 2) as conversion_rate
FROM session_pages
WHERE viewed_product = 1;

-- =====================================================
-- COHORT AND SEGMENTATION QUERIES
-- =====================================================

-- 15. User engagement segmentation
SELECT 
    CASE 
        WHEN total_clicks = 1 THEN 'Bouncer'
        WHEN total_clicks BETWEEN 2 AND 5 THEN 'Browser'
        WHEN total_clicks BETWEEN 6 AND 15 THEN 'Engaged'
        ELSE 'Power User'
    END as user_segment,
    COUNT(*) as session_count,
    ROUND(AVG(total_clicks), 2) as avg_clicks,
    ROUND(AVG(unique_products_viewed), 2) as avg_products_viewed
FROM user_sessions
GROUP BY 
    CASE 
        WHEN total_clicks = 1 THEN 'Bouncer'
        WHEN total_clicks BETWEEN 2 AND 5 THEN 'Browser'
        WHEN total_clicks BETWEEN 6 AND 15 THEN 'Engaged'
        ELSE 'Power User'
    END
ORDER BY session_count DESC;

-- =====================================================
-- BUSINESS INTELLIGENCE QUERIES
-- =====================================================

-- 16. Cross-category interest analysis
SELECT 
    c1.page_1_main_category as primary_category,
    c2.page_1_main_category as secondary_category,
    COUNT(DISTINCT c1.session_id) as sessions_viewing_both
FROM clickstream c1
JOIN clickstream c2 ON c1.session_id = c2.session_id
WHERE c1.page_1_main_category != c2.page_1_main_category 
    AND c1.page_1_main_category != 'Unknown' 
    AND c2.page_1_main_category != 'Unknown'
GROUP BY c1.page_1_main_category, c2.page_1_main_category
HAVING COUNT(DISTINCT c1.session_id) >= 10
ORDER BY sessions_viewing_both DESC
LIMIT 20;

-- 17. International preferences comparison
SELECT 
    country,
    page_1_main_category as category,
    COUNT(*) as views,
    RANK() OVER (PARTITION BY country ORDER BY COUNT(*) DESC) as category_rank
FROM clickstream 
WHERE country IN ('Poland', 'Germany', 'UK', 'France')
    AND page_1_main_category != 'Unknown'
GROUP BY country, page_1_main_category
HAVING COUNT(*) >= 5
ORDER BY country, category_rank; 