from translator_models.translator_model import TranslatorModel, TranslatorModelName
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import logging

_logger = logging.getLogger(__name__)

PRETRAINED_MODEL_FILE = 'facebook/nllb-200-3.3B'

LANGUAGE_DICT = {
    "af": "afr_Latn",
    "ak": "aka_Latn",
    "am": "amh_Ethi",
    "ar": "arb_Arab",
    "as": "asm_Beng",
    "awa": "awa_Deva",
    "ay": "ayr_Latn",
    "az": "azb_Arab",
    "ba": "bak_Cyrl",
    "bm": "bam_Latn",
    "ban": "ban_Latn",
    "be": "bel_Cyrl",
    "bem": "bem_Latn",
    "bn": "ben_Beng",
    "bho": "bho_Deva",
    "bo": "bod_Tibt",
    "bs": "bos_Latn",
    "bug": "bug_Latn",
    "bg": "bul_Cyrl",
    "ceb": "ceb_Latn",
    "cs": "ces_Latn",
    "ku": "ckb_Arab",
    "tt": "crh_Latn",
    "cy": "cym_Latn",
    "da": "dan_Latn",
    "de": "deu_Latn",
    "din": "dik_Latn",
    "dyu": "dyu_Latn",
    "dz": "dzo_Tibt",
    "en": "eng_Latn",
    "eo": "epo_Latn",
    "et": "est_Latn",
    "eu": "eus_Latn",
    "ee": "ewe_Latn",
    "es": "spa_Latn",
    "fo": "fao_Latn",
    "fj": "fij_Latn",
    "fi": "fin_Latn",
    "fon": "fon_Latn",
    "fr": "fra_Latn",
    "fur": "fur_Latn",
    "ga": "gle_Latn",
    "gl": "glg_Latn",
    "gn": "grn_Latn",
    "gu": "guj_Gujr",
    "ha": "hau_Latn",
    "he": "heb_Hebr",
    "hi": "hin_Deva",
    "hr": "hrv_Latn",
    "hu": "hun_Latn",
    "hy": "hye_Armn",
    "ig": "ibo_Latn",
    "id": "ind_Latn",
    "is": "isl_Latn",
    "it": "ita_Latn",
    "jv": "jav_Latn",
    "ja": "jpn_Jpan",
    "kab": "kab_Latn",
    "kam": "kam_Latn",
    "kn": "kan_Knda",
    "ks": "kas_Arab",
    "ka": "kat_Geor",
    "kr": "knc_Arab",
    "kk": "kaz_Cyrl",
    "rw": "kin_Latn",
    "kmb": "kmb_Latn",
    "ko": "kor_Hang",
    "lo": "lao_Laoo",
    "ln": "lin_Latn",
    "lt": "lit_Latn",
    "lg": "lug_Latn",
    "lv": "lvs_Latn",
    "mag": "mag_Deva",
    "mai": "mai_Deva",
    "ml": "mal_Mlym",
    "mr": "mar_Deva",
    "min": "min_Arab",
    "mk": "mkd_Cyrl",
    "mt": "mlt_Latn",
    "mn": "khk_Cyrl",
    "mos": "mos_Latn",
    "mi": "mri_Latn",
    "my": "mya_Mymr",
    "no": "nno_Latn",
    "ne": "npi_Deva",
    "om": "gaz_Latn",
    "pag": "pag_Latn",
    "pap": "pap_Latn",
    "fa": "pes_Arab",
    "pl": "pol_Latn",
    "pt": "por_Latn",
    "qu": "quy_Latn",
    "rn": "run_Latn",
    "ru": "rus_Cyrl",
    "sg": "sag_Latn",
    "sa": "san_Deva",
    "sat": "sat_Olck",
    "scn": "scn_Latn",
    "shn": "shn_Mymr",
    "sk": "slk_Latn",
    "sl": "slv_Latn",
    "sm": "smo_Latn",
    "sn": "sna_Latn",
    "sd": "snd_Arab",
    "so": "som_Latn",
    "sq": "als_Latn",
    "sc": "srd_Latn",
    "sr": "srp_Cyrl",
    "ss": "ssw_Latn",
    "su": "sun_Latn",
    "sv": "swe_Latn",
    "sw": "swh_Latn",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "tg": "tgk_Cyrl",
    "tl": "tgl_Latn",
    "th": "tha_Thai",
    "ti": "tir_Ethi",
    "tpi": "tpi_Latn",
    "tn": "tsn_Latn",
    "ts": "tso_Latn",
    "tk": "tuk_Latn",
    "tum": "tum_Latn",
    "tr": "tur_Latn",
    "tw": "twi_Latn",
    "uk": "ukr_Cyrl",
    "umb": "umb_Latn",
    "ur": "urd_Arab",
    "uz": "uzn_Latn",
    "vi": "vie_Latn",
    "war": "war_Latn",
    "wo": "wol_Latn",
    "xh": "xho_Latn",
    "yi": "ydd_Hebr",
    "yo": "yor_Latn",
    "zh": "zho_Hans",
    "zho": "zho_Hant",
    "ms": "zsm_Latn",
    "zu": "zul_Latn"
}
REVERSE_LANGUAGE_DICT = {key: value for key, value in LANGUAGE_DICT.items()}

LANGUAGE_PAIRS = [(lang1, lang2) for lang1 in LANGUAGE_DICT.keys() for lang2 in LANGUAGE_DICT.keys()]


class Nllb200Translator(TranslatorModel):
    model_name = TranslatorModelName.nlb200
    available_language_pairs = LANGUAGE_PAIRS
    translation_quality_grade = 2

    def _initialize_model(self):
        self._model, self._tokenizers = self._load_model()

    @staticmethod
    def _load_model():
        _logger.info(f'Loading NLLB200 Model..')

        _logger.info(f"Get AutoModelForSeq2SeqLM from pretrained model in from pretrained model in {PRETRAINED_MODEL_FILE}")
        model = AutoModelForSeq2SeqLM.from_pretrained(PRETRAINED_MODEL_FILE, use_auth_token=True).to('cuda')

        tokenizers = {}
        for key, value in LANGUAGE_DICT.items():
            _logger.info(f"Obtain AutoTokenizer from pretrained model in {PRETRAINED_MODEL_FILE} for source language {value}")
            tokenizers[key] = AutoTokenizer.from_pretrained(PRETRAINED_MODEL_FILE, use_auth_token=True,
                                                            src_lang=value)

        _logger.info(f'Finished loading of NLLB200 Model.')
        return model, tokenizers

    def translate(self, text, source_language, target_language):

        tokenizer = self._tokenizers[source_language]
        inputs = tokenizer(text, return_tensors='pt').to('cuda')
        language_code = REVERSE_LANGUAGE_DICT[target_language]

        translated_tokens = self._model.generate(
            **inputs, forced_bos_token_id=tokenizer.lang_code_to_id[language_code], max_length=1000
        )

        return tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
