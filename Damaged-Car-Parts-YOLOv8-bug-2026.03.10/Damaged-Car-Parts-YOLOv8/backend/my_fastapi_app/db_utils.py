import mysql.connector
from mysql.connector import Error
import json
import os
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

class DamageAssessmentDB:
    """车辆定损系统数据库操作类"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print(f"✅ 数据库连接成功: {DB_CONFIG['database']}")
                return True
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def add_assessment(self, task_id, vehicle_brand, vehicle_model, total_cost, conclusion=""):
        """添加定损记录"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO damage_assessments 
                (task_id, vehicle_brand, vehicle_model, total_cost, assessment_conclusion, status)
                VALUES (%s, %s, %s, %s, %s, 'completed')
            """, (task_id, vehicle_brand, vehicle_model, total_cost, conclusion))
            
            assessment_id = cursor.lastrowid
            self.connection.commit()
            print(f"✅ 添加定损记录成功: {task_id}")
            return assessment_id
            
        except Error as e:
            print(f"❌ 添加定损记录失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_assessment_by_task_id(self, task_id):
        """根据task_id获取定损记录"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM damage_assessments WHERE task_id = %s
            """, (task_id,))
            
            result = cursor.fetchone()
            return result
            
        except Error as e:
            print(f"❌ 查询定损记录失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_all_assessments(self, limit=10):
        """获取所有定损记录"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, task_id, vehicle_brand, vehicle_model, total_cost, status, created_at 
                FROM damage_assessments 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            return results
            
        except Error as e:
            print(f"❌ 查询定损记录失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def add_damage_region(self, task_id, part_name, damage_level, repair_priority,
                         detection_confidence=0.85, bbox_x=0, bbox_y=0, bbox_width=0, bbox_height=0,
                         sort_order=0):
        """添加损伤部位"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO damage_parts 
                (task_id, part_name, damage_level, repair_priority, 
                 detection_confidence, bbox_x, bbox_y, bbox_width, bbox_height, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (task_id, part_name, damage_level, repair_priority,
                 detection_confidence, bbox_x, bbox_y, bbox_width, bbox_height, sort_order))
            
            region_id = cursor.lastrowid
            self.connection.commit()
            print(f"✅ 添加损伤部位成功: {part_name} - {damage_level}")
            return region_id
            
        except Error as e:
            print(f"❌ 添加损伤部位失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_damage_regions_by_assessment(self, task_id):
        """获取任务的所有损伤部位"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM damage_parts 
                WHERE task_id = %s 
                ORDER BY sort_order
            """, (task_id,))
            
            results = cursor.fetchall()
            return results
            
        except Error as e:
            print(f"❌ 查询损伤部位失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def update_ai_analysis(self, task_id, ai_analysis_data):
        """更新AI分析结果"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE damage_assessments 
                SET ai_analysis = %s 
                WHERE task_id = %s
            """, (json.dumps(ai_analysis_data, ensure_ascii=False), task_id))
            
            self.connection.commit()
            print(f"✅ 更新AI分析结果成功: {task_id}")
            return True
            
        except Error as e:
            print(f"❌ 更新AI分析结果失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def update_priority_analysis(self, task_id, priority_analysis_data):
        """更新预修车分析结果"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE damage_assessments 
                SET priority_analysis = %s 
                WHERE task_id = %s
            """, (json.dumps(priority_analysis_data, ensure_ascii=False), task_id))
            
            self.connection.commit()
            print(f"✅ 更新预修车分析结果成功: {task_id}")
            return True
            
        except Error as e:
            print(f"❌ 更新预修车分析结果失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def get_statistics(self):
        """获取统计信息"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 品牌统计
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
            brand_stats = cursor.fetchall()
            
            # 总体统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_assessments,
                    AVG(total_cost) as avg_cost,
                    SUM(total_cost) as total_cost,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
                FROM damage_assessments
            """)
            total_stats = cursor.fetchone()
            
            return {
                'brand_stats': brand_stats,
                'total_stats': total_stats
            }
            
        except Error as e:
            print(f"❌ 获取统计信息失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 数据库连接已关闭")

# 使用示例
def example_usage():
    """使用示例"""
    db = DamageAssessmentDB()
    
    # 1. 添加定损记录
    assessment_id = db.add_assessment(
        task_id="task_004",
        vehicle_brand="奥迪",
        vehicle_model="A4",
        total_cost=2800.00,
        conclusion="车辆轻微损伤，建议及时修复"
    )
    
    if assessment_id:
        # 2. 添加损伤区域
        region_id = db.add_damage_region(
            assessment_id=assessment_id,
            image_id="img_004",
            damage_type="划痕",
            damage_part="右前门",
            severity_level="LOW",
            confidence=0.75,
            bbox_x=400, bbox_y=300, bbox_width=120, bbox_height=60,
            repair_priority=1
        )
        
        # 3. 更新AI分析结果
        ai_data = {
            "vehicle_info": {"brand": "奥迪", "model": "A4", "confidence": 0.92},
            "analysis_summary": {"total_damage_count": 1, "overall_impact": "轻微"}
        }
        db.update_ai_analysis("task_004", ai_data)
        
        # 4. 更新预修车分析结果
        priority_data = {
            "repair_sequence": [
                {"order": 1, "damage_type": "划痕", "damage_part": "右前门", 
                 "priority": "low", "estimated_cost": 2800.00}
            ]
        }
        db.update_priority_analysis("task_004", priority_data)
    
    # 5. 查询数据
    print("\n📋 最新定损记录:")
    assessments = db.get_all_assessments(5)
    for assessment in assessments:
        print(f"  📄 {assessment['task_id']} - {assessment['vehicle_brand']} {assessment['vehicle_model']} - ¥{assessment['total_cost']}")
    
    # 6. 获取统计信息
    print("\n📊 统计信息:")
    stats = db.get_statistics()
    if stats:
        print(f"  总定损记录: {stats['total_stats']['total_assessments']}")
        print(f"  平均费用: ¥{stats['total_stats']['avg_cost']:.2f}")
        print(f"  完成记录: {stats['total_stats']['completed_count']}")
    
    db.close()

if __name__ == "__main__":
    example_usage()
