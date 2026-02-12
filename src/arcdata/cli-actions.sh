#!/bin/bash -e

#
# The purpose of this file is to:
# 1.  Offload some of the scripting in platform/Makefile for the CLI so the
#     Makefile does not get bloated/verbose.
# 2. Insert some logic into the workflow as to only create a virtual environment
#    once that holds all the CLI build dependancies.
#
# The reason for (2) above is that we create only once (until cleaned) a virtual
# environment of the CLI, this saves some build cycles given how subprojects
# behave such that we are not constantly creating/installing/removing.
#

# -- manage virtual environment --
#

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
export AZURE_EXTENSION_DIR=$SCRIPT_PATH

if [ $USE_VENV ]; then
    $AZURE_EXTENSION_DIR/scripts/generate-role-template.sh
    VENV_DIRECTORY=${VENV_DIRECTORY:-"./env"}

    if [ ! -d "$VENV_DIRECTORY" ]; then
        echo "No CLI virtual environment created yet. creating..."
        python3 -m venv $VENV_DIRECTORY
        . $VENV_DIRECTORY/bin/activate
        python3 -m pip install wheel setuptools azure-cli
        python3 -m pip install -e $AZURE_EXTENSION_DIR/arcdata
    else
      . $VENV_DIRECTORY/bin/activate
    fi
fi

run() {
  echo $*
  $*
}

# -- run cli command action --
#
case "$1" in
    create-arc-dc)
      CONFIG_PROFILE="$2"
      CLUSTER_NAME="$3"
      MONITORING_CERT_DIR="$4"

      if [ $# -ne 4 ]
      then
        echo "Usage: $0 $1 CONFIG_PROFILE CLUSTER_NAME MONITORING_CERT_DIR"
        exit 1
      fi

      COMMIT_HASH=$(git rev-parse --short HEAD)
      AUTHOR_TAG=${AUTHOR_TAG:-$(git config user.email | cut -d@ -f1)}

      ARGS="--path $CONFIG_PROFILE --k8s-namespace ${CLUSTER_NAME} \
            --name ${DATA_CONTROLLER_NAME}-${AUTHOR_TAG}-${COMMIT_HASH} \
            --subscription ${SUBSCRIPTION} \
            --resource-group ${RESOURCE_GROUP} \
            --location ${LOCATION} \
            --connectivity-mode ${CONNECTIVITY_MODE} \
            --logs-ui-private-key-file ${MONITORING_CERT_DIR}/logsui-key.pem \
            --logs-ui-public-key-file ${MONITORING_CERT_DIR}/logsui-cert.pem \
            --metrics-ui-private-key-file ${MONITORING_CERT_DIR}/metricsui-key.pem \
            --metrics-ui-public-key-file ${MONITORING_CERT_DIR}/metricsui-cert.pem \
            --use-k8s"

      run az arcdata dc create $ARGS
      ;;
    create-arc-config)
      CONFIG_PROFILE="$2"
      PROFILE_TYPE="$3"

      if [ $# -ne 3 ]
      then
        echo "Usage: $0 $1 CONFIG_PROFILE PROFILE_TYPE"
        exit 1
      fi

      if [ -f $CONFIG_PROFILE ] ; then
        rm $CONFIG_PROFILE
      fi

      run az arcdata dc config init --source $PROFILE_TYPE --path $CONFIG_PROFILE --force
      ;;
    set-arc-config)
      CONFIG_PROFILE="$2"
      PATCH_FILE="$3"

      if [ $# -ne 3 ]
      then
        echo "Usage: $0 $1 CONFIG_PROFILE PATCH_FILE"
        exit 1
      fi

      run az arcdata dc config patch --path $CONFIG_PROFILE --patch-file $PATCH_FILE
      ;;
    delete-arc-dc)
      CLUSTER_NAME="$2"

      if [ $# -ne 2 ]
      then
        echo "Usage: $0 $1 CLUSTER_NAME"
        exit 1
      fi

      COMMIT_HASH=$(git rev-parse --short HEAD)
      AUTHOR_TAG=${AUTHOR_TAG:-$(git config user.email | cut -d@ -f1)}

      ARGS="--name $DATA_CONTROLLER_NAME-$AUTHOR_TAG-$COMMIT_HASH --k8s-namespace $CLUSTER_NAME --force --yes --use-k8s"
      run az arcdata dc delete $ARGS
      ;;
    copy)
      CLUSTER_NAME="$2"
      DEBUG_OUTPUT_DIRECTORY="$3"
      COPY_LOGS_TIMEOUT="$4"

      if [ $# -ne 4 ]
      then
        echo "Usage: $0 $1 CLUSTER_NAME DEBUG_OUTPUT_DIRECTORY COPY_LOGS_TIMEOUT"
        exit 1
      fi

      run az arcdata dc debug copy-logs --k8s-namespace $CLUSTER_NAME --target-folder $DEBUG_OUTPUT_DIRECTORY --verbose --timeout $COPY_LOGS_TIMEOUT --use-k8s
      ;;
    *) echo "Invalid option: $1"
     ;;
esac

# -- deactivate venv --
#
if [ $USE_VENV ]; then
    deactivate
fi
