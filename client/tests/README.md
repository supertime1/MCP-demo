# MCP Database Analytics Client - Test Suite

Comprehensive test suite for the MCP Database Analytics Client, providing automated testing for connection, tools execution, and interactive demo functionality.

## 🧪 Test Structure

```
client/tests/
├── __init__.py                 # Test package initialization
├── README.md                   # This documentation
├── run_all_tests.py           # Master test runner
├── test_connection.py         # Connection and initialization tests
├── test_tools_execution.py    # MCP tools functionality tests
└── test_interactive_demo.py   # Demo scenarios and UI tests
```

## 📋 Test Categories

### 1. Connection Tests (`test_connection.py`)
Tests basic MCP server connectivity and protocol compliance:
- **Basic Connection**: Server startup and session initialization
- **Tools Listing**: MCP tools discovery and enumeration
- **Resources Listing**: MCP resources availability
- **Simple Tool Call**: Basic tool execution validation

### 2. Tools Execution Tests (`test_tools_execution.py`)
Tests MCP tools functionality and database operations:
- **Database Tools**: SQL queries, schema access, sample data
- **Analytics Tools**: User segmentation, geographic analysis, product performance
- **Complex Queries**: Multi-table joins and aggregations
- **Error Handling**: Invalid input handling and graceful failures

### 3. Interactive Demo Tests (`test_interactive_demo.py`)
Tests demo scenarios and user interface functionality:
- **Demo Scenarios**: Common analytics demonstrations
- **Popular Queries**: Frequently used analytical queries
- **Schema Resources**: Database structure and sample data access

## 🚀 Running Tests

### Run All Tests
```bash
# From client/tests/ directory
python run_all_tests.py
```

### Run Individual Test Suites
```bash
# Connection tests only
python test_connection.py

# Tools execution tests only
python test_tools_execution.py

# Interactive demo tests only
python test_interactive_demo.py
```

### Run from Client Directory
```bash
# From client/ directory
python -m tests.run_all_tests
python -m tests.test_connection
python -m tests.test_tools_execution
python -m tests.test_interactive_demo
```

## 📊 Test Results

### Console Output
Tests provide real-time console output with:
- ✅ Success indicators with timing
- ❌ Failure indicators with error details
- 📊 Category-wise result summaries
- 🎯 Overall success rates and performance metrics

### Test Reports
Detailed JSON reports are saved as:
- `test_report_<timestamp>.json` - Complete test execution details
- Includes timing, success rates, and individual test results

## 🎯 Success Criteria

### Connection Tests (4 tests)
- Server connection and initialization
- Tools and resources discovery
- Basic tool execution

### Tools Execution Tests (11 tests)
- 4 Database tools tests
- 4 Analytics tools tests  
- 2 Complex queries tests
- 1 Error handling test

### Interactive Demo Tests (10 tests)
- 5 Demo scenario tests
- 3 Popular queries tests
- 2 Schema resource tests

**Total: 25 comprehensive tests**

## 🔧 Test Configuration

### Server Configuration
- **Server Path**: `../../server/main.py`
- **Transport**: stdio (JSON-RPC)
- **Timeout**: 30 seconds per test
- **Retries**: 3 attempts for failed connections

### Test Data
- **Database**: `../../server/ecommerce_behavior.db`
- **Records**: 165,474 e-commerce behavior records
- **Tables**: 5 tables (clickstream, user_sessions, products, categories, countries)

## 📈 Performance Benchmarks

### Expected Performance
- **Connection Tests**: ~2-5 seconds total
- **Tools Execution**: ~10-20 seconds total  
- **Demo Tests**: ~8-15 seconds total
- **Full Suite**: ~25-45 seconds total

### Success Rate Targets
- **Production Ready**: 100% success rate
- **Deployment Ready**: ≥95% success rate
- **Development**: ≥90% success rate

## 🛠️ Troubleshooting

### Common Issues

#### Server Connection Failures
```
❌ Connection failed: [Errno 2] No such file or directory
```
**Solution**: Ensure the MCP server is properly set up:
```bash
cd ../../server
python -m pip install -r requirements.txt
python main.py  # Test server startup
```

#### Database Access Errors
```
❌ Error: no such table: clickstream
```
**Solution**: Verify database file exists and has proper data:
```bash
ls -la ../../server/ecommerce_behavior.db
```

#### Import Errors
```
❌ ImportError: No module named 'mcp'
```
**Solution**: Install client dependencies:
```bash
cd ..
python -m pip install -r requirements.txt
```

### Debug Mode
For detailed debugging, add print statements or use Python debugger:
```python
import pdb; pdb.set_trace()  # Add to test files for debugging
```

## 🔄 Continuous Integration

### GitHub Actions
Include in CI pipeline:
```yaml
- name: Run MCP Client Tests
  run: |
    cd client/tests
    python run_all_tests.py
```

### Test Coverage
Current test coverage:
- **Connection**: 100% of connection scenarios
- **Tools**: 100% of available MCP tools
- **Demo**: 100% of common demo scenarios
- **Error Handling**: Key error conditions

## 📝 Contributing

### Adding New Tests
1. Create test methods in appropriate test file
2. Follow naming convention: `test_<functionality>`
3. Include timing and detailed result tracking
4. Update test counts in documentation

### Test Best Practices
- Use descriptive test names and docstrings
- Include both positive and negative test cases
- Provide meaningful error messages
- Test realistic user scenarios
- Measure and report performance

## 📞 Support

For test-related issues:
1. Check this README for common solutions
2. Review test output for specific error details
3. Verify server and database setup
4. Check MCP dependency versions

---

**Last Updated**: 2024-12-19  
**Test Suite Version**: 1.0.0  
**Compatible with**: MCP Database Analytics Server v1.0.0 