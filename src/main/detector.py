from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


class LanguageDetectionError(Exception):
    def __init__(self):
        super().__init__("Failed to detect language from text.")


class Detector:

    @staticmethod
    def detect_language(text):
        try:
            return detect(text)
        except LangDetectException:
            return LanguageDetectionError()
