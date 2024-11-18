#!/bin/bash

printf "\033[0;32mRunning pre-push hook in bash ...\033[0m\n"

# run azdev_active script
SCRIPT_PATH="$(dirname "$0")/azdev_active.sh"
. "$SCRIPT_PATH"
if [ $? -ne 0 ]; then
    exit 1
fi

# Check if azure-cli is installed in editable mode
EDITABLE_LOCATION=$(pip show azure-cli 2>/dev/null | grep "Editable project location" | cut -d" " -f4)
if [ ! -z "$EDITABLE_LOCATION" ]; then
    AZURE_CLI_FOLDER=$(dirname $(dirname "$EDITABLE_LOCATION"))
fi

# Get extension repo paths and join them with spaces
EXTENSIONS=$(azdev extension repo list -o tsv | tr '\n' ' ')

# Verify if current repo is in extension repo list
CURRENT_REPO=$(pwd)
if [ -z "$(echo "$EXTENSIONS" | grep "$CURRENT_REPO")" ]; then
    printf "\033[0;31mThe current repo is not added as an extension repo. Please run the following command to add it:\033[0m\n"
    printf "\033[0;31m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
    printf "\033[0;31mazdev extension repo add %s\033[0m\n" "$CURRENT_REPO"
    printf "\033[0;31m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
    exit 1
fi

# Fetch upstream/main branch
printf "\033[0;32mFetching upstream/main branch...\033[0m\n"
git fetch upstream main
if [ $? -ne 0 ]; then
    printf "\033[0;31mError: Failed to fetch upstream/main branch. Please run the following command to add the upstream remote:\033[0m\n"
    printf "\033[0;31m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
    printf "\033[0;31mgit remote add upstream https://github.com/Azure/azure-cli-extensions.git\033[0m\n"
    printf "\033[0;31m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
    exit 1
fi

if [ ! -z "$AZURE_CLI_FOLDER" ]; then
    printf "\033[0;32mFetching %s upstream/dev branch...\033[0m\n" "$AZURE_CLI_FOLDER"
    git -C "$AZURE_CLI_FOLDER" fetch upstream dev
    if [ $? -ne 0 ]; then
        printf "\033[0;31mError: Failed to fetch %s upstream/dev branch. Please run the following command to add the upstream remote:\033[0m\n" "$AZURE_CLI_FOLDER"
        printf "\033[0;31m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
        printf "\033[0;31mgit -C %s remote add upstream https://github.com/Azure/azure-cli.git\033[0m\n" "$AZURE_CLI_FOLDER"
        printf "\033[0;31m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
        exit 1
    fi

    # Check if current branch needs rebasing
    CLI_MERGE_BASE=$(git -C "$AZURE_CLI_FOLDER" merge-base HEAD upstream/dev)
    CLI_UPSTREAM_HEAD=$(git -C "$AZURE_CLI_FOLDER" rev-parse upstream/dev)
    if [ "$CLI_MERGE_BASE" != "$CLI_UPSTREAM_HEAD" ]; then
        printf "\n"
        printf "\033[0;33mYour %s repo code is not up to date with upstream/dev. Please run the following commands to rebase and setup:\033[0m\n" "$AZURE_CLI_FOLDER"
        printf "\033[0;33m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
        printf "\033[0;33mgit -C %s rebase upstream/dev\033[0m\n" "$AZURE_CLI_FOLDER"
        if [ ! -z "$EXTENSIONS" ]; then
            printf "\033[0;33mazdev setup -c %s -r %s\033[0m\n" "$AZURE_CLI_FOLDER" "$EXTENSIONS"
        else
            printf "\033[0;33mazdev setup -c %s\033[0m\n" "$AZURE_CLI_FOLDER"
        fi
        printf "\033[0;33m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
        printf "\n"
        printf "\033[0;33mYou have 5 seconds to stop the push (Ctrl+C)...\033[0m\n"

        # Using a C-style for loop instead of seq
        i=5
        while [ $i -ge 1 ]; do
            printf "\r\033[K\033[1;33mTime remaining: %d seconds...\033[0m" $i
            sleep 1
            i=$((i-1))
        done
        printf "\rContinuing without rebase...\n"
    fi
fi

# Check the merge base
MERGE_BASE=$(git merge-base HEAD upstream/main)

# get the current branch name
currentBranch=$(git branch --show-current)

# Detect changed extensions
changedFiles=$(git diff --name-only $MERGE_BASE $currentBranch)
changedExtensions=$(echo "$changedFiles" | grep "^src/" | cut -d'/' -f2 | sort -u)

if [ ! -z "$changedExtensions" ]; then
    printf "\033[0;32mChanged extensions: %s\033[0m\n" "$(echo $changedExtensions | tr '\n' ', ')"

    # Add each changed extension using azdev extension add
    for extension in $changedExtensions; do
        printf "Adding extension: %s\n" "$extension"
        azdev extension add "$extension"
        if [ $? -ne 0 ]; then
            printf "\033[0;31mError: Failed to add extension %s\033[0m\n" "$extension"
            exit 1
        fi
    done
fi

# Run command azdev lint
printf "\033[0;32mRunning azdev lint...\033[0m\n"
azdev linter --min-severity medium --repo ./ --src $currentBranch --tgt $MERGE_BASE 
if [ $? -ne 0 ]; then
    printf "\033[0;31mError: azdev lint check failed.\033[0m\n"
    exit 1
fi

# Run command azdev style
printf "\033[0;32mRunning azdev style...\033[0m\n"
azdev style --repo ./ --src $currentBranch --tgt $MERGE_BASE 
if [ $? -ne 0 ]; then
    error_msg=$(azdev style --repo ./ --src $currentBranch --tgt $MERGE_BASE 2>&1)
    if echo "$error_msg" | grep -q "No modules"; then
        printf "\033[0;32mPre-push hook passed.\033[0m\n"
        exit 0
    fi
    printf "\033[0;31mError: azdev style check failed.\033[0m\n"
    exit 1
fi

# Run command azdev test
printf "\033[0;32mRunning azdev test...\033[0m\n"
azdev test --repo ./ --src $currentBranch --tgt $MERGE_BASE --discover --no-exitfirst --xml-path test_results.xml 2>/dev/null
if [ $? -ne 0 ]; then
    printf "\033[0;31mError: azdev test check failed. You can check the test logs in the 'test_results.xml' file.\033[0m\n"
    exit 1
else
    # remove the test_results.xml file
    rm -f test_results.xml
fi

printf "\033[0;32mPre-push hook passed.\033[0m\n"

if [ ! -z "$AZURE_CLI_FOLDER" ]; then
    if [ "$CLI_MERGE_BASE" != "$CLI_UPSTREAM_HEAD" ]; then
        printf "\n"
        printf "\033[0;33mYour %s repo code is not up to date with upstream/dev. Please run the following commands to rebase and setup:\033[0m\n" "$AZURE_CLI_FOLDER"
        printf "\033[0;33m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
        printf "\033[0;33mgit -C %s rebase upstream/dev\033[0m\n" "$AZURE_CLI_FOLDER"
        if [ ! -z "$EXTENSIONS" ]; then
            printf "\033[0;33mazdev setup -c %s -r %s\033[0m\n" "$AZURE_CLI_FOLDER" "$EXTENSIONS"
        else
            printf "\033[0;33mazdev setup -c %s\033[0m\n" "$AZURE_CLI_FOLDER"
        fi
        printf "\033[0;33m+++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m\n"
    fi
fi
exit 0
