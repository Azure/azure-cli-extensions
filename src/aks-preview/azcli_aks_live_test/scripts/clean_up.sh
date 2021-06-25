#!/usr/bin/env bash

# login
az login --service-principal -u $AZCLI_ALT_CLIENT_ID -p $AZCLI_ALT_CLIENT_SECRET -t $TENANT_ID
az account set -s $AZCLI_ALT_SUBSCRIPTION_ID
az account show

# list the details of resource groups whose names start with "clitest"
az group list --query "([].name)[?starts_with(@, 'clitest')]" -o tsv | xargs -i az group show -n {}

# delete all resource groups whose names start with "clitest"
# az group list --query "([].name)[?starts_with(@, 'clitest')]" -o tsv | xargs -i az group delete --no-wait -y -n {}
