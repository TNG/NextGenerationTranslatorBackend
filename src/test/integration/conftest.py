"""
 Test context for testing the integration of translator service, translator and models.

 As Models, two dummy models are implemented.

 RequestLimiter and Detector are still mocked away.

"""
import importlib
from contextlib import ExitStack
from dataclasses import dataclass
from typing import List, Type
from unittest.mock import patch, MagicMock, Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient

import detector
import request_limitation
from settings import TranslatorSettings
from src.test.mocks.translator_model_mocks import TranslatorModelMockA, TranslatorModelMockB
from translator import Translator
from translator_models.translator_model import TranslatorModel


@dataclass
class TranslatorIntegrationTestEnvironment:
    request_limiter: Mock
    detector: Mock
    translator: Translator
    patched_app: Flask
    models: List[Type[TranslatorModel]]



@pytest.fixture(scope="module")
def integration_test_environment():
    """ Preparation for integration tests.

    Mocks away RequestLimiter and Detector in the 'translator_service' module.

    :return:
    """
    request_limiter_mock = MagicMock(spec=request_limitation.RequestLimiter)
    detector_mock = Mock(spec=detector.Detector)
    settings_mock = TranslatorSettings()
    settings_mock.models = ["mockA", "mockB"]

    with ExitStack() as e:
        e.enter_context(patch("request_limitation.RequestLimiter", request_limiter_mock))
        e.enter_context(patch("detector.Detector", detector_mock))
        e.enter_context(patch("translator.models", [TranslatorModelMockA, TranslatorModelMockB]))
        e.enter_context(patch("translator.settings", settings_mock))
        import translator_service
        importlib.reload(translator_service)
        translator_service.translator.initialize_models()
        yield TranslatorIntegrationTestEnvironment(request_limiter=request_limiter_mock,
                                                   detector=detector_mock,
                                                   patched_app=translator_service.app,
                                                   translator=translator_service.translator,
                                                   models=[TranslatorModelMockA, TranslatorModelMockB])


@pytest.fixture(scope="function", autouse=True)
def reset_integration_test_environment_mocks(integration_test_environment):
    """ Resetting the mocked request limiter and detector.

    Necessary, as instances are initialized in the 'translator_service' module and cannot
    easily be re-initialized/patched for every test individually. """
    integration_test_environment.request_limiter.return_value.limited_requests.reset_mock(return_value=True,
                                                                                          side_effect=True)
    integration_test_environment.detector.return_value.reset_mock(return_value=True, side_effect=True)
    integration_test_environment.translator.initialize_models()


@pytest.fixture(autouse=True)
def app_mock(integration_test_environment) -> FlaskClient:
    """ Returns a test flask client for testing the Api in the integration test environment. """
    with integration_test_environment.patched_app.test_client() as client:
        yield client
