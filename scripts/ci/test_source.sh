#!/usr/bin/env bash
set -e

# Install CLI & CLI testsdk
echo "Installing azure-cli-testsdk and azure-cli..."
pip install "git+https://github.com/Azure/azure-cli@dev#egg=azure-cli-testsdk&subdirectory=src/azure-cli-testsdk" -q
echo "Installed."

for d in src/*/azext_*/tests;
    do echo "Running tests for $d";
    if [ -d $d ]; then
        python -m unittest discover -v $d;
    else
        echo "Skipped $d as not a directory."
    fi
done;
