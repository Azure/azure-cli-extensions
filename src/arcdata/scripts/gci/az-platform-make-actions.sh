#!/bin/bash -e

#
# Description:
#
# The purpose of this file is to:
# - Run supported CLI actions in a docker container.
# - Offload some of the scripting logic  for the CLI targets
# - This script is only ever invoked from platform/Makefile and should never
#   be called directly.
#
# Prerequisites:
#
# - Run target: /projects/azure-cli-extension install
#
# Supported ACTIONS:
#
# - create-arc-dc
# - create-arc-config
# - set-arc-config
# - delete-arc-dc
# - copy
# - dump
#
# Usage:
#
# $ az-make-actions.sh <ACTION> <ARG-1> <ARG-2> ...

ACTION=$1  # CLI action to perform
DOCKER_ARGS="--rm --name $ACTION"
: "${CWD:=`cd $(dirname $0); pwd`}"

AZEXT_IMAGE = arcdatadev.azurecr.io/arcdata-dev/base/arcdata-base-test:ubuntu2004-08bc6a0fe8cc12cd350a3c9552f4273030f75a9cc3defd4683a391bced07f0d7


source .dev.env
echo "--============="
pwd
ls -la
echo "--============="
echo ${CWD}
echo ${AZEXT_IMAGE}
echo "-e AZDATA_USERNAME=${AZDATA_USERNAME}"
echo "-e DATA_CONTROLLER_NAME=${DATA_CONTROLLER_NAME}"
echo "-e SUBSCRIPTION=${SUBSCRIPTION}"
echo "-e RESOURCE_GROUP=${RESOURCE_GROUP}"
echo "-e LOCATION=${LOCATION}"
echo "-e SPN_AUTHORITY=${SPN_AUTHORITY}"
echo "-e SPN_TENANT_ID=${SPN_TENANT_ID}"
echo "-e SPN_CLIENT_ID=${SPN_CLIENT_ID}"
echo "-e WORKSPACE_ID=${WORKSPACE_ID}"
echo "============="


function run () {
    command=$*

    echo ${command}
    echo ${DOCKER_ARGS}
    echo ${AZEXT_IMAGE}

    docker run ${DOCKER_ARGS} \
        -v "${HOME}/.kube:/root/.kube" \
        -v "${CWD}/output/custom:/mnt/output" \
        -v "${CWD}/patch-config:/mnt/patch-config" \
        -e AZDATA_USERNAME=${AZDATA_USERNAME} \
        -e AZDATA_PASSWORD=${AZDATA_PASSWORD} \
        -e DATA_CONTROLLER_NAME=${DATA_CONTROLLER_NAME} \
        -e SUBSCRIPTION=${SUBSCRIPTION} \
        -e RESOURCE_GROUP=${RESOURCE_GROUP} \
        -e LOCATION=${LOCATION} \
        -e SPN_AUTHORITY=${SPN_AUTHORITY} \
        -e SPN_TENANT_ID=${SPN_TENANT_ID} \
        -e SPN_CLIENT_ID=${SPN_CLIENT_ID} \
        -e WORKSPACE_ID=${WORKSPACE_ID} \
        ${AZEXT_IMAGE} /bin/bash -c "mkdir -p ./tmp/logs && ${command}"
}

# -- run cli command action --
#
case ${ACTION} in

    create-arc-dc)
      CONFIG_PROFILE="$2"
      CLUSTER_NAME="$3"

      if [[ $# -ne 3 ]]
      then
        echo "Usage: $0 $1 CONFIG_PROFILE CLUSTER_NAME"
        exit 1
      fi

      COMMIT_HASH=$(git rev-parse --short HEAD)

      ARGS="--path mnt/${CONFIG_PROFILE} \
            --namespace ${CLUSTER_NAME} \
            --name ${DATA_CONTROLLER_NAME}-${BUILD_DOCKER_IMAGE_TAG}-${COMMIT_HASH} \
            --azure-subscription ${SUBSCRIPTION} \
            --resource-group ${RESOURCE_GROUP} \
            --location ${LOCATION} \
            --connectivity-mode ${CONNECTIVITY_MODE}"

      run az arc dc create ${ARGS}
      ;;
    delete-arc-dc)
      CLUSTER_NAME="$2"

      if [[ $# -ne 2 ]]
      then
        echo "Usage: $0 $1 CLUSTER_NAME"
        exit 1
      fi

      COMMIT_HASH=$(git rev-parse --short HEAD)
      ARGS="--name ${DATA_CONTROLLER_NAME}-${BUILD_DOCKER_IMAGE_TAG}-${COMMIT_HASH} --namespace ${CLUSTER_NAME} --force --yes"
      run az arc dc delete ${ARGS}
      ;;

    create-arc-config)
      CONFIG_PROFILE="$2"
      PROFILE_TYPE="$3"

      if [[ $# -ne 3 ]]
      then
        echo "Usage: $0 $1 CONFIG_PROFILE PROFILE_TYPE"
        exit 1
      fi

      if [[ -f ${CONFIG_PROFILE} ]] ; then
        rm ${CONFIG_PROFILE}
      fi

      run az arc dc config init --source ${PROFILE_TYPE} --path mnt/${CONFIG_PROFILE} --force
      ;;
    set-arc-config)
      CONFIG_PROFILE="$2"
      PATCH_FILE="$3"

      if [[ $# -ne 3 ]]
      then
        echo "Usage: $0 $1 CONFIG_PROFILE PATCH_FILE"
        exit 1
      fi

      run az arc dc config patch --path mnt/${CONFIG_PROFILE} --patch-file mnt/${PATCH_FILE}
      ;;




    copy)
      CLUSTER_NAME="$2"
      DEBUG_OUTPUT_DIRECTORY="$3"
      COPY_LOGS_TIMEOUT="$4"
      DOCKER_ARGS="--name $ACTION"

      if [[ $# -ne 4 ]]
      then
        echo "Usage: $0 $1 CLUSTER_NAME DEBUG_OUTPUT_DIRECTORY COPY_LOGS_TIMEOUT"
        exit 1
      fi

	  { # 'try'
        run az arc debug copy-logs --namespace ${CLUSTER_NAME} --target-folder tmp/logs --verbose --timeout ${COPY_LOGS_TIMEOUT}
        CONTAINER_ID=$(docker ps --filter="name=$ACTION" -q -a | xargs)
        docker cp ${CONTAINER_ID}:/tmp/logs ${DEBUG_OUTPUT_DIRECTORY}
      } || { # 'catch'
        echo "Failure copying log files from container to host."
      }

      docker rm ${CONTAINER_ID} # finally
      ;;
    dump)
      CLUSTER_NAME="$2"
      OUTPUT_DIRECTORY="$3"
      CONTAINER_NAME="$4"
      DOCKER_ARGS="--name $ACTION"

      if [[ $# -ne 4 ]]
      then
        echo "Usage: $0 $1 CLUSTER_NAME OUTPUT_DIRECTORY CONTAINER_NAME"
        exit 1
      fi

      { # 'try'
        run az arc debug dump --namespace ${CLUSTER_NAME} --verbose --target-folder tmp/logs --container ${CONTAINER_NAME}
        CONTAINER_ID=$(docker ps --filter="name=$ACTION" -q -a | xargs)
        docker cp ${CONTAINER_ID}:/tmp/logs ${OUTPUT_DIRECTORY}/dumps
      } || { # 'catch'
        echo "Failure coping dump files from container to host."
      }

      docker rm ${CONTAINER_ID} # finally
      ;;
    *) echo "Invalid option: $1"
     ;;
esac
