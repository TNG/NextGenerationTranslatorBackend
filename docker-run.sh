#!/usr/bin/env bash

docker run -it --volume=${HOME}/.cache/torch:/root/.cache/torch -p80:80 translator