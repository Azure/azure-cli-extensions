#!/usr/bin/env bash
set -e

for d in src/*/azext_*/tests;
    do echo "Running tests for $d";
    python -m unittest discover -v $d;
done;
