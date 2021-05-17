#!/usr/bin/env bash

# clear
cat /dev/null > env.list

# tenant, sub, client
echo "TENANT_ID=$TENANT_ID" >> env.list
echo "AZCLI_ALT_SUBSCRIPTION_ID=$AZCLI_ALT_SUBSCRIPTION_ID" >> env.list
echo "AZCLI_ALT_CLIENT_ID=$AZCLI_ALT_CLIENT_ID" >> env.list

# azdev env
echo "AZURE_CLI_TEST_DEV_SP_NAME=$AZCLI_ALT_CLIENT_ID" >> env.list
echo "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION=$TEST_LOCATION" >> env.list

# predefined variables 
echo "BUILD_REASON=$BUILD_REASON" >> env.list
echo "SYSTEM_PULLREQUEST_TARGETBRANCH=$SYSTEM_PULLREQUEST_TARGETBRANCH" >> env.list

# test
echo "COVERAGE=$COVERAGE" >> env.list
echo "TEST_MODE=$TEST_MODE" >> env.list
echo "PARALLELISM=$PARALLELISM" >> env.list
echo "TEST_CASES=$TEST_CASES" >> env.list
echo "EXT_TEST_FILTER=$EXT_TEST_FILTER" >> env.list
echo "EXT_TEST_COVERAGE=$EXT_TEST_COVERAGE" >> env.list

# repo
echo "CLI_REPO=$CLI_REPO" >> env.list
echo "CLI_BRANCH=$CLI_BRANCH" >> env.list
echo "MANUAL_EXT=$MANUAL_EXT" >> env.list
echo "EXT_REPO=$EXT_REPO" >> env.list
echo "EXT_BRANCH=$EXT_BRANCH" >> env.list

# image
echo "IMAGE_PREFIX=$IMAGE_PREFIX" >> env.list
echo "IMAGE_NAME=$IMAGE_NAME" >> env.list
echo "IMAGE_TAG=$IMAGE_TAG" >> env.list

# misc
echo "PYTHON_VERSION=$PYTHON_VERSION" >> env.list
