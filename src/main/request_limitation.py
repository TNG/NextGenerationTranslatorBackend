import os
import redis

request_key = 'current_number_of_concurrent_requests'


class RequestLimiter:
    class RequestLimitation:

        def __init__(self, request_limiter):
            self._request_limiter = request_limiter

        def __enter__(self):
            self._request_limiter.new_request()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._request_limiter.end_request()

    def __init__(self, max_number_of_concurrent_requests):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        self._redis = redis.Redis(host=redis_host, port=6379, db=0)
        self._redis.set(request_key, 0)

        self._max_number_of_concurrent_requests = max_number_of_concurrent_requests

    def limited_requests(self):
        return RequestLimiter.RequestLimitation(self)

    def new_request(self):
        print(int(self._redis.get(request_key)), self._max_number_of_concurrent_requests)
        if int(self._redis.get(request_key)) > self._max_number_of_concurrent_requests:
            raise RequestLimitExceededException()

        self._redis.incr(request_key)

    def end_request(self):
        self._redis.decr(request_key)


class RequestLimitExceededException(Exception):
    """Raised when the max number of requests is exceeded"""

    def __init__(self):
        self.message = 'Request limit exceeded'
        Exception.__init__(self)
