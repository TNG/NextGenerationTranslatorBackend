from abc import ABC

from translator_models import TranslatorModel


class TranslatorModelMockBase(TranslatorModel, ABC):

    def _initialize_model(self):
        pass

    def translate(self, text, source_language, target_language):
        if (source_language, target_language) in self.available_language_pairs:
            return f"{text}[{self.model_name};{source_language}->{target_language}]"
        raise ValueError("invalid language pair")

class TranslatorModelMockA(TranslatorModelMockBase):
    model_name = "mockA"
    available_language_pairs = [("de", "en"), ("en", "fr"), ("fr", "de"), ("hu", "de")]
    translation_quality_grade = 1


class TranslatorModelMockB(TranslatorModelMockBase):
    model_name = "mockB"
    available_language_pairs = [("de", "en"), ("en", "es"), ("es", "de")]
    translation_quality_grade = 2
