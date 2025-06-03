-- E-commerce User Behavior Database Schema
-- Based on UCI Clickstream Data for Online Shopping
-- Dataset contains 165,474 user sessions from clothing e-commerce store

-- Main clickstream table
CREATE TABLE IF NOT EXISTS clickstream (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    order_sequence INTEGER NOT NULL,  -- sequence of clicks during one session
    country TEXT NOT NULL,
    session_id INTEGER NOT NULL,
    page_1_main_category TEXT,        -- main product category
    page_2_clothing_model TEXT,       -- product code (217 different products)
    colour TEXT,                      -- product color
    location INTEGER,                 -- photo location on page (1-6)
    model_photography TEXT,           -- model photography info
    price REAL,                       -- price in US dollars
    price_2 REAL,                     -- alternative price
    page TEXT,                        -- page type/name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_clickstream_session_id ON clickstream(session_id);
CREATE INDEX IF NOT EXISTS idx_clickstream_country ON clickstream(country);
CREATE INDEX IF NOT EXISTS idx_clickstream_date ON clickstream(year, month, day);
CREATE INDEX IF NOT EXISTS idx_clickstream_category ON clickstream(page_1_main_category);
CREATE INDEX IF NOT EXISTS idx_clickstream_product ON clickstream(page_2_clothing_model);

-- User sessions summary table (aggregated view)
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id INTEGER PRIMARY KEY,
    country TEXT NOT NULL,
    start_date DATE NOT NULL,
    total_clicks INTEGER NOT NULL,
    unique_products_viewed INTEGER,
    unique_categories_viewed INTEGER,
    session_duration_minutes REAL,
    converted BOOLEAN DEFAULT FALSE,  -- whether session resulted in purchase
    total_value REAL DEFAULT 0.0,    -- total value if converted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product analytics table
CREATE TABLE IF NOT EXISTS product_analytics (
    product_code TEXT PRIMARY KEY,
    category TEXT,
    total_views INTEGER DEFAULT 0,
    unique_sessions INTEGER DEFAULT 0,
    countries_sold TEXT,              -- JSON array of countries
    avg_price REAL,
    conversion_rate REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Country analytics table  
CREATE TABLE IF NOT EXISTS country_analytics (
    country TEXT PRIMARY KEY,
    total_sessions INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    avg_session_length REAL,
    conversion_rate REAL,
    popular_categories TEXT,          -- JSON array of top categories
    total_revenue REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create additional indexes for analytics tables
CREATE INDEX IF NOT EXISTS idx_user_sessions_country ON user_sessions(country);
CREATE INDEX IF NOT EXISTS idx_user_sessions_date ON user_sessions(start_date);
CREATE INDEX IF NOT EXISTS idx_user_sessions_converted ON user_sessions(converted);
CREATE INDEX IF NOT EXISTS idx_product_analytics_category ON product_analytics(category); 