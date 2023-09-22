import logging
import os
from pathlib import Path
from typing import Tuple

from easynmt import EasyNMT

from constants import make_absolute_path
from translator_models.translator_model import TranslatorModel, TranslatorModelName
from .opusmt_languages import ISO639_LANGUAGE_TUPLES, ISO639_LANGUAGES, ISO639_TO_OPUS_MT_LANGUAGE_TUPLE_CORRECTIONS

EASY_NMT_CACHE_DIRECTORY = make_absolute_path("easy_nmt_cache")

OPUS_MT_MODEL_CACHE_DIRECTORY = os.getenv("OPUS_MT_MODEL_CACHE_DIRECTORY",
                                          str(Path(os.getenv("HOME","/root")) / ".cache/huggingface"))


_logger = logging.getLogger(__name__)


class OpusMTTranslator(TranslatorModel):
    model_name = TranslatorModelName.opus_mt
    available_language_pairs = ISO639_LANGUAGE_TUPLES
    translation_quality_grade = 2

    def _initialize_model(self):
        self._model = EasyNMT("opus-mt", cache_folder=EASY_NMT_CACHE_DIRECTORY, device='cpu',
                              max_loaded_models=50)
        _logger.info(f"Model {self.model_name} loaded.")

    def translate(self, text, source_language, target_language):
        opus_mt_source_language, opus_mt_target_language = self.__iso639_to_opus_mt_language_codes(source_language,
                                                                                                   target_language)
        text_translated = self._model.translate(text, opus_mt_target_language, source_lang=opus_mt_source_language)
        return text_translated

    @staticmethod
    def __iso639_to_opus_mt_language_codes(source_language: str, target_language: str) -> Tuple[str, str]:
        """

        :param source_language:  code according to ISO-639-1 or ISO-639-3
        :param target_language:  code according to ISO-639-1 or ISO-639-3
        :return: tuple of language codes as used in Opus MT model
        """
        if target_language not in ISO639_LANGUAGES:
            raise ValueError(
                f"Target Language '{target_language}' not available! Currently, only {ISO639_LANGUAGES} are supported as language!")
        if source_language not in ISO639_LANGUAGES:
            raise ValueError(
                f"Source Language '{source_language}' not available! Currently, only {ISO639_LANGUAGES} are supported as language!")
        iso639_language_pair = (source_language, target_language)
        if iso639_language_pair in ISO639_LANGUAGE_TUPLES:
            return ISO639_TO_OPUS_MT_LANGUAGE_TUPLE_CORRECTIONS.get(iso639_language_pair, iso639_language_pair)
        else:
            raise ValueError(f"Direct Translation from {source_language} to {target_language} is not available!")

    @staticmethod
    def __cache_exists(source: str, target: str) -> bool:
        cache_directory = Path(OPUS_MT_MODEL_CACHE_DIRECTORY) / f"hub/models--Helsinki-NLP--opus-mt-{source}-{target}"
        return cache_directory.exists()

    def preload(self):
        """ Load all available models (to store them in cache).

        Skips a language pair if the expected cache folder is detected on disk.
        """
        for i, (source, target) in enumerate(self.available_language_pairs):
            if not self.__cache_exists(source, target):
                _logger.info(f"{self.model_name}: Preload {source}->{target} (processed {i} of {len(self.available_language_pairs)} available language pairs)")
                try:
                    self.translate("text", source, target)
                except Exception as e:
                    _logger.error(f"Failed to preload {source}->{target}: {type(e)} - {e}")
            else:
                _logger.debug(f"Skipping preload {source}->{target} as cache directory has been detected")
