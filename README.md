
## Prerequisites

- Docker
- Python 3.8

## Run locally

It is highly recommended to create a venv.

Then call the following command:
```
pip install -r requirements.txt
```

To start the backend translation service, call the following command:
```
python src/main/translator_service.py
```

This will start the service at http://localhost:80.

## Build and run in Docker

To run the service in Docker, simply call the following command:
```
./docker-run.sh
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
