#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
# take the first arg as container name
container_name=${1:-"azcli-aks-live-test-container"}

# remove container
container_id=$(docker ps -aqf "name=^${container_name}")
if [[ -n "${container_id}" ]]; then
    docker rm -f ${container_id} || true
else
    echo "Could not find container ${container_name}"
fi
