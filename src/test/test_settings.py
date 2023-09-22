import os
from unittest import mock

from constants import TranslatorMode
from settings import TranslatorSettings
from translator_models.translator_model import TranslatorModelName


class TestTranslatorSettings:

    def test_settings(self):
        with mock.patch.dict(os.environ,
                             {"TRANSLATOR_PRELOAD_MODELS": "true",
                              "TRANSLATOR_RATE_LIMIT": "4",
                              "LOGLEVEL": "DEBUG",
                              "TRANSLATOR_MODELS": '["nlb-200", "opus-mt", "wmt-19"]'
                              }):
            settings = TranslatorSettings()
            assert settings.preload_models is True
            assert settings.rate_limit == 4
            assert settings.log_level == "DEBUG"
            assert settings.models == [TranslatorModelName.nlb200, TranslatorModelName.opus_mt, TranslatorModelName.wmt19]
            assert settings.mode == TranslatorMode.client