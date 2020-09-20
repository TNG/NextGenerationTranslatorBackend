from langdetect import detect


class Detector:

    @staticmethod
    def detect_language(text):
        return detect(text)
