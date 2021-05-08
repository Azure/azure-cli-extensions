#!/usr/bin/env bash

set -eux
pwd

# transcribe environment variables into file 'env.list'
source ./transcribe_env.sh

# take the first arg as container name
container_name=${1:-"azcli-aks-live-test-container"}

# start container in backgroud with tty
# mount current directory ($(Agent.BuildDirectory)/s) to /opt in container
# set working directory as /opt in container
# pass secrects as environment variables directly (instead of storing in env.list)
# pass other environment variables with env.list
docker run -t -d -v $PWD:/opt -w /opt \
-e AZCLI_ALT_CLIENT_SECRET=$MAPPED_AZCLI_ALT_CLIENT_SECRET \
-e AZURE_CLI_TEST_DEV_SP_PASSWORD=$MAPPED_AZCLI_ALT_CLIENT_SECRET \
--env-file ./env.list \
--name $container_name $IMAGE_NAME:$IMAGE_TAG

# remove env.list
rm ./env.list
