from flask import Flask, request
from flask_jsonpify import jsonify

app = Flask(__name__)


@app.route('/translate', methods=['POST'])
def index():
    print(request.json['texts'])
    return jsonify(translations=["foo", "bar"])


if __name__ == "__main__":
    app.run(port=80, host='0.0.0.0', debug=True)
