"""
Supabase Database Module | Supabase 数据库模块

Replaces SQLite with Supabase (PostgreSQL) for cloud-based storage.
用 Supabase（PostgreSQL）替换 SQLite 以实现基于云的存储。
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

# Load environment variables | 加载环境变量
load_dotenv()

# Initialize Supabase client | 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for backend

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase_client():
    """获取 Supabase 客户端 | Get Supabase client"""
    return supabase


def test_connection():
    """测试数据库连接 | Test database connection"""
    try:
        response = supabase.table('materials').select('count', count='exact').execute()
        print(f"✅ Connected to Supabase! Total materials: {response.count}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False


def generate_mock_records():
    """
    生成模拟出入库记录 | Generate mock inventory records
    
    Note: Only generates records, assumes materials already exist in Supabase
    注意：仅生成记录，假设物料已存在于 Supabase 中
    """
    try:
        # Get all material IDs | 获取所有物料 ID
        response = supabase.table('materials').select('id').execute()
        material_ids = [item['id'] for item in response.data]
        
        if not material_ids:
            print("⚠️ No materials found. Please insert materials first.")
            return
        
        reasons_in = ['采购入库', '生产完工入库', '退货入库', '调拨入库']  # Purchase, Production, Return, Transfer
        reasons_out = ['生产领料', '销售出库', '研发领用', '调拨出库', '返修出库']  # Production, Sales, R&D, Transfer, Repair
        operators = ['张三', '李四', '王五', '赵六', '系统']  # Zhang San, Li Si, Wang Wu, Zhao Liu, System
        
        records = []
        
        # Generate records for past 7 days | 生成过去7天的记录
        for day_offset in range(7, 0, -1):
            record_date = datetime.now() - timedelta(days=day_offset)
            num_records = random.randint(5, 15)  # 5-15 records per day | 每天5-15条记录
            
            for _ in range(num_records):
                material_id = random.choice(material_ids)
                record_type = random.choice(['in', 'out'])
                quantity = random.randint(5, 30)
                operator = random.choice(operators)
                reason = random.choice(reasons_in if record_type == 'in' else reasons_out)
                
                # Random time during the day | 当天的随机时间
                hour = random.randint(8, 18)
                minute = random.randint(0, 59)
                record_time = record_date.replace(hour=hour, minute=minute)
                
                records.append({
                    'material_id': material_id,
                    'type': record_type,
                    'quantity': quantity,
                    'operator': operator,
                    'reason': reason,
                    'created_at': record_time.isoformat()
                })
        
        # Generate today's records | 生成今天的记录
        today = datetime.now()
        num_today_records = random.randint(15, 25)
        
        for _ in range(num_today_records):
            material_id = random.choice(material_ids)
            record_type = random.choice(['in', 'out'])
            quantity = random.randint(5, 30)
            operator = random.choice(operators)
            reason = random.choice(reasons_in if record_type == 'in' else reasons_out)
            
            hour = random.randint(8, datetime.now().hour if datetime.now().hour > 8 else 9)
            minute = random.randint(0, 59)
            record_time = today.replace(hour=hour, minute=minute)
            
            records.append({
                'material_id': material_id,
                'type': record_type,
                'quantity': quantity,
                'operator': operator,
                'reason': reason,
                'created_at': record_time.isoformat()
            })
        
        # Insert all records | 插入所有记录
        response = supabase.table('inventory_records').insert(records).execute()
        print(f"✅ Generated {len(records)} mock inventory records")
        
    except Exception as e:
        print(f"❌ Failed to generate mock records: {e}")


if __name__ == '__main__':
    print("Testing Supabase connection...")
    print("测试 Supabase 连接...")
    
    if test_connection():
        print("\n✅ Database connection successful!")
        print("✅ 数据库连接成功！")
        
        # Ask if user wants to generate mock records
        # 询问用户是否要生成模拟记录
        response = input("\nGenerate mock inventory records? (y/n): ")
        if response.lower() == 'y':
            generate_mock_records()
    else:
        print("\n❌ Database connection failed!")
        print("❌ 数据库连接失败！")
        print("\nPlease check:")
        print("请检查：")
        print("1. .env file exists with correct credentials")
        print("   .env 文件存在且凭据正确")
        print("2. Supabase project is running")
        print("   Supabase 项目正在运行")
        print("3. Tables are created (run SQL in Supabase dashboard)")
        print("   表已创建（在 Supabase 仪表板中运行 SQL）")
