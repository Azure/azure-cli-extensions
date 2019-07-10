#!/usr/bin/env bash
set -ex

# check for index updates
modified_extensions=$(python ./scripts/ci/index_changes.py)
echo "Found the following modified extension entries:"
echo "$modified_extensions"

# run linter on each modified extension entry
while read line; do
    if [ -z "$line" ]; then
        continue
    fi
    part_array=($line)
    ext=${part_array[0]}
    source=${part_array[1]}
    echo
    echo "New index entries detected for extension:" $ext
    echo "Adding latest entry from source:" $source
    set +e
    azdev extension add $ext
    if [ $? != 0 ]; then
        continue
    fi
    set -e
    echo "Load all commands"
    az self-test
    echo "Running linter"
    azdev linter $ext
    azdev extension remove $ext
    echo $ext "extension has been removed."
done <<< "$modified_extensions"

echo "OK. Completed Verification of Modified Extensions."
