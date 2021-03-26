from unittest.mock import patch, call

import pytest

from translator_models.nllb200_translator import REVERSE_LANGUAGE_DICT, Nllb200Translator, LANGUAGE_DICT


@pytest.fixture(autouse=True)
def transformer_auto_model_mock():
    with patch("translator_models.nllb200_translator.AutoModelForSeq2SeqLM") as _auto_model_mock:
        yield _auto_model_mock


@pytest.fixture(autouse=True)
def transformer_auto_tokenizer_mock():
    with patch("translator_models.nllb200_translator.AutoTokenizer") as _tokenizer_mock:
        yield _tokenizer_mock


class TestNLB200Translator:

    def test_reverse_language_dict(self):
        assert REVERSE_LANGUAGE_DICT['en'] == 'eng_Latn'

    def test_init_transformer_calls(self, transformer_auto_model_mock, transformer_auto_tokenizer_mock):
        Nllb200Translator()

        assert transformer_auto_model_mock.mock_calls == [call.from_pretrained('facebook/nllb-200-3.3B', use_auth_token=True),
                                                          call.from_pretrained().to('cuda')]
        assert LANGUAGE_DICT
        assert transformer_auto_tokenizer_mock.mock_calls == [call.from_pretrained('facebook/nllb-200-3.3B', use_auth_token=True, src_lang=scr_lang) for scr_lang in LANGUAGE_DICT.values()]


