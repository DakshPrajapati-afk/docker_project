"""Mock LLM service.

Pretends to be a slow, expensive language model so the gateway has
something worth caching. Always takes ~2 seconds and returns a
deterministic canned answer based on the prompt.
"""
import asyncio
import time

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="mock-llm")

SIMULATED_LATENCY_SECONDS = 2.0


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    answer: str
    generated_in_ms: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    start = time.perf_counter()
    await asyncio.sleep(SIMULATED_LATENCY_SECONDS)
    elapsed_ms = (time.perf_counter() - start) * 1000
    answer = f"This is a simulated LLM answer to: '{req.prompt.strip()}'"
    return GenerateResponse(answer=answer, generated_in_ms=elapsed_ms)
