import os
import logging
import redis
from contextlib import contextmanager

request_key = 'current_number_of_concurrent_requests'
_logger = logging.getLogger(__name__)


class RequestLimiter:
    class RequestLimitation:

        def __init__(self, request_limiter):
            self._request_limiter = request_limiter

        def __enter__(self):
            self._request_limiter.new_request()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._request_limiter.end_request()

    def __init__(self, max_number_of_concurrent_requests: int):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        self._redis = redis.Redis(host=redis_host, port=6379, db=0)
        self._redis.set(request_key, 0)
        self._max_number_of_concurrent_requests = max_number_of_concurrent_requests

    def limited_requests(self):
        return RequestLimiter.RequestLimitation(self)

    def new_request(self):
        if (request_value := int(self.read_redis_key(request_key))) > self._max_number_of_concurrent_requests:
            _logger.debug(f"Raise RequestLimitExceededException as key value is {request_value}")
            raise RequestLimitExceededException()
        _logger.debug(f"Increasing request value (read value is {request_value}).")
        self._redis.incr(request_key)

    def end_request(self):
        if (request_value := int(self.read_redis_key(request_key))) > 0:
            _logger.debug(f"Decreasing request value (read value is {request_value}).")
            self._redis.decr(request_key)
        else:
            _logger.debug(f"Request ended but read value is {request_value}.")

    def read_redis_key(self, redis_key: str):
        if self._redis.get(redis_key) is None:
            self._redis.set(redis_key, 0)
            _logger.info("Redis corrupted the number of requests.. again!")
        return self._redis.get(redis_key)


    @staticmethod
    @contextmanager
    def no_limit_context():
        yield

class RequestLimitExceededException(Exception):
    """Raised when the max number of requests is exceeded"""

    def __init__(self):
        self.message = 'Request limit exceeded'
        Exception.__init__(self)


