#!/bin/bash

set -eux
pwd

# transcribe environment variables
./transcribe_env.sh

# start container
docker run -t -d --env-file ./env.list -v $PWD:/opt --name "azcli-aks-live-test-container" azcli-aks-live-test-image:latest
