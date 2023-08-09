#!/bin/bash

FLAGS=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -d) export PROJECT_DIR="$2"; shift 2;;
    *) FLAGS="$FLAGS $1"; shift;;
  esac
done

export FLAGS

#docker system prune -a # only do this for testing to ensure clean build everytime
docker compose run --rm terraform
#docker compose build