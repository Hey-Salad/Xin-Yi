<img src="https://raw.githubusercontent.com/Hey-Salad/.github/refs/heads/main/HeySalad%20Logo%20%2B%20Tagline%20Black.svg" alt="HeySalad Logo" width="400"/>

# Xin Yi WMS® - Intelligent Food Warehouse Management 🥗

> **AI-powered warehouse management system designed for fresh food logistics with FEFO intelligence**

An intelligent hardware warehouse management dashboard based on Python Flask + Supabase PostgreSQL.

## Features

- 📊 **Real-time Statistics**: Total inventory, daily in/out, stock alerts
- 📈 **Trend Analysis**: 7-day in/out trend visualization
- 🥧 **Category Distribution**: Inventory type distribution pie chart
- 📋 **TOP10 Display**: Top 10 materials by stock quantity
- ⚠️ **Alert List**: Low stock warnings below safety threshold
- 🔧 **MCP Integration**: Model Context Protocol for AI assistant integration

## Tech Stack

### Backend
- Python 3.12
- Flask (Web Framework)
- SQLite (Database)
- uv (Package Manager)
- FastMCP (MCP Server)

### Frontend
- Native HTML/CSS/JavaScript
- ECharts (Chart Library)
- Responsive Design

## Quick Start

### 1. One-Click Launch

```bash
./start.sh
```

Access at: http://localhost:2125

### 2. Manual Launch

#### Initialize Database
```bash
cd backend
uv run python database.py
```

#### Start Backend Service (Port 2124)
```bash
cd backend
uv run python app.py
```

#### Start Frontend Service (Port 2125)
```bash
cd frontend
python3 server.py
```

## Project Structure

```
warehouse_system/
├── backend/              # Backend code
│   ├── app.py           # Flask application main file
│   ├── database.py      # Database initialization and data generation
│   └── warehouse.db     # SQLite database file (generated after running)
├── frontend/            # Frontend code
│   ├── index.html       # Main page
│   ├── style.css        # Stylesheet
│   ├── app.js           # JavaScript logic
│   ├── product_detail.html  # Product detail page
│   ├── product_detail.js    # Product detail logic
│   └── server.py        # Static file server
├── mcp/                 # MCP service
│   ├── warehouse_mcp.py # MCP server
│   ├── mcp_config.json  # MCP configuration
│   ├── mcp_pipe.py      # MCP pipe
│   └── MCP_README.md    # MCP documentation
├── test/                # Test files
│   ├── test_mcp.py      # MCP tests
│   ├── test_api.py      # API tests
│   ├── test_mcp_statistics.py  # MCP statistics tests
│   ├── run_all_tests.sh # Test script
│   └── README.md        # Test documentation
├── start.sh             # Startup script
├── run_backend.py       # Backend runner
├── pyproject.toml       # Project dependencies
└── README.md            # Project documentation (Chinese)
```

## Data Description

### Material Categories
- **Mainboard**: watcher-xiaozhi main control board, expansion board, power management board, etc.
- **Sensors**: Camera, microphone, PIR sensor, temperature/humidity sensor, etc.
- **Shell & Accessories**: Shell, bracket, screws, etc.
- **Cables**: USB cable, power cable, FPC cable, etc.
- **Packaging**: Packaging box, manual, warranty card, etc.
- **Power**: Power adapter, lithium battery, etc.
- **Auxiliary Materials**: Thermal paste, insulation tape, etc.
- **Finished Products**: watcher-xiaozhi complete units and versions

### Initial Data Volume
- Material types: 37 types
- Total inventory: ~3000+ items
- Historical records: ~100+ in/out records in the last 7 days
- watcher-xiaozhi related inventory: ~80-100 finished units + supporting components

## API Endpoints

### Get Dashboard Statistics
```
GET /api/dashboard/stats
```

### Get Category Distribution
```
GET /api/dashboard/category-distribution
```

### Get 7-Day Trend
```
GET /api/dashboard/weekly-trend
```

### Get Top 10 Stock
```
GET /api/dashboard/top-stock
```

### Get Low Stock Alert
```
GET /api/dashboard/low-stock-alert
```

### Get All Materials
```
GET /api/materials/all
```

### Get watcher-xiaozhi Related Inventory
```
GET /api/materials/xiaozhi
```

### Get Product Statistics
```
GET /api/materials/product-stats?name=<product_name>
```

### Get Product Trend
```
GET /api/materials/product-trend?name=<product_name>
```

### Get Product Records
```
GET /api/materials/product-records?name=<product_name>
```

## MCP Integration

This system provides MCP (Model Context Protocol) tools for AI assistants like Claude Desktop.

### Available MCP Tools

1. **query_xiaozhi_stock** - Query product inventory
2. **stock_in** - Stock in operation
3. **stock_out** - Stock out operation
4. **list_xiaozhi_products** - List all products
5. **get_today_statistics** - Get today's statistics

### Configure Claude Desktop

Edit Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "warehouse-system": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "warehouse_mcp.py"],
      "cwd": "/path/to/your/warehouse_system/mcp"
    }
  }
}
```

**Important:** Replace `cwd` with your actual project path!

### Usage Examples

```
Query watcher-xiaozhi(标准版) inventory
```

```
Stock in 10 units of watcher-xiaozhi(标准版), reason: new purchase arrived
```

```
Stock out 5 units of watcher-xiaozhi(标准版) for sales
```

See `mcp/MCP_README.md` and `CLAUDE_DESKTOP_CONFIG.md` for detailed MCP documentation.

## Testing

### Run All Tests
```bash
./test/run_all_tests.sh
```

### Individual Tests
```bash
# MCP tool tests
python3 test/test_mcp.py

# API interface tests
python3 test/test_api.py

# MCP statistics tests
python3 test/test_mcp_statistics.py
```

See `test/README.md` for detailed test documentation.

## Stop Services

If started with `start.sh`, press `Ctrl+C` to stop all services.

If started manually, terminate backend and frontend processes separately.

## Notes

1. Ensure ports 2124 and 2125 are not occupied
2. Database and initial data are created automatically on first run
3. Database file is located at `backend/warehouse.db`
4. To regenerate data, delete the database file and run again

## Development

### Reset Database
```bash
rm backend/warehouse.db
cd backend
uv run python database.py
```

### Add Dependencies
```bash
uv add <package_name>
```

### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Features Highlights

### Real-time Updates
- Frontend auto-refreshes every 3 seconds
- Inventory list updates automatically
- No manual refresh needed

### Product Detail View
- Click any product in the inventory list
- View detailed in/out statistics
- 7-day trend chart
- Recent transaction records

### Stock Alerts
- Visual status badges (Normal/Low/Critical)
- Color-coded warnings
- Safety stock threshold monitoring

### Search & Filter
- Real-time product name search
- Instant filtering results
- Case-insensitive matching

## License

MIT License

## Documentation

- `README.md` - Project documentation (Chinese)
- `README_EN.md` - Project documentation (English)
- `mcp/MCP_README.md` - MCP integration guide
- `CLAUDE_DESKTOP_CONFIG.md` - Claude Desktop configuration guide
- `test/README.md` - Testing documentation
- `仓管 prompt 记录.md` - Development prompt history (Chinese)

## Support

For issues or questions, please refer to the documentation files or check the test scripts for examples.
