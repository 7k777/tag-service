from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from datetime import datetime, timezone

# 加载.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k, v)

from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Tag Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class TagPayload(BaseModel):
    content: str
    tags: list[str]
    author: str = "小七"
    mood: Optional[str] = None

@app.get("/")
def root():
    return {"message": "tag-service is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tags")
def list_tags(limit: int = Query(20, ge=1, le=100)):
    data = supabase.table("tags").select("*").order("created_at", desc=True).limit(limit).execute()
    return {"data": data.data}

@app.get("/tags/search")
def search_tags(q: str = Query(...)):
    data = supabase.table("tags").select("*").ilike("content", f"%{q}%").order("created_at", desc=True).limit(20).execute()
    return {"data": data.data}

@app.post("/tags")
def add_tag(payload: TagPayload):
    record = {
        "content": payload.content,
        "tags": payload.tags,
        "author": payload.author,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if payload.mood:
        record["mood"] = payload.mood
    data = supabase.table("tags").insert(record).execute()
    return {"data": data.data}


@app.get("/tags/by-tag")
def search_by_tag(tag: str = Query(...)):
    """按标签名筛选"""
    # 用SQL查询数组包含
    all_tags = supabase.table("tags").select("*").order("created_at", desc=True).limit(100).execute()
    filtered = [row for row in all_tags.data if tag in (row.get("tags") or [])]
    return {"data": filtered[:20]}


@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: str):
    """删除一条标签"""
    data = supabase.table("tags").delete().eq("id", tag_id).execute()
    return {"data": data.data, "deleted": True}

@app.get("/tags/stats")
def tag_stats():
    """统计信息"""
    try:
        all_data = supabase.table("tags").select("*").limit(1000).execute()
        total = len(all_data.data)
        authors = {}
        all_tags = []
        for row in all_data.data:
            a = row.get("author", "unknown")
            authors[a] = authors.get(a, 0) + 1
            all_tags.extend(row.get("tags") or [])
        from collections import Counter
        top_tags = Counter(all_tags).most_common(10)
        return {
            "data": {
                "total": total,
                "authors": authors,
                "top_tags": [{"tag": t, "count": c} for t, c in top_tags]
            }
        }
    except Exception as e:
        return {"error": str(e)}
