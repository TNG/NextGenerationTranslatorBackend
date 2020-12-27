import os
from _thread import start_new_thread

from flask import Flask, request, make_response
from flask_jsonpify import jsonify

from detector import Detector
from translator import Translator, TranslationError
from request_limitation import RequestLimiter, RequestLimitExceededException

app = Flask(__name__)

translator = Translator()
detector = Detector()
start_new_thread(translator.initialize_models, ())

max_number_of_concurrent_requests = int(os.getenv('MAX_NUMBER_OF_CONCURRENT_REQUESTS', 3))
request_limiter = RequestLimiter(max_number_of_concurrent_requests)


@app.route('/health', methods=['GET', 'POST'])
def health():
    return jsonify(healthy=True, serviceAvailable=translator.models_loaded)


@app.route('/translation', methods=['POST'])
def translate():
    with request_limiter.limited_requests():
        return jsonify(
            texts=[translator.translate(text, request.json['targetLanguage']) for text in request.json['texts']])


@app.route('/detection', methods=['POST'])
def detect():
    with request_limiter.limited_requests():
        return jsonify(text=detector.detect_language(request.json['text']))


@app.errorhandler(TranslationError)
def handle_translation_error(e):
    return jsonify(error=e.message), 500


@app.errorhandler(RequestLimitExceededException)
def handle_request_limit_exceeded(e):
    response = make_response(jsonify(error=e.message), 503)
    response.headers['Retry-After'] = '5'
    return response


if __name__ == "__main__":
    app.run(port=80, host='0.0.0.0', debug=True, threaded=True, processes=1)
