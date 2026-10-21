"""CacheMatrix-mini gateway.

A minimal caching gateway in front of a (mock) LLM: normalizes and hashes
incoming prompts, serves cached answers straight from Redis on a hit, and
falls through to the slow mock-llm service on a miss.
"""
import time

import httpx
import redis
from fastapi import FastAPI
from pydantic import BaseModel

from . import cache, config

app = FastAPI(title="cachematrix-mini gateway")

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    answer: str
    cache: str
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    return cache.get_stats(redis_client)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    start = time.perf_counter()
    normalized = cache.normalize_prompt(req.prompt)

    cached = cache.get_cached_answer(redis_client, normalized)
    if cached is not None:
        cache.record_hit(redis_client)
        latency_ms = (time.perf_counter() - start) * 1000
        return ChatResponse(answer=cached, cache="hit", latency_ms=latency_ms)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{config.MOCK_LLM_URL}/generate", json={"prompt": req.prompt}
        )
        response.raise_for_status()
        answer = response.json()["answer"]

    cache.store_answer(redis_client, normalized, answer)
    cache.record_miss(redis_client)
    latency_ms = (time.perf_counter() - start) * 1000
    return ChatResponse(answer=answer, cache="miss", latency_ms=latency_ms)
