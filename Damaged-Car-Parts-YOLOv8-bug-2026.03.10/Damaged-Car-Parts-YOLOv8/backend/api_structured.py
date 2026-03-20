# 后端 API 改造：从结构化表读取数据
# 替换原有的 main.py 中相关接口

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ===== 数据模型定义 =====

class DamagePart(BaseModel):
    id: int
    part_name: str
    damage_level: str
    damage_type: Optional[str] = None
    repair_priority: str
    repair_suggestion: Optional[str] = None

class RepairItem(BaseModel):
    id: int
    damage_part_id: Optional[int] = None
    item_name: str
    repair_method: Optional[str] = None
    parts_cost: float = 0.0
    labor_cost: float = 0.0
    total_cost: float = 0.0
    parts_name: Optional[str] = None
    parts_quantity: float = 1.0
    parts_unit_price: Optional[float] = None
    labor_hours: float = 0.0
    labor_hourly_rate: float = 0.0
    repair_priority: str
    repair_order: int = 0
    notes: Optional[str] = None

class SafetyTip(BaseModel):
    id: int
    tip_text: str
    tip_order: int = 0

class VehicleInfo(BaseModel):
    id: int
    brand: str
    model: str
    year: Optional[str] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    mileage: Optional[float] = None

class DamageAssessment(BaseModel):
    id: int
    task_id: str
    status: str
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    brand_confidence: Optional[float] = None
    total_parts_cost: Optional[float] = None
    total_labor_cost: Optional[float] = None
    total_cost: Optional[float] = None
    total_repair_time: Optional[float] = None
    assessment_conclusion: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class AssessmentReport(BaseModel):
    assessment: DamageAssessment
    vehicle_info: Optional[VehicleInfo] = None
    damage_parts: List[DamagePart] = []
    repair_items: List[RepairItem] = []
    safety_tips: List[SafetyTip] = []

# ===== API 接口改造 =====

@router.get('/api/detection/structured/{task_id}', response_model=AssessmentReport)
async def get_structured_assessment(task_id: str):
    """
    获取结构化的评估报告（从结构化表读取）
    """
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. 获取评估主表数据
        cursor.execute("""
            SELECT * FROM damage_assessments_new 
            WHERE task_id = %s LIMIT 1
        """, (task_id,))
        assessment_row = cursor.fetchone()
        
        if not assessment_row:
            raise HTTPException(status_code=404, detail=f"未找到任务 {task_id} 的评估数据")
        
        assessment = DamageAssessment(**assessment_row)
        
        # 2. 获取车辆信息
        cursor.execute("""
            SELECT * FROM vehicle_info 
            WHERE assessment_id = %s LIMIT 1
        """, (assessment.id,))
        vehicle_row = cursor.fetchone()
        vehicle_info = VehicleInfo(**vehicle_row) if vehicle_row else None
        
        # 3. 获取损伤部位
        cursor.execute("""
            SELECT * FROM damage_parts 
            WHERE assessment_id = %s 
            ORDER BY sort_order, id
        """, (assessment.id,))
        damage_parts = [DamagePart(**row) for row in cursor.fetchall()]
        
        # 4. 获取维修项目
        cursor.execute("""
            SELECT * FROM repair_items_new 
            WHERE assessment_id = %s 
            ORDER BY repair_priority, repair_order, id
        """, (assessment.id,))
        repair_items = [RepairItem(**row) for row in cursor.fetchall()]
        
        # 5. 获取安全提示
        cursor.execute("""
            SELECT * FROM safety_tips 
            WHERE assessment_id = %s 
            ORDER BY tip_order, id
        """, (assessment.id,))
        safety_tips = [SafetyTip(**row) for row in cursor.fetchall()]
        
        return AssessmentReport(
            assessment=assessment,
            vehicle_info=vehicle_info,
            damage_parts=damage_parts,
            repair_items=repair_items,
            safety_tips=safety_tips
        )
        
    except Exception as e:
        print(f"查询结构化数据失败: {e}")
        raise HTTPException(status_code=500, detail="查询数据失败")
    finally:
        cursor.close()
        connection.close()

@router.get('/api/detection/structured/{task_id}/summary')
async def get_assessment_summary(task_id: str):
    """
    获取评估摘要（用于列表展示）
    """
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM v_damage_assessment_report 
            WHERE task_id = %s LIMIT 1
        """, (task_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到任务 {task_id}")
        
        return result
        
    except Exception as e:
        print(f"查询评估摘要失败: {e}")
        raise HTTPException(status_code=500, detail="查询数据失败")
    finally:
        cursor.close()
        connection.close()

@router.get('/api/detection/structured/stats/damage-level')
async def get_damage_level_stats():
    """
    按损伤等级统计（用于报表）
    """
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                dp.damage_level,
                COUNT(*) as count,
                AVG(da.total_cost) as avg_cost,
                MIN(da.total_cost) as min_cost,
                MAX(da.total_cost) as max_cost
            FROM damage_assessments_new da
            JOIN damage_parts dp ON da.id = dp.assessment_id
            GROUP BY dp.damage_level
            ORDER BY 
                CASE dp.damage_level
                    WHEN '严重' THEN 1
                    WHEN '重度' THEN 2
                    WHEN '中度' THEN 3
                    WHEN '中等' THEN 4
                    WHEN '轻度' THEN 5
                    WHEN '轻微' THEN 6
                    ELSE 7
                END
        """)
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"查询统计数据失败: {e}")
        raise HTTPException(status_code=500, detail="查询数据失败")
    finally:
        cursor.close()
        connection.close()

@router.get('/api/detection/structured/stats/repair-priority')
async def get_repair_priority_stats():
    """
    按维修优先级统计
    """
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                ri.repair_priority,
                COUNT(*) as item_count,
                SUM(ri.total_cost) as total_cost,
                AVG(ri.total_cost) as avg_cost,
                SUM(ri.labor_hours) as total_labor_hours
            FROM repair_items_new ri
            GROUP BY ri.repair_priority
            ORDER BY 
                CASE ri.repair_priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END
        """)
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"查询统计数据失败: {e}")
        raise HTTPException(status_code=500, detail="查询数据失败")
    finally:
        cursor.close()
        connection.close()

# 兼容性接口：返回原有格式的数据（前端无需修改）
@router.get('/api/detection/result/{task_id}')
async def get_detection_result_legacy(task_id: str):
    """
    兼容性接口：从结构化表组装成原有格式
    """
    try:
        # 获取结构化数据
        structured_data = await get_structured_assessment(task_id)
        
        # 转换为原有格式
        regions = []
        for part in structured_data.damage_parts:
            regions.append({
                "part_code": part.part_name,
                "damage_type": part.damage_type or "UNKNOWN",
                "severity_level": map_severity_to_level(part.damage_level),
                "bbox": None,  # 结构化表不存储 bbox
                "confidence": 0.95
            })
        
        # 组装图片数据（需要从其他地方获取）
        images = []  # TODO: 从图片表获取
        
        return {
            "taskId": task_id,
            "status": structured_data.assessment.status,
            "regions": regions,
            "images": images,
            "detectionTime": structured_data.assessment.created_at.isoformat(),
            "vehicleInfo": {
                "brand": structured_data.assessment.vehicle_brand,
                "model": structured_data.assessment.vehicle_model
            } if structured_data.assessment.vehicle_brand else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"转换数据格式失败: {e}")
        raise HTTPException(status_code=500, detail="数据格式转换失败")

def map_severity_to_level(severity: str) -> str:
    """将中文严重程度映射到英文级别"""
    mapping = {
        '轻微': 'LOW',
        '轻度': 'LOW',
        '中等': 'MEDIUM',
        '中度': 'MEDIUM',
        '严重': 'HIGH',
        '重度': 'HIGH'
    }
    return mapping.get(severity, 'MEDIUM')
