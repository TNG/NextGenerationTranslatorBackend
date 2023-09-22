# Next Generation Translator Backend

This repository provides a backend translation implementation that you can consume via REST requests. The translation is
based on Facebook's very good [WMT-19 models](https://github.com/pytorch/fairseq/blob/master/examples/wmt19/README.md)
for a few languages, as well as the open source [Opus-MT](https://github.com/Helsinki-NLP/Opus-MT) models for many more
languages, but less accurate translation.

# Technicalities

## Prerequisites

- Docker
- Python 3.8

## Run locally

### Using Poetry
If you have poetry (e.g. via `pip install poetry`)
install a virtual env via
```
poetry install
```
and then open a shell with activated env via `poetry shell`
or run any  command via `poetry run <CMD>`.

### Alternative

For an existing virtual environment, install dependencies via:

```
pip install -r requirements.txt
```

Note: In order to generate a requirements.txt from Poetry,
run 
```bash
poetry export --with opusmt --without-hashes > requirements.txt 
```

For local development outside Docker, you need to start a local Redis instance:

```
src/script/start-redis.sh
```

To start the backend translation service, call the following command:

```
src/script/start-local.sh
```

To just download the models, run the following command (this is also done implicitly when starting the application):

```
python src/main/init_translation.py
```

This will start the service at http://localhost:80.

## Build and run in Docker

To run the service in Docker, simply call the following command:

```
src/script/docker-run.sh --env-file local.env
```

This will build a Docker image and run it locally. It will also start the service at http://localhost:80.


```
src/script/docker-run.sh --env-file local.env
```
you spin up an instance with only a mocked backend for testing.
## Configuration of Models

See the  `TranslatorSettings` class in `src/main/settings.py`
for detailed list of all settings which can be set up via environment
variables.

The most imprtant environment variable is `TRANSLATOR_MODELS`. Via 
```
TRANSLATOR_MODELS=["mock"]
```
you can set up the list of models to be spinned up.

Current available models are (if you do not change setup):
- nlb-200 (Note: for non-commercial use only, cf. NLB-200 license)
- opus-mt
- wmt-19
- mock (just for testing)


## Testing the application

The python code will download a pre-trained neural network (~25 GB of disk space is needed). After the download and once
the model is loaded, you can use the translator REST API.

### Detect whether the model is ready

POST to /health endpoint:

```
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' http://${DOMAIN}:${PORT}/health
```

This command will return the following JSON:

```
{"healthy": true, "serviceAvailable": true}
```

The following information can be read from this endpoint:

- "healthy" is always set to true once the service is running
- "serviceAvailable" is set to true once the translation service is ready to translate (i.e. the models are loaded)

The config is tailored in a way that health requests may still pass through even if translation requests end in a 503 (
Service unavailable) status code

### Detect language

To detect in which language a specific text is written, POST to the /detection endpoint

```
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
     --data '{ "text": "Das ist ein Test" }' http://${DOMAIN}:${PORT}/detection
```

The result will look like this:

```
{"text": "de"}
```

This means that the language has detected your text to be written in German ('de' locale).

### Translate text

To translate texts, POST to the /translation endpoint. You can omit the source language and let the backend detect it by
itself:

```
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
  --data '{ "texts": ["Hallo"], "targetLanguage": "en" }' http://${DOMAIN}:${PORT}/translation
```

Or you can define the source language as well:

```
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
  --data '{ "texts": ["burro"], "targetLanguage": "en", "sourceLanguage": "es" }' http://${DOMAIN}:${PORT}/translation
```

The result will look like this:

```
{"texts": ["Hello "]}
{"texts": ["donkey"]}
```

The resulting array will contain the translated texts in the order in which they were given as inputs.

If the service is not yet started, status code 500 and the error message will be returned.

You can also use a script shortcut script:

```
src/script/translate.sh 'Text to be translated' 'de'
```

### Supported languages

The `/languages` endpoint gives information on what languages can be translated into what. Calling it with GET returns
all supported languages (which are assumed to be connected to english).

```
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
  --data '{ "baseLanguage": "fr" }' http://${DOMAIN}:${PORT}/languages

curl http://${DOMAIN}:${PORT}/languages
```

Whatever baseLanguage you use, the reply is most likely the same, as there is probably no model that translates from a
language into another one, where both of these languages are not connected to any other supported language.

## Run (unit) tests
In the root directory in an environment with suitable Python interpreter (e.g. activated virtual environment), run
```
pytest src/test
```

## Run (load) test

To test the functionality, but also to get an impression of what it is like to test with multiple requests at once, use
the following command AFTER starting the service locally or in a container:

```
pytest -s --capture=no src/test/test_load.py
```

This will fire 100 requests with random texts from resources/test_texts.csv against the service and verify the
correctness of the results. The request will all be fired randomly within 10 seconds.

To manipulate the number of requests or timer settings, you can change the following ENV variabes:

- TEST_HOST to change the host from localhost and port from 80 (default: http://localhost:80)
- NUMBER_OF_REQUESTS to change the number of requests (default: 100)
- REQUEST_TIMESPAN to change the interval (in seconds) in which requests are sent (default: 10)
- BEARER_TOKEN to use in an environment where a bearer token is needed (like AWS)

# License and Contribution

This repository is published under the Apache License 2.0, see the [LICENSE](LICENSE) for details.

If you want to contribute, please follow the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).
# temp-test

