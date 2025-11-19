"""
Warehouse Management System (Xin Yi) Routes
Food inventory, FEFO logic, lot tracking
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from database_supabase import get_supabase_client

wms_bp = Blueprint('wms', __name__, url_prefix='/api/wms')
supabase = get_supabase_client()


@wms_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """获取仪表盘统计数据 | Get dashboard statistics"""
    try:
        # Total stock quantity
        response = supabase.table('materials').select('quantity').execute()
        total_stock = sum(item['quantity'] for item in response.data)
        
        # Today's stock-in
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        response = supabase.table('inventory_records')\
            .select('quantity')\
            .eq('type', 'in')\
            .gte('created_at', today_start)\
            .execute()
        today_in = sum(item['quantity'] for item in response.data)
        
        # Today's stock-out
        response = supabase.table('inventory_records')\
            .select('quantity')\
            .eq('type', 'out')\
            .gte('created_at', today_start)\
            .execute()
        today_out = sum(item['quantity'] for item in response.data)
        
        # Low stock count
        response = supabase.table('materials').select('id, quantity, safe_stock').execute()
        low_stock_count = sum(1 for item in response.data if item['quantity'] < item['safe_stock'])
        
        # Material types count
        response = supabase.table('materials').select('id', count='exact').execute()
        material_types = response.count
        
        # Yesterday's data for percentage change
        yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        yesterday_end = today_start
        
        response = supabase.table('inventory_records')\
            .select('quantity')\
            .eq('type', 'in')\
            .gte('created_at', yesterday_start)\
            .lt('created_at', yesterday_end)\
            .execute()
        yesterday_in = sum(item['quantity'] for item in response.data) or 1
        
        response = supabase.table('inventory_records')\
            .select('quantity')\
            .eq('type', 'out')\
            .gte('created_at', yesterday_start)\
            .lt('created_at', yesterday_end)\
            .execute()
        yesterday_out = sum(item['quantity'] for item in response.data) or 1
        
        # Calculate percentage change
        in_change = round(((today_in - yesterday_in) / yesterday_in * 100), 1) if yesterday_in > 0 else 0
        out_change = round(((today_out - yesterday_out) / yesterday_out * 100), 1) if yesterday_out > 0 else 0
        
        return jsonify({
            'total_stock': total_stock,
            'today_in': today_in,
            'today_out': today_out,
            'low_stock_count': low_stock_count,
            'material_types': material_types,
            'in_change': in_change,
            'out_change': out_change
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/dashboard/category-distribution', methods=['GET'])
def get_category_distribution():
    """获取类别分布 | Get category distribution for pie chart"""
    try:
        response = supabase.table('materials').select('category, quantity').execute()

        # Group by category
        category_map = {}
        for item in response.data:
            cat = item['category']
            category_map[cat] = category_map.get(cat, 0) + item['quantity']

        # Format for ECharts pie chart
        result = [{'name': k, 'value': v} for k, v in category_map.items()]

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/dashboard/weekly-trend', methods=['GET'])
def get_weekly_trend():
    """获取7天趋势 | Get 7-day in/out trend"""
    try:
        dates = []
        in_data = []
        out_data = []

        for i in range(6, -1, -1):  # Last 7 days
            date = datetime.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            day_end = (date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

            dates.append(date.strftime('%m/%d'))

            # Stock-in for this day
            response_in = supabase.table('inventory_records')\
                .select('quantity')\
                .eq('type', 'in')\
                .gte('created_at', day_start)\
                .lt('created_at', day_end)\
                .execute()
            in_data.append(sum(item['quantity'] for item in response_in.data))

            # Stock-out for this day
            response_out = supabase.table('inventory_records')\
                .select('quantity')\
                .eq('type', 'out')\
                .gte('created_at', day_start)\
                .lt('created_at', day_end)\
                .execute()
            out_data.append(sum(item['quantity'] for item in response_out.data))

        return jsonify({
            'dates': dates,
            'in_data': in_data,
            'out_data': out_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/dashboard/top-stock', methods=['GET'])
def get_top_stock():
    """获取库存TOP10 | Get top 10 materials by stock quantity"""
    try:
        response = supabase.table('materials')\
            .select('name, category, quantity')\
            .order('quantity', desc=True)\
            .limit(10)\
            .execute()

        names = [item['name'] for item in response.data]
        categories = [item['category'] for item in response.data]
        quantities = [item['quantity'] for item in response.data]

        return jsonify({
            'names': names,
            'categories': categories,
            'quantities': quantities
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/materials/all', methods=['GET'])
def get_all_materials():
    """获取所有物料 | Get all materials for inventory table"""
    try:
        response = supabase.table('materials')\
            .select('id, name, sku, category, quantity, unit, safe_stock, location')\
            .order('name')\
            .execute()

        # Add status information
        result = []
        for item in response.data:
            qty = item['quantity']
            safe = item['safe_stock']

            # Determine status
            if qty >= safe:
                status = 'normal'
                status_text = 'Normal | 正常'
            elif qty >= safe * 0.5:
                status = 'warning'
                status_text = 'Low | 偏低'
            else:
                status = 'danger'
                status_text = 'Critical | 严重'

            result.append({
                **item,
                'status': status,
                'status_text': status_text
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/fefo-alerts', methods=['GET'])
def get_fefo_alerts():
    """获取FEFO预警 | Get FEFO expiration alerts"""
    try:
        threshold_hours = int(request.args.get('hours', 48))
        threshold_date = (datetime.now() + timedelta(hours=threshold_hours)).date().isoformat()

        response = supabase.table('inventory_lots')\
            .select('*, materials(name, sku, category)')\
            .eq('status', 'active')\
            .lte('expiration_date', threshold_date)\
            .order('expiration_date')\
            .execute()

        alerts = []
        for lot in response.data:
            hours_until_expiry = (datetime.fromisoformat(lot['expiration_date']) - datetime.now()).total_seconds() / 3600
            alerts.append({
                'lot_number': lot['lot_number'],
                'material_name': lot['materials']['name'],
                'sku': lot['materials']['sku'],
                'category': lot['materials']['category'],
                'quantity': lot['quantity'],
                'expiration_date': lot['expiration_date'],
                'hours_until_expiry': round(hours_until_expiry, 1),
                'urgency': 'critical' if hours_until_expiry < 24 else 'warning'
            })

        return jsonify(alerts)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/spoilage-rate', methods=['GET'])
def get_spoilage_rate():
    """获取损耗率 | Get spoilage/waste rate"""
    try:
        days = int(request.args.get('days', 30))
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get expired/disposed lots
        response = supabase.table('inventory_lots')\
            .select('quantity, catch_weight, materials(name, category)')\
            .in_('status', ['expired', 'disposed'])\
            .gte('updated_at', start_date)\
            .execute()
        
        total_wasted = sum(item['quantity'] for item in response.data)
        
        # Get total inventory movement
        response_in = supabase.table('inventory_records')\
            .select('quantity')\
            .eq('type', 'in')\
            .gte('created_at', start_date)\
            .execute()
        total_in = sum(item['quantity'] for item in response_in.data)
        
        spoilage_rate = round((total_wasted / total_in * 100), 2) if total_in > 0 else 0
        
        # Top wasted items
        wasted_by_category = {}
        for item in response.data:
            cat = item['materials']['category']
            wasted_by_category[cat] = wasted_by_category.get(cat, 0) + item['quantity']
        
        top_wasted = sorted(
            [{'category': k, 'quantity': v} for k, v in wasted_by_category.items()],
            key=lambda x: x['quantity'],
            reverse=True
        )[:5]
        
        return jsonify({
            'spoilage_rate': spoilage_rate,
            'total_wasted': total_wasted,
            'period_days': days,
            'top_wasted_categories': top_wasted
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/stock/in', methods=['POST'])
def stock_in():
    """入库操作 | Stock-in operation with lot tracking"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['material_id', 'quantity', 'lot_number', 'expiration_date']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create lot record
        lot_data = {
            'material_id': data['material_id'],
            'lot_number': data['lot_number'],
            'expiration_date': data['expiration_date'],
            'quantity': data['quantity'],
            'catch_weight': data.get('catch_weight'),
            'status': 'active'
        }
        
        lot_response = supabase.table('inventory_lots').insert(lot_data).execute()
        
        # Update material quantity
        material = supabase.table('materials').select('quantity').eq('id', data['material_id']).single().execute()
        new_quantity = material.data['quantity'] + data['quantity']
        supabase.table('materials').update({'quantity': new_quantity}).eq('id', data['material_id']).execute()
        
        # Create inventory record
        record_data = {
            'material_id': data['material_id'],
            'type': 'in',
            'quantity': data['quantity'],
            'operator': data.get('operator', 'System'),
            'reason': data.get('reason', 'Stock-in')
        }
        supabase.table('inventory_records').insert(record_data).execute()
        
        return jsonify({
            'success': True,
            'lot_id': lot_response.data[0]['id'],
            'message': f"Stock-in successful: {data['quantity']} units"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@wms_bp.route('/stock/out', methods=['POST'])
def stock_out():
    """出库操作 (FEFO) | Stock-out operation with FEFO logic"""
    try:
        data = request.json
        material_id = data.get('material_id')
        quantity_needed = data.get('quantity')
        
        if not material_id or not quantity_needed:
            return jsonify({'error': 'Missing material_id or quantity'}), 400
        
        # Get active lots sorted by expiration (FEFO)
        lots = supabase.table('inventory_lots')\
            .select('*')\
            .eq('material_id', material_id)\
            .eq('status', 'active')\
            .gt('quantity', 0)\
            .order('expiration_date')\
            .execute()
        
        if not lots.data:
            return jsonify({'error': 'No available lots'}), 400
        
        # Allocate from lots (FEFO)
        remaining = quantity_needed
        used_lots = []
        
        for lot in lots.data:
            if remaining <= 0:
                break
            
            take_qty = min(remaining, lot['quantity'])
            new_lot_qty = lot['quantity'] - take_qty
            
            # Update lot quantity
            supabase.table('inventory_lots')\
                .update({'quantity': new_lot_qty})\
                .eq('id', lot['id'])\
                .execute()
            
            used_lots.append({
                'lot_number': lot['lot_number'],
                'quantity': take_qty,
                'expiration_date': lot['expiration_date']
            })
            
            remaining -= take_qty
        
        if remaining > 0:
            return jsonify({'error': f'Insufficient stock. Short by {remaining} units'}), 400
        
        # Update material total
        material = supabase.table('materials').select('quantity').eq('id', material_id).single().execute()
        new_quantity = material.data['quantity'] - quantity_needed
        supabase.table('materials').update({'quantity': new_quantity}).eq('id', material_id).execute()
        
        # Create inventory record
        record_data = {
            'material_id': material_id,
            'type': 'out',
            'quantity': quantity_needed,
            'operator': data.get('operator', 'System'),
            'reason': data.get('reason', 'Stock-out')
        }
        supabase.table('inventory_records').insert(record_data).execute()
        
        return jsonify({
            'success': True,
            'quantity': quantity_needed,
            'used_lots': used_lots,
            'message': f"Stock-out successful using FEFO: {quantity_needed} units"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
