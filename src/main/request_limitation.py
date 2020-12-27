class RequestLimiter:
    class RequestLimitation:

        def __init__(self, request_limiter):
            self._request_limiter = request_limiter

        def __enter__(self):
            self._request_limiter.new_request()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._request_limiter.end_request()

    def __init__(self, max_number_of_concurrent_requests):
        self._max_number_of_concurrent_requests = max_number_of_concurrent_requests
        self._current_number_of_concurrent_requests = 0

    def limited_requests(self):
        return RequestLimiter.RequestLimitation(self)

    def new_request(self):
        if self._current_number_of_concurrent_requests > self._max_number_of_concurrent_requests:
            raise RequestLimitExceededException()

        self._current_number_of_concurrent_requests += 1
        print(f"New request ({self._current_number_of_concurrent_requests} concurrent)")

    def end_request(self):
        self._current_number_of_concurrent_requests -= 1
        print(f"Request ended ({self._current_number_of_concurrent_requests} concurrent)")


class RequestLimitExceededException(Exception):
    """Raised when the max number of requests is exceeded"""

    def __init__(self):
        self.message = 'Request limit exceeded'
        Exception.__init__(self)
