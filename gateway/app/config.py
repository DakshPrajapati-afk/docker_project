"""Reads all runtime config from environment variables.

Keeping this in one place means the rest of the app never calls
os.environ directly, and the defaults here double as documentation
for what docker-compose.yml is expected to set.
"""
import os

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "300"))
MOCK_LLM_URL = os.environ.get("MOCK_LLM_URL", "http://mock-llm:8001")
