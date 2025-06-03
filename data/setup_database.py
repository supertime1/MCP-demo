#!/usr/bin/env python3
"""
E-commerce Database Setup Script
Downloads UCI clickstream dataset and creates SQLite database for MCP demo
"""

import sqlite3
import requests
import os
import zipfile
import io
import csv
import random
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EcommerceDataSetup:
    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "ecommerce.db"
        self.schema_path = self.data_dir / "schema.sql"
        
        # UCI dataset download URLs
        self.dataset_info = {
            "name": "Clickstream Data for Online Shopping",
            "source": "UCI Machine Learning Repository",
            "csv_url": "https://archive.ics.uci.edu/static/public/553/clickstream+data+for+online+shopping.zip",
            "backup_sample": True  # Use sample data if download fails
        }
    
    def create_database(self) -> None:
        """Create SQLite database with schema"""
        logger.info(f"Creating database at {self.db_path}")
        
        # Read schema file
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Create database and execute schema
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(schema_sql)
            conn.commit()
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            raise
        finally:
            conn.close()
    
    def download_uci_dataset(self) -> Optional[List[Dict]]:
        """Download the real UCI clickstream dataset"""
        logger.info("Attempting to download UCI clickstream dataset...")
        
        try:
            # Download the ZIP file
            response = requests.get(self.dataset_info["csv_url"], timeout=30)
            response.raise_for_status()
            
            # Extract CSV from ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # Look for CSV file in the ZIP
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                if not csv_files:
                    logger.warning("No CSV file found in downloaded ZIP")
                    return None
                
                # Read the first CSV file
                csv_filename = csv_files[0]
                logger.info(f"Reading CSV file: {csv_filename}")
                
                with zip_file.open(csv_filename) as csv_file:
                    # Read CSV data - UCI dataset uses semicolon delimiter
                    csv_content = csv_file.read().decode('utf-8')
                    csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
                    
                    data = []
                    for row in csv_reader:
                        data.append(row)
                    
                    logger.info(f"Downloaded {len(data)} real clickstream records")
                    return data
        
        except Exception as e:
            logger.warning(f"Failed to download UCI dataset: {e}")
            logger.info("Will use sample data instead")
            return None
    
    def create_sample_data(self) -> List[Dict]:
        """
        Create sample data that matches the real dataset structure
        """
        logger.info("Creating sample e-commerce clickstream data")
        
        # Sample data configuration
        countries = ['Poland', 'Germany', 'UK', 'France', 'Czech Republic', 'Slovakia', 'Other']
        categories = ['Trousers', 'Knitwear', 'Skirts', 'Blouses', 'Sale', 'Dresses', 'Lingerie', 'Jackets']
        colors = ['black', 'navy', 'brown', 'white', 'grey', 'beige', 'pink', 'red', 'green']
        
        # Generate sample sessions (scaled for demo)
        n_sessions = 5000
        n_total_clicks = 25000
        
        data = []
        
        for _ in range(n_total_clicks):
            session_id = random.randint(1, n_sessions)
            data.append({
                'year': '2008',
                'month': str(random.randint(4, 8)),  # April to August
                'day': str(random.randint(1, 30)),
                'order': str(random.randint(1, 20)),  # Click sequence in session
                'country': random.choice(countries),
                'session ID': str(session_id),
                'page 1 (main category)': random.choice(categories) if random.random() > 0.3 else '',
                'page 2 (clothing model)': f"P{random.randint(1, 217)}" if random.random() > 0.4 else '',
                'colour': random.choice(colors) if random.random() > 0.5 else '',
                'location': str(random.randint(1, 6)) if random.random() > 0.3 else '',
                'model photography': random.choice(['model', 'no_model']) if random.random() > 0.6 else '',
                'price': str(round(random.uniform(20, 200), 2)) if random.random() > 0.4 else '',
                'price 2': str(round(random.uniform(20, 200), 2)) if random.random() > 0.7 else '',
                'page': random.choice(['category', 'product', 'cart', 'checkout']) if random.random() > 0.2 else ''
            })
        
        logger.info(f"Generated {len(data)} sample clickstream records")
        return data
    
    def clean_and_process_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Clean and process the raw data"""
        logger.info("Cleaning and processing data")
        
        processed_data = []
        
        for row in raw_data:
            # Handle UCI dataset column names (with proper mapping)
            session_id = row.get('session ID', '0')
            category = row.get('page 1 (main category)', '')
            product = row.get('page 2 (clothing model)', '')
            
            # Convert country codes to names (if needed)
            country_code = row.get('country', '0')
            country_map = {
                '1': 'Poland', '2': 'Germany', '3': 'UK', '4': 'France', 
                '5': 'Czech Republic', '6': 'Slovakia', '29': 'Other'
            }
            country = country_map.get(country_code, f'Country_{country_code}')
            
            # Convert category codes to names
            category_code = category
            category_map = {
                '1': 'Trousers', '2': 'Knitwear', '3': 'Skirts', '4': 'Blouses',
                '5': 'Sale', '6': 'Dresses', '7': 'Lingerie', '8': 'Jackets'
            }
            category_name = category_map.get(category_code, f'Category_{category_code}' if category_code else 'Unknown')
            
            # Convert color codes to names
            color_code = row.get('colour', '0')
            color_map = {
                '1': 'black', '2': 'navy', '3': 'brown', '4': 'white',
                '5': 'grey', '6': 'beige', '7': 'pink', '8': 'red', '9': 'green', '10': 'other'
            }
            color_name = color_map.get(color_code, f'Color_{color_code}' if color_code and color_code != '0' else 'Unknown')
            
            processed_row = {
                'year': int(row.get('year', 2008)),
                'month': int(row.get('month', 4)),
                'day': int(row.get('day', 1)),
                'order_sequence': int(row.get('order', 1)),
                'country': country,
                'session_id': int(session_id) if session_id.isdigit() else 0,
                'page_1_main_category': category_name,
                'page_2_clothing_model': product if product else 'Unknown',
                'colour': color_name,
                'location': int(row.get('location', 0)) if str(row.get('location', '0')).isdigit() else 0,
                'model_photography': 'model' if row.get('model photography', '0') == '1' else 'no_model',
                'price': float(row.get('price', 0)) if row.get('price', '').replace('.', '').isdigit() else 0.0,
                'price_2': float(row.get('price 2', 0)) if str(row.get('price 2', '')).replace('.', '').isdigit() else 0.0,
                'page': f"Page_{row.get('page', 'Unknown')}" if row.get('page') else 'Unknown'
            }
            processed_data.append(processed_row)
        
        logger.info(f"Processed {len(processed_data)} records")
        return processed_data
    
    def import_clickstream_data(self, data: List[Dict]) -> None:
        """Import clickstream data into database"""
        logger.info("Importing clickstream data into database")
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Insert clickstream data
            insert_query = """
            INSERT INTO clickstream 
            (year, month, day, order_sequence, country, session_id, page_1_main_category, 
             page_2_clothing_model, colour, location, model_photography, price, price_2, page)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for row in data:
                conn.execute(insert_query, (
                    row['year'], row['month'], row['day'], row['order_sequence'],
                    row['country'], row['session_id'], row['page_1_main_category'],
                    row['page_2_clothing_model'], row['colour'], row['location'],
                    row['model_photography'], row['price'], row['price_2'], row['page']
                ))
            
            # Generate analytics tables
            self.generate_analytics_tables(conn)
            
            conn.commit()
            logger.info("Data import completed successfully")
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            raise
        finally:
            conn.close()
    
    def generate_analytics_tables(self, conn: sqlite3.Connection) -> None:
        """Generate aggregated analytics tables"""
        logger.info("Generating analytics tables")
        
        # User sessions analytics
        sessions_query = """
        INSERT OR REPLACE INTO user_sessions 
        (session_id, country, start_date, total_clicks, unique_products_viewed, unique_categories_viewed)
        SELECT 
            session_id,
            country,
            DATE(year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) as start_date,
            COUNT(*) as total_clicks,
            COUNT(DISTINCT page_2_clothing_model) as unique_products_viewed,
            COUNT(DISTINCT page_1_main_category) as unique_categories_viewed
        FROM clickstream 
        GROUP BY session_id, country
        """
        
        # Product analytics
        product_query = """
        INSERT OR REPLACE INTO product_analytics 
        (product_code, category, total_views, unique_sessions, avg_price)
        SELECT 
            page_2_clothing_model as product_code,
            page_1_main_category as category,
            COUNT(*) as total_views,
            COUNT(DISTINCT session_id) as unique_sessions,
            AVG(CASE WHEN price > 0 THEN price END) as avg_price
        FROM clickstream 
        WHERE page_2_clothing_model != 'Unknown'
        GROUP BY page_2_clothing_model, page_1_main_category
        """
        
        # Country analytics  
        country_query = """
        INSERT OR REPLACE INTO country_analytics 
        (country, total_sessions, total_clicks, avg_session_length)
        SELECT 
            country,
            COUNT(DISTINCT session_id) as total_sessions,
            COUNT(*) as total_clicks,
            CAST(COUNT(*) AS REAL) / COUNT(DISTINCT session_id) as avg_session_length
        FROM clickstream 
        GROUP BY country
        """
        
        conn.execute(sessions_query)
        conn.execute(product_query) 
        conn.execute(country_query)
        
        logger.info("Analytics tables generated")
    
    def verify_data(self) -> None:
        """Verify the imported data"""
        logger.info("Verifying imported data")
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Check table counts
            tables = ['clickstream', 'user_sessions', 'product_analytics', 'country_analytics']
            
            for table in tables:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"{table}: {count} records")
            
            # Sample data verification
            cursor = conn.execute("SELECT * FROM clickstream LIMIT 5")
            sample_data = cursor.fetchall()
            logger.info(f"Sample clickstream data: {len(sample_data)} records shown")
            
            # Show some basic stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(DISTINCT country) as countries,
                    COUNT(DISTINCT page_1_main_category) as categories,
                    COUNT(DISTINCT session_id) as sessions
                FROM clickstream
            """)
            stats = cursor.fetchone()
            logger.info(f"Database contains data from {stats[0]} countries, {stats[1]} categories, {stats[2]} sessions")
            
        except Exception as e:
            logger.error(f"Error verifying data: {e}")
            raise
        finally:
            conn.close()
    
    def setup_complete_database(self) -> None:
        """Complete database setup process"""
        logger.info("Starting complete database setup")
        
        # Create database
        self.create_database()
        
        # Try to download real data, fall back to sample data
        raw_data = self.download_uci_dataset()
        if raw_data is None:
            raw_data = self.create_sample_data()
        
        # Process and import data
        processed_data = self.clean_and_process_data(raw_data)
        self.import_clickstream_data(processed_data)
        
        # Verify setup
        self.verify_data()
        
        logger.info("Database setup completed successfully!")
        logger.info(f"Database location: {self.db_path}")

def main():
    """Main setup function"""
    print("🛍️  E-commerce MCP Demo Database Setup")
    print("=====================================")
    print("📥 Downloading UCI clickstream dataset...")
    print("📊 (Will use sample data if download fails)")
    
    setup = EcommerceDataSetup()
    
    try:
        setup.setup_complete_database()
        print("\n✅ Database setup completed successfully!")
        print(f"📁 Database location: {setup.db_path}")
        print("\n🚀 Ready for MCP server setup!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 