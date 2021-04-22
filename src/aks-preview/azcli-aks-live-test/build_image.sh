#!/bin/bash

set -eux
pwd

# build docker image
docker build -t azcli-aks-live-test-image:latest -f ./Dockerfile .
