from unittest.mock import patch, call, MagicMock

import pytest

from translator_models.wmt19_translator import Wmt19Translator


@pytest.fixture(autouse=True)
def transformer_model_mock():
    with patch("translator_models.wmt19_translator.FSMTForConditionalGeneration") as _model_mock:
        yield _model_mock


@pytest.fixture(autouse=True)
def transformer_tokenizer_mock():
    with patch("translator_models.wmt19_translator.FSMTTokenizer") as _tokenizer_mock:
        yield _tokenizer_mock


class TestWMT19Translator:

    def test_init_transformer_calls(self, transformer_model_mock, transformer_tokenizer_mock):
        Wmt19Translator()

        assert transformer_model_mock.mock_calls == [call.from_pretrained('facebook/wmt19-en-de'),
                                                     call.from_pretrained().to('cuda'),
                                                     call.from_pretrained('facebook/wmt19-de-en'),
                                                     call.from_pretrained().to('cuda')
                                                     ]
        assert transformer_tokenizer_mock.mock_calls == [call.from_pretrained('facebook/wmt19-en-de'),
                                                         call.from_pretrained('facebook/wmt19-de-en')]

    @staticmethod
    def _setup_models_and_tokenizers(transformer_model_mock, transformer_tokenizer_mock):
        en_model = MagicMock()
        de_model = MagicMock()
        transformer_model_mock.from_pretrained.return_value.to.side_effect = [en_model, de_model]
        en_tokenizer = MagicMock()
        de_tokenizer = MagicMock()
        transformer_tokenizer_mock.from_pretrained.side_effect = [en_tokenizer, de_tokenizer]
        return {"en-de": [en_tokenizer, en_model], "de-en": [de_tokenizer, de_model]}

    @pytest.mark.parametrize("source,target", [("en", "de"), ("de", "en")])
    def test_translate(self, source, target, transformer_model_mock, transformer_tokenizer_mock):
        model_tokenizer_mocks = self._setup_models_and_tokenizers(transformer_model_mock, transformer_tokenizer_mock)

        used_tokenizer, used_model = model_tokenizer_mocks[f"{source}-{target}"]
        unused_tokenizer, unused_model = model_tokenizer_mocks[f"{target}-{source}"]

        wmt19 = Wmt19Translator()

        res = wmt19.translate("input_text", source, target)
        assert used_model.mock_calls == [call.generate(), call.generate().__getitem__(0)]
        assert used_tokenizer.mock_calls == [call("input_text", return_tensors='pt'),
                                               call().to('cuda'),
                                               call().to().keys(),  # from: model.generate(**inputs)
                                               call().to().keys().__iter__(),  # from: model.generate(**inputs)
                                               call.decode(used_model.generate.return_value.__getitem__.return_value, skip_special_tokens=True)]
        assert unused_model.mock_calls == []
        assert unused_tokenizer.mock_calls == []

        assert res == used_tokenizer.decode.return_value
