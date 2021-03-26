from typing import List, Optional

from pydantic import BaseModel


class TranslatorApiResponseModelsSchema(BaseModel):
    models: List[str]

class TranslatorApiResponseHealthSchema(BaseModel):
    healthy: bool
    serviceAvailable: bool


class TranslatorApiResponseDetectionSchema(BaseModel):
    text: str

class TranslatorApiDetectionSchema(BaseModel):
    text: str


class TranslatorApiResponseLanguagesSchema(BaseModel):
    languages: List[str]

class TranslatorApiResponseTranslationSchema(BaseModel):
    texts: List[str]

class TranslatorApiTranslationSchema(BaseModel):
    texts: List[str]
    targetLanguage: str
    sourceLanguage: Optional[str]
