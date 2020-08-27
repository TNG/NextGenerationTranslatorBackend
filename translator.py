from flask import Flask, request
from flask_jsonpify import jsonify
import torch
import os

app = Flask(__name__)

torch.hub.set_dir(f"{os.path.dirname(os.path.realpath(__file__))}/cache")


# de2en = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.de-en',
#                       checkpoint_file='model1.pt:model2.pt:model3.pt:model4.pt',
#                       tokenizer='moses', bpe='fastbpe')

@app.route('/health', methods=['GET', 'POST'])
def health():
    print("Health called")
    return jsonify(healthy=True)


@app.route('/', methods=['POST'])
def index():
    print("Translate called")
    return jsonify(translation=translate(request.json['text']))


def translate(text):
    return text + " 1"
#    return de2en.translate(text)


if __name__ == "__main__":
    app.run(port=3000, host='0.0.0.0', debug=False)
