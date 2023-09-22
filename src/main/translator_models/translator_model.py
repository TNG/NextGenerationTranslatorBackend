import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple

from utils.timer import Timer

_logger = logging.getLogger(__name__)

class TranslatorModelName(str, Enum):
    nlb200 = "nlb-200"
    opus_mt = "opus-mt"
    wmt19 = "wmt-19"
    mock = "mock"

class TranslatorModel(ABC):

    def __init__(self):
        self.__initialize_model()

    def __initialize_model(self):
        _logger.info(f"Initializing {self.model_name} model...")
        with Timer(f"{self.model_name} load time"):
            self._initialize_model()
        # print(self.translate('Das Model ist nun geladen', 'de', 'en'))

    @classmethod
    @property
    @abstractmethod
    def model_name(cls) -> TranslatorModelName:
        pass

    @classmethod
    @property
    @abstractmethod
    def available_language_pairs(cls) -> List[Tuple[str, str]]:
        pass

    @classmethod
    @property
    @abstractmethod
    def translation_quality_grade(cls) -> int:
        pass

    @abstractmethod
    def _initialize_model(self):
        pass

    @abstractmethod
    def translate(self, text, source_language, target_language):
        """

        :param text:
        :param source_language: Source language code according to ISO-639-1 (2 letter) or ISO-639-3 (3 letter; if language not in ISO-639-1)
        :param target_language: Target language code according to ISO-639-1 (2 letter) or ISO-639-3 (3 letter; if language not in ISO-639-1)
        :return:
        """
        pass

    def preload(self):
        """ Load all available models (to store them in cache). """
        for i, (source, target) in enumerate(self.available_language_pairs):
            _logger.info(f"{self.model_name}: Preload {source}->{target} (processed {i} of {len(self.available_language_pairs)} available language pairs)")
            try:
                self.translate("text", source, target)
            except Exception as e:
                _logger.error(f"Failed to preload {source}->{target}: {type(e)} - {e}")
