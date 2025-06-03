"""
Visualization Tools for MCP Database Analytics Demo

This module provides MCP tools for creating various types of data visualizations
including charts, heatmaps, and funnel diagrams.
"""

import base64
import io
import json
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
from mcp.server.models import Tool
from mcp.types import TextContent, ImageContent
from config import DATABASE_PATH

# Set matplotlib style for better-looking charts
plt.style.use('default')
sns.set_palette("husl")


class VisualizationTools:
    """Collection of visualization tools for the MCP server."""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Execute a database query and return results as DataFrame."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn, params=params or ())
            conn.close()
            return df
        except Exception as e:
            raise Exception(f"Database query failed: {str(e)}")
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return img_str
    
    def _plotly_to_base64(self, fig) -> str:
        """Convert plotly figure to base64 string."""
        img_bytes = fig.to_image(format="png", width=800, height=600, scale=2)
        img_str = base64.b64encode(img_bytes).decode()
        return img_str

    async def create_chart(
        self,
        data_query: str,
        chart_type: str = "bar",
        title: str = "Chart",
        x_column: str = None,
        y_column: str = None,
        color_column: str = None,
        aggregation: str = "sum",
        limit: int = 20,
        width: int = 10,
        height: int = 6
    ) -> List[TextContent | ImageContent]:
        """
        Create various types of charts from database query results.
        
        Args:
            data_query: SQL query to fetch data
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', 'histogram')
            title: Chart title
            x_column: Column for x-axis (auto-detected if None)
            y_column: Column for y-axis (auto-detected if None)
            color_column: Column for color grouping
            aggregation: Aggregation method ('sum', 'count', 'avg', 'max', 'min')
            limit: Maximum number of data points
            width: Chart width in inches
            height: Chart height in inches
        """
        try:
            # Execute query and get data
            df = self._execute_query(data_query)
            
            if df.empty:
                return [TextContent(type="text", text="No data found for the given query.")]
            
            # Auto-detect columns if not specified
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if x_column is None:
                x_column = categorical_cols[0] if categorical_cols else df.columns[0]
            if y_column is None:
                y_column = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
            
            # Apply aggregation if needed
            if aggregation != "none" and x_column in categorical_cols and y_column in numeric_cols:
                if aggregation == "count":
                    df_agg = df.groupby(x_column).size().reset_index(name=y_column)
                elif aggregation == "sum":
                    df_agg = df.groupby(x_column)[y_column].sum().reset_index()
                elif aggregation == "avg":
                    df_agg = df.groupby(x_column)[y_column].mean().reset_index()
                elif aggregation == "max":
                    df_agg = df.groupby(x_column)[y_column].max().reset_index()
                elif aggregation == "min":
                    df_agg = df.groupby(x_column)[y_column].min().reset_index()
                else:
                    df_agg = df
            else:
                df_agg = df
            
            # Apply limit
            if len(df_agg) > limit:
                if chart_type in ['bar', 'pie'] and y_column in numeric_cols:
                    df_agg = df_agg.sort_values(y_column, ascending=False).head(limit)
                else:
                    df_agg = df_agg.head(limit)
            
            # Create chart based on type
            fig, ax = plt.subplots(figsize=(width, height))
            
            if chart_type == "bar":
                bars = ax.bar(df_agg[x_column], df_agg[y_column])
                ax.set_xlabel(x_column.replace('_', ' ').title())
                ax.set_ylabel(y_column.replace('_', ' ').title())
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.0f}', ha='center', va='bottom')
            
            elif chart_type == "line":
                ax.plot(df_agg[x_column], df_agg[y_column], marker='o', linewidth=2, markersize=6)
                ax.set_xlabel(x_column.replace('_', ' ').title())
                ax.set_ylabel(y_column.replace('_', ' ').title())
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
            
            elif chart_type == "pie":
                wedges, texts, autotexts = ax.pie(df_agg[y_column], labels=df_agg[x_column], 
                                                 autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                
                # Improve text readability
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            elif chart_type == "scatter":
                if len(numeric_cols) >= 2:
                    scatter = ax.scatter(df_agg[x_column], df_agg[y_column], 
                                       alpha=0.7, s=60, edgecolors='black', linewidth=0.5)
                    ax.set_xlabel(x_column.replace('_', ' ').title())
                    ax.set_ylabel(y_column.replace('_', ' ').title())
                    ax.grid(True, alpha=0.3)
                else:
                    return [TextContent(type="text", text="Scatter plot requires at least 2 numeric columns.")]
            
            elif chart_type == "histogram":
                ax.hist(df_agg[y_column], bins=min(30, len(df_agg)//2), 
                       alpha=0.7, edgecolor='black', linewidth=0.5)
                ax.set_xlabel(y_column.replace('_', ' ').title())
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            plt.tight_layout()
            
            # Convert to base64
            img_str = self._fig_to_base64(fig)
            
            # Create summary text
            summary = f"""Chart created successfully:
            - Type: {chart_type.title()}
            - Data points: {len(df_agg)}
            - X-axis: {x_column}
            - Y-axis: {y_column}
            - Aggregation: {aggregation}"""
            
            return [
                TextContent(type="text", text=summary),
                ImageContent(type="image", data=img_str, mimeType="image/png")
            ]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating chart: {str(e)}")]

    async def create_heatmap(
        self,
        data_query: str,
        title: str = "Heatmap",
        x_column: str = None,
        y_column: str = None,
        value_column: str = None,
        aggregation: str = "sum",
        colormap: str = "YlOrRd",
        width: int = 12,
        height: int = 8
    ) -> List[TextContent | ImageContent]:
        """
        Create a heatmap from database query results.
        
        Args:
            data_query: SQL query to fetch data
            title: Heatmap title
            x_column: Column for x-axis
            y_column: Column for y-axis
            value_column: Column for heatmap values
            aggregation: Aggregation method
            colormap: Matplotlib colormap name
            width: Chart width in inches
            height: Chart height in inches
        """
        try:
            df = self._execute_query(data_query)
            
            if df.empty:
                return [TextContent(type="text", text="No data found for the given query.")]
            
            # Auto-detect columns if not specified
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if x_column is None:
                x_column = categorical_cols[0] if categorical_cols else df.columns[0]
            if y_column is None:
                y_column = categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0]
            if value_column is None:
                value_column = numeric_cols[0] if numeric_cols else 'count'
            
            # Create pivot table
            if value_column == 'count':
                pivot_df = df.groupby([y_column, x_column]).size().unstack(fill_value=0)
            else:
                if aggregation == "sum":
                    pivot_df = df.groupby([y_column, x_column])[value_column].sum().unstack(fill_value=0)
                elif aggregation == "avg":
                    pivot_df = df.groupby([y_column, x_column])[value_column].mean().unstack(fill_value=0)
                elif aggregation == "count":
                    pivot_df = df.groupby([y_column, x_column])[value_column].count().unstack(fill_value=0)
                else:
                    pivot_df = df.groupby([y_column, x_column])[value_column].sum().unstack(fill_value=0)
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(width, height))
            
            heatmap = sns.heatmap(pivot_df, annot=True, fmt='.0f', cmap=colormap, 
                                 cbar_kws={'label': value_column.replace('_', ' ').title()},
                                 ax=ax, linewidths=0.5)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel(x_column.replace('_', ' ').title())
            ax.set_ylabel(y_column.replace('_', ' ').title())
            
            plt.tight_layout()
            
            # Convert to base64
            img_str = self._fig_to_base64(fig)
            
            summary = f"""Heatmap created successfully:
            - Dimensions: {pivot_df.shape[0]} x {pivot_df.shape[1]}
            - X-axis: {x_column}
            - Y-axis: {y_column}
            - Values: {value_column}
            - Aggregation: {aggregation}"""
                        
            return [
                TextContent(type="text", text=summary),
                ImageContent(type="image", data=img_str, mimeType="image/png")
            ]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating heatmap: {str(e)}")]

    async def create_funnel_chart(
        self,
        stages_query: str,
        title: str = "Conversion Funnel",
        stage_column: str = "stage",
        value_column: str = "count",
        width: int = 10,
        height: int = 8
    ) -> List[TextContent | ImageContent]:
        """
        Create a funnel chart showing conversion stages.
        
        Args:
            stages_query: SQL query returning funnel stages and values
            title: Chart title
            stage_column: Column containing stage names
            value_column: Column containing stage values
            width: Chart width in inches
            height: Chart height in inches
        """
        try:
            df = self._execute_query(stages_query)
            
            if df.empty:
                return [TextContent(type="text", text="No data found for the given query.")]
            
            # Sort by value descending (typical funnel order)
            df = df.sort_values(value_column, ascending=False)
            
            stages = df[stage_column].tolist()
            values = df[value_column].tolist()
            
            # Calculate conversion rates
            conversion_rates = []
            for i, value in enumerate(values):
                if i == 0:
                    conversion_rates.append(100.0)
                else:
                    rate = (value / values[0]) * 100
                    conversion_rates.append(rate)
            
            # Create funnel using Plotly for better funnel visualization
            fig = go.Figure(go.Funnel(
                y=stages,
                x=values,
                textinfo="value+percent initial",
                texttemplate='%{label}<br>%{value:,}<br>(%{percentInitial})',
                textfont=dict(size=12),
                connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}},
                marker={"color": ["deepskyblue", "lightsalmon", "tan", "teal", "silver"],
                       "line": {"color": ["wheat", "wheat", "wheat", "wheat", "wheat"], "width": 2}}
            ))
            
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'family': 'Arial, sans-serif'}
                },
                font=dict(size=12),
                width=width * 80,
                height=height * 80,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            # Convert to base64
            img_str = self._plotly_to_base64(fig)
            
            # Calculate drop-off rates
            dropoff_analysis = []
            for i in range(len(stages) - 1):
                current_stage = stages[i]
                next_stage = stages[i + 1]
                current_value = values[i]
                next_value = values[i + 1]
                dropoff = current_value - next_value
                dropoff_rate = (dropoff / current_value) * 100 if current_value > 0 else 0
                
                dropoff_analysis.append(f"• {current_stage} → {next_stage}: {dropoff:,} users dropped ({dropoff_rate:.1f}%)")
            
            summary = f"""Funnel chart created successfully:

            **Conversion Summary:**
            - Total stages: {len(stages)}
            - Top of funnel: {values[0]:,} users
            - Bottom of funnel: {values[-1]:,} users
            - Overall conversion rate: {conversion_rates[-1]:.1f}%

            **Stage-by-stage drop-off:**
            {chr(10).join(dropoff_analysis)}

            **Conversion rates by stage:**
            {chr(10).join([f"• {stage}: {rate:.1f}%" for stage, rate in zip(stages, conversion_rates)])}"""
            
            return [
                TextContent(type="text", text=summary),
                ImageContent(type="image", data=img_str, mimeType="image/png")
            ]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating funnel chart: {str(e)}")]

    async def create_time_series(
        self,
        data_query: str,
        title: str = "Time Series",
        date_column: str = "date",
        value_column: str = "value",
        groupby_column: str = None,
        date_format: str = "%Y-%m-%d",
        width: int = 12,
        height: int = 6
    ) -> List[TextContent | ImageContent]:
        """
        Create a time series chart from database query results.
        
        Args:
            data_query: SQL query to fetch time series data
            title: Chart title
            date_column: Column containing dates
            value_column: Column containing values
            groupby_column: Optional column for multiple series
            date_format: Date format string
            width: Chart width in inches
            height: Chart height in inches
        """
        try:
            df = self._execute_query(data_query)
            
            if df.empty:
                return [TextContent(type="text", text="No data found for the given query.")]
            
            # Convert date column to datetime
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.sort_values(date_column)
            
            fig, ax = plt.subplots(figsize=(width, height))
            
            if groupby_column and groupby_column in df.columns:
                # Multiple series
                for group in df[groupby_column].unique():
                    group_data = df[df[groupby_column] == group]
                    ax.plot(group_data[date_column], group_data[value_column], 
                           marker='o', label=str(group), linewidth=2, markersize=4)
                ax.legend(title=groupby_column.replace('_', ' ').title())
            else:
                # Single series
                ax.plot(df[date_column], df[value_column], 
                       marker='o', linewidth=2, markersize=4, color='steelblue')
            
            ax.set_xlabel('Date')
            ax.set_ylabel(value_column.replace('_', ' ').title())
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Convert to base64
            img_str = self._fig_to_base64(fig)
            
            # Calculate basic statistics
            date_range = f"{df[date_column].min().strftime('%Y-%m-%d')} to {df[date_column].max().strftime('%Y-%m-%d')}"
            total_points = len(df)
            avg_value = df[value_column].mean()
            
            summary = f"""Time series chart created successfully:
            - Date range: {date_range}
            - Data points: {total_points}
            - Average value: {avg_value:.2f}
            - Series: {len(df[groupby_column].unique()) if groupby_column else 1}"""
            
            return [
                TextContent(type="text", text=summary),
                ImageContent(type="image", data=img_str, mimeType="image/png")
            ]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating time series chart: {str(e)}")]


# MCP Tool Definitions
def get_visualization_tools() -> List[Tool]:
    """Return list of visualization tools for MCP server."""
    
    return [
        Tool(
            name="create_chart",
            description="Create various types of charts (bar, line, pie, scatter, histogram) from database query results",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_query": {
                        "type": "string",
                        "description": "SQL query to fetch data for the chart"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "pie", "scatter", "histogram"],
                        "default": "bar",
                        "description": "Type of chart to create"
                    },
                    "title": {
                        "type": "string",
                        "default": "Chart",
                        "description": "Chart title"
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column for x-axis (auto-detected if not specified)"
                    },
                    "y_column": {
                        "type": "string", 
                        "description": "Column for y-axis (auto-detected if not specified)"
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": ["sum", "count", "avg", "max", "min", "none"],
                        "default": "sum",
                        "description": "Aggregation method for grouped data"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum number of data points to display"
                    }
                },
                "required": ["data_query"]
            }
        ),
        
        Tool(
            name="create_heatmap",
            description="Create a heatmap visualization from database query results",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_query": {
                        "type": "string",
                        "description": "SQL query to fetch data for the heatmap"
                    },
                    "title": {
                        "type": "string",
                        "default": "Heatmap",
                        "description": "Heatmap title"
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column for x-axis (auto-detected if not specified)"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Column for y-axis (auto-detected if not specified)" 
                    },
                    "value_column": {
                        "type": "string",
                        "description": "Column for heatmap values (auto-detected if not specified)"
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": ["sum", "count", "avg"],
                        "default": "sum",
                        "description": "Aggregation method for grouped data"
                    },
                    "colormap": {
                        "type": "string",
                        "default": "YlOrRd",
                        "description": "Matplotlib colormap name"
                    }
                },
                "required": ["data_query"]
            }
        ),
        
        Tool(
            name="create_funnel_chart",
            description="Create a conversion funnel chart showing stages and drop-off rates",
            inputSchema={
                "type": "object", 
                "properties": {
                    "stages_query": {
                        "type": "string",
                        "description": "SQL query returning funnel stages and values"
                    },
                    "title": {
                        "type": "string",
                        "default": "Conversion Funnel",
                        "description": "Chart title"
                    },
                    "stage_column": {
                        "type": "string",
                        "default": "stage",
                        "description": "Column containing stage names"
                    },
                    "value_column": {
                        "type": "string", 
                        "default": "count",
                        "description": "Column containing stage values"
                    }
                },
                "required": ["stages_query"]
            }
        ),
        
        Tool(
            name="create_time_series",
            description="Create a time series chart from database query results",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_query": {
                        "type": "string",
                        "description": "SQL query to fetch time series data"
                    },
                    "title": {
                        "type": "string",
                        "default": "Time Series",
                        "description": "Chart title"
                    },
                    "date_column": {
                        "type": "string",
                        "default": "date", 
                        "description": "Column containing dates"
                    },
                    "value_column": {
                        "type": "string",
                        "default": "value",
                        "description": "Column containing values"
                    },
                    "groupby_column": {
                        "type": "string",
                        "description": "Optional column for multiple series"
                    }
                },
                "required": ["data_query"]
            }
        )
    ] 