#!/bin/bash

echo "\033[0;32mRunning pre-push hook in bash ...\033[0m"

<<<<<<< HEAD
# run azdev_active script
$scriptPath = Join-Path $PSScriptRoot "azdev_active.sh"
. $scriptPath
if [ $? -ne 0 ]; then
=======
# Check if in the python environment
PYTHON_FILE=$(which python)
echo "Python file path: $PYTHON_FILE"

if [ -z "$PYTHON_FILE" ]; then
    echo "\033[0;31mError: Please activate the python environment first.\033[0m"
>>>>>>> 95083cf1a (fix error message)
    exit 1
fi

# Fetch upstream/main branch
echo "\033[0;32mFetching upstream/main branch...\033[0m"
git fetch upstream main
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: Failed to fetch upstream/main branch. Please run 'git remote add upstream https://github.com/Azure/azure-cli-extensions.git' first.\033[0m"
    exit 1
fi

# get the current branch name
currentBranch=$(git branch --show-current)

# Run command azdev lint
echo "\033[0;32mRunning azdev lint...\033[0m"
azdev linter --repo ./ --tgt $currentBranch --src upstream/main
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: azdev lint check failed.\033[0m"
    exit 1
fi

# Run command azdev style
echo "\033[0;32mRunning azdev style...\033[0m"
azdev style --repo ./ --tgt $currentBranch --src upstream/main
if [ $? -ne 0 ]; then
    error_msg=$(azdev style --repo ./ --tgt $currentBranch --src upstream/main 2>&1)
    if [[ $error_msg == *"No modules"* ]]; then
        exit 0
    fi
    echo "\033[0;31mError: azdev style check failed.\033[0m"
    exit 1
fi

# Run command azdev test
echo "\033[0;32mRunning azdev test...\033[0m"
azdev test --repo ./ --tgt $currentBranch --src upstream/main
if [ $? -ne 0 ]; then
    echo "\033[0;31mError: azdev test check failed.\033[0m"
    exit 1
fi

echo "\033[0;32mPre-push hook passed.\033[0m"
exit 0

