from fastapi import FastAPI, Query, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import hashlib
import secrets
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

# ============ 账号系统 ============

def hash_password(password: str, salt: str = None):
    """密码哈希（PBKDF2 + 随机盐），返回 (salt, hash)"""
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt, h.hex()

def verify_password(password: str, salt: str, expected_hash: str):
    h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return secrets.compare_digest(h.hex(), expected_hash)

# token 存内存：token -> {"email": ...}
tokens = {}

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "未登录")
    token = authorization[7:]
    if token not in tokens:
        raise HTTPException(401, "登录已过期，请重新登录")
    return tokens[token]

class RegisterPayload(BaseModel):
    email: str
    password: str

class LoginPayload(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(payload: RegisterPayload):
    existing = supabase.table("users").select("id").eq("email", payload.email).execute()
    if existing.data:
        raise HTTPException(400, "邮箱已注册")
    salt, h = hash_password(payload.password)
    record = {
        "email": payload.email,
        "password_hash": f"{salt}${h}",
    }
    supabase.table("users").insert(record).execute()
    return {"ok": True, "message": "注册成功"}

@app.post("/login")
def login(payload: LoginPayload):
    data = supabase.table("users").select("*").eq("email", payload.email).execute()
    if not data.data:
        raise HTTPException(401, "邮箱或密码错误")
    user = data.data[0]
    salt, h = user["password_hash"].split("$", 1)
    if not verify_password(payload.password, salt, h):
        raise HTTPException(401, "邮箱或密码错误")
    token = secrets.token_hex(32)
    tokens[token] = {"email": user["email"]}
    return {"token": token, "email": user["email"]}

# ============ tags 接口（每个账号独立） ============

class TagPayload(BaseModel):
    content: str
    tags: list[str]
    mood: Optional[str] = None

@app.get("/")
def root():
    return {"message": "tag-service is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tags")
def list_tags(limit: int = Query(20, ge=1, le=100), user=Depends(get_current_user)):
    data = supabase.table("tags").select("*").eq("user_email", user["email"]).order("created_at", desc=True).limit(limit).execute()
    return {"data": data.data}

@app.get("/tags/search")
def search_tags(q: str = Query(...), user=Depends(get_current_user)):
    data = supabase.table("tags").select("*").ilike("content", f"%{q}%").eq("user_email", user["email"]).order("created_at", desc=True).limit(20).execute()
    return {"data": data.data}

@app.post("/tags")
def add_tag(payload: TagPayload, user=Depends(get_current_user)):
    record = {
        "content": payload.content,
        "tags": payload.tags,
        "user_email": user["email"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if payload.mood:
        record["mood"] = payload.mood
    data = supabase.table("tags").insert(record).execute()
    return {"data": data.data}

@app.get("/tags/by-tag")
def search_by_tag(tag: str = Query(...), user=Depends(get_current_user)):
    all_tags = supabase.table("tags").select("*").eq("user_email", user["email"]).order("created_at", desc=True).limit(100).execute()
    filtered = [row for row in all_tags.data if tag in (row.get("tags") or [])]
    return {"data": filtered[:20]}

@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: str, user=Depends(get_current_user)):
    data = supabase.table("tags").delete().eq("id", tag_id).eq("user_email", user["email"]).execute()
    return {"data": data.data, "deleted": True}

@app.get("/tags/stats")
def tag_stats(user=Depends(get_current_user)):
    try:
        all_data = supabase.table("tags").select("*").eq("user_email", user["email"]).limit(1000).execute()
        rows = all_data.data
        total = len(rows)
        all_tags = []
        for row in rows:
            all_tags.extend(row.get("tags") or [])
        from collections import Counter
        top_tags = Counter(all_tags).most_common(10)
        return {
            "data": {
                "total": total,
                "top_tags": [{"tag": t, "count": c} for t, c in top_tags]
            }
        }
    except Exception as e:
        return {"error": str(e)}
