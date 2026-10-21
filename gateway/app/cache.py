"""Caching logic for the gateway, kept separate from the FastAPI routes
so it can be unit-tested with fakeredis instead of a real Redis server.
"""
import hashlib

from . import config

ANSWER_KEY_PREFIX = "cm:answer:"
STATS_HITS_KEY = "cm:stats:hits"
STATS_MISSES_KEY = "cm:stats:misses"


def normalize_prompt(prompt: str) -> str:
    return prompt.strip().lower()


def hash_prompt(normalized_prompt: str) -> str:
    return hashlib.sha256(normalized_prompt.encode("utf-8")).hexdigest()


def get_cached_answer(redis_client, normalized_prompt: str) -> str | None:
    key = ANSWER_KEY_PREFIX + hash_prompt(normalized_prompt)
    value = redis_client.get(key)
    return value.decode("utf-8") if value is not None else None


def store_answer(redis_client, normalized_prompt: str, answer: str) -> None:
    key = ANSWER_KEY_PREFIX + hash_prompt(normalized_prompt)
    redis_client.set(key, answer, ex=config.CACHE_TTL_SECONDS)


def record_hit(redis_client) -> None:
    redis_client.incr(STATS_HITS_KEY)


def record_miss(redis_client) -> None:
    redis_client.incr(STATS_MISSES_KEY)


def get_stats(redis_client) -> dict:
    hits = int(redis_client.get(STATS_HITS_KEY) or 0)
    misses = int(redis_client.get(STATS_MISSES_KEY) or 0)
    total = hits + misses
    hit_rate = hits / total if total > 0 else 0.0
    return {"hits": hits, "misses": misses, "hit_rate": round(hit_rate, 4)}
