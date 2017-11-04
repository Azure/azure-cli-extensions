#!/usr/bin/env bash
set -ex

# Install CLI & CLI testsdk
echo "Installing azure-cli-testsdk and azure-cli..."
# TODO Update the git commit when we need a new version of azure-cli-testsdk
pip install "git+https://github.com/Azure/azure-cli@68460748e47f20cba462686c9fd20d2c720cf98c#egg=azure-cli-testsdk&subdirectory=src/azure-cli-testsdk" -q
echo "Installed."


_AZURE_EXTENSION_DIR="$AZURE_EXTENSION_DIR"

for d in src/*/azext_*/tests;
    do echo "Running tests for $d";
    if [ -d $d ]; then
        export AZURE_EXTENSION_DIR=$(mktemp -d);
        pip install --upgrade --target $AZURE_EXTENSION_DIR/ext $d/../..;
        python -m unittest discover -v $d;
        rm -rf $AZURE_EXTENSION_DIR;
    else
        echo "Skipped $d as not a directory."
    fi
done;

if ! [ -z "${_AZURE_EXTENSION_DIR+_}" ] ; then
    AZURE_EXTENSION_DIR="$_AZURE_EXTENSION_DIR"
    export AZURE_EXTENSION_DIR
    unset _AZURE_EXTENSION_DIR
fi

echo "OK. Completed tests."
