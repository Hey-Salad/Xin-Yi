#!/usr/bin/env python3
"""
仓库管理系统 MCP 服务器 | Warehouse Management System MCP Server

提供 watcher-xiaozhi 产品的库存管理功能：
Provides inventory management functions for watcher-xiaozhi products:
- 查询库存 | Query inventory
- 入库操作 | Stock-in operation
- 出库操作 | Stock-out operation
- 查询当天统计数据（入库、出库、库存总量）| Query today's statistics (stock-in, stock-out, total inventory)
"""

from fastmcp import FastMCP
import sys
import logging
import os

# 配置日志 | Configure logging
logger = logging.getLogger('WarehouseMCP')

# 修复 Windows 控制台 UTF-8 编码 | Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# 导入数据库操作 | Import database operations
# 获取项目根目录（mcp的父目录）| Get project root directory (parent of mcp)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_dir)
# 切换到backend目录，确保数据库路径正确 | Switch to backend directory to ensure correct database path
os.chdir(backend_dir)
from database import get_db_connection

# 创建 MCP 服务器 | Create MCP server
mcp = FastMCP("Warehouse System")


def get_xiaozhi_materials():
    """获取所有 watcher-xiaozhi 相关物料 | Get all watcher-xiaozhi related materials"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, sku, quantity, unit, safe_stock, location
        FROM materials
        WHERE name LIKE '%xiaozhi%' OR name LIKE '%watcher%'
        ORDER BY name
    ''')

    materials = []
    for row in cursor.fetchall():
        materials.append({
            'id': row['id'],
            'name': row['name'],
            'sku': row['sku'],
            'quantity': row['quantity'],
            'unit': row['unit'],
            'safe_stock': row['safe_stock'],
            'location': row['location']
        })

    conn.close()
    return materials


@mcp.tool()
def query_xiaozhi_stock(product_name: str = "watcher-xiaozhi(标准版)") -> dict:
    """
    查询 watcher-xiaozhi 产品的库存信息 | Query watcher-xiaozhi product inventory information

    参数 | Parameters:
        product_name: 产品名称，默认为 "watcher-xiaozhi(标准版)" | Product name, defaults to "watcher-xiaozhi(标准版)"
                     可选值 | Optional values:
                     - "watcher-xiaozhi(标准版)" | Standard version
                     - "watcher-xiaozhi(专业版)" | Professional version
                     - "watcher-xiaozhi整机" | Complete unit
                     - "watcher-xiaozhi主控板" | Main control board
                     - "watcher-xiaozhi扩展板" | Expansion board
                     - "watcher-xiaozhi外壳(上)" | Shell (upper)
                     - "watcher-xiaozhi外壳(下)" | Shell (lower)

    返回 | Returns:
        包含库存信息的字典 | Dictionary containing inventory information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, sku, quantity, unit, safe_stock, location, created_at
            FROM materials
            WHERE name = ?
        ''', (product_name,))

        row = cursor.fetchone()
        conn.close()

        if row:
            quantity = row['quantity']
            safe_stock = row['safe_stock']

            # 判断库存状态 | Determine stock status
            if quantity >= safe_stock:
                status = "正常"  # Normal
            elif quantity >= safe_stock * 0.5:
                status = "偏低"  # Low
            else:
                status = "告急"  # Critical

            result = {
                'success': True,
                'product': {
                    'name': row['name'],
                    'sku': row['sku'],
                    'quantity': quantity,
                    'unit': row['unit'],
                    'safe_stock': safe_stock,
                    'location': row['location'],
                    'status': status
                },
                'message': f"查询成功：{row['name']} 当前库存 {quantity} {row['unit']}"
            }

            logger.info(f"查询库存: {product_name}, 数量: {quantity}")
            return result
        else:
            logger.warning(f"产品不存在: {product_name}")
            return {
                'success': False,
                'error': f"未找到产品: {product_name}",
                'message': f"产品 '{product_name}' 不存在，请检查产品名称"
            }

    except Exception as e:
        logger.error(f"查询库存失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': f"查询失败: {str(e)}"
        }


@mcp.tool()
def stock_in(product_name: str, quantity: int, reason: str = "采购入库", operator: str = "MCP系统") -> dict:
    """
    watcher-xiaozhi 产品入库操作 | watcher-xiaozhi product stock-in operation

    参数 | Parameters:
        product_name: 产品名称（必填）| Product name (required)
        quantity: 入库数量（必填，必须大于0）| Stock-in quantity (required, must be > 0)
        reason: 入库原因，默认为"采购入库" | Stock-in reason, defaults to "Purchase"
        operator: 操作人，默认为"MCP系统" | Operator, defaults to "MCP System"

    返回 | Returns:
        包含操作结果的字典 | Dictionary containing operation result
    """
    try:
        if quantity <= 0:
            return {
                'success': False,
                'error': '入库数量必须大于0',
                'message': f"入库失败：数量 {quantity} 无效"
            }

        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询产品 | Query product
        cursor.execute('SELECT id, name, quantity, unit FROM materials WHERE name = ?', (product_name,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {
                'success': False,
                'error': f"产品不存在: {product_name}",  # Product does not exist
                'message': f"入库失败：未找到产品 '{product_name}'"  # Stock-in failed: Product not found
            }

        material_id = row['id']
        old_quantity = row['quantity']
        unit = row['unit']
        new_quantity = old_quantity + quantity

        # 更新库存 | Update inventory
        cursor.execute('''
            UPDATE materials
            SET quantity = ?
            WHERE id = ?
        ''', (new_quantity, material_id))

        # 记录入库 | Record stock-in
        from datetime import datetime
        cursor.execute('''
            INSERT INTO inventory_records (material_id, type, quantity, operator, reason, created_at)
            VALUES (?, 'in', ?, ?, ?, ?)
        ''', (material_id, quantity, operator, reason, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        conn.close()

        result = {
            'success': True,
            'operation': 'stock_in',
            'product': {
                'name': product_name,
                'old_quantity': old_quantity,
                'in_quantity': quantity,
                'new_quantity': new_quantity,
                'unit': unit
            },
            'message': f"入库成功：{product_name} 入库 {quantity} {unit}，库存从 {old_quantity} 更新到 {new_quantity} {unit}"
        }

        logger.info(f"入库操作: {product_name}, 数量: {quantity}, 操作人: {operator}")
        return result

    except Exception as e:
        logger.error(f"入库失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': f"入库失败: {str(e)}"
        }


@mcp.tool()
def stock_out(product_name: str, quantity: int, reason: str = "销售出库", operator: str = "MCP系统") -> dict:
    """
    watcher-xiaozhi 产品出库操作 | watcher-xiaozhi product stock-out operation

    参数 | Parameters:
        product_name: 产品名称（必填）| Product name (required)
        quantity: 出库数量（必填，必须大于0）| Stock-out quantity (required, must be > 0)
        reason: 出库原因，默认为"销售出库" | Stock-out reason, defaults to "Sales"
        operator: 操作人，默认为"MCP系统" | Operator, defaults to "MCP System"

    返回 | Returns:
        包含操作结果的字典 | Dictionary containing operation result
    """
    try:
        if quantity <= 0:
            return {
                'success': False,
                'error': '出库数量必须大于0',
                'message': f"出库失败：数量 {quantity} 无效"
            }

        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询产品 | Query product
        cursor.execute('SELECT id, name, quantity, unit, safe_stock FROM materials WHERE name = ?', (product_name,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {
                'success': False,
                'error': f"产品不存在: {product_name}",  # Product does not exist
                'message': f"出库失败：未找到产品 '{product_name}'"  # Stock-out failed: Product not found
            }

        material_id = row['id']
        old_quantity = row['quantity']
        unit = row['unit']
        safe_stock = row['safe_stock']

        # 检查库存是否足够 | Check if stock is sufficient
        if old_quantity < quantity:
            conn.close()
            return {
                'success': False,
                'error': '库存不足',  # Insufficient stock
                'message': f"出库失败：{product_name} 库存不足，当前库存 {old_quantity} {unit}，需要出库 {quantity} {unit}"
                # Stock-out failed: Insufficient stock
            }

        new_quantity = old_quantity - quantity

        # 更新库存 | Update inventory
        cursor.execute('''
            UPDATE materials
            SET quantity = ?
            WHERE id = ?
        ''', (new_quantity, material_id))

        # 记录出库 | Record stock-out
        from datetime import datetime
        cursor.execute('''
            INSERT INTO inventory_records (material_id, type, quantity, operator, reason, created_at)
            VALUES (?, 'out', ?, ?, ?, ?)
        ''', (material_id, quantity, operator, reason, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        conn.close()

        # 检查是否低于安全库存 | Check if below safety stock
        warning = ""
        if new_quantity < safe_stock:
            if new_quantity < safe_stock * 0.5:
                warning = f"⚠️ 警告：库存告急！当前库存 {new_quantity} {unit}，低于安全库存 {safe_stock} {unit} 的50%"
                # Warning: Stock critical! Current stock below 50% of safety stock
            else:
                warning = f"⚠️ 提醒：库存偏低，当前库存 {new_quantity} {unit}，低于安全库存 {safe_stock} {unit}"
                # Reminder: Stock low, below safety stock

        result = {
            'success': True,
            'operation': 'stock_out',
            'product': {
                'name': product_name,
                'old_quantity': old_quantity,
                'out_quantity': quantity,
                'new_quantity': new_quantity,
                'unit': unit,
                'safe_stock': safe_stock
            },
            'message': f"出库成功：{product_name} 出库 {quantity} {unit}，库存从 {old_quantity} 更新到 {new_quantity} {unit}",
            'warning': warning
        }

        logger.info(f"出库操作: {product_name}, 数量: {quantity}, 操作人: {operator}, 剩余: {new_quantity}")
        return result

    except Exception as e:
        logger.error(f"出库失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': f"出库失败: {str(e)}"
        }


@mcp.tool()
def list_xiaozhi_products() -> dict:
    """
    列出所有 watcher-xiaozhi 相关产品 | List all watcher-xiaozhi related products

    返回 | Returns:
        包含所有产品列表的字典 | Dictionary containing list of all products
    """
    try:
        materials = get_xiaozhi_materials()

        result = {
            'success': True,
            'count': len(materials),
            'products': materials,
            'message': f"查询成功，共找到 {len(materials)} 种 watcher-xiaozhi 相关产品"
        }

        logger.info(f"列出所有产品，共 {len(materials)} 种")
        return result

    except Exception as e:
        logger.error(f"查询产品列表失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': f"查询失败: {str(e)}"
        }


@mcp.tool()
def get_today_statistics() -> dict:
    """
    查询当天的仓库统计数据 | Query today's warehouse statistics

    返回 | Returns:
        包含今日入库数量、出库数量和当前库存总量的字典
        Dictionary containing today's stock-in quantity, stock-out quantity, and total inventory
    """
    try:
        from datetime import datetime

        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取今天的日期 | Get today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # 查询今日入库总数 | Query today's total stock-in
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0) as total_in
            FROM inventory_records
            WHERE type = 'in' AND DATE(created_at) = ?
        ''', (today,))
        today_in = cursor.fetchone()['total_in']

        # 查询今日出库总数 | Query today's total stock-out
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0) as total_out
            FROM inventory_records
            WHERE type = 'out' AND DATE(created_at) = ?
        ''', (today,))
        today_out = cursor.fetchone()['total_out']

        # 查询当前库存总量 | Query current total inventory
        cursor.execute('''
            SELECT COALESCE(SUM(quantity), 0) as total_stock
            FROM materials
        ''')
        total_stock = cursor.fetchone()['total_stock']

        # 查询库存预警数量 | Query low stock alert count
        cursor.execute('''
            SELECT COUNT(*) as low_stock_count
            FROM materials
            WHERE quantity < safe_stock
        ''')
        low_stock_count = cursor.fetchone()['low_stock_count']

        conn.close()

        result = {
            'success': True,
            'date': today,
            'statistics': {
                'today_in': today_in,
                'today_out': today_out,
                'total_stock': total_stock,
                'low_stock_count': low_stock_count,
                'net_change': today_in - today_out
            },
            'message': f"查询成功：{today} 入库 {today_in} 件，出库 {today_out} 件，当前库存总量 {total_stock} 件"
        }

        logger.info(f"查询今日统计: 入库 {today_in}, 出库 {today_out}, 库存 {total_stock}")
        return result

    except Exception as e:
        logger.error(f"查询统计数据失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': f"查询统计数据失败: {str(e)}"
        }


# 启动服务器 | Start server
if __name__ == "__main__":
    mcp.run(transport="stdio")
