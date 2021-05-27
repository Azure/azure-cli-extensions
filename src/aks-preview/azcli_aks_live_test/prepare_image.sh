#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${IMAGE_PREFIX}" ]] && (echo "IMAGE_PREFIX is empty"; exit 1)
[[ -z "${IMAGE_NAME}" ]] && (echo "IMAGE_NAME is empty"; exit 1)
[[ -z "${IMAGE_TAG}" ]] && (echo "IMAGE_TAG is empty"; exit 1)

# dir
pwd
ls -alh

# prepare docker image
echo "Pulling test image from '${IMAGE_PREFIX}/${IMAGE_NAME}:${IMAGE_TAG}'..."
docker pull ${IMAGE_PREFIX}/${IMAGE_NAME}:${IMAGE_TAG}
docker tag ${IMAGE_PREFIX}/${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:${IMAGE_TAG}
