import fakeredis
import pytest

from app import cache


@pytest.fixture
def redis_client():
    return fakeredis.FakeRedis()


def test_normalize_prompt_trims_and_lowercases():
    assert cache.normalize_prompt("  Hello World  ") == "hello world"


def test_hash_prompt_is_deterministic():
    assert cache.hash_prompt("hello") == cache.hash_prompt("hello")
    assert cache.hash_prompt("hello") != cache.hash_prompt("world")


def test_miss_then_hit(redis_client):
    normalized = cache.normalize_prompt("What is Docker?")

    assert cache.get_cached_answer(redis_client, normalized) is None
    cache.record_miss(redis_client)

    cache.store_answer(redis_client, normalized, "Docker is a container platform.")
    cache.record_hit(redis_client)

    assert cache.get_cached_answer(redis_client, normalized) == "Docker is a container platform."


def test_stats_hit_rate(redis_client):
    cache.record_hit(redis_client)
    cache.record_hit(redis_client)
    cache.record_miss(redis_client)

    stats = cache.get_stats(redis_client)
    assert stats == {"hits": 2, "misses": 1, "hit_rate": pytest.approx(2 / 3)}


def test_stats_with_no_traffic(redis_client):
    assert cache.get_stats(redis_client) == {"hits": 0, "misses": 0, "hit_rate": 0.0}


def test_different_casing_and_whitespace_share_cache_entry(redis_client):
    cache.store_answer(redis_client, cache.normalize_prompt("Hello"), "hi there")

    assert cache.get_cached_answer(redis_client, cache.normalize_prompt("  hello  ")) == "hi there"
    assert cache.get_cached_answer(redis_client, cache.normalize_prompt("HELLO")) == "hi there"
