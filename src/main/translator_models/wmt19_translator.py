import itertools
import logging

from transformers import FSMTTokenizer, FSMTForConditionalGeneration

from translator_models.translator_model import TranslatorModel, TranslatorModelName

_logger = logging.getLogger(__name__)

LANGUAGE_PAIRS = ["de-en", "en-de"]  # Pairs "en-ru", "ru-en" removed to keep WMT19 GPU memory usage expectedly below 16GB
LANGUAGE_TUPLES = [tuple(str.split(language_pair, "-")) for language_pair in LANGUAGE_PAIRS]
LANGUAGES = list(set(itertools.chain.from_iterable(LANGUAGE_TUPLES)))

PRETRAINED_MODEL_FILES = {
    "en-de": "facebook/wmt19-en-de",
    "de-en": "facebook/wmt19-de-en"
}

class Wmt19Translator(TranslatorModel):
    model_name = TranslatorModelName.wmt19
    available_language_pairs = LANGUAGE_TUPLES
    translation_quality_grade = 1

    def __init__(self):
        super().__init__()

    def _initialize_model(self):
        self._models, self._tokenizers = self._load_models()

    @staticmethod
    def _load_models():
        _logger.info(f'Loading WMT19 Model..')

        tokenizers = {}
        models = {}
        for key, mfile in PRETRAINED_MODEL_FILES.items():
            _logger.info(f"Obtain AutoTokenizer from pretrained model in {mfile} for language pair {key}")
            tokenizers[key] = FSMTTokenizer.from_pretrained(mfile)

            _logger.info(f"Obtain model in {mfile} for language pair {key}")
            models[key] = FSMTForConditionalGeneration.from_pretrained(mfile).to('cuda')

        _logger.info(f'Finished loading of WMT19 Model.')
        return models, tokenizers

    def translate(self, text, source_language, target_language):

        tokenizer = self._tokenizers[f"{source_language}-{target_language}"]
        model = self._models[f"{source_language}-{target_language}"]


        inputs = tokenizer(text, return_tensors='pt').to('cuda')

        translated_tokens = model.generate(**inputs)

        return tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
