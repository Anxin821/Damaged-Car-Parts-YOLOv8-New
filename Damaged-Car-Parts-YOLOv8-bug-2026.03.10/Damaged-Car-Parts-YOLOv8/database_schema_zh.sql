-- 车辆定损系统数据库结构说明（简体中文）
-- 数据库: damage_assessment_db
-- 创建时间: 2026-03-19

-- 1. 评估任务表 (assessment_tasks)
-- 存储YOLO检测任务的主要信息
CREATE TABLE `assessment_tasks` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` varchar(36) NOT NULL COMMENT '检测任务唯一标识符',
  `status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态(pending/processing/completed/failed)',
  `progress` int DEFAULT '0' COMMENT '任务进度百分比(0-100)',
  `damage_types` json DEFAULT NULL COMMENT '检测到的损伤类型数组(JSON格式)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='车辆损伤检测任务表 - 存储YOLO检测任务的主要信息';

-- 2. 损伤评估表 (damage_assessments)
-- 存储详细的损伤评估结果和费用信息
CREATE TABLE `damage_assessments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` varchar(36) NOT NULL,
  `status` enum('pending','detecting','analyzing','completed','failed') DEFAULT 'pending',
  `vehicle_brand` varchar(50) DEFAULT NULL COMMENT '车辆品牌',
  `vehicle_model` varchar(100) DEFAULT NULL COMMENT '车辆型号',
  `brand_confidence` decimal(5,2) DEFAULT NULL COMMENT '品牌识别置信度',
  `total_parts_cost` decimal(10,2) DEFAULT '0.00' COMMENT '配件总费用',
  `total_labor_cost` decimal(10,2) DEFAULT '0.00' COMMENT '工时总费用',
  `total_cost` decimal(10,2) DEFAULT '0.00' COMMENT '维修总费用',
  `total_repair_time` int DEFAULT '0' COMMENT '总维修时间(小时)',
  `assessment_conclusion` text COMMENT '评估结论',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` timestamp NULL DEFAULT NULL,
  `ai_analysis` json DEFAULT NULL COMMENT 'AI分析结果(JSON)',
  `priority_analysis` json DEFAULT NULL COMMENT '优先级分析(JSON)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_vehicle_brand` (`vehicle_brand`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='损伤评估表 - 存储详细的损伤评估结果和费用信息';

-- 3. 损伤区域表 (damage_regions)
-- 存储YOLO检测到的每个损伤区域的详细信息
CREATE TABLE `damage_regions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` varchar(36) NOT NULL COMMENT '关联的检测任务ID',
  `region_id` varchar(50) NOT NULL COMMENT '损伤区域唯一标识符(如img_0_r0, img_0_r1)',
  `image_id` varchar(50) NOT NULL COMMENT '关联的图像ID',
  `bbox` varchar(50) DEFAULT NULL COMMENT '边界框坐标(x1,y1,x2,y2格式)',
  `damage_type` varchar(50) DEFAULT NULL COMMENT '标准化的损伤类型(GLASS_DAMAGE/PAINT_DAMAGE等)',
  `damage_type_label` varchar(100) DEFAULT NULL COMMENT '原始损伤标签(如damaged headlight)',
  `severity_level` varchar(20) DEFAULT NULL COMMENT '严重程度等级(LOW/MEDIUM/HIGH)',
  `part_code` varchar(100) DEFAULT NULL COMMENT '损伤部位代码或名称',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_region_id` (`region_id`),
  KEY `idx_image_id` (`image_id`),
  KEY `idx_damage_type` (`damage_type`),
  CONSTRAINT `damage_regions_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `assessment_tasks` (`task_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='损伤区域详情表 - 存储YOLO检测到的每个损伤区域的详细信息';

-- 4. 维修项目表 (repair_items)
-- 存储具体的维修项目和费用明细
CREATE TABLE `repair_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `assessment_id` int NOT NULL,
  `region_id` int DEFAULT NULL,
  `item_name` varchar(100) NOT NULL COMMENT '维修项目名称',
  `repair_method` varchar(50) DEFAULT NULL COMMENT '维修方法',
  `parts_cost` decimal(8,2) DEFAULT '0.00' COMMENT '配件费用',
  `labor_cost` decimal(8,2) DEFAULT '0.00' COMMENT '工时费用',
  `total_cost` decimal(8,2) DEFAULT '0.00' COMMENT '总费用',
  `parts_name` varchar(100) DEFAULT NULL COMMENT '配件名称',
  `parts_quantity` int DEFAULT '1' COMMENT '配件数量',
  `parts_unit_price` decimal(8,2) DEFAULT '0.00' COMMENT '配件单价',
  `labor_hours` decimal(4,1) DEFAULT '0.0' COMMENT '工时数',
  `labor_hourly_rate` decimal(6,2) DEFAULT '0.00' COMMENT '工时单价',
  `repair_priority` int DEFAULT '0' COMMENT '维修优先级',
  `repair_order` int DEFAULT '0' COMMENT '维修顺序',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_assessment_id` (`assessment_id`),
  KEY `idx_region_id` (`region_id`),
  KEY `idx_repair_priority` (`repair_priority`),
  CONSTRAINT `repair_items_ibfk_1` FOREIGN KEY (`assessment_id`) REFERENCES `damage_assessments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `repair_items_ibfk_2` FOREIGN KEY (`region_id`) REFERENCES `damage_regions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维修项目表 - 存储具体的维修项目和费用明细';

-- 5. 任务图像表 (task_images)
-- 存储每个检测任务上传的图像信息
CREATE TABLE `task_images` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` varchar(36) NOT NULL COMMENT '关联的检测任务ID',
  `image_id` varchar(50) NOT NULL COMMENT '图像唯一标识符(如img_0, img_1)',
  `image_url` longtext COMMENT '图像的base64编码URL',
  `thumb_url` text COMMENT '缩略图URL(预留字段)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `original_path` text COMMENT '原始图片本地存储路径',
  `annotated_path` text COMMENT '标注图片本地存储路径',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  KEY `idx_image_id` (`image_id`),
  CONSTRAINT `task_images_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `assessment_tasks` (`task_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测任务图像表 - 存储每个检测任务上传的图像信息';

-- 6. 用户反馈表 (user_feedback)
-- 存储用户提交的反馈信息
CREATE TABLE `user_feedback` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `feedback_id` varchar(36) NOT NULL COMMENT '反馈唯一标识符',
  `contact_info` varchar(100) DEFAULT NULL COMMENT '联系方式(手机/微信/邮箱)',
  `feedback_type` varchar(50) NOT NULL COMMENT '反馈类型(产品建议/功能异常/体验交互等)',
  `feedback_content` text NOT NULL COMMENT '反馈内容详情',
  `assessment_task_id` varchar(36) DEFAULT NULL COMMENT '关联的定损任务ID(可选)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `feedback_id` (`feedback_id`),
  KEY `idx_feedback_id` (`feedback_id`),
  KEY `idx_assessment_task_id` (`assessment_task_id`),
  KEY `idx_feedback_type` (`feedback_type`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户意见与反馈表 - 存储用户提交的反馈信息';

-- 表关系说明:
-- assessment_tasks (主任务表)
--   ├── damage_assessments (评估结果) - 一对一关系
--   ├── damage_regions (损伤区域) - 一对多关系
--   ├── task_images (任务图像) - 一对多关系
--   └── user_feedback (用户反馈) - 可选关联
--
-- damage_assessments (评估结果)
--   └── repair_items (维修项目) - 一对多关系
--
-- damage_regions (损伤区域)
--   └── repair_items (维修项目) - 可选关联
