#!/bin/bash

echo "\033[0;32mRunning pre-push hook in bash ...\033[0m"

# Check if in the python environment
PYTHON_FILE=$(which python)
echo "Python file path: $PYTHON_FILE"

if [ -z "$PYTHON_FILE" ]; then
    echo "\033[0;31mError: Python not found in PATH\033[0m"
    exit 1
fi

PYTHON_ENV_FOLDER=$(dirname "$PYTHON_FILE")
PYTHON_ACTIVE_FILE="$PYTHON_ENV_FOLDER/activate"

if [ ! -f "$PYTHON_ACTIVE_FILE" ]; then
    echo "Python active file does not exist: $PYTHON_ACTIVE_FILE"
    echo "\033[0;31mError: Please activate the python environment first.\033[0m"
    exit 1
fi

# Construct the full path to the .azdev/env_config directory
AZDEV_ENV_CONFIG_FOLDER="$HOME/.azdev/env_config"
echo "AZDEV_ENV_CONFIG_FOLDER: $AZDEV_ENV_CONFIG_FOLDER"

# Check if the directory exists
if [ ! -d "$AZDEV_ENV_CONFIG_FOLDER" ]; then
    echo "AZDEV_ENV_CONFIG_FOLDER does not exist: $AZDEV_ENV_CONFIG_FOLDER"
    echo "\033[0;31mError: azdev environment is not completed, please run 'azdev setup' first.\033[0m"
    exit 1
fi

PYTHON_ENV_FOLDER=$(dirname "$PYTHON_ENV_FOLDER")

CONFIG_FILE="$AZDEV_ENV_CONFIG_FOLDER${PYTHON_ENV_FOLDER:2}/config"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "CONFIG_FILE does not exist: $CONFIG_FILE"
    echo "\033[0;31mError: azdev environment is not completed, please run 'azdev setup' first.\033[0m"
    exit 1
fi

echo "CONFIG_FILE: $CONFIG_FILE"


# Fetch upstream/main branch
echo "\033[0;32mFetching upstream/main branch...\033[0m"
git fetch upstream main
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: Failed to fetch upstream/main branch. Please run 'git remote add upstream https://github.com/Azure/azure-cli-extensions.git' first.\033[0m"
    exit 1
fi

# Run command azdev style
echo "\033[0;32mRunning azdev style...\033[0m"
azdev style elastic-san
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: azdev style check failed.\033[0m"
    exit 1
fi

# Run command azdev lint
echo "\033[0;32mRunning azdev lint...\033[0m"
azdev linter elastic-san
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: azdev lint check failed.\033[0m"
    exit 1
fi

# Run command azdev test
echo "\033[0;32mRunning azdev test...\033[0m"
azdev test elastic-san2
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: azdev test check failed.\033[0m"
    exit 1
fi

exit 0

