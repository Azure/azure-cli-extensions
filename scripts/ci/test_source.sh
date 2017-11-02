#!/usr/bin/env bash
set -e

if compgen -G "src/*/azext_*/tests" > /dev/null; then
    for d in src/*/azext_*/tests;
        do echo "Running tests for $d";
        python -m unittest discover -v $d;
    done;
fi
