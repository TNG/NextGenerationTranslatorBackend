import asyncio
import json
import os
import random
from _csv import reader

import aiohttp
import pytest

from datetime import datetime

base_url = os.getenv('TEST_HOST', 'http://localhost')
number_of_requests = int(os.getenv('NUMBER_OF_REQUESTS', 100))
request_timespan = int(os.getenv('REQUEST_TIMESPAN', 10))
token = os.getenv('BEARER_TOKEN', None)
start_server_timeout = 2

headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
if token is not None:
    headers['Authorization'] = f"Bearer {token}"


class TestLoad:

    @pytest.mark.asyncio
    @pytest.fixture(autouse=True)
    def server_configure(self, event_loop):
        event_loop.run_until_complete(self._wait_until_service_is_ready())
        self.pytest_configure()

        yield self

    async def _wait_until_service_is_ready(self):
        async with aiohttp.ClientSession(headers=headers) as session:
            await self._wait_until_service_available(session)

    # noinspection PyBroadException
    @staticmethod
    async def _wait_until_service_available(session):
        running = False
        while not running:
            await asyncio.sleep(start_server_timeout)

            try:
                async with session.post(f"{base_url}/health") as resp:
                    response_text = await resp.text()
                    result = json.loads(response_text)
                    if result['serviceAvailable']:
                        running = True
            except Exception:
                pass

        return True

    def pytest_configure(self):
        with open('resources/test_texts.csv', 'r') as file:
            csv_reader = reader(file)
            self._texts = list(csv_reader)

        self.max_timeout = request_timespan

    @pytest.mark.asyncio
    def test_http_client(self, event_loop):
        print(f"Running {number_of_requests} requests")
        event_loop.run_until_complete(self._start_requests())

    async def _start_requests(self):
        n_requests = number_of_requests
        async with aiohttp.ClientSession(headers=headers) as session:
            await asyncio.gather(
                *[self._translate_and_assert(session, i) for i in range(n_requests)]
            )

    async def _translate_and_assert(self, session, req_n):
        text_to_translate = self._texts[random.randint(0, len(self._texts) - 1)]
        pause = random.random() * self.max_timeout

        request_body = json.dumps({'targetLanguage': text_to_translate[2], 'texts': [text_to_translate[0]]})
        print(f"Waiting for {pause.__format__('.2f')} seconds at {datetime.now()}")
        await asyncio.sleep(pause)
        print(f"Creating request {req_n} for text '{text_to_translate[0]}' to {base_url} at {datetime.now()}")

        async with session.post(f"{base_url}/translation", data=request_body) as resp:
            if resp.status == 200:
                response_text = await resp.text()
                result = json.loads(response_text)
                result_text = result['texts'][0]

                print(f"Got result for request {req_n} as text '{result_text}' at {datetime.now()}")
                assert result_text == text_to_translate[1]
                return result
