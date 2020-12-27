
## Prerequisites

- Docker
- Python 3.8

## Run locally

It is highly recommended to create a venv.

Then call the following command:
```
pip install -r requirements.txt
```

You need to start a local Redis instance:
```
src/script/start-redis.sh
```

To start the backend translation service, call the following command:
```
src/script/start-local.sh
```

This will start the service at http://localhost:80.

## Build and run in Docker

To run the service in Docker, simply call the following command:
```
src/script/docker-run.sh
```

This will build a Docker image and run it locally.
It will also start the service at http://localhost:80.

## Testing the application

The python code will download a pre-trained neural network (~25 GB of disk space is needed). 
After the download and once the model is loaded, you can use the translator REST API.

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

The config is tailored in a way that health requests may still pass through even if translation requests end in 
a 503 (Service unavailable) status code

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

To translate texts to German or English, POST to the /detection endpoint

```
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
  --data '{ "texts": ["Hallo"], "targetLanguage": "en" }' http://${DOMAIN}:${PORT}/translation
```

The result will look like this:

```
{"texts": ["Hello "]}
```

The resulting array will contain the translated texts in the order in which they were given as inputs.

If the service is not yet started, status code 500 and the error message will be returned.

You can also use a script shortcut script:

```
src/script/translate.sh 'Text to be translated' 'de'
```

## Run (load) test

To test the functionality, but also to get an impression of what it is like to test with multiple requests at once,
use the following command AFTER starting the service locally or in a container:

```
pytest -s --capture=no
```

This will fire 100 requests with random texts from resources/test_texts.csv against the service
and verify the correctness of the results. The request will all be fired randomly within 10 seconds.

To manipulate the number of requests or timer settings, you can change the following ENV variabes:
- TEST_HOST to change the host from localhost and port from 80 (default: http://localhost:80)
- NUMBER_OF_REQUESTS to change the number of requests (default: 100)
- REQUEST_TIMESPAN to change the interval (in seconds) in which requests are sent (default: 10)
- BEARER_TOKEN to use in an environment where a bearer token is needed (like AWS)
