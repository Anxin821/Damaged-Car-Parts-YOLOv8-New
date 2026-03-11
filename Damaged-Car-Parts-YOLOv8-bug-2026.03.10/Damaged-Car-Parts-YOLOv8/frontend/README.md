# 车辆损伤检测系统前端

基于 Vue 3 + JavaScript 的车辆损伤检测系统前端项目。

## 项目结构

```
frontend/
├── public/             # 静态资源
│   ├── images/         # 图片资源
│   └── icons/          # 图标资源
├── dist/               # 构建输出目录
├── src/                # 源代码
│   ├── assets/         # 静态资源
│   │   ├── images/     # 图片
│   │   ├── icons/      # 图标
│   │   └── styles/     # 样式文件
│   ├── pages/          # 页面组件
│   ├── components/     # 通用组件
│   │   ├── common/     # 通用组件
│   │   ├── detection/  # 检测相关组件
│   │   └── layout/     # 布局组件
│   ├── hooks/          # 自定义 Hooks
│   ├── store/          # 状态管理
│   ├── router/         # 路由配置
│   ├── api/            # API 接口
│   ├── utils/          # 工具函数
│   ├── config/         # 配置文件
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html          # HTML 模板
├── vite.config.js      # Vite 配置
├── package.json        # 项目依赖
├── README.md           # 项目说明
└── .env.example        # 环境变量示例
```

## 技术栈

- Vue 3
- JavaScript
- Vue Router
- Pinia
- Axios
- Element Plus
- Vite

## 功能特点

- 车辆图片上传
- 智能损伤检测
- 损伤程度评估
- 检测历史记录
- 响应式设计

## 安装和运行

### 安装依赖

```bash
npm install
```

### 开发模式运行

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 环境变量

复制 `.env.example` 文件为 `.env`，并根据实际情况修改配置。

## 接口说明

### 检测相关

- `POST /api/detection` - 上传图片进行检测
- `GET /api/detection/history` - 获取检测历史
- `GET /api/detection/:id` - 获取检测详情

### 用户相关

- `POST /api/user/login` - 用户登录
- `POST /api/user/register` - 用户注册
- `GET /api/user/info` - 获取用户信息

## 贡献

欢迎提交 Issue 和 Pull Request！
