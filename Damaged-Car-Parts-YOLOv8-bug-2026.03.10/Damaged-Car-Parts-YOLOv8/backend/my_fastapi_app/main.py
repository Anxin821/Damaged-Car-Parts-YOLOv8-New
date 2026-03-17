import io
import uuid
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
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

    total = max(1, len(files_bytes))
    for idx, file_bytes in enumerate(files_bytes):
      _tasks[task_id]["progress"] = int(5 + (idx / total) * 80)

      image_id = f"img_{idx}"

      pil = Image.open(io.BytesIO(file_bytes)).convert("RGB")
      arr = np.array(pil)
      bgr = arr[:, :, ::-1].copy()

      det = detection(bgr)
      classes = det.get("classes") or []
      boxes = det.get("boxes") or []

      for c in classes:
       all_damage_types.add(_map_damage_type(c))

      for b_i, box in enumerate(boxes):
       try:
         x, y, w, h = box
         x2 = x + w
         y2 = y + h
         bbox = f"{x},{y},{x2},{y2}"
       except Exception:
         bbox = ""

       raw_label = classes[b_i] if b_i < len(classes) else "unknown"
       damage_type = _map_damage_type(raw_label)

       regions_payload.append({
         "id": f"{image_id}_r{b_i}",
         "image_id": image_id,
         "bbox": bbox,
         "damage_type": damage_type,
         "damage_type_label": raw_label,
         "severity_level": "MEDIUM",
         "part_code": raw_label,
       })

      img_b64 = base64.b64encode(file_bytes).decode("utf-8")
      images_payload.append({
        "id": image_id,
        "image_url": f"data:image/jpeg;base64,{img_b64}",
        "thumb_url": None,
      })

    _tasks[task_id]["result"] = {
      "taskId": task_id,
      "damage_types": sorted(list(all_damage_types)),
      "images": images_payload,
      "regions": regions_payload,
    }
    _tasks[task_id]["status"] = "completed"
    _tasks[task_id]["progress"] = 100
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
  task = _tasks.get(task_id)
  if not task:
    raise HTTPException(status_code=404, detail='Task not found')
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
  all_items = list(_tasks.values())
  all_items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
  total = len(all_items)
  start = (page - 1) * pageSize
  end = start + pageSize
  items = all_items[start:end]
  return {"items": items, "page": page, "pageSize": pageSize, "total": total}


@app.get('/api/detection/{task_id}')
def get_detection_detail(task_id: str):
  task = _tasks.get(task_id)
  if not task:
    raise HTTPException(status_code=404, detail='Not found')
  return task


@app.delete('/api/detection/history/{task_id}')
def delete_detection_history(task_id: str):
  if task_id in _tasks:
    del _tasks[task_id]
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

@router.post('/api/llm/analyze', response_model=AnalyzeResponse)
async def analyze_with_llm(task_id: str):
    """
    使用豆包大模型分析车辆损伤图片
    """
    # 1. 校验任务状态
    task = _tasks.get(task_id)
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
        damage_summary.append(f"{part}: {damage}")
    
    damage_text = "; ".join(damage_summary) if damage_summary else "未检测到明显损伤"
    
    # 4. 构建提示词
    prompt = f"""你是一位专业的车辆定损评估专家，请分析这张车辆损伤图片，严格按照以下JSON格式输出评估报告，不要添加任何多余文字：

{{
    "vehicle_info": {{
        "brand": "车辆品牌",
        "model": "具体车型"
    }},
    "damage_level": {{
        "部位1": "轻微/中等/严重",
        "部位2": "轻微/中等/严重"
    }},
    "repair_suggestion": "具体维修方案",
    "cost_estimate": "费用区间",
    "safety_tips": "行车安全提示",
    "pre_repair_analysis": {{
        "high_priority": [
            {{
                "part": "损伤部位名称",
                "damage_type": "损伤类型",
                "severity": "损伤程度",
                "impact_analysis": "影响分析描述",
                "repair_suggestion": "具体维修建议"
            }}
        ],
        "medium_priority": [
            {{
                "part": "损伤部位名称",
                "damage_type": "损伤类型",
                "severity": "损伤程度",
                "impact_analysis": "影响分析描述",
                "repair_suggestion": "具体维修建议"
            }}
        ],
        "low_priority": [
            {{
                "part": "损伤部位名称",
                "damage_type": "损伤类型",
                "severity": "损伤程度",
                "impact_analysis": "影响分析描述",
                "repair_suggestion": "具体维修建议"
            }}
        ]
    }}
}}

分析依据：
检测到的损伤信息：{damage_text}

分析要求：
1. 车辆识别：仔细观察车辆外观特征，准确识别品牌和车型，必须填写vehicle_info字段
2. 损伤程度评估：对每个部位给出明确的严重程度
3. 维修建议：具体到维修工艺（如钣金、喷漆、更换配件等）
4. 费用估算：基于市场行情给出合理区间
5. 安全提示：指出影响行车安全的关键损伤
6. 预修车分析：按破损影响程度排序维修优先级
   - 高优先级：涉及行车安全的紧急维修项目（如大灯、刹车系统等）
   - 中优先级：影响使用但不危及安全的维修项目（如保险杠、车门等）
   - 低优先级：仅外观影响的维修项目（如轻微划痕等）
   - 每个优先级项目必须包含：部位、损伤类型、程度、影响分析、维修建议

重要：必须严格按照上述JSON格式输出，不要添加任何其他字段。
"""
    
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
        print(f"[LLM Request] Body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
        
        # 7. 发送HTTP请求
        async with httpx.AsyncClient(timeout=60.0) as client:
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

# 注册 router 到 app
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


