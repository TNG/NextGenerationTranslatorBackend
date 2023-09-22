#!/usr/bin/env bash
_DIR=$(pwd)
MAIN_DIR="$(cd "$(dirname $(dirname $(dirname "${BASH_SOURCE[0]}")))" >/dev/null 2>&1 && pwd)"
cd "${MAIN_DIR}"
docker build -t translator-backend .
echo "Executing"
# you may want to mount a caching directory, eg. via --volume=~/.cache/torch:/root/.cache/torch
cd $_DIR
docker run -it -p80:80 "$@" translator-backend
