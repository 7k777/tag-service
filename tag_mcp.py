from typing import Any
import httpx
import os

TAG_SERVICE_URL = "http://localhost:18111"

async def add_tag(content: str, tags: list[str], author: str = "小七", mood: str = "") -> dict:
    """存一条回忆标签"""
    body = {"content": content, "tags": tags, "author": author}
    if mood:
        body["mood"] = mood
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{TAG_SERVICE_URL}/tags", json=body, timeout=10)
        return r.json()

async def list_tags(limit: int = 10) -> dict:
    """查看最近的回忆标签"""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{TAG_SERVICE_URL}/tags?limit={limit}", timeout=10)
        return r.json()

async def search_tags(q: str) -> dict:
    """搜索回忆标签"""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{TAG_SERVICE_URL}/tags/search?q={q}", timeout=10)
        return r.json()
