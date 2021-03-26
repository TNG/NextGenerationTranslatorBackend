from unittest.mock import patch, call

import pytest

from translator_models.opusmt_translator import OpusMTTranslator, EASY_NMT_CACHE_DIRECTORY


@pytest.fixture(autouse=True)
def easy_nmt_mock():
    with patch("translator_models.opusmt_translator.EasyNMT") as _easy_nmt_mock:
        yield _easy_nmt_mock


class TestOpusMTTranslator:

    def test_init(self, easy_nmt_mock):

        OpusMTTranslator()
        easy_nmt_mock.assert_called_once_with('opus-mt',
                                              cache_folder=EASY_NMT_CACHE_DIRECTORY,
                                              device='cpu',
                                              max_loaded_models=50)

    @pytest.mark.parametrize("iso_pair", [("nan", "nan"), ("fr", "ja")])
    def test_fail_for_invalid_tuple(self, iso_pair):
        with pytest.raises(ValueError):
            OpusMTTranslator().translate("some_text", source_language=iso_pair[0], target_language=iso_pair[1])