#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
from util import diff_code

from subprocess import run

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def azdev_style_check(diff_ref):
    cmd = ['azdev', 'style']
    for tname, ext_path in diff_ref:
        ext_name = ext_path.split('/')[-1]
        cmd += [ext_name]
        logger.info(f'cmd: {cmd}')
        out = run(cmd, capture_output=True, text=True)
        if out.returncode:
            raise RuntimeError(f"{cmd} failed")


def main():
    logger.info("Start azdev style test ...\n")
    diff_ref = diff_code('main', 'HEAD')
    azdev_style_check(diff_ref)


if __name__ == '__main__':
    main()
