import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env.local')

# 数据库连接配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'damage_assessment_db'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

# 数据库连接URL
DATABASE_URL = f"mysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"

class DamageAssessmentDB:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print(f"✅ 成功连接到MySQL数据库: {DB_CONFIG['database']}")
                return True
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def create_database(self):
        """创建数据库"""
        try:
            # 连接到MySQL服务器（不指定数据库）
            config = DB_CONFIG.copy()
            database_name = config.pop('database')
            
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            
            # 创建数据库
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {database_name} 
                CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            print(f"✅ 数据库 '{database_name}' 创建成功")
            
            cursor.close()
            connection.close()
            
            # 重新连接到新创建的数据库
            return self.connect()
            
        except Error as e:
            print(f"❌ 创建数据库失败: {e}")
            return False
    
    def create_tables(self):
        """创建数据表"""
        if not self.connection or not self.connection.is_connected():
            print("❌ 数据库未连接")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 1. 定损检测主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS damage_assessments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    task_id VARCHAR(36) UNIQUE NOT NULL,
                    status ENUM('pending', 'detecting', 'analyzing', 'completed', 'failed') DEFAULT 'pending',
                    vehicle_brand VARCHAR(50),
                    vehicle_model VARCHAR(100),
                    brand_confidence DECIMAL(5,2),
                    total_parts_cost DECIMAL(10,2) DEFAULT 0.00,
                    total_labor_cost DECIMAL(10,2) DEFAULT 0.00,
                    total_cost DECIMAL(10,2) DEFAULT 0.00,
                    total_repair_time INT DEFAULT 0,
                    assessment_conclusion TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    ai_analysis JSON,
                    priority_analysis JSON,
                    
                    INDEX idx_task_id (task_id),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at),
                    INDEX idx_vehicle_brand (vehicle_brand)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 2. 检测图片表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessment_images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    assessment_id INT NOT NULL,
                    image_id VARCHAR(36) NOT NULL,
                    original_filename VARCHAR(255),
                    original_path VARCHAR(500),
                    annotated_path VARCHAR(500),
                    thumbnail_path VARCHAR(500),
                    file_size INT,
                    width INT,
                    height INT,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_primary BOOLEAN DEFAULT FALSE,
                    
                    FOREIGN KEY (assessment_id) REFERENCES damage_assessments(id) ON DELETE CASCADE,
                    INDEX idx_assessment_id (assessment_id),
                    INDEX idx_image_id (image_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 3. 损伤区域表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS damage_regions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    assessment_id INT NOT NULL,
                    image_id VARCHAR(36),
                    damage_type VARCHAR(50) NOT NULL,
                    damage_part VARCHAR(100),
                    severity_level ENUM('LOW', 'MEDIUM', 'HIGH', 'SEVERE', 'CRITICAL'),
                    confidence DECIMAL(5,2),
                    bbox_x INT,
                    bbox_y INT,
                    bbox_width INT,
                    bbox_height INT,
                    repair_priority INT DEFAULT 0,
                    repair_order INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (assessment_id) REFERENCES damage_assessments(id) ON DELETE CASCADE,
                    INDEX idx_assessment_id (assessment_id),
                    INDEX idx_priority (repair_priority),
                    INDEX idx_damage_type (damage_type),
                    INDEX idx_severity (severity_level)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 4. 维修项目明细表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repair_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    assessment_id INT NOT NULL,
                    region_id INT,
                    item_name VARCHAR(100) NOT NULL,
                    repair_method VARCHAR(50),
                    parts_cost DECIMAL(8,2) DEFAULT 0.00,
                    labor_cost DECIMAL(8,2) DEFAULT 0.00,
                    total_cost DECIMAL(8,2) DEFAULT 0.00,
                    parts_name VARCHAR(100),
                    parts_quantity INT DEFAULT 1,
                    parts_unit_price DECIMAL(8,2) DEFAULT 0.00,
                    labor_hours DECIMAL(4,1) DEFAULT 0.0,
                    labor_hourly_rate DECIMAL(6,2) DEFAULT 0.00,
                    repair_priority INT DEFAULT 0,
                    repair_order INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (assessment_id) REFERENCES damage_assessments(id) ON DELETE CASCADE,
                    FOREIGN KEY (region_id) REFERENCES damage_regions(id) ON DELETE CASCADE,
                    INDEX idx_assessment_id (assessment_id),
                    INDEX idx_region_id (region_id),
                    INDEX idx_repair_priority (repair_priority)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            self.connection.commit()
            print("✅ 数据表创建成功")
            return True
            
        except Error as e:
            print(f"❌ 创建数据表失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def insert_sample_data(self):
        """插入示例数据"""
        if not self.connection or not self.connection.is_connected():
            print("❌ 数据库未连接")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 插入定损记录
            assessments_data = [
                ('task_001', '丰田', '凯美瑞', 0.95, 2500.00, 800.00, 3300.00, 360,
                 '车辆前部受到中等程度损伤，建议及时修复，不影响行车安全', 'completed'),
                ('task_002', '本田', '雅阁', 0.88, 1800.00, 600.00, 2400.00, 240,
                 '车辆侧面轻微损伤，建议择期修复', 'completed'),
                ('task_003', '大众', '帕萨特', 0.92, 3200.00, 1200.00, 4400.00, 480,
                 '车辆后部严重损伤，建议立即处理', 'completed')
            ]
            
            cursor.executemany("""
                INSERT INTO damage_assessments 
                (task_id, vehicle_brand, vehicle_model, brand_confidence, 
                 total_parts_cost, total_labor_cost, total_cost, total_repair_time,
                 assessment_conclusion, status, created_at, completed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, assessments_data)
            
            # 获取插入的assessment_id
            assessment_ids = []
            for i in range(len(assessments_data)):
                assessment_ids.append(cursor.lastrowid - len(assessments_data) + i + 1)
            
            # 插入图片记录
            images_data = [
                (assessment_ids[0], 'img_001', 'car_damage_001.jpg',
                 'assets/original/2026/03/19/task_001.jpg',
                 'assets/annotated/2026/03/19/task_001_annotated.jpg',
                 'assets/thumbnails/task_001_thumb.jpg', 2048576, 1920, 1080, True),
                (assessment_ids[1], 'img_002', 'car_damage_002.jpg',
                 'assets/original/2026/03/19/task_002.jpg',
                 'assets/annotated/2026/03/19/task_002_annotated.jpg',
                 'assets/thumbnails/task_002_thumb.jpg', 1536000, 1280, 720, True),
                (assessment_ids[2], 'img_003', 'car_damage_003.jpg',
                 'assets/original/2026/03/19/task_003.jpg',
                 'assets/annotated/2026/03/19/task_003_annotated.jpg',
                 'assets/thumbnails/task_003_thumb.jpg', 1843200, 1920, 1080, True)
            ]
            
            cursor.executemany("""
                INSERT INTO assessment_images 
                (assessment_id, image_id, original_filename, original_path, 
                 annotated_path, thumbnail_path, file_size, width, height, is_primary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, images_data)
            
            # 插入损伤区域记录
            regions_data = [
                (assessment_ids[0], 'img_001', '车漆损伤', '前保险杠', 'MEDIUM', 0.85,
                 300, 400, 200, 100, 1, 1),
                (assessment_ids[0], 'img_001', '划痕', '左前门', 'LOW', 0.72,
                 600, 350, 150, 80, 2, 2),
                (assessment_ids[1], 'img_002', '玻璃损伤', '前挡风玻璃', 'MEDIUM', 0.78,
                 400, 200, 300, 150, 1, 1),
                (assessment_ids[2], 'img_003', '钣金损伤', '后保险杠', 'HIGH', 0.88,
                 500, 600, 250, 120, 1, 1)
            ]
            
            cursor.executemany("""
                INSERT INTO damage_regions 
                (assessment_id, image_id, damage_type, damage_part, severity_level,
                 confidence, bbox_x, bbox_y, bbox_width, bbox_height,
                 repair_priority, repair_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, regions_data)
            
            # 获取region_id
            region_ids = []
            for i in range(len(regions_data)):
                region_ids.append(cursor.lastrowid - len(regions_data) + i + 1)
            
            # 插入维修项目记录
            repair_items_data = [
                (assessment_ids[0], region_ids[0], '前保险杠修复', '喷漆修复',
                 1200.00, 450.00, 1650.00, '前保险杠', 1, 1200.00, 3.0, 150.00, 1, 1),
                (assessment_ids[0], region_ids[1], '左前门划痕修复', '抛光处理',
                 0.00, 150.00, 150.00, None, 0, 0.00, 1.0, 150.00, 2, 2),
                (assessment_ids[1], region_ids[2], '前挡风玻璃修复', '玻璃修复',
                 1500.00, 300.00, 1800.00, '前挡风玻璃', 1, 1500.00, 2.0, 150.00, 1, 1),
                (assessment_ids[2], region_ids[3], '后保险杠更换', '钣金更换',
                 2000.00, 600.00, 2600.00, '后保险杠', 1, 2000.00, 4.0, 150.00, 1, 1)
            ]
            
            cursor.executemany("""
                INSERT INTO repair_items 
                (assessment_id, region_id, item_name, repair_method,
                 parts_cost, labor_cost, total_cost, parts_name, parts_quantity, parts_unit_price,
                 labor_hours, labor_hourly_rate, repair_priority, repair_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, repair_items_data)
            
            # 插入AI分析数据
            ai_analysis_data = {
                "vehicle_info": {
                    "brand": "丰田",
                    "model": "凯美瑞",
                    "year": "2022",
                    "confidence": 0.95
                },
                "analysis_summary": {
                    "total_damage_count": 2,
                    "severity_distribution": {
                        "medium": 1,
                        "low": 1
                    },
                    "overall_impact": "中等"
                },
                "budget_breakdown": {
                    "total_parts_cost": 1200.00,
                    "total_labor_cost": 600.00,
                    "total_cost": 1800.00,
                    "currency": "CNY"
                }
            }
            
            cursor.execute("""
                UPDATE damage_assessments 
                SET ai_analysis = %s 
                WHERE task_id = 'task_001'
            """, (json.dumps(ai_analysis_data, ensure_ascii=False),))
            
            # 插入预修车分析数据
            priority_analysis_data = {
                "repair_sequence": [
                    {
                        "order": 1,
                        "damage_type": "车漆损伤",
                        "damage_part": "前保险杠",
                        "priority": "medium",
                        "reason": "影响车辆外观，可能进一步扩大",
                        "estimated_time": "3小时",
                        "estimated_cost": 1650.00
                    },
                    {
                        "order": 2,
                        "damage_type": "划痕",
                        "damage_part": "左前门",
                        "priority": "low",
                        "reason": "仅影响外观，不影响功能",
                        "estimated_time": "1小时",
                        "estimated_cost": 150.00
                    }
                ],
                "summary": {
                    "total_items": 2,
                    "total_time": "4小时",
                    "total_cost": 1800.00,
                    "priority_distribution": {
                        "high": 0,
                        "medium": 1,
                        "low": 1
                    }
                }
            }
            
            cursor.execute("""
                UPDATE damage_assessments 
                SET priority_analysis = %s 
                WHERE task_id = 'task_001'
            """, (json.dumps(priority_analysis_data, ensure_ascii=False),))
            
            self.connection.commit()
            print("✅ 示例数据插入成功")
            return True
            
        except Error as e:
            print(f"❌ 插入示例数据失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def query_data(self):
        """查询数据"""
        if not self.connection or not self.connection.is_connected():
            print("❌ 数据库未连接")
            return
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 查询定损记录
            print("\n📋 定损记录:")
            cursor.execute("SELECT * FROM damage_assessments ORDER BY created_at DESC")
            assessments = cursor.fetchall()
            
            for assessment in assessments:
                print(f"  📄 {assessment['task_id']} - {assessment['vehicle_brand']} {assessment['vehicle_model']} - ¥{assessment['total_cost']}")
            
            # 查询损伤区域
            print("\n🔍 损伤区域:")
            cursor.execute("""
                SELECT da.task_id, dr.damage_type, dr.damage_part, dr.severity_level, dr.repair_priority
                FROM damage_regions dr
                JOIN damage_assessments da ON dr.assessment_id = da.id
                ORDER BY dr.repair_order
            """)
            regions = cursor.fetchall()
            
            for region in regions:
                print(f"  ⚠️  {region['task_id']} - {region['damage_type']} ({region['damage_part']}) - {region['severity_level']} - 优先级{region['repair_priority']}")
            
            # 统计信息
            print("\n📊 统计信息:")
            cursor.execute("""
                SELECT 
                    vehicle_brand,
                    COUNT(*) as assessment_count,
                    AVG(total_cost) as avg_cost,
                    SUM(total_cost) as total_cost
                FROM damage_assessments 
                WHERE status = 'completed'
                GROUP BY vehicle_brand
                ORDER BY assessment_count DESC
            """)
            stats = cursor.fetchall()
            
            for stat in stats:
                print(f"  🚗 {stat['vehicle_brand']}: {stat['assessment_count']}次, 平均¥{stat['avg_cost']:.2f}, 总计¥{stat['total_cost']:.2f}")
            
        except Error as e:
            print(f"❌ 查询数据失败: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 数据库连接已关闭")

def main():
    print("🚗 开始初始化车辆定损系统数据库...")
    
    # 创建数据库实例
    db = DamageAssessmentDB()
    
    if not db.connection or not db.connection.is_connected():
        print("❌ 无法连接到数据库，尝试创建数据库...")
        if not db.create_database():
            print("💥 数据库初始化失败！")
            return
    
    # 创建数据表
    if not db.create_tables():
        print("💥 创建数据表失败！")
        return
    
    # 插入示例数据
    if not db.insert_sample_data():
        print("💥 插入示例数据失败！")
        return
    
    # 查询数据
    db.query_data()
    
    # 关闭连接
    db.close()
    
    print("\n🎉 数据库初始化完成！")

if __name__ == "__main__":
    main()
