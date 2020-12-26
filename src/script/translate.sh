#!/usr/bin/env bash

TEXT_TO_TRANSLATE=$1
TARGET_LANGUAGE=$2
curl -s -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' \
      --data "{ \"texts\": [\"${TEXT_TO_TRANSLATE}\"], \"targetLanguage\": \"${TARGET_LANGUAGE}\" }" http://localhost:80/translation | \
  jq ".texts[0]"