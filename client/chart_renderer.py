"""
Chart Rendering Component for MCP Database Analytics Client

This module handles the display and rendering of charts received from the MCP server.
Supports both matplotlib and plotly rendering with automatic format detection.
"""

import base64
import io
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union
import logging

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import numpy as np

from config import ClientConfig

logger = logging.getLogger(__name__)

class ChartRenderer:
    """Chart renderer for displaying MCP server visualization responses"""
    
    def __init__(self, display_method: str = None):
        self.display_method = display_method or ClientConfig.CHART_DISPLAY_METHOD
        self.chart_counter = 0
        ClientConfig.setup_directories()
    
    def render_chart(self, image_data: str, title: str = "Chart", show: bool = True, save: bool = True) -> Optional[Path]:
        """
        Render a chart from base64 image data
        
        Args:
            image_data: Base64 encoded image data
            title: Chart title for display and saving
            show: Whether to display the chart
            save: Whether to save the chart to disk
            
        Returns:
            Path to saved chart file if saved, None otherwise
        """
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Load image using PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for matplotlib
            img_array = np.array(image)
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=ClientConfig.CHART_FIGSIZE, dpi=ClientConfig.CHART_DPI)
            ax.imshow(img_array)
            ax.axis('off')  # Hide axes for clean display
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            saved_path = None
            
            # Save chart if requested
            if save:
                saved_path = self._save_chart(fig, title)
            
            # Display chart if requested
            if show:
                self._display_chart(fig, title)
            
            return saved_path
            
        except Exception as e:
            logger.error(f"Error rendering chart: {e}")
            raise ChartRenderingError(f"Failed to render chart: {str(e)}")
    
    def render_multiple_charts(
        self, 
        chart_data: List[Tuple[str, str]], 
        show: bool = True, 
        save: bool = True
    ) -> List[Optional[Path]]:
        """
        Render multiple charts in a grid layout
        
        Args:
            chart_data: List of (image_data, title) tuples
            show: Whether to display the charts
            save: Whether to save individual charts
            
        Returns:
            List of paths to saved chart files
        """
        try:
            saved_paths = []
            
            # Calculate grid layout
            n_charts = len(chart_data)
            n_cols = min(2, n_charts)
            n_rows = (n_charts + n_cols - 1) // n_cols
            
            # Create subplots
            fig, axes = plt.subplots(
                n_rows, n_cols, 
                figsize=(ClientConfig.CHART_FIGSIZE[0] * n_cols, ClientConfig.CHART_FIGSIZE[1] * n_rows),
                dpi=ClientConfig.CHART_DPI
            )
            
            # Ensure axes is always a list
            if n_charts == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = list(axes)
            else:
                axes = axes.flatten()
            
            # Render each chart
            for i, (image_data, title) in enumerate(chart_data):
                try:
                    # Decode and load image
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    img_array = np.array(image)
                    
                    # Display in subplot
                    axes[i].imshow(img_array)
                    axes[i].axis('off')
                    axes[i].set_title(title, fontsize=12, fontweight='bold')
                    
                    # Save individual chart if requested
                    if save:
                        individual_path = self.render_chart(image_data, title, show=False, save=True)
                        saved_paths.append(individual_path)
                    else:
                        saved_paths.append(None)
                        
                except Exception as e:
                    logger.error(f"Error rendering chart {i}: {e}")
                    axes[i].text(0.5, 0.5, f"Error: {str(e)}", 
                               transform=axes[i].transAxes, ha='center', va='center')
                    axes[i].axis('off')
                    saved_paths.append(None)
            
            # Hide unused subplots
            for i in range(len(chart_data), len(axes)):
                axes[i].axis('off')
            
            plt.suptitle("Analytics Dashboard", fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Display combined chart if requested
            if show:
                self._display_chart(fig, "Multiple Charts")
            
            return saved_paths
            
        except Exception as e:
            logger.error(f"Error rendering multiple charts: {e}")
            raise ChartRenderingError(f"Failed to render multiple charts: {str(e)}")
    
    def _save_chart(self, fig, title: str) -> Path:
        """Save chart to disk with automatic naming"""
        try:
            # Create safe filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            self.chart_counter += 1
            filename = f"chart_{self.chart_counter:03d}_{safe_title}.png"
            
            save_path = ClientConfig.CHART_SAVE_DIR / filename
            
            fig.savefig(
                save_path,
                dpi=ClientConfig.CHART_DPI,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            logger.info(f"Chart saved to: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            return None
    
    def _display_chart(self, fig, title: str):
        """Display chart using matplotlib"""
        try:
            if self.display_method in ["matplotlib", "both"]:
                plt.show()
            
            # Note: Additional display methods (like plotly) could be added here
            
        except Exception as e:
            logger.error(f"Error displaying chart: {e}")
    
    def show_chart_info(self, image_data: str) -> dict:
        """Get information about a chart without rendering it"""
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "data_size": len(image_bytes),
                "data_size_mb": len(image_bytes) / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error getting chart info: {e}")
            return {"error": str(e)}
    
    def clear_saved_charts(self) -> int:
        """Clear all saved charts from the charts directory"""
        try:
            count = 0
            for chart_file in ClientConfig.CHART_SAVE_DIR.glob("chart_*.png"):
                chart_file.unlink()
                count += 1
            
            logger.info(f"Cleared {count} saved charts")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing charts: {e}")
            return 0

class ChartRenderingError(Exception):
    """Custom exception for chart rendering errors"""
    pass

# Helper functions for easy usage
def render_chart_from_response(image_data: str, title: str = "Chart") -> Optional[Path]:
    """Convenience function to render a single chart"""
    renderer = ChartRenderer()
    return renderer.render_chart(image_data, title)

def render_charts_from_responses(chart_responses: List[Tuple[str, str]]) -> List[Optional[Path]]:
    """Convenience function to render multiple charts"""
    renderer = ChartRenderer()
    return renderer.render_multiple_charts(chart_responses) 