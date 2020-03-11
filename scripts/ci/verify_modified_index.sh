#!/usr/bin/env bash
set -e


log_section_title()
{
    printf "\n\n"
    echo   "********************************************************************************************"
    echo   "*   ${1}"
    echo   "********************************************************************************************"
    printf "\n"
}


# Install CLI
log_section_title "Cloning azure-cli ..."

git clone --single-branch -b dev https://github.com/Azure/azure-cli.git ../azure-cli


# Install azdev
log_section_title "Installing azure-cli-dev-tools ..."

pip install azdev
azdev setup -c ../azure-cli

echo "Installed."


log_section_title "Running az --version"

az --version


# Check for index updates
log_section_title "Checking modified extensions ..."

modified_extensions=$(python ./scripts/ci/index_changes.py)

if [ -z "${modified_extensions}" ]; then
    echo "No modified extension needs to be verify."
else
    echo "Found the following modified extension entries:"

    while read -r line
    do
        arr=(${line})
        printf "[ %-30s ]  %-s\n" "${arr[0]}" "${arr[1]}"
    done <<< "${modified_extensions}"
fi


# Run linter on each modified extension entry
while read -r line; do
    if [ -z "${line}" ]; then
        continue
    fi

    part_array=($line)
    ext=${part_array[0]}
    source=${part_array[1]}

    log_section_title "Verifying new entries detected for extension: [ ${ext} ]"

    echo "Adding latest extension from: [ ${source} ]"

    az extension add -s "${source}" -y

    # TODO migrate to public azdev
#    echo "Load all commands..."
#    azdev verify load-all

    echo "Running linter on extension:  [ ${ext} ] ..."
    azdev linter --include-whl-extensions "${ext}"

    az extension remove -n "${ext}"

    echo "extension: [ ${ext} ] has been removed."
done <<< "$modified_extensions"


log_section_title "OK. Verification of Modified Extensions Completed."
