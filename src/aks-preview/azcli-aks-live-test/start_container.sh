#!/bin/bash

set -eux
pwd

# transcribe environment variables
./transcribe_env.sh

# start container in backgroud with env.list as environment varialbes
# mount current directory ($(Agent.BuildDirectory)/s) to /opt in container
# set working directory as /opt in container
docker run -t -d --env-file ./env.list -v $PWD:/opt -w /opt --name "azcli-aks-live-test-container" $IMAGE_NAME:$IMAGE_TAG
