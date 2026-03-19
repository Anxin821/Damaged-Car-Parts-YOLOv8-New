# 启动前后端服务

## 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

## 1. 配置环境变量

### 后端配置 (backend/my_fastapi_app/.env.local)
```
# 豆包API配置
ARK_API_KEY=your_api_key_here

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=damage_assessment_db
```

## 2. 启动后端服务

```bash
# 进入后端目录
cd backend/my_fastapi_app

# 安装依赖 (如未安装)
pip install -r requirements.txt

# 启动服务
python main.py
```

后端服务将运行在: http://localhost:8000

## 3. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖 (如未安装)
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在: http://localhost:5173

## 4. 验证服务启动

- 后端API测试: http://localhost:8000/api/detection
- 前端页面访问: http://localhost:5173
- 豆包分析API: http://localhost:8000/api/llm/analyze

## 5. 常用命令

```bash
# 检查后端端口
netstat -ano | findstr :8000

# 检查前端端口
netstat -ano | findstr :5173

# 重启后端服务
# Ctrl+C 停止后重新运行 python main.py

# 重启前端服务
# Ctrl+C 停止后重新运行 npm run dev
```

## 6. 故障排查

### 后端启动失败
1. 检查环境变量是否正确配置
2. 检查MySQL数据库是否启动
3. 检查端口8000是否被占用

### 前端启动失败
1. 检查Node.js版本是否>=16
2. 检查端口5173是否被占用
3. 删除 node_modules 重新安装: `rm -rf node_modules && npm install`

### API调用超时
- 豆包分析API需要较长时间(15-30秒)，请耐心等待
- 确保网络连接正常
