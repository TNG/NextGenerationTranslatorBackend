#!/usr/bin/env bash

docker build -t translator-backend .
echo "Executing"
docker run -it --volume=/Users/endrest/.cache/torch:/root/.cache/torch -p80:80 translator-backend