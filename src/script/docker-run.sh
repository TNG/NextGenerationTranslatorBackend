#!/usr/bin/env bash

MAIN_DIR="$(cd "$(dirname $(dirname $(dirname "${BASH_SOURCE[0]}")))" >/dev/null 2>&1 && pwd)"
cd "${MAIN_DIR}"

docker build -t translator-backend .
echo "Executing"
docker run -it --volume=/Users/endrest/.cache/torch:/root/.cache/torch -p80:80 translator-backend