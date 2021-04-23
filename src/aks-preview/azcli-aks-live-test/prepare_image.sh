#!/bin/bash

set -eux
pwd

# prepare docker image
if [[ $BUILD_IMAGE == true ]]; then
    echo "Building test image '$IMAGE_NAME:$IMAGE_TAG'..."
    docker build -t $IMAGE_NAME:$IMAGE_TAG -f ./Dockerfile .
else
    echo "Pulling test image from '$IMAGE_PREFIX/$IMAGE_NAME:$IMAGE_TAG'..."
    if ! docker pull $IMAGE_PREFIX/$IMAGE_NAME:$IMAGE_TAG; then
        echo "Failed to pull image, start local build..."
        docker build -t $IMAGE_NAME:$IMAGE_TAG -f ./Dockerfile .
    fi
fi
