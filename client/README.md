# MCP Database Analytics Client

A natural language interface for querying e-commerce analytics data through the Model Context Protocol (MCP).

## Features

🤖 **Natural Language Queries** - Ask questions in plain English  
📊 **Rich Visualizations** - Automatic chart generation and display  
💬 **Interactive Chat** - Rich terminal interface with suggestions  
📈 **Chart Rendering** - Matplotlib integration with save functionality  
📝 **Query History** - Persistent history with session statistics  
🔧 **CLI Interface** - Command-line options for automation  

## Quick Start

### 1. Install Dependencies

```bash
cd client
pip install -r requirements.txt
```

### 2. Start Interactive Mode

```bash
python main.py
```

### 3. Ask Questions

```
🤖 Ask me anything: Show me the top countries by user sessions
🤖 Ask me anything: Create a chart of daily activity trends
🤖 Ask me anything: What are the most popular product categories?
```

## Usage Examples

### Interactive Mode (Default)
```bash
python main.py
```

### Single Query Mode
```bash
python main.py --query "Show me user activity by country"
python main.py --query "Create a funnel chart for conversions"
```

### Debug Mode
```bash
python main.py --debug
```

### Disable Charts
```bash
python main.py --no-charts
```

## Sample Queries

### Data Exploration
- "Show me the database schema"
- "Give me sample data from the clickstream table"
- "How many records are in the database?"

### Country Analysis
- "Show me the top 5 countries by user sessions"
- "Create a chart of user activity by country"
- "What countries have the most engagement?"

### Product Analysis
- "What are the most popular product categories?"
- "Show me product performance analytics"
- "Create a chart of category preferences"

### Time-based Analysis
- "Show me daily activity trends"
- "Create a time series of user behavior"
- "How does activity vary by day?"

### Advanced Visualizations
- "Create a heatmap of user interactions"
- "Show me a conversion funnel chart"
- "Visualize geographic user distribution"

### User Behavior
- "Analyze user segmentation patterns"
- "Show me conversion funnel analysis"
- "What's the average session behavior?"

## Chat Commands

### Help & Navigation
- `help` or `?` - Show help information
- `suggestions` - Display sample queries
- `clear` - Clear the screen

### History & Stats
- `history` - Show recent queries
- `stats` - Display session statistics

### Chart Management
- `clear charts` - Remove all saved charts

### Exit
- `exit`, `quit`, or `Ctrl+C` - Exit the application

## File Structure

```
client/
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── mcp_client.py        # Core MCP client implementation
├── chat_interface.py    # Rich terminal interface
├── chart_renderer.py    # Chart rendering and display
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── charts/             # Saved charts (auto-created)
└── .query_history      # Query history (auto-created)
```

## Configuration

The client can be configured through `config.py`:

### Chart Settings
- `CHART_DISPLAY_METHOD` - "matplotlib", "plotly", or "both"
- `CHART_DPI` - Chart resolution (default: 150)
- `CHART_FIGSIZE` - Chart dimensions (default: 10x6)

### Server Connection
- `SERVER_TIMEOUT` - Connection timeout in seconds
- `SERVER_SCRIPT` - Path to MCP server script

### UI Settings
- `MAX_HISTORY_SIZE` - Number of queries to remember
- `MAX_RESPONSE_LENGTH` - Text truncation limit

## Error Handling

The client includes comprehensive error handling:

- **Connection Issues** - Clear messages about server connectivity
- **Query Errors** - Helpful suggestions for query reformulation
- **Chart Errors** - Graceful fallback when visualizations fail
- **Timeout Handling** - Automatic retry and timeout management

## Development

### Environment Variables

```bash
export MCP_CLIENT_ENV=development  # Extended timeouts
export MCP_CLIENT_ENV=demo         # High-resolution charts
```

### Debug Mode

```bash
python main.py --debug
```

Shows detailed logging including:
- MCP protocol messages
- Query routing decisions
- Chart rendering details
- Error stack traces

## Architecture

### MCP Client (`mcp_client.py`)
- Handles MCP protocol communication
- Routes natural language queries to appropriate tools
- Manages server connection lifecycle

### Chat Interface (`chat_interface.py`)
- Rich terminal UI with colors and formatting
- Query history and session management
- Special command handling

### Chart Renderer (`chart_renderer.py`)
- Processes base64 image data from server
- Matplotlib integration for display
- File management for saved charts

### Main Application (`main.py`)
- CLI argument parsing
- Application lifecycle management
- Error handling and logging

## Performance

- **Query Processing**: ~1-2 seconds typical
- **Chart Generation**: ~2-3 seconds including rendering
- **Memory Usage**: ~50-100MB during operation
- **Chart File Size**: ~150KB average PNG files

## Troubleshooting

### Server Connection Failed
```
❌ Failed to connect to MCP server
```
**Solution**: Ensure you're in the correct directory and the server dependencies are installed.

### Charts Not Displaying
```
📈 Error generating chart
```
**Solution**: Check that matplotlib is properly installed and you have display capabilities.

### Query Not Understood
```
❓ Invalid query format
```
**Solution**: Try rephrasing your question or use `suggestions` for examples.

## Roadmap

- [ ] LLM-enhanced query routing
- [ ] Plotly integration for interactive charts
- [ ] Query auto-completion
- [ ] Custom visualization templates
- [ ] Export functionality (PDF, CSV)
- [ ] Multi-language support 