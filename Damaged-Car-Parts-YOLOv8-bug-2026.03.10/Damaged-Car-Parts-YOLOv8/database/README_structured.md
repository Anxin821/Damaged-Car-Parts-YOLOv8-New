# 数据库结构化迁移指南

## 概述
将现有的 `damage_assessments` 表中的 JSON 数据拆解到规范化的结构化表中，提高查询性能和数据一致性。

## 文件说明
- `schema_structured.sql` - 新的表结构定义
- `migration_structured.sql` - 数据迁移脚本
- `api_structured.py` - 后端 API 改造示例

## 迁移步骤

### 1. 备份原数据库
```bash
mysqldump -u username -p damage_assessment_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 执行表结构创建
```sql
source database/schema_structured.sql
```

### 3. 执行数据迁移
```sql
source database/migration_structured.sql
```

### 4. 验证迁移结果
检查迁移脚本输出的验证信息，确保数据完整。

### 5. 更新应用代码
使用新的 API 接口（见 `api_structured.py`）

### 6. 切换到新表（可选）
验证无误后，可以重命名表：
```sql
RENAME TABLE damage_assessments TO damage_assessments_old;
RENAME TABLE damage_assessments_new TO damage_assessments;
-- 其他表类似
```

## 新表结构优势

### 1. 查询性能提升
- 直接索引查询，无需解析 JSON
- 支持复杂 JOIN 和统计查询
- 减少数据传输量

### 2. 数据一致性
- 外键约束保证数据完整性
- 避免数据重复存储
- 类型安全的字段定义

### 3. 扩展性
- 易于添加新字段
- 支持更复杂的业务逻辑
- 便于数据分析和报表

## 常用查询示例

### 获取完整评估报告
```sql
SELECT * FROM v_damage_assessment_report 
WHERE task_id = 'your-task-id';
```

### 按损伤等级统计
```sql
SELECT damage_level, COUNT(*) as count, AVG(total_cost) as avg_cost
FROM damage_assessments_new da
JOIN damage_parts dp ON da.id = dp.assessment_id
GROUP BY damage_level;
```

### 查询高优先级维修项目
```sql
SELECT ri.*, da.vehicle_brand, da.vehicle_model
FROM repair_items_new ri
JOIN damage_assessments_new da ON ri.assessment_id = da.id
WHERE ri.repair_priority = 'high'
ORDER BY ri.repair_order;
```

## 注意事项

1. **数据备份**：迁移前务必备份原数据库
2. **停机时间**：迁移期间可能需要短暂停机
3. **应用兼容**：需要同时更新后端 API 和前端代码
4. **性能测试**：迁移后进行性能测试对比
5. **回滚方案**：保留原表作为回滚备份

## 回滚方案
如果需要回滚，可以：
```sql
RENAME TABLE damage_assessments TO damage_assessments_new;
RENAME TABLE damage_assessments_old TO damage_assessments;
-- 恢复其他表...
```
