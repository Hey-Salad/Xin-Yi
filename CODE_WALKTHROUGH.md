# Code Walkthrough - Warehouse Management System

## Overview | 概述

This document provides a detailed walkthrough of how the warehouse management system works, with bilingual explanations.

本文档详细介绍仓库管理系统的工作原理，提供双语解释。

---

## Architecture | 架构

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Port 2125)                                   │
│  前端 (端口 2125)                                        │
│  - HTML/CSS/JavaScript                                  │
│  - ECharts for visualization | ECharts 图表可视化       │
│  - Auto-refresh every 3s | 每3秒自动刷新                │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTP REST API calls
                 │ HTTP REST API 调用
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Backend (Port 2124)                                    │
│  后端 (端口 2124)                                        │
│  - Flask web framework | Flask 网络框架                 │
│  - REST API endpoints | REST API 端点                   │
│  - Business logic | 业务逻辑                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ SQL queries
                 │ SQL 查询
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Database (SQLite)                                      │
│  数据库 (SQLite)                                         │
│  - materials table | 物料表                             │
│  - inventory_records table | 出入库记录表                │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema | 数据库架构

### 1. Materials Table | 物料表

Stores all inventory items with their current quantities and locations.

存储所有库存物料及其当前数量和位置。

```sql
CREATE TABLE materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID | 唯一标识
    name TEXT NOT NULL,                    -- Product name | 产品名称
    sku TEXT UNIQUE NOT NULL,              -- Stock Keeping Unit | 库存单位编码
    category TEXT NOT NULL,                -- Category (Mainboard, Sensor, etc.) | 类别（主板、传感器等）
    quantity INTEGER DEFAULT 0,            -- Current stock quantity | 当前库存数量
    unit TEXT DEFAULT '个',                -- Unit of measure | 计量单位
    safe_stock INTEGER DEFAULT 20,         -- Safety stock threshold | 安全库存阈值
    location TEXT,                         -- Warehouse location | 仓库位置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation time | 创建时间
)
```

**Key Fields | 关键字段:**
- `quantity`: Current inventory level | 当前库存水平
- `safe_stock`: Minimum safe quantity; alerts trigger when `quantity < safe_stock` | 最小安全数量；当 `quantity < safe_stock` 时触发警报
- `location`: Physical warehouse location (e.g., "A区-01") | 物理仓库位置（例如"A区-01"）

### 2. Inventory Records Table | 出入库记录表

Tracks all stock movements (in/out) with timestamps and reasons.

跟踪所有库存移动（入库/出库）及其时间戳和原因。

```sql
CREATE TABLE inventory_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID | 唯一标识
    material_id INTEGER NOT NULL,          -- Foreign key to materials | 物料外键
    type TEXT NOT NULL,                    -- 'in' or 'out' | '入库' 或 '出库'
    quantity INTEGER NOT NULL,             -- Quantity moved | 移动数量
    operator TEXT DEFAULT '系统',          -- Who performed the operation | 操作人
    reason TEXT,                           -- Reason for movement | 移动原因
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When it happened | 发生时间
    FOREIGN KEY (material_id) REFERENCES materials (id)
)
```

**Key Fields | 关键字段:**
- `type`: Either 'in' (stock-in) or 'out' (stock-out) | '入库' 或 '出库'
- `reason`: Examples: "采购入库" (Purchase), "销售出库" (Sales), etc. | 示例："采购入库"、"销售出库"等

---

## Backend API Endpoints | 后端 API 端点

### Dashboard Statistics | 仪表盘统计

**Endpoint:** `GET /api/dashboard/stats`

**Purpose | 用途:** Returns key metrics for the dashboard | 返回仪表盘的关键指标

**Response | 响应:**
```json
{
    "total_stock": 3300,        // Total inventory across all items | 所有物料的总库存
    "today_in": 50,             // Today's stock-in quantity | 今日入库数量
    "today_out": 30,            // Today's stock-out quantity | 今日出库数量
    "low_stock_count": 5,       // Number of items below safe stock | 低于安全库存的物料数
    "material_types": 37,       // Total number of SKUs | SKU 总数
    "in_change": 12.5,          // % change vs yesterday | 与昨天相比的百分比变化
    "out_change": -5.2          // % change vs yesterday | 与昨天相比的百分比变化
}
```

**How it works | 工作原理:**

1. **Total Stock | 总库存:** Sums all `quantity` fields from `materials` table
   
   从 `materials` 表汇总所有 `quantity` 字段

2. **Today's In/Out | 今日出入库:** Queries `inventory_records` where `created_at >= today 00:00:00`
   
   查询 `inventory_records` 表中 `created_at >= 今天 00:00:00` 的记录

3. **Percentage Change | 百分比变化:** Compares today vs yesterday: `((today - yesterday) / yesterday) * 100`
   
   比较今天与昨天：`((今天 - 昨天) / 昨天) * 100`

---

### Category Distribution | 类别分布

**Endpoint:** `GET /api/dashboard/category-distribution`

**Purpose | 用途:** Returns inventory grouped by category for pie chart | 返回按类别分组的库存用于饼图

**Response | 响应:**
```json
[
    {"name": "主板类", "value": 338},      // Mainboard category | 主板类
    {"name": "传感器类", "value": 488},    // Sensor category | 传感器类
    {"name": "外壳配件类", "value": 833},  // Shell & accessories | 外壳配件类
    ...
]
```

**SQL Query | SQL 查询:**
```sql
SELECT category, SUM(quantity) as total
FROM materials
GROUP BY category
ORDER BY total DESC
```

---

### Weekly Trend | 近7天趋势

**Endpoint:** `GET /api/dashboard/weekly-trend`

**Purpose | 用途:** Returns daily stock-in/out for the last 7 days | 返回过去7天的每日出入库数据

**Response | 响应:**
```json
{
    "dates": ["11-13", "11-14", "11-15", ...],  // Last 7 days | 过去7天
    "in_data": [45, 52, 38, ...],               // Daily stock-in | 每日入库
    "out_data": [32, 28, 41, ...]               // Daily stock-out | 每日出库
}
```

**How it works | 工作原理:**

Loops through the last 7 days and for each day:

循环过去7天，对每一天：

1. Calculate day start: `date.replace(hour=0, minute=0, second=0)`
2. Calculate day end: `day_start + 1 day`
3. Query records between start and end
4. Sum quantities by type ('in' or 'out')

---

### Product Detail APIs | 产品详情 API

#### Get Product Statistics | 获取产品统计

**Endpoint:** `GET /api/materials/product-stats?name=<product_name>`

**Purpose | 用途:** Returns detailed stats for a single product | 返回单个产品的详细统计

**Response | 响应:**
```json
{
    "name": "watcher-xiaozhi(标准版)",
    "sku": "FG-WZ-STD",
    "current_stock": 52,           // Current quantity | 当前数量
    "unit": "台",                  // Unit | 单位
    "safe_stock": 15,              // Safety threshold | 安全阈值
    "location": "H区-02",          // Location | 位置
    "today_in": 10,                // Today's stock-in | 今日入库
    "today_out": 5,                // Today's stock-out | 今日出库
    "in_change": 25.0,             // % change | 百分比变化
    "out_change": -16.7,           // % change | 百分比变化
    "total_in": 150,               // All-time stock-in | 历史总入库
    "total_out": 98                // All-time stock-out | 历史总出库
}
```

#### Get Product Trend | 获取产品趋势

**Endpoint:** `GET /api/materials/product-trend?name=<product_name>`

**Purpose | 用途:** Returns 7-day trend for a specific product | 返回特定产品的7天趋势

#### Get Product Records | 获取产品记录

**Endpoint:** `GET /api/materials/product-records?name=<product_name>`

**Purpose | 用途:** Returns last 30 stock movements for a product | 返回产品的最近30条库存移动记录

---

## Frontend Flow | 前端流程

### Page Load Sequence | 页面加载顺序

1. **DOM Ready | DOM 就绪**
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
       initCharts();        // Initialize ECharts | 初始化图表
       loadAllData();       // Load all data | 加载所有数据
       initSearchFilter();  // Setup search | 设置搜索
       startAutoUpdate();   // Start 3s timer | 启动3秒定时器
   });
   ```

2. **Initialize Charts | 初始化图表**
   - Creates 3 ECharts instances: trend, category, topStock
   - 创建3个 ECharts 实例：趋势图、类别图、TOP10图

3. **Load All Data | 加载所有数据**
   - Calls 5 API endpoints in parallel using `Promise.all()`
   - 使用 `Promise.all()` 并行调用5个 API 端点
   - Updates DOM with received data
   - 用接收到的数据更新 DOM

4. **Start Auto-Update | 启动自动更新**
   - Sets interval to refresh every 3 seconds
   - 设置每3秒刷新一次的定时器
   - Shows countdown: "自动更新: 3秒"
   - 显示倒计时："自动更新: 3秒"

### Search & Filter | 搜索与过滤

**How it works | 工作原理:**

```javascript
function filterMaterials(keyword) {
    if (!keyword) {
        renderInventoryTable(allMaterials);  // Show all | 显示全部
        return;
    }

    // Filter by name or SKU | 按名称或 SKU 过滤
    const filtered = allMaterials.filter(item =>
        item.name.toLowerCase().includes(keyword) ||
        item.sku.toLowerCase().includes(keyword)
    );
    
    renderInventoryTable(filtered);  // Show filtered | 显示过滤结果
}
```

**Features | 特性:**
- Real-time filtering (no button click needed) | 实时过滤（无需点击按钮）
- Case-insensitive | 不区分大小写
- Searches both name and SKU | 同时搜索名称和 SKU

### Status Badges | 状态标签

Products are color-coded based on stock level:

产品根据库存水平进行颜色编码：

```javascript
if (quantity >= safe_stock) {
    status = 'normal';      // Green | 绿色
    status_text = '正常';   // Normal
} else if (quantity >= safe_stock * 0.5) {
    status = 'warning';     // Yellow | 黄色
    status_text = '偏低';   // Low
} else {
    status = 'danger';      // Red | 红色
    status_text = '告急';   // Critical
}
```

---

## MCP Integration | MCP 集成

The system includes MCP (Model Context Protocol) tools for AI assistant integration.

系统包含 MCP（模型上下文协议）工具，用于 AI 助手集成。

### Available Tools | 可用工具

1. **query_xiaozhi_stock** - Query product inventory | 查询产品库存
2. **stock_in** - Perform stock-in operation | 执行入库操作
3. **stock_out** - Perform stock-out operation | 执行出库操作
4. **list_xiaozhi_products** - List all products | 列出所有产品
5. **get_today_statistics** - Get today's statistics | 获取今日统计

### How MCP Works | MCP 工作原理

```python
@mcp.tool()
def stock_in(product_name: str, quantity: int, reason: str = "采购入库", operator: str = "MCP系统") -> dict:
    """
    Stock-in operation | 入库操作
    
    1. Validate quantity > 0 | 验证数量 > 0
    2. Find product in database | 在数据库中查找产品
    3. Update materials.quantity | 更新 materials.quantity
    4. Insert record into inventory_records | 插入记录到 inventory_records
    5. Return success/error | 返回成功/错误
    """
```

**Integration with Claude Desktop | 与 Claude Desktop 集成:**

When configured in Claude Desktop, you can use natural language:

在 Claude Desktop 中配置后，可以使用自然语言：

```
User: "请为 watcher-xiaozhi(标准版) 入库 10 台"
      (Stock in 10 units of watcher-xiaozhi standard version)

Claude: [Calls stock_in MCP tool]
        [调用 stock_in MCP 工具]
        
        "入库成功！库存从 52 更新到 62 台"
        (Stock-in successful! Inventory updated from 52 to 62 units)
```

---

## Data Flow Example | 数据流示例

### Example: Stock-In Operation | 示例：入库操作

**Scenario | 场景:** User stocks in 10 units via MCP | 用户通过 MCP 入库10个单位

```
1. MCP Tool Called | MCP 工具被调用
   ↓
   stock_in(product_name="watcher-xiaozhi(标准版)", quantity=10)

2. Backend Processing | 后端处理
   ↓
   a. Query materials table for product | 查询 materials 表获取产品
   b. old_quantity = 52
   c. new_quantity = 52 + 10 = 62
   d. UPDATE materials SET quantity = 62 WHERE id = X
   e. INSERT INTO inventory_records (material_id, type, quantity, ...)
      VALUES (X, 'in', 10, ...)

3. Database Updated | 数据库已更新
   ↓
   materials.quantity: 52 → 62
   inventory_records: +1 new record | +1 新记录

4. Frontend Auto-Refresh (within 3s) | 前端自动刷新（3秒内）
   ↓
   a. loadAllData() called | 调用 loadAllData()
   b. Fetches /api/materials/all
   c. Receives updated quantity: 62
   d. Re-renders table with new value | 用新值重新渲染表格
   e. User sees updated inventory | 用户看到更新的库存
```

---

## Key Concepts | 关键概念

### 1. Safety Stock | 安全库存

**Definition | 定义:** Minimum quantity that should be maintained | 应保持的最小数量

**Purpose | 目的:** 
- Prevent stockouts | 防止缺货
- Trigger reorder alerts | 触发补货警报
- Maintain buffer for demand fluctuations | 为需求波动保持缓冲

**Implementation | 实现:**
```sql
-- Find items below safety stock | 查找低于安全库存的物料
SELECT * FROM materials WHERE quantity < safe_stock
```

### 2. Stock Movement Types | 库存移动类型

**Stock-In (入库):**
- Purchase arrival | 采购到货
- Production completion | 生产完工
- Return from customer | 客户退货
- Transfer from other warehouse | 从其他仓库调拨

**Stock-Out (出库):**
- Sales shipment | 销售出货
- Production consumption | 生产消耗
- R&D usage | 研发领用
- Transfer to other warehouse | 调拨到其他仓库
- Repair/maintenance | 返修/维护

### 3. Real-Time Updates | 实时更新

**Auto-Refresh Mechanism | 自动刷新机制:**

```javascript
// Every 3 seconds | 每3秒
setInterval(function() {
    countdownSeconds--;
    if (countdownSeconds <= 0) {
        loadAllData();      // Refresh all data | 刷新所有数据
        countdownSeconds = 3;
    }
}, 1000);
```

**Why 3 seconds? | 为什么是3秒？**
- Balance between freshness and server load | 在数据新鲜度和服务器负载之间平衡
- Fast enough for warehouse operations | 对仓库操作足够快
- Not too frequent to cause performance issues | 不会太频繁导致性能问题

---

## Common Operations | 常见操作

### 1. Add New Material | 添加新物料

```sql
INSERT INTO materials (name, sku, category, quantity, unit, safe_stock, location)
VALUES ('新产品', 'NEW-001', '成品', 100, '台', 20, 'H区-04');
```

### 2. Stock-In | 入库

```sql
-- Update quantity | 更新数量
UPDATE materials SET quantity = quantity + 10 WHERE id = 1;

-- Record movement | 记录移动
INSERT INTO inventory_records (material_id, type, quantity, operator, reason)
VALUES (1, 'in', 10, '张三', '采购入库');
```

### 3. Stock-Out | 出库

```sql
-- Check if enough stock | 检查库存是否足够
SELECT quantity FROM materials WHERE id = 1;

-- If sufficient, update | 如果足够，更新
UPDATE materials SET quantity = quantity - 5 WHERE id = 1;

-- Record movement | 记录移动
INSERT INTO inventory_records (material_id, type, quantity, operator, reason)
VALUES (1, 'out', 5, '李四', '销售出库');
```

### 4. Check Low Stock | 检查低库存

```sql
SELECT name, quantity, safe_stock, (safe_stock - quantity) as shortage
FROM materials
WHERE quantity < safe_stock
ORDER BY shortage DESC;
```

---

## Performance Considerations | 性能考虑

### Database Indexes | 数据库索引

**Recommended indexes | 推荐索引:**

```sql
-- For faster lookups | 加快查找速度
CREATE INDEX idx_materials_sku ON materials(sku);
CREATE INDEX idx_materials_category ON materials(category);

-- For faster date queries | 加快日期查询
CREATE INDEX idx_records_created_at ON inventory_records(created_at);
CREATE INDEX idx_records_material_id ON inventory_records(material_id);
```

### Frontend Optimization | 前端优化

1. **Parallel API Calls | 并行 API 调用**
   ```javascript
   await Promise.all([...])  // Load 5 endpoints simultaneously | 同时加载5个端点
   ```

2. **Chart Reuse | 图表重用**
   - Charts are initialized once, then updated with `setOption()`
   - 图表初始化一次，然后用 `setOption()` 更新

3. **Debounced Search | 防抖搜索**
   - Search filters on every keystroke (instant feedback)
   - 每次按键都过滤搜索（即时反馈）

---

## Troubleshooting | 故障排除

### Common Issues | 常见问题

**1. "Failed to load data" | "加载数据失败"**

**Cause | 原因:** Backend not running | 后端未运行

**Solution | 解决方案:**
```bash
cd backend
uv run python app.py
```

**2. Database locked | 数据库锁定**

**Cause | 原因:** Multiple processes accessing SQLite | 多个进程访问 SQLite

**Solution | 解决方案:** Ensure only one backend instance is running | 确保只有一个后端实例在运行

**3. Charts not displaying | 图表不显示**

**Cause | 原因:** ECharts library not loaded | ECharts 库未加载

**Solution | 解决方案:** Check internet connection (CDN) or use local ECharts | 检查网络连接（CDN）或使用本地 ECharts

---

## Next Steps | 下一步

Now that you understand how the system works, you can:

现在您了解了系统的工作原理，可以：

1. **Modify for food inventory | 修改为食品库存**
   - Add expiration_date field | 添加 expiration_date 字段
   - Implement FEFO logic | 实现 FEFO 逻辑
   - Add temperature monitoring | 添加温度监控

2. **Deploy to cloud | 部署到云端**
   - Migrate to Supabase (PostgreSQL) | 迁移到 Supabase（PostgreSQL）
   - Deploy frontend to Cloudflare Pages | 部署前端到 Cloudflare Pages
   - Deploy backend to Railway/Render | 部署后端到 Railway/Render

3. **Add multi-tenancy | 添加多租户**
   - Add organizations table | 添加 organizations 表
   - Implement row-level security | 实现行级安全
   - Add subscription billing | 添加订阅计费

---

## Questions? | 有问题？

Refer to:
- `README.md` - Project overview | 项目概述
- `README_EN.md` - English documentation | 英文文档
- `mcp/MCP_README.md` - MCP integration guide | MCP 集成指南
- `test/README.md` - Testing guide | 测试指南
