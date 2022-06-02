#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import subprocess
import shlex


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

pwd = subprocess.run(['pwd'], stdout=subprocess.PIPE).stdout.decode("UTF-8")
logger.debug(pwd)


# try:
#     resp = subprocess.run(['pwd'], check=True, stdout=subprocess.PIPE)
# except subprocess.CalledProcessError:
#     error_flag = True
# number = json.loads(resp.stdout.decode("UTF-8"))['number']
#     return number

# git config
cmd = shlex.split("az keyvault secret show --vault-name kv-azuresdk --name azclibot-pat --query value -otsv")
GITHUB_TOKEN = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("UTF-8")
cmd = shlex.split('git config --global user.email "AzPyCLI@microsoft.com"')
logger.debug(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("UTF-8"))
cmd = shlex.split('git config --global user.name "Azure CLI Team"')
logger.debug(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("UTF-8"))
cmd = shlex.split('git remote add azclibot https://azclibot:${GITHUB_TOKEN}@github.com/azclibot/azure-cli-extensions.git')
logger.debug(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("UTF-8"))
cmd = shlex.split('git status')
logger.debug(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("UTF-8"))

#
# if [[ ! -f "upgrade_extensions.txt" ]]; then
#     echo "no extension upgrade, no need to create PR (1)."
#     exit 0
# fi
#
# if [[ -z "$(git status --short src/index.json)" ]]; then
#     echo "no extension upgrade, no need to create PR (2)."
#     exit 0
# fi
#
# #######################
# # prepare
# #######################
#
# upgraded_extensions=""
# for extension in $(cat upgrade_extensions.txt)
# do
#     ext=`echo $extension | sed -e 's/\n//'`
#     upgraded_extensions+="[ $ext ] "
# done
#
# extension_commit_id="$(Build.SourceVersion)"
#
# commit_url="https://github.com/Azure/azure-cli-extensions/commit/${extension_commit_id}"
# commit_msg_title="[Release] Update index.json for extension $upgraded_extensions"
# commit_msg_body="Triggered by Azure CLI Extensions Release Pipeline - ADO_BUILD_ID=$(Build.BuildId)"
# commit_msg="${commit_msg_title}\n\n ${commit_msg_body}\n\nLast commit against main: ${commit_url}"
#
#
# #######################
# # save branch
# #######################
#
# temp_branch="release-$(date +%Y%m%d-%H%M%S)"
# git checkout -b "$temp_branch"
# git add src/index.json
# git commit -m "${commit_msg_title}" -m "${commit_msg_body}" -m "Last commit: ${commit_url}"
# git push -u azclibot "$temp_branch"
#
#
# #######################
# # ceate PR
# #######################
#
# pr_title="$commit_msg_title"
# pr_body="$commit_msg"
# pr_head="azclibot:${temp_branch}"
#
# curl \
# -H "Authorization: token ${GITHUB_TOKEN}" \
# -d "{\"title\": \"${pr_title}\", \"body\": \"${pr_body}\", \"head\": \"${pr_head}\", \"base\": \"main\"}" \
# https://api.github.com/repos/Azure/azure-cli-extensions/pulls
