#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import logging
import requests
import shlex
import subprocess
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def auto_merge(headers, number):
    # curl -X PUT https://api.github.com/repos/OWNER/REPO/pulls/PULL_NUMBER/merge
    merge_url = f'https://api.github.com/repos/Azure/azure-cli-extensions/pulls/{number}/merge'
    logger.debug(merge_url)
    # merge_method: merge, squash or rebase
    body = {
        'merge_method': 'rebase'
    }
    try:
        r = requests.put(merge_url, json=body, headers=headers)
    except requests.RequestException as e:
        raise e
    if r.status_code != 200:
        logger.debug(r)
        logger.debug(r.text)
        sys.exit(1)


def main():
    with open('/tmp/token.txt') as f:
        token = f.readline().replace("\n", "")
    headers = {'Authorization': 'token %s' % token}
    with open('/tmp/create_pr.json') as f:
        ref = f.read()
    number = json.loads(ref)['number']
    auto_merge(headers, number)


if __name__ == '__main__':
    main()