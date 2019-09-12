import json

import redis as _redis
from redis import Redis

import settings


class MyRedis(Redis):
    def get(self, name):
        """get返回预期的格式  str 或者 json"""
        result = super().get(name)
        try:
            result = result.decode()
            try:
                result = json.loads(result)
            except TypeError:
                return None
            else:
                return result
        except AttributeError:
            return None

    def hget(self, name, key):
        result = super().hget(name, key)
        try:
            result = result.decode()
            try:
                result = json.loads(result)
            except TypeError:
                return None
            else:
                return result
        except AttributeError:
            return None


def connect_to_redis():
    if settings.REDIS_SETTINGS.get('PASSWORD'):
        rds = MyRedis(connection_pool=_redis.ConnectionPool(
            host=settings.REDIS_SETTINGS.get('HOST', '192.168.0.13'),
            port=settings.REDIS_SETTINGS.get('PORT', 15010),
            db=settings.REDIS_SETTINGS.get('DB', 0),
            password=settings.REDIS_SETTINGS.get('PASSWORD')
        ))
    else:
        rds = MyRedis(connection_pool=_redis.ConnectionPool(
            host=settings.REDIS_SETTINGS.get('HOST', '192.168.0.13'),
            port=settings.REDIS_SETTINGS.get('PORT', 15010),
            db=settings.REDIS_SETTINGS.get('DB', 0),
        ))
    return rds


def cache_to_redis(key, timeout=86400 * 30):
    """缓存到redis的装饰器"""
    def wrapper(func):
        def inner(*args, **kwargs):
            data = redis.get(key)
            if not data:
                data = func(*args, **kwargs)
                redis.setex(key, timeout, json.dumps(data))
            return data
        return inner
    return wrapper


redis = connect_to_redis()
