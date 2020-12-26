import asyncio
import json
import random

import aiohttp
import pytest

from datetime import datetime


class TestLoad:

    @pytest.fixture(autouse=True)
    def pytest_configure(self):
        self._texts = [
            ('Hello', 'Hallo ')
        ]

    async def make_request(self, session, req_n):
        text_to_translate = self._texts[random.randint(0, len(self._texts) - 1)]

        url = "http://localhost/translation"
        request_body = json.dumps({'targetLanguage': 'de', 'texts': [text_to_translate[0]]})
        print(f"making request {req_n} to {url} at {datetime.now()}")

        async with session.post(url, data=request_body) as resp:
            if resp.status == 200:
                response_text = await resp.text()
                result = json.loads(response_text)
                assert result['texts'][0] == text_to_translate[1]
                return result

    async def start_requests(self):
        headers = {'content-type': 'application/json'}
        n_requests = 1
        async with aiohttp.ClientSession(headers=headers) as session:
            x = await asyncio.gather(
                *[self.make_request(session, i) for i in range(n_requests)]
            )
            print(x)

    @pytest.mark.asyncio
    def test_http_client(self, event_loop):
        event_loop.run_until_complete(self.start_requests())
        assert 0       # TODO remove
