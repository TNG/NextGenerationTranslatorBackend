from contextlib import ExitStack
from unittest.mock import patch, Mock, AsyncMock, call, MagicMock

import pytest

from schemas import TranslatorApiResponseHealthSchema, TranslatorApiResponseDetectionSchema, TranslatorApiDetectionSchema, TranslatorApiResponseTranslationSchema, \
    TranslatorApiTranslationSchema
from settings import TranslatorSettings
from src.test.mocks.translator_model_mocks import TranslatorModelMockA, TranslatorModelMockB
from translator import TranslatorProxy, TranslatorNotReadyException, UnexpectedTranslationError
from translator_proxy_client import FailedTranslatorProxyRequest


@pytest.fixture(scope="module", autouse=True)
def _env_mock():
    """ Preparation for integration tests.

    Mocks away RequestLimiter and Detector in the 'translator_service' module.

    :return:
    """
    settings_mock = TranslatorSettings()
    settings_mock.models = ["mockA", "mockB"]
    settings_mock.translator_clients = ["client_a", "client_b"]
    with ExitStack() as e:
        e.enter_context(patch("translator.models", [TranslatorModelMockA, TranslatorModelMockB]))
        e.enter_context(patch("translator.settings", settings_mock))
        yield


@pytest.fixture(autouse=True)
def proxy_mock():
    proxy_mock = Mock()
    with patch("translator.TranslatorProxyClient", proxy_mock):
        proxy_mock.return_value.get_models = AsyncMock()
        proxy_mock.return_value.get_models.return_value = Mock(models=["mockA"])
        proxy_mock.return_value.get_health = AsyncMock()
        proxy_mock.return_value.post_translation = AsyncMock()
        proxy_mock.return_value.post_detection = AsyncMock()
        yield proxy_mock


@pytest.fixture(autouse=True)
def patch_tenacity_sleep():
    # avoid tenacity actually waiting for retry
    with patch("tenacity.nap.time.sleep", MagicMock()):
        yield


class TestTranslatorProxy:

    def test_init(self, proxy_mock):
        translator_proxy = TranslatorProxy()
        assert translator_proxy.models_determined is False
        translator_proxy.initialize_models()
        assert translator_proxy.models_determined is True
        assert proxy_mock.mock_calls == [call('client_a'), call().get_models(),
                                         call('client_b'), call().get_models()]

    def test_list_models(self, proxy_mock):
        proxy_mock.return_value.get_models.side_effect = [Mock(models=["mockA"]), Mock(models=["mockB"])]
        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        assert translator_proxy.list_models() == [TranslatorModelMockA, TranslatorModelMockB]

    def test_models_loaded_true(self, proxy_mock):
        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        assert translator_proxy.models_loaded is True

    def test_models_loaded_false(self, proxy_mock):
        translator_proxy = TranslatorProxy()
        proxy_mock.return_value.get_health.side_effect = [TranslatorApiResponseHealthSchema(healthy=True, serviceAvailable=False),
                                                          TranslatorApiResponseHealthSchema(healthy=True, serviceAvailable=True)]
        translator_proxy.initialize_models()
        assert translator_proxy.models_loaded is False
        assert proxy_mock.return_value.get_health.call_count == 2

    def test_language_detect(self, proxy_mock):
        response = TranslatorApiResponseDetectionSchema(text="testLanguage")
        translator_proxy = TranslatorProxy()
        proxy_mock.return_value.post_detection.return_value = response
        translator_proxy.initialize_models()
        assert translator_proxy.detect_language("test") == response.text
        proxy_mock.return_value.post_detection.assert_called_once_with(TranslatorApiDetectionSchema(text='test'))

    def test_translate(self, proxy_mock):
        response = TranslatorApiResponseTranslationSchema(texts=["testAnswer"])
        translator_proxy = TranslatorProxy()
        proxy_mock.return_value.post_translation.return_value = response
        translator_proxy.initialize_models()
        assert translator_proxy.translate("testText", target_language="de", source_language="en") == response.texts[0]
        assert proxy_mock.return_value.post_translation.mock_calls == [
            call(TranslatorApiTranslationSchema(texts=['testText'], targetLanguage='fr', sourceLanguage='en')),
            call(TranslatorApiTranslationSchema(texts=['testAnswer'], targetLanguage='de', sourceLanguage='fr'))
        ]  # cf. TranslatorModelMockA and TranslatorModelMockB

    def test_list_models_uninitialized(self):
        translator_proxy = TranslatorProxy()
        with pytest.raises(TranslatorNotReadyException):
            translator_proxy.list_models()

    def test_detect_uninitialized(self):
        translator_proxy = TranslatorProxy()
        with pytest.raises(TranslatorNotReadyException):
            translator_proxy.detect_language("test")

    def test_translate_uninitialized(self):
        translator_proxy = TranslatorProxy()
        with pytest.raises(TranslatorNotReadyException):
            translator_proxy.translate("test", "de", "en")

    def test_initialize_retry(self, proxy_mock):
        proxy_mock.return_value.get_models.side_effect = [Mock(models=["mockA"]), FailedTranslatorProxyRequest("client", "dummy"),  # attempt 1: one client failes
                                                          Mock(models=[]), Mock(models=["mockA"]),  # attempt 2: one client has no models
                                                          Mock(models=["mockA"]), Mock(models=["mockB"])]  # attempt 3: ok

        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        assert proxy_mock.mock_calls == [call('client_a'), call().get_models(),
                                         call('client_b'), call().get_models()]*3


    def test_catch_proxy_error_on_health_check(self, proxy_mock):
        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        proxy_mock.return_value.get_health.side_effect = FailedTranslatorProxyRequest("client", "dummy")
        with pytest.raises(UnexpectedTranslationError):
            translator_proxy.models_loaded


    def test_catch_proxy_error_on_translate(self, proxy_mock):
        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        proxy_mock.return_value.post_translation.side_effect = FailedTranslatorProxyRequest("client", "dummy")
        with pytest.raises(UnexpectedTranslationError):
            translator_proxy.translate("test", "de", "en")

    def test_catch_proxy_error_on_detection(self, proxy_mock):
        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        proxy_mock.return_value.post_detection.side_effect = FailedTranslatorProxyRequest("client", "dummy")
        with pytest.raises(UnexpectedTranslationError):
            translator_proxy.detect_language("test")


    def test_returns_error_if_model_not_loaded(self, proxy_mock, _env_mock):
        translator_proxy = TranslatorProxy()
        translator_proxy.initialize_models()
        proxy_mock.return_value.get_health.return_value = TranslatorApiResponseHealthSchema(healthy = True, serviceAvailable = False)
        with pytest.raises(TranslatorNotReadyException):
            translator_proxy.translate("test", "de", "en")