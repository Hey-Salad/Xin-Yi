# 仓库管理系统 / Warehouse Management System

一个基于 Python Flask + SQLite 的智能硬件仓库管理系统仪表盘。

> **English documentation available:** See [README_EN.md](README_EN.md) for English version.

---

## 功能特性

- 📊 **实时统计**：库存总量、今日出入库、库存预警
- 📈 **趋势分析**：近7天出入库趋势可视化
- 🥧 **分类分布**：库存类型占比饼图
- 📋 **TOP10展示**：库存最多的物料排行
- ⚠️ **预警列表**：低于安全库存的物料提醒
- 🔧 **MCP集成**：支持AI助手通过模型上下文协议集成

## 技术栈

### 后端
- Python 3.12
- Flask (Web框架)
- SQLite (数据库)
- uv (包管理工具)
- FastMCP (MCP服务器)

### 前端
- 原生 HTML/CSS/JavaScript
- ECharts (图表库)
- 响应式设计

## 快速开始

### 1. 一键启动

```bash
./start.sh
```

启动后访问：http://localhost:2125

### 2. 手动启动

#### 初始化数据库
```bash
cd backend
uv run python database.py
```

#### 启动后端服务（端口 2124）
```bash
cd backend
uv run python app.py
```

#### 启动前端服务（端口 2125）
```bash
cd frontend
python3 server.py
```

## 项目结构

```
warehouse_system/
├── backend/              # 后端代码
│   ├── app.py           # Flask 应用主文件
│   ├── database.py      # 数据库初始化和数据生成
│   └── warehouse.db     # SQLite 数据库文件（运行后生成）
├── frontend/            # 前端代码
│   ├── index.html       # 主页面
│   ├── style.css        # 样式文件
│   ├── app.js           # JavaScript 逻辑
│   ├── product_detail.html  # 产品详情页
│   ├── product_detail.js    # 产品详情逻辑
│   └── server.py        # 静态文件服务器
├── mcp/                 # MCP 服务
│   ├── warehouse_mcp.py # MCP 服务器
│   ├── mcp_config.json  # MCP 配置
│   ├── mcp_pipe.py      # MCP 管道
│   └── MCP_README.md    # MCP 文档
├── test/                # 测试文件
│   ├── test_mcp.py      # MCP 测试
│   ├── test_api.py      # API 测试
│   ├── test_mcp_statistics.py  # MCP 统计测试
│   ├── run_all_tests.sh # 测试脚本
│   └── README.md        # 测试文档
├── start.sh             # 启动脚本
├── run_backend.py       # 后端启动器
├── pyproject.toml       # 项目依赖
├── README.md            # 项目说明（中文）
└── README_EN.md         # 项目说明（英文）
```

## 数据说明

### 物料分类
- **主板类**：watcher-xiaozhi主控板、扩展板、电源管理板等
- **传感器类**：摄像头、麦克风、PIR传感器、温湿度传感器等
- **外壳配件类**：外壳、支架、螺丝等
- **线材类**：USB线、电源线、排线等
- **包装类**：包装盒、说明书、保修卡等
- **电源类**：电源适配器、锂电池等
- **辅料类**：导热硅胶、绝缘胶带等
- **成品**：watcher-xiaozhi整机及各版本

### 初始数据量
- 物料种类：37种
- 总库存量：约3000+件
- 历史记录：近7天约100+条出入库记录
- watcher-xiaozhi相关库存：约80-100台成品 + 配套零部件

## API 接口

### 获取仪表盘统计
```
GET /api/dashboard/stats
```

### 获取类型分布
```
GET /api/dashboard/category-distribution
```

### 获取近7天趋势
```
GET /api/dashboard/weekly-trend
```

### 获取库存TOP10
```
GET /api/dashboard/top-stock
```

### 获取库存预警
```
GET /api/dashboard/low-stock-alert
```

### 获取所有物料
```
GET /api/materials/all
```

### 获取watcher-xiaozhi相关库存
```
GET /api/materials/xiaozhi
```

### 获取产品统计数据
```
GET /api/materials/product-stats?name=<产品名称>
```

### 获取产品趋势
```
GET /api/materials/product-trend?name=<产品名称>
```

### 获取产品出入库记录
```
GET /api/materials/product-records?name=<产品名称>
```

## MCP 集成

本系统提供 MCP（模型上下文协议）工具，可与 Claude Desktop 等 AI 助手集成。

### 可用的 MCP 工具

1. **query_xiaozhi_stock** - 查询产品库存
2. **stock_in** - 入库操作
3. **stock_out** - 出库操作
4. **list_xiaozhi_products** - 列出所有产品
5. **get_today_statistics** - 获取今日统计数据

### 配置 Claude Desktop

编辑 Claude Desktop 配置文件：

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

**重要：** 将 `cwd` 替换为你的实际项目路径！

### 使用示例

```
查询 watcher-xiaozhi(标准版) 的库存
```

```
watcher-xiaozhi(标准版) 采购到货 10 台，请帮忙入库
```

```
销售了 5 台 watcher-xiaozhi(标准版)，请出库
```

详见 `mcp/MCP_README.md` 和 `CLAUDE_DESKTOP_CONFIG.md` 获取完整的 MCP 文档。

## 停止服务

如果使用 `start.sh` 启动，按 `Ctrl+C` 即可停止所有服务。

如果手动启动，需要分别终止后端和前端进程。

## 测试

### 运行所有测试
```bash
./test/run_all_tests.sh
```

### 单独测试
```bash
# MCP 工具测试
python3 test/test_mcp.py

# API 接口测试
python3 test/test_api.py

# MCP 统计测试
python3 test/test_mcp_statistics.py
```

详见 `test/README.md` 获取详细测试文档。

## 注意事项

1. 确保端口 2124 和 2125 未被占用
2. 首次运行会自动创建数据库和初始数据
3. 数据库文件位于 `backend/warehouse.db`
4. 重新生成数据可删除数据库文件后重新运行

## 开发说明

### 重置数据库
```bash
rm backend/warehouse.db
cd backend
uv run python database.py
```

### 添加依赖
```bash
uv add <package_name>
```

### 安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 功能亮点

### 实时更新
- 前端每3秒自动刷新
- 库存列表自动更新
- 无需手动刷新

### 产品详情视图
- 点击库存列表中的任意产品
- 查看详细的出入库统计
- 7天趋势图表
- 最近交易记录

### 库存预警
- 可视化状态标签（正常/偏低/告急）
- 颜色编码警告
- 安全库存阈值监控

### 搜索与过滤
- 实时产品名称搜索
- 即时过滤结果
- 不区分大小写匹配

## 许可证

MIT License

## 文档

- `README.md` - 项目说明（中文）
- `README_EN.md` - 项目说明（英文）
- `mcp/MCP_README.md` - MCP 集成指南
- `CLAUDE_DESKTOP_CONFIG.md` - Claude Desktop 配置指南
- `test/README.md` - 测试文档
- `仓管 prompt 记录.md` - 开发提示词记录

## 支持

如有问题或疑问，请参考文档文件或查看测试脚本示例。
