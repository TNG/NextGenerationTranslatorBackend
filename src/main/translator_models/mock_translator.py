import logging
import time

from translator_models.translator_model import TranslatorModel, TranslatorModelName

_logger = logging.getLogger(__name__)

class MockTranslator(TranslatorModel):
    model_name = TranslatorModelName.mock
    available_language_pairs = [("de","en"), ("en", "de")]
    translation_quality_grade = 2

    def _initialize_model(self):
        _logger.info("mock translator loaded")

    def translate(self, text, source_language, target_language):
        time.sleep(1)
        if source_language == "de":
            return f"{text} auf Englisch"
        elif source_language == "en":
            return f"{text} in German"
        else:
            raise ValueError(f"Direct Translation from {source_language} to {target_language} is not available!")
