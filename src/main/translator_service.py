import logging
from _thread import start_new_thread

from flask import Flask, request, make_response, jsonify

from constants import TranslatorMode
from request_limitation import RequestLimiter, RequestLimitExceededException
from settings import settings
from translator import Translator, UnexpectedTranslationError, UnsupportedTranslationInputException, \
    TranslatorNotReadyException, TranslatorProxy
from translator_proxy_client import ForwardedTranslatorProxyError
from utils.logger import configure_logger

_logger = logging.getLogger(__name__)

app = Flask(__name__)
configure_logger()
if settings.mode == TranslatorMode.proxy:
    _logger.info("Starting translator in proxy mode.")
    translator = TranslatorProxy()
else:
    _logger.info("Starting translator in client mode.")
    translator = Translator()

start_new_thread(translator.initialize_models, (), {"preload": settings.preload_models})

if settings.rate_limit > 0:
    _logger.info(f"Rate limiting enabled with limit of {settings.rate_limit}")
    request_limiter = RequestLimiter(settings.rate_limit)
    request_limit_context = request_limiter.limited_requests
else:
    _logger.info(f"Rate limiting disabled")
    request_limit_context = RequestLimiter.no_limit_context


class MissingArgumentError(Exception):
    pass


@app.route('/health', methods=['GET', 'POST'])
def health():
    return jsonify(healthy=True, serviceAvailable=translator.models_loaded)


@app.route('/translation', methods=['POST'])
def translate():
    with request_limit_context():
        return jsonify(
            texts=[translator.translate(text,
                                        request.json['targetLanguage'],
                                        source_language=request.json.get('sourceLanguage')
                                        )
                   for text in request.json['texts']])


@app.route('/detection', methods=['POST'])
def detect():
    with request_limit_context():
        return jsonify(
            text=translator.detect_language(request.json['text']))


@app.route('/languages', methods=['POST'])
def list_connected_languages():
    with request_limit_context():
        if 'baseLanguage' not in request.json:
            raise MissingArgumentError("Missing parameter 'baseLanguage'")
        return jsonify(languages=translator.list_available_languages(request.json['baseLanguage']))


@app.route('/languages', methods=['GET'])
def list_all_languages():
    with request_limit_context():
        return jsonify(languages=translator.list_available_languages("en"))

@app.route('/models', methods=['GET'])
def list_provided_models():
    with request_limit_context():
        return jsonify(models=[m.model_name for m in translator.list_models()])

@app.errorhandler(UnexpectedTranslationError)
def handle_translation_error(e):
    _logger.error(f"Handling UnexpectedTranslationError '{e}'; returning 500")
    return jsonify(error=e.message), 500


@app.errorhandler(UnsupportedTranslationInputException)
def handle_unsupported_translation_input_exception(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(MissingArgumentError)
def handle_missing_argument_error(e: MissingArgumentError):
    return make_response(jsonify(error=str(e)), 400)


@app.errorhandler(RequestLimitExceededException)
def handle_request_limit_exceeded(e):
    _logger.debug(f"Handling RequestLimitExceededException '{e}'; return 503")
    response = make_response(jsonify(error=e.message), 503)
    response.headers['Retry-After'] = '5'
    return response


@app.errorhandler(TranslatorNotReadyException)
def handle_translator_not_ready(e):
    _logger.debug(f"Handling TranslatorNotReadyException '{e}'; return 503")
    response = make_response(jsonify(error=e.message), 503)
    response.headers['Retry-After'] = '5'
    return response

@app.errorhandler(ForwardedTranslatorProxyError)
def handle_forwarded_exception(e: ForwardedTranslatorProxyError):
    _logger.debug(f"Handling forwarded ForwardedTranslatorProxyError '{e}'; return {e.status_code}")
    response = make_response(jsonify(error=e.error), e.status_code)
    response.headers['Retry-After'] = '5'
    return response

if __name__ == "__main__":
    app.run(port=80, host='0.0.0.0', debug=True, threaded=True, processes=1)
