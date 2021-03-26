import asyncio
import functools
import logging
import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Dict

from tenacity import retry, before_sleep_log, wait_fixed, retry_if_exception_type

from detector import Detector
from schemas import TranslatorApiResponseHealthSchema, TranslatorApiTranslationSchema, TranslatorApiDetectionSchema, TranslatorApiResponseModelsSchema
from translator_models import models, TranslatorModel
from translator_models.translator_model import TranslatorModelName
from translator_proxy_client import TranslatorProxyClient, FailedTranslatorProxyRequest
from utils.translation_graph import TranslationGraph
from settings import settings

_logger = logging.getLogger(__name__)


class UnexpectedTranslationError(Exception):
    def __init__(self, message):
        self.message = message


class UnsupportedTranslationInputException(Exception):
    pass


class UnsupportedLanguageException(UnsupportedTranslationInputException):
    def __init__(self, language):
        super().__init__(f"Language '{language}' is not supported.")


class UnsupportedLanguagePairException(UnsupportedTranslationInputException):
    def __init__(self, source_language, target_language):
        super().__init__(f"Translation '{source_language}' to '{target_language}' not supported.")


class TranslatorNotReadyException(Exception):
    """Raised when the translator models have not yet been loaded or determined."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _require_model_loaded(func):
    @functools.wraps(func)
    def _func(self, *args, **kwargs):
        if not self.models_loaded:
            _logger.debug(f"Call to {func.__name__} raises TranslatorNotReadyException since models not loaded.")
            raise TranslatorNotReadyException("Models have not been loaded yet.")
        return func(self, *args, **kwargs)

    return _func


def _require_models_determined(func):
    @functools.wraps(func)
    def _func(self, *args, **kwargs):
        if not self.models_determined:
            _logger.debug(f"Call to {func.__name__} raises TranslatorNotReadyException since models not determined yet.")
            raise TranslatorNotReadyException("Models have not been determined yet.")
        return func(self, *args, **kwargs)

    return _func


def _catch_proxy_error(func):
    @functools.wraps(func)
    def _func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FailedTranslatorProxyRequest as e:
            _logger.error(f"Call to client {e.client} failed with {e}")
            raise UnexpectedTranslationError("There was an unexpected error with the translator proxy client.")
    return _func


class _TranslatorBase(ABC):

    def __init__(self):

        self._translation_graph_cache = None

    @property
    @abstractmethod
    def models_loaded(self) -> bool:
        pass

    @property
    @abstractmethod
    def models_determined(self) -> bool:
        pass

    @abstractmethod
    def initialize_models(self, preload: bool = False) -> None:
        pass

    @property
    def _translation_graph(self) -> TranslationGraph:
        if not self._translation_graph_cache:
            self._translation_graph_cache = TranslationGraph(self.list_models())
        return self._translation_graph_cache

    def __determine_translation_steps(self, source_language, target_language):
        try:
            translation_path = self._translation_graph.find_optimal_translation_path(source_language, target_language)
            _logger.debug(self._translation_graph.format_translation_path(translation_path, source_language, target_language))
            return translation_path
        except Exception:
            raise UnsupportedLanguagePairException(source_language, target_language)

    def __process_input_languages(self, text: str, source_language: str, target_language: str) -> Tuple[str, str]:
        if not source_language:
            source_language = self.detect_language(text)
        for language in (source_language, target_language):
            if language not in self._translation_graph:
                raise UnsupportedLanguageException(language)
        return source_language, target_language

    @_require_model_loaded
    def translate(self, text, target_language, source_language=None):
        source_language, target_language = self.__process_input_languages(text, source_language, target_language)
        translation_steps = self.__determine_translation_steps(source_language, target_language)
        for language_pair, translation_model_class in translation_steps:
            text = self._direct_translate_with_model(translation_model_class, text, language_pair)
        return text

    @abstractmethod
    def _direct_translate_with_model(self, model_class: Type[TranslatorModel], text: str, language_pair: Tuple[str, str]) -> str:
        """ Template method that directly translates from source to target language with the given model.

        Direct meaning no further Dijkstra-Path-Finding involved."""
        pass

    def list_available_languages(self, base_language: str) -> List[str]:
        """ Lists all available language, i.e. languages that be translated into as well as from.

        :param base_language: One language that must be contained in the list (as possibly the models could
         yield two (or more) sets of languages with no connection in between).
        :return:
        """
        return list(self._translation_graph.get_strongly_connected_component(base_language))

    @abstractmethod
    def detect_language(self, text: str) -> str:
        pass

    @abstractmethod
    def list_models(self) -> List[Type[TranslatorModel]]:
        pass


class Translator(_TranslatorBase):

    def __init__(self):
        self._model_selection = [m for m in models if m.model_name in settings.models]
        self._models = None
        self._models_loaded = False
        self._detector = Detector()
        super().__init__()

    @property
    def models_loaded(self) -> bool:
        return self._models_loaded

    @property
    def models_determined(self) -> bool:
        """ If available model classes have been determined.

         Normal translator client directly determines this directly from settings. """
        return True

    def initialize_models(self, preload: bool = False):

        _logger.info(f"Starting initialization of models {[m.model_name for m in self._model_selection]}.")
        self._models = {model.model_name: model() for model in self._model_selection}

        if preload:
            for model in self._models.values():
                model.preload()

        self._models_loaded = True
        _logger.info(f"Models {list(self._models)} have been loaded")

    @_require_model_loaded
    def _direct_translate_with_model(self, model_class: Type[TranslatorModel], text: str, language_pair: Tuple[str, str]):
        return self._models[model_class.model_name].translate(text, language_pair[0], language_pair[1])

    def detect_language(self, text: str) -> str:
        return self._detector.detect_language(text)

    def list_models(self) -> List[Type[TranslatorModel]]:
        return self._model_selection


class TranslatorProxy(_TranslatorBase):

    def __init__(self):
        super().__init__()
        self._models_determined = False
        self._clients = settings.translator_clients
        self._client_models = {}
        self._model_to_clients: Dict[TranslatorModelName, List[str]] = {}

    async def _determine_client_models(self):
        client_model_responses: List[TranslatorApiResponseModelsSchema] = await asyncio.gather(*[TranslatorProxyClient(client).get_models() for client in self._clients])
        for client, model_response in zip(self._clients, client_model_responses):
            assert model_response.models, f"Client {client} did not return any models."
            _logger.debug(f"Received models {model_response.models} from client {client}")
            self._client_models[client] = [m for m in models if m.model_name in model_response.models]


    @retry(wait=wait_fixed(30),
           before_sleep=before_sleep_log(_logger, logging.WARNING),
           retry=retry_if_exception_type((FailedTranslatorProxyRequest, AssertionError)))
    def initialize_models(self, preload: bool = False) -> None:
        _logger.info("Starting translator proxy initialization.")
        asyncio.run(self._determine_client_models())
        for client, client_models in self._client_models.items():
            for model in client_models:
                self._model_to_clients.setdefault(model.model_name, []).append(client)
        _logger.info(f"Detected client models: { {client: [m.model_name for m in _models] for client, _models in self._client_models.items()} }")
        self._models_determined = True

    async def _get_client_health_status(self) -> List[TranslatorApiResponseHealthSchema]:
        return await asyncio.gather(*[TranslatorProxyClient(client).get_health() for client in self._clients])

    @property
    @_catch_proxy_error
    def models_loaded(self) -> bool:
        if not self._models_determined:
            return False
        health_status: List[TranslatorApiResponseHealthSchema] = asyncio.run(self._get_client_health_status())
        _logger.debug(f"Client health status: {health_status}")
        return all(h.serviceAvailable for h in health_status)

    @property
    def models_determined(self) -> bool:
        return self._models_determined

    @_catch_proxy_error
    def _direct_translate_with_model(self, model_class: Type[TranslatorModel], text: str, language_pair: Tuple[str, str]) -> str:
        client = random.choice(self._model_to_clients[model_class.model_name])
        _logger.debug(f"Using client {client} for model {model_class.model_name} to translate {language_pair}")
        translation = asyncio.run(TranslatorProxyClient(client).post_translation(
            TranslatorApiTranslationSchema(texts=[text],
                                           sourceLanguage=language_pair[0],
                                           targetLanguage=language_pair[1])))
        return translation.texts[0]

    @_require_models_determined
    @_catch_proxy_error
    def detect_language(self, text: str) -> str:
        client = random.choice(self._clients)
        _logger.debug(f"Language detection call to {client}")
        detection = asyncio.run(TranslatorProxyClient(client).post_detection(
            TranslatorApiDetectionSchema(text=text)))
        return detection.text

    @_require_models_determined
    def list_models(self) -> List[Type[TranslatorModel]]:
        return [m for m in models if m.model_name in self._model_to_clients]
