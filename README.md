# tag-service

回忆标签服务 — 记录生活中的小瞬间。

用标签的方式，把值得记住的事存下来。支持 markdown 部署，开箱即用。

## API 文档

### 查询标签

```bash
# 获取最新标签（默认20条）
GET /tags?limit=20

# 按内容搜索
GET /tags/search?q=关键词

# 按标签名筛选
GET /tags/by-tag?tag=小七

# 统计信息
GET /tags/stats
```

### 添加标签

```bash
POST /tags
Content-Type: application/json

{
    "content": "今天完成了什么什么事",
    "tags": ["标签1", "标签2"],
    "author": "小七",
    "mood": "开心"    # 可选
}
```

### 删除标签

```bash
DELETE /tags/{id}
```

### 健康检查

```bash
GET /health
```

## 快速部署

1. 克隆仓库
2. `pip install -r requirements.txt`
3. `cp .env.example .env` 并填入你的 Supabase 配置
4. `python run.py`

### 数据库

需要在 Supabase 中创建 `tags` 表：

```sql
CREATE TABLE IF NOT EXISTS tags (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    author TEXT DEFAULT '小七',
    mood TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 技术栈

- FastAPI
- Supabase (PostgreSQL)
- Uvicorn

## 协议

MIT
