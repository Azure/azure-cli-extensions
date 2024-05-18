#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${AZCLI_ALT_SUBSCRIPTION_ID}" ]] && (echo "AZCLI_ALT_SUBSCRIPTION_ID is empty"; exit 1)
[[ -z "${IDENTITY_RESOURCE_ID}" ]] && (echo "IDENTITY_RESOURCE_ID is empty"; exit 1)
[[ -z "${LOOKBACK}" ]] && (echo "LOOKBACK is empty"; exit 1)
[[ -z "${PREFIX}" ]] && (echo "PREFIX is empty"; exit 1)

# login
az login --identity -u "${IDENTITY_RESOURCE_ID}"
az account set -s "${AZCLI_ALT_SUBSCRIPTION_ID}"
az account show

# get lookback date
cond_date=$(date -u -d "${LOOKBACK} hours ago" '+%Y-%m-%dT%H:%M:%SZ')

# list matched result
az group list --query "[? @.tags.date < '${cond_date}'] | [? starts_with(@.name, '${PREFIX}')]"
echo "Length:" $(az group list --query "[? @.tags.date < '${cond_date}'] | [? starts_with(@.name, '${PREFIX}')] | length(@)")

# delete
az group list --query "[? @.tags.date < '${cond_date}'] | [? starts_with(@.name, '${PREFIX}')].name" -o tsv | xargs -i az group delete --no-wait -y -n {}
