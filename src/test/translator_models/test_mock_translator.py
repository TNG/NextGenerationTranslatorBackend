from translator_models import MockTranslator


class TestMockTranslator:


    def test_model_translation(self):
        """ Tests the WMT19 Translator model to correctly tokenize and re-assemble translations.

        """
        mock = MockTranslator()
        assert mock.translate("blabla", "en", "de") == "blabla in German"
        assert mock.translate("blabla", "de", "en") == "blabla auf Englisch"
