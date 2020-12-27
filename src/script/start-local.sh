#!/usr/bin/env bash


MAIN_DIR="$(cd "$(dirname $(dirname $(dirname "${BASH_SOURCE[0]}")))" >/dev/null 2>&1 && pwd)"
cd "${MAIN_DIR}/src/main"

# Workers are limited to 1 so we do not have to load the model multiple times
# 5 threads are in use since concurrent translation requests are limited to 3 parallel request, so health requests still pass through
gunicorn --bind 0.0.0.0:80 wsgi:app  -w 1 --threads 5