import importlib
from contextlib import ExitStack
from dataclasses import dataclass
from unittest.mock import Mock, MagicMock, call, patch

import pytest
from flask.testing import FlaskClient

import request_limitation
import translator


@pytest.fixture(scope="module")
def patched_app():
    # since Translator, Detector, RequestLimiter is initialized in module / at import and requires a Redis, we brute force mock it away
    translator_mock = Mock(spec=translator.Translator)
    request_limiter_mock = MagicMock(spec=request_limitation.RequestLimiter)
    with ExitStack() as e:
        e.enter_context(patch("request_limitation.RequestLimiter", request_limiter_mock))
        e.enter_context(patch("translator.Translator", translator_mock))
        import translator_service
        importlib.reload(translator_service)
        yield translator_service.app, translator_mock, request_limiter_mock


@dataclass
class AppMockEnvironment:
    client: FlaskClient
    translator: Mock
    request_limiter: Mock


@pytest.fixture(autouse=True)
def app_mock(patched_app) -> AppMockEnvironment:
    app, translator_mock, request_limiter_mock = patched_app
    request_limiter_mock.reset_mock()
    translator_mock.reset_mock()
    translator_mock.return_value.translate.return_value = "dummy_translated_text"
    translator_mock.return_value.detect_language.return_value = "dummy_language"
    with app.test_client() as client:
        yield AppMockEnvironment(client, translator_mock, request_limiter_mock)


class TestTranslatorService:
    """ Unit tests for the TranslatorService. """

    def test_translation(self, app_mock):
        """ Test the /translation endpoint. """

        response_wrapper = app_mock.client.post("translation",
                                           json={"targetLanguage": "dummy_target",
                                                 "sourceLanguage": "dummy_source",
                                                 "texts": ["dummy_text"]})
        assert response_wrapper.status_code == 200
        app_mock.translator.assert_has_calls([call().translate('dummy_text',
                                                           'dummy_target',
                                                           source_language="dummy_source")])
        assert response_wrapper.json == {'texts': ['dummy_translated_text']}


    def test_detection(self, app_mock):
        response_wrapper = app_mock.client.post("detection",
                                                json={"text": "dummy_text" })
        assert response_wrapper.status_code == 200
        app_mock.translator.return_value.detect_language.assert_called_once_with("dummy_text")
        assert response_wrapper.json == {'text': "dummy_language"}