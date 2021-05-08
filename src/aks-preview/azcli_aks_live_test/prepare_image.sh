#!/bin/bash

set -eux
pwd

# prepare docker image
echo "Pulling test image from '$IMAGE_PREFIX/$IMAGE_NAME:$IMAGE_TAG'..."
docker pull $IMAGE_PREFIX/$IMAGE_NAME:$IMAGE_TAG
docker tag $IMAGE_PREFIX/$IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$IMAGE_TAG
