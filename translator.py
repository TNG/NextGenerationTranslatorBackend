from flask import Flask, request
from flask_jsonpify import jsonify
import torch
from _thread import start_new_thread

app = Flask(__name__)
de2en = None


@app.route('/health', methods=['GET', 'POST'])
def health():
    return jsonify(healthy=True)


@app.route('/', methods=['POST'])
def index():
    return jsonify(translation=translate(request.json['text']))


def translate(text):
    if de2en is not None:
        return de2en.translate(text)
    else:
        return text + " 1"


def load_model():
    global de2en
    de2en = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.de-en',
                           checkpoint_file='model1.pt:model2.pt:model3.pt:model4.pt',
                           tokenizer='moses', bpe='fastbpe')
    print("Model loaded")
    print(de2en.translate("Alles funktioniert einwandfrei"))


if __name__ == "__main__":
    start_new_thread(load_model, ())
    app.run(port=80, host='0.0.0.0', debug=False, threaded=True)
