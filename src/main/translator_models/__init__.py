from typing import List, Type

from translator_models.mock_translator import MockTranslator
from translator_models.translator_model import TranslatorModel
from translator_models.opusmt_translator import OpusMTTranslator
from translator_models.wmt19_translator import Wmt19Translator
from translator_models.nllb200_translator import Nllb200Translator



models: List[Type[TranslatorModel]] = [
    Nllb200Translator,
    OpusMTTranslator,
    Wmt19Translator,
    MockTranslator
]
