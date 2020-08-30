from flask import Flask, request
from flask_jsonpify import jsonify
from translator import Translator, TranslationError
from _thread import start_new_thread

app = Flask(__name__)
translator = Translator()
start_new_thread(translator.initialize_model, ())


@app.route('/health', methods=['GET', 'POST'])
def health():
    return jsonify(healthy=True)


@app.route('/translate', methods=['POST'])
def index():
    return jsonify(translation=translator.translate(request.json['text']))


@app.errorhandler(TranslationError)
def handle_translation_error(e):
    return jsonify(error=e.message), 500


if __name__ == "__main__":
    app.run(port=80, host='0.0.0.0', debug=True, threaded=True)
