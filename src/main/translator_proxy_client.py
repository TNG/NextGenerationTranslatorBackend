import functools
import logging
from contextlib import AsyncExitStack
from typing import Any, Optional

import aiodns
import aiohttp
import tenacity
from tenacity import AsyncRetrying

from schemas import TranslatorApiResponseModelsSchema, TranslatorApiResponseHealthSchema, TranslatorApiResponseTranslationSchema, \
    TranslatorApiTranslationSchema, TranslatorApiResponseDetectionSchema, TranslatorApiDetectionSchema
from settings import settings

_logger = logging.getLogger(__name__)

class FailedTranslatorProxyRequest(Exception):
    def __init__(self, client: str, msg: str):
        self.client = client
        _logger.error(msg)
        super().__init__(msg)

class ForwardedTranslatorProxyError(Exception):
    def __init__(self, error, client, status_code):
        self.client = client
        self.error = error
        self.status_code = status_code
        _logger.debug(f"received {status_code} from client: {error}")
        super().__init__(error)

def _async_retry(coroutine):
    @functools.wraps(coroutine)
    async def _coroutine(self, *args, **kwargs):
        async for attempt in AsyncRetrying(stop=tenacity.stop_after_attempt(3),
                                           retry=tenacity.retry_if_exception_type(FailedTranslatorProxyRequest),
                                           wait=tenacity.wait_fixed(5),
                                           reraise=True
                                           ):
            with attempt:
                return await coroutine(self, *args, **kwargs)
    return _coroutine

class TranslatorProxyClient:
    """ Makes http calls to the translator client in the local namespace."""


    def __init__(self, client: str, session: Optional[aiohttp.ClientSession] = None):
        self.client = client
        self._session: aiohttp.ClientSession | None = session
        self._client_url_cache = None

    @property
    def _client_domain(self) -> str:
        return f"{self.client}.{settings.dns_namespace}"

    @_async_retry
    async def _get_client_url_from_srv_dns(self, domain):

        if self._client_url_cache:
            return self._client_url_cache

        resolver = aiodns.DNSResolver()
        # resolve the SRV record
        try:
            srv_records = await resolver.query(domain, 'SRV')
        except aiodns.error.DNSError as e:
            raise FailedTranslatorProxyRequest(self.client, f'Failed to resolve SRV domain: {str(e)}')

        if not srv_records:
            raise FailedTranslatorProxyRequest(self.client, f"No SRV records found for {domain}.")
        # pick the first available SRV record
        srv_record = srv_records[0]
        self._client_url_cache =  f"http://{srv_record.host}:{srv_record.port}"
        return self._client_url_cache

    @_async_retry
    async def _request(self, endpoint: str, method = "GET", **kwargs) -> Any:
        base_url = await self._get_client_url_from_srv_dns(self._client_domain)
        try:
            async with AsyncExitStack() as stack:
                session = self._session
                if not session:
                    session = await stack.enter_async_context(aiohttp.ClientSession())
                _logger.debug(f"Send {method} request to {base_url}/{endpoint}")
                response = await stack.enter_async_context(session.request(method,
                                                                           f"{base_url}/{endpoint}",
                                                                           headers={'Accept': 'application/json',
                                                                                    'Content-Type': 'application/json'},
                                                                           raise_for_status=False,
                                                                           **kwargs
                                                                           ))
                result = await response.json()
                if not response.ok:
                    raise ForwardedTranslatorProxyError(result.get("error", ""), self.client, response.status)
                return result
        except Exception as e:
            raise FailedTranslatorProxyRequest(self.client, f'Failed to get /{endpoint}: {str(e)}')

    @_async_retry
    async def get_models(self) -> TranslatorApiResponseModelsSchema:
        return TranslatorApiResponseModelsSchema(**(await self._request("models")))

    async def get_health(self) -> TranslatorApiResponseHealthSchema:
        return TranslatorApiResponseHealthSchema(**(await self._request("health")))

    async def post_translation(self, body: TranslatorApiTranslationSchema) -> TranslatorApiResponseTranslationSchema:
        return TranslatorApiResponseTranslationSchema(**(await self._request("translation", method="POST", data=body.json())))

    async def post_detection(self, body: TranslatorApiDetectionSchema) -> TranslatorApiResponseDetectionSchema:
        return TranslatorApiResponseDetectionSchema(**(await self._request("detection", method="POST", data=body.json())))
