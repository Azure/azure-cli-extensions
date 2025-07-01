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
EXTENSIONS=$(azdev extension repo list -o tsv | tr '\n' ' ' | sed 's/ $//')

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
    printf "\033[0;36mInitial CLI_MERGE_BASE: %s\033[0m\n" "$CLI_MERGE_BASE"

    if [ "$CLI_MERGE_BASE" != "$CLI_UPSTREAM_HEAD" ]; then
        printf "\n"
        printf "\033[1;33mYour branch is not up to date with upstream/dev.\033[0m\n"
        printf "\033[1;33mWould you like to automatically rebase and setup? [Y/n]\033[0m\n"

        read -r INPUT < /dev/tty
        if [ "$INPUT" = "Y" ] || [ "$INPUT" = "y" ]; then
            printf "\033[0;32mRebasing with upstream/dev...\033[0m\n"
            git -C "$AZURE_CLI_FOLDER" rebase upstream/dev
            if [ $? -ne 0 ]; then
                printf "\033[0;31mRebase failed. Please resolve conflicts and try again.\033[0m\n"
                exit 1
            fi
            printf "\033[0;32mRebase completed successfully.\033[0m\n"
            CLI_MERGE_BASE=$(git -C "$AZURE_CLI_FOLDER" merge-base HEAD upstream/dev)
            printf "\033[0;36mUpdated CLI_MERGE_BASE: %s\033[0m\n" "$CLI_MERGE_BASE"

            printf "\033[0;32mRunning azdev setup...\033[0m\n"
            if [ -n "$EXTENSIONS" ]; then
                azdev setup -c "$AZURE_CLI_FOLDER" -r "$EXTENSIONS"
            else
                azdev setup -c "$AZURE_CLI_FOLDER"
            fi
            if [ $? -ne 0 ]; then
                printf "\033[0;31mazdev setup failed. Please check your environment.\033[0m\n"
                exit 1
            fi
            printf "\033[0;32mSetup completed successfully.\033[0m\n"
        elif [ "$INPUT" = "N" ] || [ "$INPUT" = "n" ]; then
            printf "\r\033[K\033[1;33mSkipping rebase and setup. Continue push...\033[0m\n"
        else
            printf "\033[0;31mInvalid input. Aborting push...\033[0m\n"
            exit 1
        fi
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
exit 0
