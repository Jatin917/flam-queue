# redis_connection.py
import redis

class RedisConnection:
    _client = None

    @classmethod
    def get_client(cls, url="redis://localhost:6379/0"):
        if cls._client is None:
            cls._client = redis.Redis.from_url(url, decode_responses=True)
        return cls._client
