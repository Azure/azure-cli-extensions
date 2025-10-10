#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the AzureDevOps Releases pipeline. Not
# intended to be ran manually:
# https://msdata.visualstudio.com/Tina/_release?_a=releases&view=mine&definitionId=111
#
# Script Pull Request to `Azure/azure-cli-extensions` github repo for releasing
# the arcdata azure-cli-extension on the behalf of `arcdatabot` gh machine-user.
#
# Envs:
#
# ${ARCDATABOTGHSECRET} populated from key-vault and token is valid for 1 year
# https://github.com/settings/tokens?type=beta
#
# Usage:
#
# $ azure-cli-extensions-pr.sh
#
# Result:
#
# A new PR in upstream `Azure/azure-cli-extensions` with the latest arcdata
# `index.json` whl entry on branch `arcdatabot/ci/arcdata-${CLI_VERSION}`
#

# !!! Important !!!
# Do not $echo or `set -vx` to avoid sending sensitive information to stdout
set -e

if [[ -z "${ARCDATABOTGHSECRET}" ]]; then
  echo "ARCDATABOTGHSECRET is undefined, this ENV is required to execute!"
  exit 1
fi

CLI_VERSION={{CLI_VERSION}} # pipeline will substitute version value
COMMIT_MSG="chore(arcdata): version bump to ${CLI_VERSION}"
LABEL=arcdata
BRANCH=arcdatabot/ci/arcdata-${CLI_VERSION}
HEAD=arcdatabot:${BRANCH}
REMOTE_REPOSITORY=Azure/azure-cli-extensions
UPSTREAM_REPOSITORY=github.com/Azure/azure-cli-extensions.git
FORKED_REPOSITORY=github.com/arcdatabot/azure-cli-extensions.git

# -- Always sync latest upstream:main with forked arcdatabot:main --
git clone https://${FORKED_REPOSITORY} && cd "$(basename "$_" .git)"
git remote add upstream https://${UPSTREAM_REPOSITORY}
git fetch upstream
git checkout main
git rebase upstream/main  # local arcdatabot:main is now sync with upstream

echo "!!! Creating branch ${BRANCH} !!!"
git branch ${BRANCH}
git checkout ${BRANCH}
git merge main --no-ff

# -- update index.json from main with new arcdata latest entry from CI --
# CWD --> `./azure-cli-extensions` from git clone, copy ADO index.json closer
cp ../_azure-cli-extension*/extension-index/index.json ../
ARCDATA_INDEX_FILE=../index.json
python -c "import json;i = json.load(open('./src/index.json', 'r'));i['extensions']['arcdata'].insert(0, json.load(open('${ARCDATA_INDEX_FILE}', 'r'))['extensions']['arcdata'][0]);open('./src/index.json', 'w').write(json.dumps(i, indent=4, sort_keys=True));"
git status

# -- add/commit/push-remote `index.json` change onto ${BRANCH} --
git add -A
git commit -m "${COMMIT_MSG}"
git push -f https://${ARCDATABOTGHSECRET}@${FORKED_REPOSITORY} # push to remote

# -- Download and install gh-cli for easy automated PR's --
GH_VERSION=`curl "https://api.github.com/epos/cli/cli/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/' | cut -c2-`
curl -sSL https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz -o gh_${GH_VERSION}_linux_amd64.tar.gz
tar xvf gh_${GH_VERSION}_linux_amd64.tar.gz
gh=../gh_${GH_VERSION}_linux_amd64/bin/gh
${gh} version

# -- Authenticate for PR's via gh-cli --
echo "${ARCDATABOTGHSECRET}" > ../.githubtoken
${gh} auth login --with-token < ../.githubtoken
rm ../.githubtoken

# -- PR check, if no PR create one --
NO_PR_OPEN=`${gh} pr status`
if [[ "$NO_PR_OPEN" == *"You have no open pull requests"* ]]; then
  echo "No open pull requests, creating a new PR to ${REMOTE_REPOSITORY}"
  ${gh} repo set-default ${REMOTE_REPOSITORY}
  ${gh} pr create --label ${LABEL} --base main --head ${HEAD} --title "${COMMIT_MSG}" --body "${COMMIT_MSG}"
fi
