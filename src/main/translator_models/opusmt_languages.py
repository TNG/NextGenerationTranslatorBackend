"""
 File to transform and filter the available OpusMT languages.

 Language codes are transformed to ISO639 codes and then filtered by (empirically determined) quality checks.

 (Main purpose of this file is to encapsulate this data-like file.)
"""

import itertools

# _OPUS_MT_LANGUAGE_PAIRS: List of language pairs of known available OpusMT models.
# For each, more infos can be found at https://huggingface.co/Helsinki-NLP/opus-mt-<PAIR>
_OPUS_MT_LANGUAGE_PAIRS = [
    "aav-en", "aed-es", "af-de", "af-en", "af-eo", "af-es", "af-fi", "af-fr", "af-nl", "af-ru", "af-sv",
    "alv-en", "am-sv", "ar-de", "ar-el", "ar-en", "ar-eo", "ar-es", "ar-fr", "ar-he", "ar-it", "ar-pl",
    "ar-ru", "ar-tr", "art-en", "ase-de", "ase-en", "ase-es", "ase-fr", "ase-sv", "az-en", "az-es",
    "az-tr", "bat-en", "bcl-de", "bcl-en", "bcl-es", "bcl-fi", "bcl-fr", "bcl-sv", "be-es", "bem-en",
    "bem-es", "bem-fi", "bem-fr", "bem-sv", "ber-en", "ber-es", "ber-fr", "bg-de", "bg-en", "bg-eo",
    "bg-es", "bg-fi", "bg-fr", "bg-it", "bg-ru", "bg-sv", "bg-tr", "bg-uk", "bi-en", "bi-es", "bi-fr",
    "bi-sv", "bn-en", "bnt-en", "bzs-en", "bzs-es", "bzs-fi", "bzs-fr", "bzs-sv", "ca-de", "ca-en",
    "ca-es", "ca-fr", "ca-it", "ca-nl", "ca-pt", "ca-uk", "cau-en", "ccs-en", "ceb-en", "ceb-es",
    "ceb-fi", "ceb-fr", "ceb-sv", "cel-en", "chk-en", "chk-es", "chk-fr", "chk-sv", "cpf-en", "crs-de",
    "crs-en", "crs-es", "crs-fi", "crs-fr", "crs-sv", "cs-de", "cs-en", "cs-eo", "cs-fi", "cs-fr",
    "cs-sv", "cs-uk", "csg-es", "csn-es", "cus-en", "cy-en", "da-de", "da-en", "da-eo", "da-es", "da-fi",
    "da-fr", "da-no", "da-ru", "de-af", "de-ar", "de-ase", "de-bcl", "de-bg", "de-bi", "de-bzs", "de-ca",
    "de-crs", "de-cs", "de-da", "de-ee", "de-efi", "de-el", "de-en", "de-eo", "de-es", "de-et", "de-eu",
    "de-fi", "de-fj", "de-fr", "de-gaa", "de-gil", "de-guw", "de-ha", "de-he", "de-hil", "de-ho", "de-hr",
    "de-ht", "de-hu", "de-ig", "de-ilo", "de-is", "de-iso", "de-it", "de-kg", "de-ln", "de-loz", "de-lt",
    "de-lua", "de-ms", "de-mt", "de-niu", "de-nl", "de-no", "de-nso", "de-ny", "de-pag", "de-pap",
    "de-pis", "de-pl", "de-pon", "de-tl", "de-uk", "de-vi", "dra-en", "ee-de", "ee-en", "ee-es", "ee-fi",
    "ee-fr", "ee-sv", "efi-de", "efi-en", "efi-fi", "efi-fr", "efi-sv", "el-ar", "el-eo", "el-fi",
    "el-fr", "el-sv", "en-aav", "en-af", "en-alv", "en-ar", "en-az", "en-bat", "en-bcl", "en-bem",
    "en-ber", "en-bg", "en-bi", "en-bnt", "en-bzs", "en-ca", "en-ceb", "en-cel", "en-chk", "en-cpf",
    "en-crs", "en-cs", "en-cus", "en-cy", "en-da", "en-de", "en-dra", "en-ee", "en-efi", "en-el", "en-eo",
    "en-es", "en-et", "en-eu", "en-euq", "en-fi", "en-fj", "en-fr", "en-ga", "en-gaa", "en-gil", "en-gl",
    "en-grk", "en-guw", "en-gv", "en-ha", "en-he", "en-hi", "en-hil", "en-ho", "en-ht", "en-hu", "en-hy",
    "en-id", "en-ig", "en-ilo", "en-is", "en-iso", "en-it", "en-jap", "en-kg", "en-kj", "en-kqn",
    "en-kwn", "en-kwy", "en-lg", "en-ln", "en-loz", "en-lu", "en-lua", "en-lue", "en-lun", "en-luo",
    "en-lus", "en-map", "en-mfe", "en-mg", "en-mh", "en-mk", "en-mkh", "en-ml", "en-mos", "en-mr",
    "en-mt", "en-mul", "en-ng", "en-nic", "en-niu", "en-nl", "en-nso", "en-ny", "en-nyk", "en-om",
    "en-pag", "en-pap", "en-phi", "en-pis", "en-pon", "en-poz", "en-pqe", "en-pqw", "en-rn", "en-rnd",
    "en-ro", "en-roa", "en-ru", "en-run", "en-rw", "en-sal", "en-sg", "en-sit", "en-sk", "en-sm", "en-sn",
    "en-sq", "en-ss", "en-st", "en-sv", "en-sw", "en-swc", "en-tdt", "en-ti", "en-tiv", "en-tl", "en-tll",
    "en-tn", "en-to", "en-toi", "en-tpi", "en-trk", "en-ts", "en-tut", "en-tvl", "en-tw", "en-ty",
    "en-uk", "en-umb", "en-ur", "en-vi", "en-xh", "en-zh", "eo-af", "eo-bg", "eo-cs", "eo-da", "eo-de",
    "eo-el", "eo-en", "eo-es", "eo-fi", "eo-fr", "eo-he", "eo-hu", "eo-it", "eo-nl", "eo-pl", "eo-pt",
    "eo-ro", "eo-ru", "eo-sh", "eo-sv", "es-aed", "es-af", "es-ar", "es-ase", "es-bcl", "es-ber", "es-bg",
    "es-bi", "es-bzs", "es-ca", "es-ceb", "es-crs", "es-cs", "es-csg", "es-csn", "es-da", "es-de",
    "es-ee", "es-efi", "es-el", "es-en", "es-eo", "es-et", "es-eu", "es-fi", "es-fj", "es-fr", "es-gaa",
    "es-gil", "es-gl", "es-guw", "es-ha", "es-he", "es-hil", "es-ho", "es-hr", "es-ht", "es-id", "es-ig",
    "es-ilo", "es-is", "es-iso", "es-it", "es-kg", "es-ln", "es-loz", "es-lt", "es-lua", "es-lus",
    "es-mfs", "es-mk", "es-mt", "es-niu", "es-nl", "es-no", "es-nso", "es-ny", "es-pag", "es-pap",
    "es-pis", "es-pl", "es-pon", "es-prl", "es-rn", "es-ro", "es-ru", "es-rw", "es-sg", "es-sl", "es-sm",
    "es-sn", "es-srn", "es-st", "es-swc", "es-tl", "es-tll", "es-tn", "es-to", "es-tpi", "es-tvl",
    "es-tw", "es-ty", "es-tzo", "es-uk", "es-ve", "es-vi", "es-war", "es-wls", "es-xh", "es-yo", "es-yua",
    "es-zai", "et-de", "et-en", "et-es", "et-fi", "et-fr", "et-ru", "et-sv", "eu-de", "eu-en", "eu-es",
    "eu-ru", "euq-en", "fi-af", "fi-bcl", "fi-bem", "fi-bg", "fi-bzs", "fi-ceb", "fi-crs", "fi-cs",
    "fi-de", "fi-ee", "fi-efi", "fi-el", "fi-en", "fi-eo", "fi-es", "fi-et", "fi-fj", "fi-fr", "fi-fse",
    "fi-gaa", "fi-gil", "fi-guw", "fi-ha", "fi-he", "fi-hil", "fi-ho", "fi-hr", "fi-ht", "fi-hu", "fi-id",
    "fi-ig", "fi-ilo", "fi-is", "fi-iso", "fi-it", "fi-kg", "fi-kqn", "fi-lg", "fi-ln", "fi-lu", "fi-lua",
    "fi-lue", "fi-lus", "fi-lv", "fi-mfe", "fi-mg", "fi-mh", "fi-mk", "fi-mos", "fi-mt", "fi-niu",
    "fi-nl", "fi-no", "fi-nso", "fi-ny", "fi-pag", "fi-pap", "fi-pis", "fi-pon", "fi-ro", "fi-ru",
    "fi-run", "fi-rw", "fi-sg", "fi-sk", "fi-sl", "fi-sm", "fi-sn", "fi-sq", "fi-srn", "fi-st", "fi-sv",
    "fi-sw", "fi-swc", "fi-tiv", "fi-tll", "fi-tn", "fi-to", "fi-toi", "fi-tpi", "fi-tr", "fi-ts",
    "fi-tvl", "fi-tw", "fi-ty", "fi-uk", "fi-ve", "fi-war", "fi-wls", "fi-xh", "fi-yap", "fi-yo",
    "fi-zne", "fj-en", "fj-fr", "fr-af", "fr-ar", "fr-ase", "fr-bcl", "fr-bem", "fr-ber", "fr-bg",
    "fr-bi", "fr-bzs", "fr-ca", "fr-ceb", "fr-crs", "fr-de", "fr-ee", "fr-efi", "fr-el", "fr-en", "fr-eo",
    "fr-es", "fr-fj", "fr-gaa", "fr-gil", "fr-guw", "fr-ha", "fr-he", "fr-hil", "fr-ho", "fr-hr", "fr-ht",
    "fr-hu", "fr-id", "fr-ig", "fr-ilo", "fr-iso", "fr-kg", "fr-kqn", "fr-kwy", "fr-lg", "fr-ln",
    "fr-loz", "fr-lu", "fr-lua", "fr-lue", "fr-lus", "fr-mfe", "fr-mh", "fr-mos", "fr-ms", "fr-mt",
    "fr-niu", "fr-no", "fr-nso", "fr-ny", "fr-pag", "fr-pap", "fr-pis", "fr-pl", "fr-pon", "fr-rnd",
    "fr-ro", "fr-ru", "fr-run", "fr-rw", "fr-sg", "fr-sk", "fr-sl", "fr-sm", "fr-sn", "fr-srn", "fr-st",
    "fr-sv", "fr-swc", "fr-tiv", "fr-tl", "fr-tll", "fr-tn", "fr-to", "fr-tpi", "fr-ts", "fr-tum",
    "fr-tvl", "fr-tw", "fr-ty", "fr-uk", "fr-ve", "fr-vi", "fr-war", "fr-wls", "fr-xh", "fr-yap", "fr-yo",
    "fr-zne", "fse-fi", "ga-en", "gaa-de", "gaa-en", "gaa-es", "gaa-fi", "gaa-fr", "gaa-sv", "gil-en",
    "gil-es", "gil-fi", "gil-fr", "gil-sv", "gl-en", "gl-es", "gl-pt", "grk-en", "guw-de", "guw-en",
    "guw-es", "guw-fi", "guw-fr", "guw-sv", "gv-en", "ha-en", "ha-es", "ha-fi", "ha-fr", "ha-sv", "he-ar",
    "he-de", "he-eo", "he-es", "he-fi", "he-it", "he-ru", "he-sv", "he-uk", "hi-en", "hi-ur",
    "hil-de", "hil-en", "hil-fi", "ho-en", "hr-es", "hr-fi", "hr-fr", "hr-sv", "ht-en", "ht-es", "ht-fi",
    "ht-fr", "ht-sv", "hu-de", "hu-en", "hu-eo", "hu-fi", "hu-fr", "hu-sv", "hu-uk", "hy-en", "hy-ru",
    "id-en", "id-es", "id-fi", "id-fr", "id-sv", "ig-de", "ig-en", "ig-es", "ig-fi", "ig-fr", "ig-sv",
    "ilo-de", "ilo-en", "ilo-es", "ilo-fi", "ilo-sv", "is-de", "is-en", "is-eo", "is-es", "is-fi",
    "is-fr", "is-it", "is-sv", "iso-en", "iso-es", "iso-fi", "iso-fr", "iso-sv", "it-ar", "it-bg",
    "it-ca", "it-de", "it-en", "it-eo", "it-es", "it-fr", "it-is", "it-lt", "it-ms", "it-sv", "it-uk",
    "it-vi", "ja-ar", "ja-bg", "ja-da", "ja-de", "ja-en", "ja-es", "ja-fi", "ja-fr", "ja-he", "ja-hu",
    "ja-it", "ja-ms", "ja-nl", "ja-pl", "ja-pt", "ja-ru", "ja-sh", "ja-sv", "ja-tr", "ja-vi", "jap-en",
    "ka-en", "ka-ru", "kab-en", "kg-en", "kg-es", "kg-fr", "kg-sv", "kj-en", "kl-en", "ko-de", "ko-en",
    "ko-es", "ko-fi", "ko-fr", "ko-hu", "ko-ru", "ko-sv", "kqn-en", "kqn-es", "kqn-fr", "kqn-sv",
    "kwn-en", "kwy-en", "kwy-fr", "kwy-sv", "lg-en", "lg-es", "lg-fi", "lg-fr", "lg-sv", "ln-de", "ln-en",
    "ln-es", "ln-fr", "loz-de", "loz-en", "loz-es", "loz-fi", "loz-fr", "loz-sv", "lt-de", "lt-eo",
    "lt-es", "lt-fr", "lt-it", "lt-pl", "lt-ru", "lt-sv", "lt-tr", "lu-en", "lu-es", "lu-fi", "lu-fr",
    "lu-sv", "lua-en", "lua-es", "lua-fi", "lua-fr", "lua-sv", "lue-en", "lue-es", "lue-fi", "lue-fr",
    "lue-sv", "lun-en", "luo-en", "lus-en", "lus-es", "lus-fi", "lus-fr", "lus-sv", "lv-en", "lv-es",
    "lv-fi", "lv-fr", "lv-ru", "lv-sv", "mfe-en", "mfe-es", "mfs-es", "mg-en", "mg-es", "mh-en", "mh-es",
    "mh-fi", "mk-en", "mk-es", "mk-fi", "mk-fr", "mkh-en", "ml-en", "mos-en", "mr-en", "ms-de", "ms-fr",
    "ms-it", "mt-en", "mt-es", "mt-fi", "mt-fr", "mt-sv", "mul-en", "ng-en", "nic-en", "niu-de", "niu-en",
    "niu-es", "niu-fi", "niu-fr", "niu-sv", "nl-af", "nl-ca", "nl-en", "nl-eo", "nl-es", "nl-fi", "nl-fr",
    "nl-no", "nl-sv", "nl-uk", "no-da", "no-de", "no-es", "no-fi", "no-fr", "no-nl", "no-pl", "no-ru",
    "no-sv", "no-uk", "nso-de", "nso-en", "nso-es", "nso-fi", "nso-fr", "nso-sv", "ny-de", "ny-en",
    "ny-es", "nyk-en", "om-en", "pa-en", "pag-de", "pag-en", "pag-es", "pag-fi", "pag-sv", "pap-de",
    "pap-en", "pap-es", "pap-fi", "pap-fr", "phi-en", "pis-en", "pis-es", "pis-fi", "pis-fr", "pis-sv",
    "pl-ar", "pl-de", "pl-en", "pl-eo", "pl-es", "pl-fr", "pl-lt", "pl-no", "pl-sv", "pl-uk", "pon-en",
    "pon-es", "pon-fi", "pon-fr", "pon-sv", "pqe-en", "prl-es", "pt-ca", "pt-eo", "pt-gl", "pt-tl",
    "pt-uk", "rn-de", "rn-en", "rn-es", "rn-fr", "rn-ru", "rnd-en", "rnd-fr", "rnd-sv", "ro-eo", "ro-fi",
    "ro-fr", "ro-sv", "roa-en", "ru-af", "ru-ar", "ru-bg", "ru-da", "ru-en", "ru-eo", "ru-es", "ru-et",
    "ru-eu", "ru-fi", "ru-fr", "ru-he", "ru-hy", "ru-lt", "ru-lv", "ru-no", "ru-sl", "ru-sv", "ru-uk",
    "ru-vi", "run-en", "run-es", "run-sv", "rw-en", "rw-es", "rw-fr", "rw-sv", "sal-en", "sg-en", "sg-es",
    "sg-fi", "sg-fr", "sg-sv", "sh-eo", "sh-uk", "sk-en", "sk-es", "sk-fi", "sk-fr", "sk-sv", "sl-es",
    "sl-fi", "sl-fr", "sl-ru", "sl-sv", "sl-uk", "sm-en", "sm-es", "sm-fr", "sn-en", "sn-es", "sn-fr",
    "sn-sv", "sq-en", "sq-es", "sq-sv", "srn-en", "srn-es", "srn-fr", "srn-sv", "ss-en", "ssp-es",
    "st-en", "st-es", "st-fi", "st-fr", "st-sv", "sv-af", "sv-ase", "sv-bcl", "sv-bem", "sv-bg", "sv-bi",
    "sv-bzs", "sv-ceb", "sv-chk", "sv-crs", "sv-cs", "sv-ee", "sv-efi", "sv-el", "sv-en", "sv-eo",
    "sv-es", "sv-et", "sv-fi", "sv-fj", "sv-fr", "sv-gaa", "sv-gil", "sv-guw", "sv-ha", "sv-he", "sv-hil",
    "sv-ho", "sv-hr", "sv-ht", "sv-hu", "sv-id", "sv-ig", "sv-ilo", "sv-is", "sv-iso", "sv-kg", "sv-kqn",
    "sv-kwy", "sv-lg", "sv-ln", "sv-lu", "sv-lua", "sv-lue", "sv-lus", "sv-lv", "sv-mfe", "sv-mh",
    "sv-mos", "sv-mt", "sv-niu", "sv-nl", "sv-no", "sv-nso", "sv-ny", "sv-pag", "sv-pap", "sv-pis",
    "sv-pon", "sv-rnd", "sv-ro", "sv-ru", "sv-run", "sv-rw", "sv-sg", "sv-sk", "sv-sl", "sv-sm", "sv-sn",
    "sv-sq", "sv-srn", "sv-st", "sv-swc", "sv-th", "sv-tiv", "sv-tll", "sv-tn", "sv-to", "sv-toi",
    "sv-tpi", "sv-ts", "sv-tum", "sv-tvl", "sv-tw", "sv-ty", "sv-uk", "sv-umb", "sv-ve", "sv-war",
    "sv-wls", "sv-xh", "sv-yap", "sv-yo", "sv-zne", "swc-en", "swc-es", "swc-fi", "swc-fr", "swc-sv",
    "taw-en", "th-en", "th-fr", "ti-en", "tiv-en", "tiv-fr", "tiv-sv", "tl-de", "tl-en", "tl-es", "tl-pt",
    "tll-en", "tll-es", "tll-fi", "tll-fr", "tll-sv", "tn-en", "tn-es", "tn-fr", "tn-sv", "to-en",
    "to-es", "to-fr", "to-sv", "toi-en", "toi-es", "toi-fi", "toi-fr", "toi-sv", "tpi-en", "tpi-sv",
    "tr-ar", "tr-az", "tr-en", "tr-eo", "tr-es", "tr-fr", "tr-lt", "tr-sv", "tr-uk", "trk-en", "ts-en",
    "ts-es", "ts-fi", "ts-fr", "ts-sv", "tum-en", "tum-es", "tum-fr", "tum-sv", "tvl-en", "tvl-es",
    "tvl-fi", "tvl-fr", "tvl-sv", "tw-es", "tw-fi", "tw-fr", "tw-sv", "ty-es", "ty-fi", "ty-fr", "ty-sv",
    "tzo-es", "uk-bg", "uk-ca", "uk-cs", "uk-de", "uk-en", "uk-es", "uk-fi", "uk-fr", "uk-he", "uk-hu",
    "uk-it", "uk-nl", "uk-no", "uk-pl", "uk-pt", "uk-ru", "uk-sh", "uk-sl", "uk-sv", "uk-tr", "umb-en",
    "ur-en", "ve-en", "ve-es", "vi-de", "vi-en", "vi-eo", "vi-es", "vi-fr", "vi-it", "vi-ru", "vsl-es",
    "wa-en", "wal-en", "war-en", "war-es", "war-fi", "war-fr", "war-sv", "wls-en", "wls-fr", "wls-sv",
    "xh-en", "xh-es", "xh-fr", "xh-sv", "yap-en", "yap-fr", "yap-sv", "yo-en", "yo-es", "yo-fi", "yo-fr",
    "yo-sv", "zai-es", "zh-bg", "zh-de", "zh-en", "zh-fi", "zh-he", "zh-it", "zh-ms", "zh-nl", "zh-sv",
    "zh-uk", "zh-vi", "zne-es", "zne-fi", "zne-fr", "zne-sv"]

# The following languages are excluded since they reference multiple languages/language families
# (and are in particular not part of the ISO 639-3 standard)
# or are according to ISO-639- sign languages
# Before including those again, a correct mapping to language names needs to be determined
# (some are included in ISO 639-5 as families of languages)
_OPUS_MT_EXCLUDED_LANGUAGES = {'cpf',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-cpf
                               'bnt',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-bnt
                               'roa',  # https://huggingface.co/Helsinki-NLP/opus-mt-roa-en
                               'art',  # https://huggingface.co/Helsinki-NLP/opus-mt-art-en
                               'phi',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-phi
                               'pqe',  # https://huggingface.co/Helsinki-NLP/opus-mt-pqe-en
                               'map',  # https://metatext.io/models/Helsinki-NLP-opus-mt-en-map
                               'trk',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-trk
                               'pqw',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-pqw
                               'nic',  # https://huggingface.co/Helsinki-NLP/opus-mt-nic-en
                               'cel',  # https://huggingface.co/Helsinki-NLP/opus-mt-cel-en
                               'bat',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-bat
                               'poz',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-poz
                               'aav',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-aav
                               'sit',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-sit
                               'cau',  # https://huggingface.co/Helsinki-NLP/opus-mt-cau-en
                               'mkh',  # https://huggingface.co/Helsinki-NLP/opus-mt-mkh-en
                               'alv',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-alv
                               'dra',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-dra
                               'tut',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-tut
                               'ber',  # https://huggingface.co/Helsinki-NLP/opus-mt-ber-es
                               'aed',  # Argentine Sign Language (?)
                               'ase',  # American Sign Language (?)
                               'bzs',  # Brazilian Sign Language (?)
                               'csg',  # Chilean Sign Language (?)
                               'csn',  # Colombian Sign Language (?)
                               'fse',  # Finnish Sign Language (?)
                               'mfs',  # Mexican Sign Language (?)
                               'prl',  # Peruvian Sign Language (?)
                               'ssp',  # Spanish Sign Language (?)
                               'vsl',  # Venezuelan Sign Language (?)
                               }

# Filter the OpusMT pairs and transform to tuples
_OPUS_MT_LANGUAGE_TUPLES = [tuple(str.split(language_pair, "-")) for language_pair in _OPUS_MT_LANGUAGE_PAIRS
                            if not any(code in _OPUS_MT_EXCLUDED_LANGUAGES for code in language_pair)]

# The following codes do not follow the ISO standards/are outdated/prefer a 3 letter code over a 2 letter code.
# This mapping (Opus MT code -> ISO 639-1 or 639-3) encodes corrections of those codes.
_OPUS_MT_LANGUAGE_CODE_CORRECTIONS = {
    'jap': 'ja',
    'run': 'rn',
    'sal': 'shs',  # https://huggingface.co/Helsinki-NLP/opus-mt-sal-en
    'cus': 'som',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-cus
    'grk': 'el',  # https://huggingface.co/Helsinki-NLP/opus-mt-en-grk
    'ccs': 'ka',  # https://huggingface.co/Helsinki-NLP/opus-mt-ccs-en
    'sh': 'hbs',  # sh is outdated (cf. https://en.wikipedia.org/wiki/Serbo-Croatian#ISO_classification)
    'euq': 'eus'  # https://huggingface.co/Helsinki-NLP/opus-mt-euq-en
}

ISO639_TO_OPUS_MT_LANGUAGE_TUPLE_CORRECTIONS = {
    iso639_tuple: (source, target)
    for (source, target) in _OPUS_MT_LANGUAGE_TUPLES
    if (iso639_tuple :=
        (
            _OPUS_MT_LANGUAGE_CODE_CORRECTIONS.get(source, source),
            _OPUS_MT_LANGUAGE_CODE_CORRECTIONS.get(target, target)))
       != (source, target)
}

_OPUS_MT_TO_ISO639_LANGUAGE_TUPLE_CORRECTIONS = {v: k for k, v in ISO639_TO_OPUS_MT_LANGUAGE_TUPLE_CORRECTIONS.items()}

# Now, obtain the available language in ISO639
ISO639_LANGUAGE_TUPLES = [_OPUS_MT_TO_ISO639_LANGUAGE_TUPLE_CORRECTIONS.get(language_pair, language_pair)
                          for language_pair in _OPUS_MT_LANGUAGE_TUPLES]

# Finally, filter by empirical quality checks.
# In November 2022, some rudimentary quality checks were made on the models at this time
# selecting more or less acceptable quality results:
_QUALITY_CHECKED_ISO639_LANGUAGES = {'bg', 'ca', 'cs', 'da', 'de',
                                     'en', 'eo', 'es', 'et', 'eu',
                                     'fi', 'fr', 'ga', 'gl', 'he',
                                     'hr', 'hu', 'id', 'is', 'it',
                                     'lt', 'lv', 'mk', 'mt', 'nl',
                                     'pl', 'pt', 'ro', 'ru',
                                     'sk', 'sl', 'sq', 'sv', 'uk',
                                     'vi', 'zh'}

ISO639_LANGUAGE_TUPLES = [language_pair for language_pair in ISO639_LANGUAGE_TUPLES
                          if set(language_pair).issubset(_QUALITY_CHECKED_ISO639_LANGUAGES)]

ISO639_LANGUAGES = list(set(itertools.chain.from_iterable(ISO639_LANGUAGE_TUPLES)))