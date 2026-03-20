import io
import uuid
import os
import mysql.connector
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import uvicorn
import numpy as np
from enum import Enum
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from pydantic import BaseModel
import json
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
from typing import List, Optional
from numpy import ndarray
from typing import Tuple
from PIL import Image
import base64
from fastapi import Response
import httpx
from dotenv import load_dotenv

# 加载 .env 和 .env.local 文件
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))

# 数据库连接配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'damage_assessment_db'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def create_feedback_table_if_not_exists():
    """创建反馈表（如果不存在）"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                feedback_id VARCHAR(36) UNIQUE NOT NULL COMMENT '反馈唯一标识符',
                contact_info VARCHAR(100) COMMENT '联系方式（手机/微信/邮箱）',
                feedback_type VARCHAR(50) NOT NULL COMMENT '反馈类型（产品建议/功能异常/体验交互等）',
                feedback_content TEXT NOT NULL COMMENT '反馈内容详情',
                assessment_task_id VARCHAR(36) COMMENT '关联的定损任务ID（可选）',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                
                INDEX idx_feedback_id (feedback_id),
                INDEX idx_assessment_task_id (assessment_task_id),
                INDEX idx_feedback_type (feedback_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='用户意见与反馈表 - 存储用户提交的反馈信息'
        """)
        
        # 创建检测相关的表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                task_id VARCHAR(36) UNIQUE NOT NULL COMMENT '检测任务唯一标识符',
                status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态（pending/processing/completed/failed）',
                progress INT DEFAULT 0 COMMENT '任务进度百分比（0-100）',
                damage_types JSON COMMENT '检测到的损伤类型数组（JSON格式）',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                
                INDEX idx_task_id (task_id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='车辆损伤检测任务表 - 存储YOLO检测任务的主要信息'
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_images (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                task_id VARCHAR(36) NOT NULL COMMENT '关联的检测任务ID',
                image_type ENUM('original', 'yolo_annotated', 'damage_marked') DEFAULT 'original' COMMENT '图片类型',
                image_url VARCHAR(500) NOT NULL COMMENT '图片URL地址',
                original_url VARCHAR(500) COMMENT '原始图片地址',
                annotated_url VARCHAR(500) COMMENT 'YOLO标注后图片地址',
                
                INDEX idx_task_id (task_id),
                INDEX idx_image_type (image_type),
                FOREIGN KEY (task_id) REFERENCES assessment_tasks(task_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='任务图片表 - 存储评估相关的图片文件信息'
        """)
        
        connection.commit()
        print("✅ 数据库表检查/创建完成")
        return True
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 初始化时创建反馈表
create_feedback_table_if_not_exists()
  
  




class Detection:
 def __init__(self, 
      model_path: str, 
   classes: List[str]
  ):
  self.model_path = model_path
  self.classes = classes
  self.model = self.__load_model()

 def __load_model(self) -> cv2.dnn_Net:
  net = cv2.dnn.readNet(self.model_path)
  net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
  net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
  return net

 def __extract_ouput(self, 
      preds: ndarray, 
   image_shape: Tuple[int, int], 
   input_shape: Tuple[int, int],
   score: float=0.1,
   nms: float=0.0, 
   confidence: float=0.0
  ) -> dict:
  class_ids, confs, boxes = list(), list(), list()

  image_height, image_width = image_shape
  input_height, input_width = input_shape
  x_factor = image_width / input_width
  y_factor = image_height / input_height
  
  rows = preds[0].shape[0]
  for i in range(rows):
   row = preds[0][i]
   conf = row[4]
   
   classes_score = row[4:]
   _,_,_, max_idx = cv2.minMaxLoc(classes_score)
   class_id = max_idx[1]
   # print(classes_score[class_id])
   if (classes_score[class_id] > score):
    confs.append(conf)
    label = self.classes[int(class_id)]
    class_ids.append(label)
    
    #extract boxes
    x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
    left = int((x - 0.5 * w) * x_factor)
    top = int((y - 0.5 * h) * y_factor)
    width = int(w * x_factor)
    height = int(h * y_factor)
    box = np.array([left, top, width, height])
    boxes.append(box)

  r_class_ids, r_confs, r_boxes = list(), list(), list()
  indexes = cv2.dnn.NMSBoxes(boxes, confs, confidence, nms) 
  for i in indexes:
   r_class_ids.append(class_ids[i])
   r_confs.append(confs[i]*100)
   r_boxes.append(boxes[i].tolist())

  return {
   'boxes' : r_boxes, 
   'confidences': r_confs, 
   'classes': r_class_ids
  }

 def __call__(self,
   image: ndarray, 
   width: int=640, 
   height: int=640, 
   score: float=0.1,
   nms: float=0.0, 
   confidence: float=0.0
  )-> dict:
  
  blob = cv2.dnn.blobFromImage(
     image, 1/255.0, (width, height), 
     swapRB=True, crop=False
    )
  self.model.setInput(blob)
  preds = self.model.forward()
  preds = preds.transpose((0, 2, 1))

  # extract output
  results = self.__extract_ouput(
   preds=preds,
   image_shape=image.shape[:2],
   input_shape=(height, width),
   score=score,
   nms=nms,
   confidence=confidence
  )
  return results 

detection = Detection(
   model_path=os.path.join(os.path.dirname(__file__), 'best.onnx'), 
   classes=['damaged door', 'damaged window', 'damaged headlight', 'damaged mirror', 'dent', 'damaged hood', 'damaged bumper', 'damaged wind shield'] 
)


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


_executor = ThreadPoolExecutor(max_workers=2)
_tasks = {}


def _map_damage_type(label: str) -> str:
  s = (label or "").strip().lower()
  if not s:
   return "PAINT_DAMAGE"
  if "window" in s or "wind shield" in s or "windshield" in s or "headlight" in s or "mirror" in s:
   return "GLASS_DAMAGE"
  if "dent" in s:
   return "METAL_DAMAGE"
  if "door" in s or "hood" in s or "bumper" in s:
   return "PAINT_DAMAGE"
  return "PAINT_DAMAGE"


def _run_detection_task(task_id: str, files_bytes: List[bytes]):
  _tasks[task_id]["status"] = "processing"
  _tasks[task_id]["progress"] = 5
  try:
    images_payload = []
    regions_payload = []
    all_damage_types = set()

    # 创建任务目录结构
    import os
    # 获取项目根目录的assets文件夹
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    base_assets_dir = os.path.join(project_root, "assets")
    
    task_dir = os.path.join(base_assets_dir, task_id)
    original_dir = os.path.join(task_dir, "original")
    annotated_dir = os.path.join(task_dir, "annotated")
    
    print(f"[Detection] Current dir: {current_dir}")
    print(f"[Detection] Project root: {project_root}")
    print(f"[Detection] Assets dir: {base_assets_dir}")
    
    # 确保目录存在
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(annotated_dir, exist_ok=True)
    
    print(f"[Detection] Created directories for task {task_id}: {task_dir}")

    total = max(1, len(files_bytes))
    for idx, file_bytes in enumerate(files_bytes):
      _tasks[task_id]["progress"] = int(5 + (idx / total) * 80)

      image_id = f"img_{idx}"
      
      # 保存原始图片
      original_filename = f"{image_id}_original.jpg"
      original_filepath = os.path.join(original_dir, original_filename)
      with open(original_filepath, "wb") as f:
        f.write(file_bytes)
      print(f"[Detection] Saved original image: {original_filepath}")

      pil = Image.open(io.BytesIO(file_bytes)).convert("RGB")
      arr = np.array(pil)
      bgr = arr[:, :, ::-1].copy()

      det = detection(bgr)
      classes = det.get("classes") or []
      boxes = det.get("boxes") or []
      confidences = det.get("confidences") or []

      # 在图片上绘制标注
      annotated_bgr = bgr.copy()
      for box, cls, conf in zip(boxes, classes, confidences):
        # YOLO输出格式: [left, top, width, height] -> 转换为 [x1, y1, x2, y2]
        left, top, width, height = map(int, box)
        x1, y1 = left, top
        x2, y2 = left + width, top + height
        damage_type = _map_damage_type(cls)
        all_damage_types.add(damage_type)
        
        # 绘制边界框
        color = (0, 255, 0) if damage_type == "PAINT_DAMAGE" else (0, 0, 255)
        cv2.rectangle(annotated_bgr, (x1, y1), (x2, y2), color, 2)
        
        # 添加标签
        label = f"{cls} {conf:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(annotated_bgr, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        cv2.putText(annotated_bgr, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # 保存损伤区域信息
        region_id = f"{image_id}_r{len(regions_payload)}"
        bbox_str = f"{x1},{y1},{x2},{y2}"
        
        regions_payload.append({
          "id": region_id,
          "image_id": image_id,
          "bbox": bbox_str,
          "damage_type": damage_type,
          "damage_type_label": cls,
          "severity_level": "MEDIUM",  # 默认中等严重程度
          "part_code": cls,
        })

      # 保存标注后的图片
      annotated_filename = f"{image_id}_annotated.jpg"
      annotated_filepath = os.path.join(annotated_dir, annotated_filename)
      annotated_rgb = annotated_bgr[:, :, ::-1]  # 转换回RGB
      annotated_pil = Image.fromarray(annotated_rgb)
      annotated_pil.save(annotated_filepath, "JPEG", quality=95)
      print(f"[Detection] Saved annotated image: {annotated_filepath}")

      # 将原始图片转换为base64用于前端显示
      img_buffer = io.BytesIO()
      pil.save(img_buffer, format='JPEG', quality=85)
      img_b64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

      # 将标注图片也转换为base64，用于前端切换显示
      annotated_buffer = io.BytesIO()
      annotated_pil.save(annotated_buffer, format='JPEG', quality=85)
      annotated_b64 = base64.b64encode(annotated_buffer.getvalue()).decode('utf-8')
      
      images_payload.append({
        "id": image_id,
        "image_url": f"data:image/jpeg;base64,{img_b64}",
        "annotated_image_url": f"data:image/jpeg;base64,{annotated_b64}",
        "thumb_url": None,
        "original_path": original_filepath,
        "annotated_path": annotated_filepath,
      })

    _tasks[task_id]["result"] = {
      "taskId": task_id,
      "damage_types": sorted(list(all_damage_types)),
      "images": images_payload,
      "regions": regions_payload,
    }
    _tasks[task_id]["status"] = "completed"
    _tasks[task_id]["progress"] = 100
    
    # 保存检测结果到数据库
    try:
      connection = get_db_connection()
      if connection:
        cursor = connection.cursor()
        
        # 插入主检测记录
        cursor.execute("""
          INSERT INTO assessment_tasks 
          (task_id, status, progress, damage_types, created_at, updated_at)
          VALUES (%s, %s, %s, %s, NOW(), NOW())
          ON DUPLICATE KEY UPDATE
          status = VALUES(status),
          progress = VALUES(progress),
          damage_types = VALUES(damage_types),
          updated_at = VALUES(updated_at)
        """, (
          task_id,
          "completed",
          100,
          json.dumps(sorted(list(all_damage_types)))
        ))
        
        # 插入图像记录（使用新的表结构）
        for img in images_payload:
          cursor.execute("""
            INSERT INTO task_images 
            (task_id, image_id, image_url, original_path, annotated_path)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            image_url = VALUES(image_url),
            original_path = VALUES(original_path),
            annotated_path = VALUES(annotated_path)
          """, (
            task_id,
            img.get("id", f"img_{len(images_payload)}"),
            img["image_url"],
            img.get("original_path", ""),
            img.get("annotated_path", "")
          ))
        
        # 插入损伤部位记录
        for i, region in enumerate(regions_payload):
            # 映射严重程度
            severity_mapping = {
                "LOW": "light",
                "MEDIUM": "medium", 
                "HIGH": "severe"
            }
            damage_level = severity_mapping.get(region.get('severity_level', 'MEDIUM'), 'medium')
            
            # 映射维修优先级
            priority_mapping = {
                "LOW": "low",
                "MEDIUM": "medium",
                "HIGH": "high"
            }
            repair_priority = priority_mapping.get(region.get('severity_level', 'MEDIUM'), 'medium')
            
            cursor.execute("""
                INSERT INTO damage_regions 
                (task_id, region_id, image_id, bbox, damage_type, damage_type_label, severity_level, part_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                bbox = VALUES(bbox),
                damage_type = VALUES(damage_type),
                damage_type_label = VALUES(damage_type_label),
                severity_level = VALUES(severity_level),
                part_code = VALUES(part_code)
            """, (
                task_id,
                region.get('id', f'region_{i}'),
                region.get('image_id', 'img_0'),
                region.get('bbox', ''),
                region.get('damage_type', ''),
                region.get('damage_type_label', ''),
                region.get('severity_level', ''),
                region.get('part_code', '')
            ))
        
        connection.commit()
        cursor.close()
        connection.close()
        print(f"[Detection] Task {task_id} results saved to database and local files")
        
    except Exception as db_error:
      print(f"[Detection Error] Failed to save to database: {db_error}")
      # 不影响主流程，继续返回结果
  except Exception as e:
    _tasks[task_id]["status"] = "failed"
    _tasks[task_id]["error"] = str(e)
    _tasks[task_id]["progress"] = 100


@app.post('/api/detection')
async def post_detection_api(
  file: Optional[UploadFile] = File(None),
  files: Optional[List[UploadFile]] = File(None),
):
  upload_files = []
  if files:
    upload_files.extend(files)
  if file:
    upload_files.append(file)

  if not upload_files:
    raise HTTPException(status_code=422, detail='field required: file/files')

  files_bytes = [await f.read() for f in upload_files]

  task_id = str(uuid.uuid4())
  _tasks[task_id] = {
    "id": task_id,
    "status": "queued",
    "progress": 0,
    "createdAt": datetime.utcnow().isoformat() + "Z",
    "result": None,
    "error": None,
    "fileCount": len(files_bytes),
  }
  _executor.submit(_run_detection_task, task_id, files_bytes)
  return {"taskId": task_id}


@app.get('/api/detection/result/{task_id}')
def get_detection_result(task_id: str):
  # 首先从内存中查找
  task = _tasks.get(task_id)
  
  if not task:
    # 如果内存中没有，尝试从数据库中查找
    try:
      connection = get_db_connection()
      if connection:
        cursor = connection.cursor(dictionary=True)
        
        # 查询主任务记录
        cursor.execute("""
          SELECT * FROM assessment_tasks 
          WHERE task_id = %s
        """, (task_id,))
        
        db_task = cursor.fetchone()
        if db_task:
          # 查询图像记录
          cursor.execute("""
            SELECT * FROM task_images 
            WHERE task_id = %s
          """, (task_id,))
          images = cursor.fetchall()
          
          # 查询损伤部位记录
          cursor.execute("""
            SELECT * FROM damage_parts 
            WHERE task_id = %s
            ORDER BY sort_order
          """, (task_id,))
          regions = cursor.fetchall()
          
          # 构建响应数据
          images_payload = []
          for img in images:
            annotated_image_url = None
            try:
              annotated_url = img.get("annotated_url")
              if annotated_url and annotated_url.startswith("http"):
                annotated_image_url = annotated_url
              elif annotated_url and os.path.exists(annotated_url):
                with open(annotated_url, "rb") as f:
                  annotated_b64 = base64.b64encode(f.read()).decode("utf-8")
                annotated_image_url = f"data:image/jpeg;base64,{annotated_b64}"
            except Exception as e:
              print(f"[Database] Failed to read annotated image for task {task_id}: {e}")

            images_payload.append({
              "id": img["id"],
              "image_url": img["image_url"],
              "original_url": img.get("original_url", img["image_url"]),
              "annotated_image_url": annotated_image_url,
              "image_type": img.get("image_type", "original")
            })
          
          regions_payload = []
          for region in regions:
            regions_payload.append({
              "id": region["region_id"],
              "image_id": region["image_id"],
              "bbox": region["bbox"],
              "damage_type": region["damage_type"],
              "damage_type_label": region["damage_type_label"],
              "severity_level": region["severity_level"],
              "part_code": region["part_code"],
            })
          
          # 解析损伤类型JSON
          damage_types = []
          if db_task["damage_types"]:
            try:
              damage_types = json.loads(db_task["damage_types"])
            except:
              damage_types = []
          
          result_data = {
            "taskId": task_id,
            "damage_types": damage_types,
            "images": images_payload,
            "regions": regions_payload,
          }
          
          cursor.close()
          connection.close()
          
          print(f"[Database] Retrieved task {task_id} from database")
          return {
            "status": db_task["status"],
            "progress": db_task["progress"],
            **result_data,
          }
        
        cursor.close()
        connection.close()
        
    except Exception as e:
      print(f"[Database Error] Failed to retrieve task {task_id}: {e}")
    
    # 如果内存和数据库都没有找到，返回404
    raise HTTPException(status_code=404, detail='Task not found')
  
  # 如果内存中找到，按原逻辑处理
  if task["status"] == "completed":
    payload = task.get("result") or {}
    return {
      "status": "completed",
      "progress": 100,
      **payload,
    }
  if task["status"] == "failed":
    return {
      "status": "failed",
      "progress": task.get("progress", 100),
      "error": task.get("error") or "Detection failed",
    }
  return {
    "status": "processing",
    "progress": task.get("progress", 0),
  }


@app.get('/api/detection/history')
def get_detection_history(page: int = 1, pageSize: int = 10, startDate: str = None, endDate: str = None, damageType: str = None, severity: str = None):
  # 从数据库读取历史记录
  all_items = []
  try:
    connection = get_db_connection()
    if connection:
      cursor = connection.cursor(dictionary=True)
      # 查询所有已完成的任务，按创建时间倒序
      cursor.execute("""
        SELECT 
          at.task_id as taskId,
          at.status,
          at.created_at as createdAt,
          da.vehicle_brand as brand,
          da.total_cost as amount,
          (SELECT COUNT(*) FROM damage_regions dr WHERE dr.task_id = at.task_id) as damageCount,
          '车辆损伤检测' as location
        FROM assessment_tasks at
        LEFT JOIN damage_assessments da ON at.task_id = da.task_id
        WHERE at.status = 'completed'
        ORDER BY at.created_at DESC
      """)
      
      db_items = cursor.fetchall()
      for item in db_items:
        all_items.append({
          "taskId": item["taskId"],
          "status": item["status"],
          "createdAt": item["createdAt"].isoformat() if item["createdAt"] else None,
          "brand": item["brand"] or "未知品牌",
          "amount": float(item["amount"]) if item["amount"] else 0,
          "damageCount": item["damageCount"] or 0,
          "location": item["location"]
        })
      
      cursor.close()
      connection.close()
      print(f"[History] Loaded {len(all_items)} records from database")
  except Exception as e:
    print(f"[History Error] Failed to load from database: {e}")
  
  # 如果数据库为空，回退到内存数据
  if not all_items:
    all_items = list(_tasks.values())
    all_items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
  
  total = len(all_items)
  start = (page - 1) * pageSize
  end = start + pageSize
  items = all_items[start:end]
  
  # 返回前端期望的数据格式
  return {"list": items, "page": page, "pageSize": pageSize, "total": total}


@app.get('/api/detection/{task_id}')
def get_detection_detail(task_id: str):
  task = _tasks.get(task_id)
  if not task:
    raise HTTPException(status_code=404, detail='Not found')
  return task


@app.delete('/api/detection/history/{task_id}')
def delete_detection_history(task_id: str):
  # 删除内存中的数据
  if task_id in _tasks:
    del _tasks[task_id]
  
  # 删除数据库中的数据
  try:
    connection = get_db_connection()
    if connection:
      cursor = connection.cursor()
      
      # 手动删除所有相关表的数据（按依赖关系顺序）
      # 1. 先删除子表数据
      cursor.execute("DELETE FROM repair_items WHERE assessment_id IN (SELECT id FROM damage_assessments WHERE task_id = %s)", (task_id,))
      cursor.execute("DELETE FROM damage_regions WHERE task_id = %s", (task_id,))
      cursor.execute("DELETE FROM task_images WHERE task_id = %s", (task_id,))
      cursor.execute("DELETE FROM damage_assessments WHERE task_id = %s", (task_id,))
      # 2. 最后删除主表数据
      cursor.execute("DELETE FROM assessment_tasks WHERE task_id = %s", (task_id,))
      
      connection.commit()
      cursor.close()
      connection.close()
      print(f"[Database] Deleted task {task_id} and all related data from database")
  except Exception as e:
    print(f"[Database Error] Failed to delete task {task_id}: {e}")
  
  return {"success": True}


@app.delete('/api/detection/history')
def batch_delete_detection_history(payload: dict):
  ids = payload.get("ids") or []
  for task_id in ids:
    if task_id in _tasks:
      del _tasks[task_id]
  return {"success": True}


@app.get('/api/detection/export/{task_id}')
def export_report(task_id: str, format: str = 'pdf'):
  task = _tasks.get(task_id)
  if not task:
    raise HTTPException(status_code=404, detail='Not found')
  content = (
    f"Detection Report\n"
    f"ID: {task_id}\n"
    f"Status: {task.get('status')}\n"
    f"CreatedAt: {task.get('createdAt')}\n\n"
    f"Result:\n{task.get('result')}\n"
  ).encode('utf-8')
  headers = {"Content-Disposition": f"attachment; filename=detection-report-{task_id}.{format}"}
  return StreamingResponse(io.BytesIO(content), media_type='application/octet-stream', headers=headers)


@app.get('/', response_class=HTMLResponse)
def get_ui():
  return """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Damage Detection API Tester</title>
    <style>
      :root { color-scheme: light dark; }
      body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; line-height: 1.35; }
      .wrap { max-width: 980px; margin: 0 auto; }
      .card { border: 1px solid rgba(127,127,127,0.35); border-radius: 12px; padding: 16px; }
      .row { display: flex; gap: 16px; flex-wrap: wrap; }
      .col { flex: 1 1 320px; min-width: 320px; }
      button { padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(127,127,127,0.35); cursor: pointer; }
      input[type=file] { width: 100%; }
      pre { overflow: auto; padding: 12px; border-radius: 10px; border: 1px solid rgba(127,127,127,0.35); }
      img { max-width: 100%; border-radius: 10px; border: 1px solid rgba(127,127,127,0.35); }
      .muted { opacity: 0.75; }
      .ok { color: #16a34a; }
      .bad { color: #dc2626; }
    </style>
  </head>
  <body>
    <div class=\"wrap\">
      <h2>Damage Detection API Tester</h2>
      <p class=\"muted\">Upload an image and call <code>POST /detection</code>. Results will be shown as JSON.</p>

      <div class=\"card\">
        <div class=\"row\">
          <div class=\"col\">
            <h3>Request</h3>
            <input id=\"file\" type=\"file\" accept=\"image/*\" />
            <div style=\"margin-top: 12px; display:flex; gap: 10px; align-items:center;\">
              <button id=\"btn\">Send</button>
              <span id=\"status\" class=\"muted\"></span>
            </div>
            <div style=\"margin-top: 12px;\">
              <img id=\"preview\" alt=\"preview\" />
            </div>
          </div>

          <div class=\"col\">
            <h3>Response</h3>
            <pre id=\"out\">(no response yet)</pre>
          </div>
        </div>
      </div>

      <p class=\"muted\" style=\"margin-top: 14px;\">Tip: you can also open <a href=\"/docs\">/docs</a>.</p>
    </div>

    <script>
      const fileEl = document.getElementById('file');
      const btnEl = document.getElementById('btn');
      const outEl = document.getElementById('out');
      const statusEl = document.getElementById('status');
      const previewEl = document.getElementById('preview');

      function setStatus(text, ok) {
        statusEl.textContent = text || '';
        statusEl.className = ok === true ? 'ok' : ok === false ? 'bad' : 'muted';
      }

      fileEl.addEventListener('change', () => {
        const f = fileEl.files && fileEl.files[0];
        if (!f) {
          previewEl.removeAttribute('src');
          return;
        }
        const url = URL.createObjectURL(f);
        previewEl.src = url;
      });

      btnEl.addEventListener('click', async () => {
        const f = fileEl.files && fileEl.files[0];
        if (!f) {
          setStatus('Please choose an image file first.', false);
          return;
        }

        setStatus('Sending request...', null);
        outEl.textContent = '(waiting...)';

        const fd = new FormData();
        fd.append('file', f);

        try {
          const res = await fetch('/api/detection', { method: 'POST', body: fd });
          const text = await res.text();

          if (!res.ok) {
            setStatus(`HTTP ${res.status} ${res.statusText}`, false);
            outEl.textContent = text;
            return;
          }

          let obj;
          try { obj = JSON.parse(text); } catch { obj = text; }
          if (obj && obj.taskId) {
            outEl.textContent = JSON.stringify(obj, null, 2);
            setStatus('Task created, polling...', null);
            const pollUrl = `/api/detection/result/${obj.taskId}`;
            const poll = async () => {
              const r = await fetch(pollUrl);
              const t = await r.text();
              let o;
              try { o = JSON.parse(t); } catch { o = t; }
              outEl.textContent = typeof o === 'string' ? o : JSON.stringify(o, null, 2);
              if (o && o.status && (o.status === 'completed' || o.status === 'failed')) {
                setStatus(o.status === 'completed' ? 'OK' : 'Failed', o.status === 'completed');
                return;
              }
              setTimeout(poll, 800);
            };
            poll();
          } else {
            outEl.textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
            setStatus('OK', true);
          }
        } catch (e) {
          setStatus('Request failed: ' + (e && e.message ? e.message : String(e)), false);
          outEl.textContent = String(e);
        }
      });
    </script>
  </body>
</html>"""


@app.post('/detection')
def post_detection(file: bytes = File(...)):
   image = Image.open(io.BytesIO(file)).convert("RGB")
   image = np.array(image)
   image = image[:,:,::-1].copy()
   results = detection(image)
   return results


router = APIRouter()

class AnalyzeResponse(BaseModel):
    """结构化响应模型"""
    task_id: str
    analysis: dict
    model: str
    timestamp: str


@router.get('/api/llm/analyze', response_model=AnalyzeResponse)
async def get_saved_llm_analysis(task_id: str):
    """从数据库读取已保存的AI分析结果（damage_assessments.ai_analysis）"""
    try:
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT ai_analysis, completed_at
            FROM damage_assessments
            WHERE task_id = %s
            LIMIT 1
            """,
            (task_id,)
        )
        row = cursor.fetchone()

        if not row or not row.get("ai_analysis"):
            raise HTTPException(status_code=404, detail=f"No saved analysis for task {task_id}")

        raw = row.get("ai_analysis")
        if isinstance(raw, (dict, list)):
            analysis = raw
        else:
            analysis = json.loads(raw)

        ts = row.get("completed_at")
        timestamp = ts.isoformat() + "Z" if ts else datetime.utcnow().isoformat() + "Z"

        return {
            "task_id": task_id,
            "analysis": analysis,
            "model": "saved",
            "timestamp": timestamp,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取AI分析失败: {str(e)}")
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if connection:
                connection.close()
        except Exception:
            pass

@router.post('/api/llm/analyze', response_model=AnalyzeResponse)
async def analyze_with_llm(task_id: str):
    """
    使用豆包大模型分析车辆损伤图片
    """
    # 1. 校验任务状态 - 先从内存查找，再从数据库查找
    task = _tasks.get(task_id)
    
    if not task:
        # 如果内存中没有，尝试从数据库中查找
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                
                # 查询主任务记录
                cursor.execute("""
                    SELECT * FROM assessment_tasks 
                    WHERE task_id = %s AND status = 'completed'
                """, (task_id,))
                
                db_task = cursor.fetchone()
                if db_task:
                    # 查询图像记录
                    cursor.execute("""
                        SELECT * FROM task_images 
                        WHERE task_id = %s
                    """, (task_id,))
                    images = cursor.fetchall()
                    
                    # 查询损伤部位记录
                    cursor.execute("""
                        SELECT * FROM damage_parts 
                        WHERE task_id = %s
                        ORDER BY sort_order
                    """, (task_id,))
                    regions = cursor.fetchall()
                    
                    # 构建任务数据结构
                    images_payload = []
                    for img in images:
                        images_payload.append({
                            "id": img["id"],
                            "image_url": img["image_url"],
                            "original_url": img.get("original_url", img["image_url"]),
                            "annotated_url": img.get("annotated_url"),
                            "image_type": img.get("image_type", "original")
                        })
                    
                    regions_payload = []
                    for region in regions:
                        regions_payload.append({
                            "id": region["region_id"],
                            "image_id": region["image_id"],
                            "bbox": region["bbox"],
                            "damage_type": region["damage_type"],
                            "damage_type_label": region["damage_type_label"],
                            "severity_level": region["severity_level"],
                            "part_code": region["part_code"],
                        })
                    
                    # 解析损伤类型JSON
                    damage_types = []
                    if db_task["damage_types"]:
                        try:
                            damage_types = json.loads(db_task["damage_types"])
                        except:
                            damage_types = []
                    
                    task = {
                        "status": db_task["status"],
                        "progress": db_task["progress"],
                        "result": {
                            "taskId": task_id,
                            "damage_types": damage_types,
                            "images": images_payload,
                            "regions": regions_payload,
                        }
                    }
                    
                    print(f"[Database] Retrieved task {task_id} from database for LLM analysis")
                
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"[Database Error] Failed to retrieve task {task_id} for LLM analysis: {e}")
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task.get("status") != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Task {task_id} status is {task.get('status')}, expected 'completed'"
        )
    
    result = task.get("result", {})
    images = result.get("images", [])
    if not images:
        raise HTTPException(status_code=400, detail=f"No images found in task {task_id}")
    
    # 2. 获取图片URL
    first_image = images[0]
    image_url = first_image.get("image_url", "")
    
    # 3. 整理损伤信息
    regions = result.get("regions", [])
    damage_summary = []
    for r in regions:
        part = r.get("part_code", "未知部位")
        damage = r.get("damage_type_label", "未知损伤")
        damage_summary.append(part + ": " + damage)
    
    damage_text = "; ".join(damage_summary) if damage_summary else "未检测到明显损伤"
    
    # 4. 构建提示词 - 使用简化版本避免JSON格式问题
    prompt = """请分析这张车辆损伤图片，返回JSON格式：
{
    "vehicle_info": {
        "brand": "车辆品牌",
        "model": "车型"
    },
    "damage_level": {
        "部位1": "轻微/中等/严重",
        "部位2": "轻微/中等/严重"
    },
    "repair_suggestion": "具体维修方案",
    "cost_estimate": "费用区间",
    "safety_tips": "行车安全提示",
    "pre_repair_analysis": {
        "high_priority": [
            {
                "part": "损伤部位名称",
                "damage_type": "损伤类型",
                "severity": "损伤程度",
                "repair_suggestion": "具体维修建议"
            }
        ],
        "medium_priority": [
            {
                "part": "损伤部位名称", 
                "damage_type": "损伤类型",
                "severity": "损伤程度",
                "repair_suggestion": "具体维修建议"
            }
        ],
        "low_priority": [
            {
                "part": "损伤部位名称",
                "damage_type": "损伤类型", 
                "severity": "损伤程度",
                "repair_suggestion": "具体维修建议"
            }
        ]
    },
    "detailed_cost_breakdown": {
        "brand_confidence": 85.5,
        "total_parts_cost": 8500.00,
        "total_labor_cost": 3500.00,
        "total_cost": 12000.00,
        "total_repair_time": 8,
        "cost_breakdown": [
            {
                "part_name": "维修部件名称",
                "parts_cost": 配件成本(元),
                "labor_cost": 工时成本(元),
                "labor_hours": 工时数(小时),
                "total_cost": 该部件总成本(元)
            }
        ]
    }
}

检测到的损伤信息：""" + damage_text + """

重要：必须严格按照上述JSON格式输出，所有数值字段必须提供具体的数字。"""
    
    try:
        # 5. 从环境变量获取配置
        api_key = os.getenv('ARK_API_KEY')
        endpoint = 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'
        model_id = 'doubao-seed-2-0-pro-260215'
        
        if not api_key:
            raise HTTPException(status_code=500, detail='Environment variable ARK_API_KEY is required')
        
        # 6. 严格按照用户指定的格式构建请求
        request_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        request_body = {
            'model': model_id,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a professional vehicle damage assessment expert. Analyze the vehicle damage image and provide detailed assessment report in JSON format.'
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': image_url
                            }
                        },
                        {
                            'type': 'text',
                            'text': prompt
                        }
                    ]
                }
            ]
        }
        
        # 打印请求日志（显示完整 Authorization 用于调试）
        print(f"[LLM Request] URL: {endpoint}")
        print(f"[LLM Request] Headers: {json.dumps(request_headers, indent=2)}")
        print(f"[LLM Request] Body: {json.dumps(request_body, indent=2)}")
        
        # 7. 发送HTTP请求
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                endpoint,
                headers=request_headers,
                json=request_body
            )
        
        # 8. 处理响应
        print(f"[LLM Response] Status: {response.status_code}")
        print(f"[LLM Response] Headers: {dict(response.headers)}")
        print(f"[LLM Response] Body: {response.text[:1000]}...")  # 限制长度避免日志过长
        
        if response.status_code != 200:
            error_detail = f"LLM API error (status: {response.status_code}): {response.text[:500]}"
            raise HTTPException(status_code=500, detail=error_detail)
        
        data = response.json()
        
        # 解析 chat.completions 响应格式
        if data.get('choices') and len(data['choices']) > 0:
            llm_response = data['choices'][0].get('message', {}).get('content', '')
        else:
            raise HTTPException(status_code=500, detail='Empty response from LLM API')
        
        # 尝试解析JSON
        try:
            analysis_result = json.loads(llm_response)
        except json.JSONDecodeError:
            analysis_result = {
                "raw_response": llm_response,
                "error": "Model returned non-JSON format"
            }
        
        # 保存分析结果到数据库
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                
                # 提取车辆信息
                vehicle_info = analysis_result.get("vehicle_info", {})
                vehicle_brand = vehicle_info.get("brand", "")
                vehicle_model = vehicle_info.get("model", "")
                
                # 提取损伤等级信息
                damage_level = analysis_result.get("damage_level", {})
                
                # 提取维修建议和费用估算
                repair_suggestion = analysis_result.get("repair_suggestion", "")
                cost_estimate = analysis_result.get("cost_estimate", "")
                safety_tips = analysis_result.get("safety_tips", "")
                
                # 预修车分析
                pre_repair_analysis = analysis_result.get("pre_repair_analysis", {})
                
                # 提取详细成本分解
                detailed_cost = analysis_result.get("detailed_cost_breakdown", {})
                brand_confidence = detailed_cost.get("brand_confidence", 0.0)
                total_parts_cost = detailed_cost.get("total_parts_cost", 0.0)
                total_labor_cost = detailed_cost.get("total_labor_cost", 0.0)
                total_cost = detailed_cost.get("total_cost", 0.0)
                total_repair_time = detailed_cost.get("total_repair_time", 0)
                cost_breakdown = detailed_cost.get("cost_breakdown", [])
                
                # 更新或插入定损记录
                cursor.execute("""
                    INSERT INTO damage_assessments 
                    (task_id, status, vehicle_brand, vehicle_model, 
                     assessment_conclusion, ai_analysis, priority_analysis,
                     brand_confidence, total_parts_cost, total_labor_cost, 
                     total_cost, total_repair_time, completed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                    vehicle_brand = VALUES(vehicle_brand),
                    vehicle_model = VALUES(vehicle_model),
                    assessment_conclusion = VALUES(assessment_conclusion),
                    ai_analysis = VALUES(ai_analysis),
                    priority_analysis = VALUES(priority_analysis),
                    brand_confidence = VALUES(brand_confidence),
                    total_parts_cost = VALUES(total_parts_cost),
                    total_labor_cost = VALUES(total_labor_cost),
                    total_cost = VALUES(total_cost),
                    total_repair_time = VALUES(total_repair_time),
                    completed_at = VALUES(completed_at),
                    status = VALUES(status)
                """, (
                    task_id, 
                    'completed',
                    vehicle_brand, 
                    vehicle_model,
                    f"维修建议: {repair_suggestion}\n费用估算: {cost_estimate}\n安全提示: {safety_tips}",
                    json.dumps(analysis_result, ensure_ascii=False),
                    json.dumps(pre_repair_analysis, ensure_ascii=False),
                    brand_confidence,
                    total_parts_cost,
                    total_labor_cost,
                    total_cost,
                    total_repair_time
                ))
                
                # 损伤区域信息已经在检测阶段保存到damage_regions表，这里不需要重复保存
                
                connection.commit()
                cursor.close()
                connection.close()
                print(f"[Database] LLM analysis for task {task_id} saved to database")
                
        except Exception as db_error:
            print(f"[Database Error] Failed to save LLM analysis: {db_error}")
            # 不影响API返回，继续执行
        
        return {
            "task_id": task_id,
            "analysis": analysis_result,
            "model": model_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"LLM API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")

# ========================================
# 意见与反馈API接口
# ========================================

# 反馈数据模型
class FeedbackRequest(BaseModel):
    contact: Optional[str] = None  # 前端发送的字段名
    category: str  # 前端发送的字段名
    content: str  # 前端发送的字段名
    assessment_task_id: Optional[str] = None

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None

# 内存存储反馈数据（作为备用，主要使用数据库）
feedback_storage = {}

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """提交意见与反馈"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        # 生成唯一的反馈ID
        feedback_id = f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
        
        # 保存到数据库
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user_feedback 
            (feedback_id, contact_info, feedback_type, feedback_content, assessment_task_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (feedback_id, feedback.contact, feedback.category, feedback.content, feedback.assessment_task_id))
        
        connection.commit()
        
        # 同时保存到内存（用于GET接口，作为缓存）
        feedback_data = {
            "feedback_id": feedback_id,
            "contact_info": feedback.contact,
            "feedback_type": feedback.category,
            "feedback_content": feedback.content,
            "assessment_task_id": feedback.assessment_task_id,
            "created_at": datetime.now().isoformat()
        }
        feedback_storage[feedback_id] = feedback_data
        
        print(f"[Feedback] New feedback saved to database: {feedback_id}")
        print(f"[Feedback] Type: {feedback.category}")
        print(f"[Feedback] Contact: {feedback.contact}")
        
        return FeedbackResponse(
            success=True,
            message="反馈提交成功，感谢您的意见！",
            feedback_id=feedback_id
        )
        
    except Exception as e:
        print(f"[Feedback Error] {str(e)}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.get("/api/feedback", response_model=dict)
async def get_feedback(feedback_type: Optional[str] = None, limit: int = 20):
    """获取反馈列表"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if feedback_type:
            cursor.execute("""
                SELECT * FROM user_feedback 
                WHERE feedback_type = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (feedback_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM user_feedback 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
        
        feedbacks = cursor.fetchall()
        
        return {
            "success": True,
            "data": feedbacks,
            "total": len(feedbacks)
        }
        
    except Exception as e:
        print(f"[Feedback Error] {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取反馈列表失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.get("/api/feedback/{feedback_id}", response_model=dict)
async def get_feedback_by_id(feedback_id: str):
    """根据ID获取反馈详情"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM user_feedback WHERE feedback_id = %s
        """, (feedback_id,))
        
        feedback = cursor.fetchone()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")
        
        return {
            "success": True,
            "data": feedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Feedback Error] {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取反馈详情失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.get("/api/feedback/statistics", response_model=dict)
async def get_feedback_statistics():
    """获取反馈统计信息"""
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 按类型统计
        cursor.execute("""
            SELECT feedback_type, COUNT(*) as count
            FROM user_feedback
            GROUP BY feedback_type
        """)
        type_stats = cursor.fetchall()
        
        # 总体统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_feedback,
                COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as this_week_count
            FROM user_feedback
        """)
        total_stats = cursor.fetchone()
        
        return {
            "success": True,
            "data": {
                "total_feedback": total_stats["total_feedback"],
                "this_week_count": total_stats["this_week_count"],
                "type_statistics": {item["feedback_type"]: item["count"] for item in type_stats}
            }
        }
        
    except Exception as e:
        print(f"[Feedback Error] {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 注册 router 到 app
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


