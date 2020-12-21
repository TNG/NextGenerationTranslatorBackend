from _thread import start_new_thread

from flask import Flask, request
from flask_jsonpify import jsonify

from detector import Detector
from translator import Translator, TranslationError

app = Flask(__name__)
translator = Translator()

print("hello")
translator.initialize_models()
detector = Detector()
print("done")
#start_new_thread(translator.initialize_models, ())



@app.route('/health', methods=['GET', 'POST'])
def health():
    return jsonify(healthy=True)


@app.route('/translation', methods=['POST'])
def translate():
    return jsonify(texts=[translator.translate(text, request.json['targetLanguage']) for text in request.json['texts']])


@app.route('/detection', methods=['POST'])
def detect():
    return jsonify(text=detector.detect_language(request.json['text']))


@app.errorhandler(TranslationError)
def handle_translation_error(e):
    return jsonify(error=e.message), 500


if __name__ == "__main__":
    app.run(port=80, host='0.0.0.0', debug=True)
